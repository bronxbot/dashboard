import json
import os
import time
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Optional
import threading

class CommandUsageTracker:
    def __init__(self):
        self.command_counts = defaultdict(int)
        self.daily_counts = defaultdict(int)
        self.total_commands = 0
        self.hourly_counts = defaultdict(int)
        self.command_history = deque(maxlen=1000)  # Keep last 1000 commands
        self.error_counts = defaultdict(int)
        self.user_command_counts = defaultdict(int)
        self.guild_command_counts = defaultdict(int)
        self.execution_times = defaultdict(list)
        
        # Real-time stats for dashboard
        self.current_session_commands = 0
        self.session_start_time = time.time()
        self.last_command_time = None
        
        # Auto-save settings
        self.auto_save_interval = 300  # 5 minutes
        self.auto_save_task = None
        self.data_file = "data/command_usage.json"
        
        # Load existing data
        self.load_data()
        
        # Start background tasks
        self._running = True
        self.background_task = None

    def load_data(self):
        """Load command usage data from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.command_counts = defaultdict(int, data.get('command_counts', {}))
                    self.daily_counts = defaultdict(int, data.get('daily_counts', {}))
                    self.total_commands = data.get('total_commands', 0)
                    self.hourly_counts = defaultdict(int, data.get('hourly_counts', {}))
                    self.error_counts = defaultdict(int, data.get('error_counts', {}))
                    self.user_command_counts = defaultdict(int, data.get('user_command_counts', {}))
                    self.guild_command_counts = defaultdict(int, data.get('guild_command_counts', {}))
                    
                    # Load execution times (keep only recent ones)
                    exec_times = data.get('execution_times', {})
                    for cmd, times in exec_times.items():
                        # Only keep recent execution times (last 100 per command)
                        self.execution_times[cmd] = deque(times[-100:], maxlen=100)
                    
                    logging.info(f"Loaded command usage data: {self.total_commands} total commands")
        except Exception as e:
            logging.error(f"Failed to load command usage data: {e}")

    def save_data(self):
        """Save command usage data to file"""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            # Convert execution times to regular lists for JSON serialization
            exec_times = {}
            for cmd, times in self.execution_times.items():
                exec_times[cmd] = list(times)
            
            data = {
                'command_counts': dict(self.command_counts),
                'daily_counts': dict(self.daily_counts),
                'total_commands': self.total_commands,
                'hourly_counts': dict(self.hourly_counts),
                'error_counts': dict(self.error_counts),
                'user_command_counts': dict(self.user_command_counts),
                'guild_command_counts': dict(self.guild_command_counts),
                'execution_times': exec_times,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            logging.debug("Command usage data saved successfully")
        except Exception as e:
            logging.error(f"Failed to save command usage data: {e}")

    def track_command(self, ctx, command_name: str, execution_time: float, error: bool = False):
        """Track a command execution"""
        try:
            # Update counters
            self.command_counts[command_name] += 1
            self.total_commands += 1
            self.current_session_commands += 1
            self.last_command_time = time.time()
            
            # Track daily counts
            today = datetime.now().strftime('%Y-%m-%d')
            self.daily_counts[today] += 1
            
            # Track hourly counts
            current_hour = datetime.now().strftime('%Y-%m-%d-%H')
            self.hourly_counts[current_hour] += 1
            
            # Track user and guild
            if hasattr(ctx, 'author') and ctx.author:
                self.user_command_counts[str(ctx.author.id)] += 1
            
            if hasattr(ctx, 'guild') and ctx.guild:
                self.guild_command_counts[str(ctx.guild.id)] += 1
            
            # Track execution time
            self.execution_times[command_name].append(execution_time)
            
            # Track errors
            if error:
                self.error_counts[command_name] += 1
            
            # Add to history
            self.command_history.append({
                'command': command_name,
                'timestamp': time.time(),
                'user_id': str(ctx.author.id) if hasattr(ctx, 'author') and ctx.author else None,
                'guild_id': str(ctx.guild.id) if hasattr(ctx, 'guild') and ctx.guild else None,
                'execution_time': execution_time,
                'error': error
            })
            
            # Send real-time update to dashboard if not in dev mode
            asyncio.create_task(self._send_realtime_update(command_name, execution_time, error))
            
        except Exception as e:
            logging.error(f"Error tracking command: {e}")

    async def _send_realtime_update(self, command_name: str, execution_time: float, error: bool):
        """Send real-time command update to dashboard"""
        try:
            # Check if we're in development mode by looking for config
            is_dev = False
            try:
                with open("data/config.json", "r") as f:
                    config = json.load(f)
                    is_dev = config.get('DEV', False)
            except:
                pass
                
            # Don't send if in dev mode 
            if is_dev:
                logging.debug("Skipping real-time update in development mode")
                return
                
            update_data = {
                'type': 'command_executed',
                'command': command_name,
                'timestamp': time.time(),
                'execution_time': execution_time,
                'error': error,
                'total_commands': self.total_commands,
                'session_commands': self.current_session_commands
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://bronxbot.onrender.com/api/stats/realtime',
                    json=update_data,
                    timeout=5
                ) as resp:
                    if resp.status == 200:
                        logging.debug("Real-time update sent successfully")
                    else:
                        logging.warning(f"Failed to send realtime update: {resp.status}")
                        
        except Exception as e:
            logging.debug(f"Failed to send realtime update: {e}")

    def get_daily_stats(self) -> int:
        """Get today's command count"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.daily_counts.get(today, 0)

    def get_total_commands(self) -> int:
        """Get total command count"""
        return self.total_commands

    def get_command_breakdown(self) -> Dict[str, int]:
        """Get command breakdown"""
        return dict(self.command_counts)

    def get_hourly_stats(self) -> Dict[str, int]:
        """Get hourly command statistics"""
        return dict(self.hourly_counts)

    def get_error_stats(self) -> Dict[str, int]:
        """Get error statistics"""
        return dict(self.error_counts)

    def get_top_commands(self, limit: int = 10) -> List[tuple]:
        """Get top commands by usage"""
        return sorted(self.command_counts.items(), key=lambda x: x[1], reverse=True)[:limit]

    def get_recent_commands(self, limit: int = 50) -> List[dict]:
        """Get recent command history"""
        return list(self.command_history)[-limit:]

    def get_average_execution_time(self, command_name: str) -> float:
        """Get average execution time for a command"""
        times = self.execution_times.get(command_name, [])
        return sum(times) / len(times) if times else 0.0

    def get_session_stats(self) -> Dict:
        """Get current session statistics"""
        session_duration = time.time() - self.session_start_time
        return {
            'commands_this_session': self.current_session_commands,
            'session_duration': session_duration,
            'commands_per_minute': (self.current_session_commands / (session_duration / 60)) if session_duration > 0 else 0,
            'last_command_time': self.last_command_time
        }

    def start_auto_save(self):
        """Start the auto-save background task"""
        if self.auto_save_task is None or self.auto_save_task.done():
            self.auto_save_task = asyncio.create_task(self._auto_save_loop())
            logging.info("Command tracker auto-save started")

    async def _auto_save_loop(self):
        """Background task to auto-save data"""
        while self._running:
            try:
                await asyncio.sleep(self.auto_save_interval)
                if self._running:
                    self.save_data()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in auto-save loop: {e}")

    def cleanup(self):
        """Cleanup resources"""
        self._running = False
        if self.auto_save_task and not self.auto_save_task.done():
            self.auto_save_task.cancel()
        
        # Final save
        self.save_data()
        logging.info("Command tracker cleanup completed")

    def reset_daily_stats(self):
        """Reset daily statistics (called at midnight)"""
        today = datetime.now().strftime('%Y-%m-%d')
        self.daily_counts[today] = 0

    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old data to prevent memory bloat"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            cutoff_str = cutoff_date.strftime('%Y-%m-%d')
            
            # Clean up daily counts
            keys_to_remove = [k for k in self.daily_counts.keys() if k < cutoff_str]
            for key in keys_to_remove:
                del self.daily_counts[key]
            
            # Clean up hourly counts
            cutoff_hour = cutoff_date.strftime('%Y-%m-%d-%H')
            keys_to_remove = [k for k in self.hourly_counts.keys() if k < cutoff_hour]
            for key in keys_to_remove:
                del self.hourly_counts[key]
            
            logging.info(f"Cleaned up old command tracking data (kept {days_to_keep} days)")
            
        except Exception as e:
            logging.error(f"Error cleaning up old data: {e}")

# Global instance
usage_tracker = CommandUsageTracker()
