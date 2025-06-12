from flask import Flask, render_template, redirect, request, make_response, url_for, jsonify, Response
from flask.templating import TemplateNotFound
import requests
import json
from functools import wraps
import time
import os
import hmac
import hashlib
from pymongo import MongoClient
import pymongo.errors
from dotenv import load_dotenv
from datetime import datetime, timedelta
import threading
import fcntl  # For file locking
import traceback  # For error tracing


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)  # Initialize Flask app at module level

# Configure for production
app.config['SERVER_NAME'] = None

# Initialize MongoDB with better error handling
MONGODB_URI = os.environ.get("MONGO_URI")
try:
    mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)  # 5 second timeout
    # Test the connection
    mongo_client.admin.command('ping')
    db = mongo_client.bronxbot
    MONGODB_AVAILABLE = True
    print("MongoDB connection successful")
except pymongo.errors.ServerSelectionTimeoutError as e:
    print(f"MongoDB connection failed: {e}")
    print("Running without database functionality")
    MONGODB_AVAILABLE = False
    db = None
except Exception as e:
    print(f"Unexpected MongoDB error: {e}")
    MONGODB_AVAILABLE = False
    db = None


# Create data directory if it doesn't exist
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Stats file path
stats_file = os.path.join(data_dir, 'stats.json')

# Check if we're running in production (use in-memory storage for ephemeral filesystems like Render)
IS_PRODUCTION = os.environ.get('FLASK_ENV') == 'production'

# Global stats dictionary for production deployments (stored in memory per session)
GLOBAL_STATS = {
    "uptime": {"days": 0, "hours": 0, "minutes": 0, "total_seconds": 0, "start_time": time.time()},
    "guilds": {"count": 76, "history": [{"count": 76, "date": "2025-06-12", "timestamp": "2025-06-12T12:56:07.470168"}], "list": [], "detailed": []},
    "commands": {
        "total_executed": 476,
        "daily_metrics": [
            {"date": "2025-06-05", "count": 45, "timestamp": "2025-06-05T23:59:59.000000"},
            {"date": "2025-06-06", "count": 52, "timestamp": "2025-06-06T23:59:59.000000"},
            {"date": "2025-06-07", "count": 38, "timestamp": "2025-06-07T23:59:59.000000"},
            {"date": "2025-06-08", "count": 67, "timestamp": "2025-06-08T23:59:59.000000"},
            {"date": "2025-06-09", "count": 41, "timestamp": "2025-06-09T23:59:59.000000"},
            {"date": "2025-06-10", "count": 55, "timestamp": "2025-06-10T23:59:59.000000"},
            {"date": "2025-06-11", "count": 73, "timestamp": "2025-06-11T23:59:59.000000"},
            {"date": "2025-06-12", "count": 132, "timestamp": "2025-06-12T13:06:28.417408"}
        ],
        "command_types": {
            "fish": 110, "fishinv": 2, "leaderboard": 2, "sellfish": 4, "shop": 6,
            "deposit": 2, "bankupgrade": 2, "pay": 2, "balance": 2
        },
        "daily_count": 0
    },
    "performance": {"user_count": 0, "latency": 0, "shard_count": 1},
    "last_updated": datetime.now().isoformat()
}

# Log the storage mode being used
print(f"Dashboard storage mode: {'PRODUCTION (in-memory)' if IS_PRODUCTION else 'DEVELOPMENT (file-based)'}")
print(f"FLASK_ENV: {os.environ.get('FLASK_ENV', 'not set')}")

# File locking mechanism
file_lock = threading.Lock()

def load_stats():
    """Load stats from MongoDB, global variable (production) or JSON file (development)"""
    global GLOBAL_STATS
    
    # Default stats structure
    default_stats = {
        "uptime": {"days": 0, "hours": 0, "minutes": 0, "total_seconds": 0, "start_time": time.time()},
        "guilds": {"count": 0, "history": [], "list": [], "detailed": []},
        "commands": {"total_executed": 0, "daily_metrics": [], "command_types": {}, "daily_count": 0},
        "performance": {"user_count": 0, "latency": 0, "shard_count": 1},
        "last_updated": datetime.now().isoformat()
    }
    
    # Try loading from MongoDB first if available
    if MONGODB_AVAILABLE and db is not None:
        try:
            # Get the global stats document
            stats_doc = db.bot_stats.find_one({"_id": "global_stats"})
            if stats_doc:
                print("Loading stats from MongoDB")
                # Create a copy of default stats to ensure all keys exist
                mongo_stats = default_stats.copy()
                
                # Update command stats
                mongo_stats["commands"]["total_executed"] = stats_doc.get("command_count", 0)
                mongo_stats["commands"]["daily_count"] = stats_doc.get("daily_commands", 0)
                mongo_stats["commands"]["command_types"] = stats_doc.get("command_types", {})
                
                # Update last_updated timestamp
                if "last_update" in stats_doc:
                    mongo_stats["last_updated"] = datetime.fromtimestamp(
                        stats_doc["last_update"]).isoformat()
                
                # Load guild information if available in stats_doc or merge with existing data
                if "guilds" in GLOBAL_STATS:
                    mongo_stats["guilds"] = GLOBAL_STATS["guilds"]
                
                # Load performance data if available or use default
                mongo_stats["performance"] = GLOBAL_STATS.get("performance", default_stats["performance"])
                
                # Update uptime if available or use default
                mongo_stats["uptime"] = GLOBAL_STATS.get("uptime", default_stats["uptime"])
                
                # Merge with GLOBAL_STATS for any missing fields
                for key in default_stats:
                    if key not in mongo_stats:
                        mongo_stats[key] = GLOBAL_STATS.get(key, default_stats[key])
                
                return mongo_stats
        except Exception as e:
            print(f"Error loading stats from MongoDB: {e}")
            # Fall back to other methods
    
    if IS_PRODUCTION:
        # Use global stats for production deployments (in-memory storage)
        # Ensure GLOBAL_STATS has all required keys
        for key, value in default_stats.items():
            if key not in GLOBAL_STATS:
                GLOBAL_STATS[key] = value
        
        # Ensure uptime has start_time for real-time calculation
        if 'start_time' not in GLOBAL_STATS.get('uptime', {}):
            GLOBAL_STATS['uptime']['start_time'] = time.time()
        
        # Calculate total_seconds for uptime display
        if 'start_time' in GLOBAL_STATS['uptime']:
            current_time = time.time()
            start_time = GLOBAL_STATS['uptime']['start_time']
            total_seconds = int(current_time - start_time)
            GLOBAL_STATS['uptime']['total_seconds'] = total_seconds
            
            # Update days, hours, minutes from total_seconds
            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            minutes = (total_seconds % 3600) // 60
            
            GLOBAL_STATS['uptime']['days'] = days
            GLOBAL_STATS['uptime']['hours'] = hours
            GLOBAL_STATS['uptime']['minutes'] = minutes
        
        return GLOBAL_STATS
    
    # Development mode: use file-based storage
    with file_lock:
        try:
            with open(stats_file, 'r') as f:
                content = f.read().strip()
                if not content or content == '{}':
                    # File is empty or contains only empty object
                    return default_stats
                stats = json.loads(content)
            # Ensure all required keys exist
            for key, value in default_stats.items():
                if key not in stats:
                    stats[key] = value
                elif isinstance(value, dict):
                    # Ensure nested keys exist
                    for nested_key, nested_value in value.items():
                        if nested_key not in stats[key]:
                            stats[key][nested_key] = nested_value
            
            # Calculate total_seconds if missing
            if 'uptime' in stats and 'total_seconds' not in stats['uptime']:
                days = stats['uptime'].get('days', 0)
                hours = stats['uptime'].get('hours', 0)
                minutes = stats['uptime'].get('minutes', 0)
                stats['uptime']['total_seconds'] = (days * 86400) + (hours * 3600) + (minutes * 60)
            
            return stats
        except FileNotFoundError:
            # Return default stats if file doesn't exist
            return default_stats
        except json.JSONDecodeError as e:
            print(f"JSON decode error loading stats: {e}")
            return default_stats
        except Exception as e:
            print(f"Error loading stats: {e}")
            return default_stats

def save_stats(stats):
    """Save stats to MongoDB (if available), global variable (production) or JSON file (development)"""
    global GLOBAL_STATS
    
    stats['last_updated'] = datetime.now().isoformat()
    
    # Try saving to MongoDB first if available
    if MONGODB_AVAILABLE and db is not None:
        try:
            print("Saving stats to MongoDB")
            # Convert stats to MongoDB-friendly format
            mongo_data = {
                "command_count": stats.get('commands', {}).get('total_executed', 0),
                "daily_commands": stats.get('commands', {}).get('daily_count', 0),
                "command_types": stats.get('commands', {}).get('command_types', {}),
                "last_update": datetime.now().timestamp(),
            }
            
            # Add daily metrics if available
            if 'daily_metrics' in stats.get('commands', {}):
                # Convert datetime strings to timestamps for MongoDB
                mongo_data['daily_metrics'] = stats['commands']['daily_metrics']
                
            # Add guild info if available
            if 'guilds' in stats:
                mongo_data['guild_count'] = stats['guilds'].get('count', 0)
                # Only store minimal guild info to avoid excessive document size
                
            # Upsert to MongoDB - use _id as "global_stats" to make it a singleton document
            db.bot_stats.update_one(
                {"_id": "global_stats"},
                {"$set": mongo_data},
                upsert=True
            )
            
            # Continue with regular storage methods as backup
        except Exception as e:
            print(f"Error saving stats to MongoDB: {e}")
            # Continue with other storage methods as fallback
    
    if IS_PRODUCTION:
        # Update global stats for production deployments (in-memory storage)
        GLOBAL_STATS.update(stats)
        return True
    
    # Development mode: use file-based storage
    with file_lock:
        try:
            # Write to a temporary file first, then rename (atomic operation)
            temp_file = stats_file + '.tmp'
            with open(temp_file, 'w') as f:
                json.dump(stats, f, indent=2)
            
            # Atomic rename
            os.rename(temp_file, stats_file)
            return True
        except Exception as e:
            print(f"Error saving stats: {e}")
            # Clean up temp file if it exists
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            return False

def update_production_stats():
    """Update stats in production mode to simulate real-time data"""
    global GLOBAL_STATS
    
    if not IS_PRODUCTION:
        return
    
    # Simulate gradual command count increases
    current_total = GLOBAL_STATS['commands']['total_executed']
    GLOBAL_STATS['commands']['total_executed'] = current_total + 1
    
    # Update today's metrics
    today = datetime.now().strftime('%Y-%m-%d')
    daily_metrics = GLOBAL_STATS['commands']['daily_metrics']
    
    # Find today's entry or create it
    today_entry = None
    for metric in daily_metrics:
        if metric.get('date') == today:
            today_entry = metric
            break
    
    if today_entry:
        today_entry['count'] += 1
        today_entry['timestamp'] = datetime.now().isoformat()
    else:
        # Add today's entry
        new_entry = {
            "date": today,
            "count": 1,
            "timestamp": datetime.now().isoformat()
        }
        daily_metrics.append(new_entry)
        
        # Keep only last 14 days
        if len(daily_metrics) > 14:
            daily_metrics.pop(0)
    
    # Update last_updated timestamp
    GLOBAL_STATS['last_updated'] = datetime.now().isoformat()

def get_guild_settings(guild_id: str):
    """Get guild settings synchronously with error handling"""
    if not MONGODB_AVAILABLE or db is None:
        print("MongoDB not available, returning default settings")
        return {
            'prefixes': ['.'],
            'welcome': {
                'enabled': False,
                'channel_id': None,
                'message': 'Welcome to the server!'
            },
            'moderation': {
                'log_channel': None,
                'mute_role': None,
                'jail_role': None
            }
        }
    
    try:
        settings = db.guild_settings.find_one({"_id": str(guild_id)})
        return settings if settings else {}
    except Exception as e:
        print(f"Error getting guild settings: {e}")
        return {}

def get_user_balance(user_id: str):
    """Get user balance from database"""
    if not MONGODB_AVAILABLE or not db:
        return {'balance': 0, 'bank': 0}
    
    try:
        user_data = db.users.find_one({"_id": str(user_id)})
        if user_data:
            return {
                'balance': user_data.get('balance', 0),
                'bank': user_data.get('bank', 0)
            }
        return {'balance': 0, 'bank': 0}
    except Exception as e:
        print(f"Error getting user balance: {e}")
        return {'balance': 0, 'bank': 0}

def get_guild_stats(guild_id: str):
    """Get guild statistics from database"""
    if not MONGODB_AVAILABLE or not db:
        return {'member_count': 0, 'message_count': 0, 'active_users': 0}
    
    try:
        stats = db.guild_stats.find_one({"_id": str(guild_id)})
        if stats:
            return {
                'member_count': stats.get('member_count', 0),
                'message_count': stats.get('message_count', 0),
                'active_users': stats.get('active_users', 0)
            }
        return {'member_count': 0, 'message_count': 0, 'active_users': 0}
    except Exception as e:
        print(f"Error getting guild stats: {e}")
        return {'member_count': 0, 'message_count': 0, 'active_users': 0}

# Add thousands filter
@app.template_filter('thousands')
def thousands_filter(value):
    """Format a number with thousands separator"""
    try:
        return "{:,}".format(int(value))
    except (ValueError, TypeError):
        return "0"

# Initialize configuration with default empty values
DISCORD_CLIENT_ID = None
DISCORD_CLIENT_SECRET = None
DISCORD_BOT_OWNER_ID = None
DISCORD_BOT_TOKEN = None
config = {}

def load_config():
    """Load configuration from environment variables or config file"""
    global DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, DISCORD_BOT_OWNER_ID, DISCORD_BOT_TOKEN, config
    
    # First try environment variables
    DISCORD_CLIENT_ID = os.environ.get('DISCORD_CLIENT_ID')
    DISCORD_CLIENT_SECRET = os.environ.get('DISCORD_CLIENT_SECRET')
    DISCORD_BOT_OWNER_ID = os.environ.get('DISCORD_BOT_OWNER_ID')
    DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
    
    # If env vars not set, try config file
    if not all([DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, DISCORD_BOT_OWNER_ID]):
        try:
            with open("data/config.json", "r") as f:
                config = json.load(f)
            DISCORD_CLIENT_ID = DISCORD_CLIENT_ID or config.get('CLIENT_ID')
            DISCORD_CLIENT_SECRET = DISCORD_CLIENT_SECRET or config.get('CLIENT_SECRET')
            DISCORD_BOT_OWNER_ID = DISCORD_BOT_OWNER_ID or config.get('OWNER_ID')
            DISCORD_BOT_TOKEN = DISCORD_BOT_TOKEN or config.get('TOKEN')
        except FileNotFoundError:
            print("Config file not found, using environment variables only")
        except json.JSONDecodeError:
            print("Invalid JSON in config file, using environment variables only")
    
    return all([DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, DISCORD_BOT_OWNER_ID])

def require_discord_config(f):
    """Decorator to ensure Discord configuration is available"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not load_config():
            return jsonify({
                "error": "Discord configuration is not set up. Please configure DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, and DISCORD_BOT_OWNER_ID."
            }), 503
        return f(*args, **kwargs)
    return decorated_function

# Try initial config load but don't fail if unsuccessful
try:
    load_config()
except Exception as e:
    print(f"Warning: Error loading initial configuration: {e}")

# Set callback URI based on environment
if os.environ.get('RENDER_EXTERNAL_URL'):
    DISCORD_REDIRECT_URI = f"{os.environ['RENDER_EXTERNAL_URL']}/callback"
else:
    DISCORD_REDIRECT_URI = 'http://localhost:5000/callback'

# Global stats dictionary
bot_stats = {
    'server_count': 0,
    'user_count': 0,
    'uptime': 0,
    'latency': 0,
    'guilds': []  # List of guild IDs where bot is present
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.cookies.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/stats', methods=['GET', 'POST'])
def api_stats():
    """Handle bot stats - GET to retrieve, POST to update from bot"""
    global bot_stats
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # print(f"Received stats update: {data}")  # Debug print
            
            # Update the global bot_stats with new format
            if 'uptime' in data:
                bot_stats['uptime'] = data['uptime'].get('total_seconds', 0)
                bot_stats['uptime_details'] = data['uptime']
            
            if 'guilds' in data:
                bot_stats['server_count'] = data['guilds'].get('count', 0)
                bot_stats['guilds'] = data['guilds'].get('list', [])
            
            if 'performance' in data:
                bot_stats['user_count'] = data['performance'].get('user_count', 0)
                bot_stats['latency'] = data['performance'].get('latency', 0)
                bot_stats['shard_count'] = data['performance'].get('shard_count', 1)
            
            # Handle command metrics and store in data/stats.json
            if 'commands' in data:
                stats_file = os.path.join('data', 'stats.json')
                
                # Load existing stats
                try:
                    with open(stats_file, 'r') as f:
                        existing_stats = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    existing_stats = {
                        "uptime": {},
                        "guilds": {"count": 0, "history": []},
                        "commands": {"total_executed": 0, "daily_metrics": [], "command_types": {}},
                        "last_updated": datetime.now().isoformat()
                    }
                
                # Update with new data
                if 'uptime' in data:
                    existing_stats['uptime'] = {
                        "days": data['uptime'].get('days', 0),
                        "hours": data['uptime'].get('hours', 0),
                        "minutes": data['uptime'].get('minutes', 0),
                        "start_time": data['uptime'].get('start_time', time.time())
                    }
                
                if 'guilds' in data:
                    existing_stats['guilds']['count'] = data['guilds'].get('count', 0)
                    # Add to history if it's a new day or significant change
                    today = datetime.now().strftime('%Y-%m-%d')
                    if not existing_stats['guilds']['history'] or \
                       existing_stats['guilds']['history'][-1]['date'] != today:
                        existing_stats['guilds']['history'].append({
                            'count': data['guilds'].get('count', 0),
                            'date': today,
                            'timestamp': datetime.now().isoformat()
                        })
                        # Keep only last 30 days
                        if len(existing_stats['guilds']['history']) > 30:
                            existing_stats['guilds']['history'] = existing_stats['guilds']['history'][-30:]
                
                if 'commands' in data:
                    if 'total_executed' in data['commands']:
                        existing_stats['commands']['total_executed'] = data['commands']['total_executed']
                    
                    if 'daily_count' in data['commands'] and data['commands']['daily_count'] > 0:
                        today = datetime.now().strftime('%Y-%m-%d')
                        # Update today's count or add new entry
                        daily_metrics = existing_stats['commands']['daily_metrics']
                        updated = False
                        for metric in daily_metrics:
                            if metric['date'] == today:
                                metric['count'] = data['commands']['daily_count']
                                metric['timestamp'] = datetime.now().isoformat()
                                updated = True
                                break
                        
                        if not updated:
                            daily_metrics.append({
                                'date': today,
                                'count': data['commands']['daily_count'],
                                'timestamp': datetime.now().isoformat()
                            })
                            # Keep only last 30 days
                            if len(daily_metrics) > 30:
                                existing_stats['commands']['daily_metrics'] = daily_metrics[-30:]
                    
                    if 'command_types' in data['commands']:
                        existing_stats['commands']['command_types'] = data['commands']['command_types']
                
                existing_stats['last_updated'] = datetime.now().isoformat()
                
                # Save updated stats
                os.makedirs('data', exist_ok=True)
                with open(stats_file, 'w') as f:
                    json.dump(existing_stats, f, indent=2)
            
            return jsonify({"status": "success", "message": "Stats updated successfully"})
            
        except Exception as e:
            print(f"Error updating stats: {e}")
            return jsonify({"error": str(e)}), 500
    
    # GET request - return current stats
    return jsonify(load_stats())

@app.route('/')
def home():
    user_id = request.cookies.get('user_id')
    
    # Load real stats from file with error handling
    try:
        stats = load_stats()
        # Ensure stats is a dictionary
        if not isinstance(stats, dict):
            stats = {
                "uptime": {"days": 0, "hours": 0, "minutes": 0},
                "guilds": {"count": 0, "history": []},
                "commands": {"total_executed": 0, "daily_metrics": [], "command_types": {}},
                "last_updated": datetime.now().isoformat()
            }
    except Exception as e:
        print(f"Error loading stats in home route: {e}")
        # Provide fallback stats
        stats = {
            "uptime": {"days": 0, "hours": 0, "minutes": 0},
            "guilds": {"count": 0, "history": []},
            "commands": {"total_executed": 0, "daily_metrics": [], "command_types": {}},
            "last_updated": datetime.now().isoformat()
        }
    
    # Only check bot owner ID if Discord config is loaded
    if DISCORD_BOT_OWNER_ID and user_id and user_id == DISCORD_BOT_OWNER_ID and request.host == 'localhost:5000':
        username = request.cookies.get('username', 'User')
        return render_template('DEVindex.html', username=username, stats=stats) 
    elif user_id:
        username = request.cookies.get('username', 'User')
        return render_template('index.html', username=username, stats=stats)
    return render_template('home.html', stats=stats)

@app.route('/login')
def login():
    if not DISCORD_CLIENT_ID:
        return "Discord configuration not set up", 503
    return redirect(f'https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify+guilds')

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return 'No authorization code provided', 400
        
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI,
        'scope': 'identify'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
    if response.status_code == 200:
        credentials = response.json()
        access_token = credentials['access_token']
        
        # Get user info
        user_response = requests.get('https://discord.com/api/users/@me', headers={
            'Authorization': f'Bearer {access_token}'
        })
        user = user_response.json()
        
        resp = make_response(redirect('/'))
        resp.set_cookie('user_id', user['id'])
        resp.set_cookie('username', user['username'])
        resp.set_cookie('avatar_hash', user.get('avatar', ''))
        resp.set_cookie('access_token', access_token)
        return resp
    return 'Authentication failed', 400

def get_lastfm_credentials():
    """Get Last.fm API credentials from env or config.json"""
    api_key = os.getenv("LASTFM_API_KEY")
    api_secret = os.getenv("LASTFM_API_SECRET")
    if api_key and api_secret:
        return api_key, api_secret
    # Fallback to config.json
    try:
        with open("data/config.json", "r") as f:
            config = json.load(f)
        api_key = api_key or config.get("LASTFM_API_KEY")
        api_secret = api_secret or config.get("LASTFM_API_SECRET")
        return api_key, api_secret
    except Exception as e:
        print(f"Could not load Last.fm credentials from config.json: {e}")
        return None, None

@app.route('/api/lastfm/callback')
def lastfm_callback():
    token = request.args.get('token')
    discord_id = request.args.get('discord_id')

    if not token or not discord_id:
        return jsonify({'error': 'Missing token or Discord ID'}), 400

    api_key, api_secret = get_lastfm_credentials()
    if not api_key or not api_secret:
        return jsonify({'error': 'Missing Last.fm credentials'}), 500

    # Generate API signature
    params = {
        'method': 'auth.getSession',
        'api_key': api_key,
        'token': token
    }
    sig_base = ''.join(f"{k}{v}" for k, v in sorted(params.items())) + api_secret
    print("Signature base string:", sig_base)
    api_sig = hashlib.md5(sig_base.encode()).hexdigest()
    print("API signature:", api_sig)

    params['api_sig'] = api_sig
    params['format'] = 'json'
    try:
        response = requests.get("https://ws.audioscrobbler.com/2.0/", params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        app.logger.error(f"Last.fm API error: {e}")
        return jsonify({'error': 'Failed to contact Last.fm', 'details': str(e)}), 500

    try:
        data = response.json()
    except Exception as e:
        app.logger.error(f"Last.fm JSON decode error: {e}")
        return jsonify({'error': 'Failed to decode Last.fm response'}), 500

    if 'error' in data:
        app.logger.warning(f"Last.fm error: {data.get('message', 'Unknown error')}")
        return jsonify({'error': data.get('message', 'Unknown Last.fm error')}), 400

    session = data.get('session')
    if not session or 'key' not in session or 'name' not in session:
        app.logger.error(f"Last.fm session missing in response: {data}")
        return jsonify({'error': 'Invalid session data from Last.fm'}), 500

    session_key = session['key']
    username = session['name']

    # Save to MongoDB or fallback to JSON file
    if MONGODB_AVAILABLE and db is not None:
        try:
            db.users.update_one(
                {"_id": str(discord_id)},
                {"$set": {"lastfm": {"username": username, "session": session_key}}},
                upsert=True
            )
        except Exception as e:
            app.logger.error(f"MongoDB error saving Last.fm session: {e}")
            return jsonify({'error': 'Failed to save Last.fm session to database'}), 500
    else:
        # Fallback: Save to JSON file
        fallback_dir = "data"
        fallback_path = os.path.join(fallback_dir, "lastfm_fallback.json")
        try:
            # Ensure the directory exists
            os.makedirs(fallback_dir, exist_ok=True)
            if os.path.exists(fallback_path):
                with open(fallback_path, "r", encoding="utf-8") as f:
                    try:
                        fallback_data = json.load(f)
                    except Exception:
                        # File is empty or invalid, start fresh
                        fallback_data = {}
            else:
                fallback_data = {}
            fallback_data[str(discord_id)] = {
                "username": username,
                "session": session_key
            }
            with open(fallback_path, "w", encoding="utf-8") as f:
                json.dump(fallback_data, f, indent=2)
        except Exception as e:
            app.logger.error(f"Error saving Last.fm session to fallback JSON: {e}")
            return jsonify({'error': 'Failed to save Last.fm session to file'}), 500

    return render_template("success.html", username=username)

@app.route('/logout')
def logout():
    resp = make_response(redirect('/'))
    resp.delete_cookie('user_id')
    resp.delete_cookie('username')
    resp.delete_cookie('access_token')
    return resp

def get_user_guilds(access_token):
    """Fetch user's Discord servers"""
    response = requests.get('https://discord.com/api/users/@me/guilds', headers={
        'Authorization': f'Bearer {access_token}'
    })
    if response.status_code == 200:
        return response.json()
    return []

def get_bot_guilds():
    """Fetch bot's server list from stats"""
    global bot_stats
    return bot_stats.get('guilds', [])

def get_bot_guild_details():
    """Fetch detailed bot guild data from stats file"""
    try:
        stats = load_stats()
        return stats.get('guilds', {}).get('detailed', [])
    except Exception as e:
        print(f"Error loading guild details: {e}")
        return []

@app.route('/health')
def health():
    """Health check endpoint for testing and monitoring"""
    try:
        # Basic health checks
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'environment': os.environ.get('FLASK_ENV', 'production')
        }
        
        # Check MongoDB connection
        if MONGODB_AVAILABLE and db is not None:
            try:
                db.admin.command('ping')
                health_status['database'] = 'connected'
            except Exception as e:
                health_status['database'] = 'disconnected'
                health_status['database_error'] = str(e)
        else:
            health_status['database'] = 'unavailable'
        
        # Check Discord configuration
        config_loaded = load_config()
        health_status['discord_config'] = 'configured' if config_loaded else 'missing'
        
        # Check required environment variables
        required_vars = ['SECRET_KEY', 'MONGO_URI']
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        health_status['environment_vars'] = 'complete' if not missing_vars else 'incomplete'
        if missing_vars:
            health_status['missing_vars'] = missing_vars
        
        # Overall status
        if (health_status['database'] in ['connected', 'unavailable'] and 
            health_status['discord_config'] == 'configured' and
            health_status['environment_vars'] == 'complete'):
            health_status['status'] = 'healthy'
            return jsonify(health_status), 200
        else:
            health_status['status'] = 'degraded'
            return jsonify(health_status), 200
            
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/test')
def api_test():
    """Test API endpoint for automated testing"""
    return jsonify({
        'message': 'API is working',
        'timestamp': datetime.now().isoformat(),
        'mongodb_available': MONGODB_AVAILABLE,
        'discord_configured': bool(DISCORD_CLIENT_ID and DISCORD_CLIENT_SECRET)
    })

@app.route('/api/test/production-stats')
def test_production_stats():
    """Test endpoint to simulate command execution in production mode"""
    if IS_PRODUCTION:
        # Simulate a command execution
        update_production_stats()
        stats = load_stats()
        return jsonify({
            'message': 'Production stats updated',
            'storage_mode': 'production (in-memory)',
            'total_commands': stats['commands']['total_executed'],
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({
            'message': 'Not in production mode',
            'storage_mode': 'development (file-based)',
            'flask_env': os.environ.get('FLASK_ENV', 'not set'),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/privacy')
@app.route('/PRIVACY')
def privacy():
    """Privacy policy page"""
    try:
        return render_template('privacy.html')
    except TemplateNotFound as e:
        print(f"Template not found: {e}")
        return f"Template not found: {e}", 404
    except Exception as e:
        print(f"Error rendering privacy template: {e}")
        return f"Error rendering privacy template: {e}", 500


@app.route('/faq')
@app.route('/FAQ')
def faq():
    """FAQ page"""
    try:
        return render_template('faq.html')
    except TemplateNotFound as e:
        print(f"Template not found: {e}")
        return f"Template not found: {e}", 404
    except Exception as e:
        print(f"Error rendering FAQ template: {e}")
        return f"Error rendering FAQ template: {e}", 500

@app.route('/servers')
@app.route('/SERVERS')
@login_required
def servers():
    """Show list of servers the user has access to"""
    access_token = request.cookies.get('access_token')
    if not access_token:
        return redirect('/login')
        
    user_guilds = get_user_guilds(access_token)
    bot_guilds = get_bot_guilds()
    bot_guild_details = get_bot_guild_details()
    
    # Create a lookup dictionary for bot guild details
    bot_guild_lookup = {detail['id']: detail for detail in bot_guild_details}
    
    # Filter guilds where user has manage server permission
    manage_guilds = [
        guild for guild in user_guilds 
        if (int(guild['permissions']) & 0x20) == 0x20  # Check for MANAGE_GUILD permission
    ]
    
    # Mark guilds where bot is present and add icon URLs and member counts
    for guild in manage_guilds:
        guild_id = str(guild['id'])
        guild['bot_present'] = guild_id in bot_guilds
        guild['icon_url'] = f"https://cdn.discordapp.com/icons/{guild['id']}/{guild['icon']}.png" if guild['icon'] else None
        
        # Add member count from bot data if available
        if guild_id in bot_guild_lookup:
            guild['member_count'] = bot_guild_lookup[guild_id].get('member_count', 0)
        else:
            guild['member_count'] = 0
            
        # Add server settings if bot is present
        if guild['bot_present']:
            guild['settings'] = get_guild_settings(guild_id)
        else:
            guild['settings'] = None
    
    # Sort guilds to show bot-present servers first
    manage_guilds.sort(key=lambda g: (not g['bot_present'], g['name'].lower()))
    
    return render_template('servers.html', 
        guilds=manage_guilds,
        username=request.cookies.get('username', 'User'),
        config={'CLIENT_ID': DISCORD_CLIENT_ID}
    )

@app.route('/webhooks/topgg', methods=['POST'])
def topgg_webhook():
    """Handle Top.gg vote webhook"""
    # Verify the signature
    TOPGG_WEBHOOK_SECRET = os.environ.get('TOPGG_WEBHOOK_SECRET')
    if not TOPGG_WEBHOOK_SECRET:
        return jsonify({"error": "Webhook secret not configured"}), 500
        
    signature = request.headers.get('Authorization')
    if not signature:
        return jsonify({"error": "Unauthorized"}), 401
    
    # Verify HMAC signature
    body = request.get_data()
    expected_signature = hmac.new(
        TOPGG_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        return jsonify({"error": "Invalid signature"}), 401
    
    data = request.json
    user_id = data['user']
    
    try:
        # Process the vote reward (1000 coins)
        reward_amount = 1000
        db.users.update_one(
            {"_id": str(user_id)},
            {
                "$inc": {"wallet": reward_amount},
                "$set": {"last_vote": datetime.now()}
            },
            upsert=True
        )
        
        # Log the vote
        print(f"Processed vote reward for user {user_id}")
        return jsonify({"success": True}), 200
        
    except Exception as e:
        print(f"Error processing vote: {e}")
        return jsonify({"error": "Failed to process vote"}), 500

@app.route('/servers/<guild_id>/settings')
@login_required
def server_settings(guild_id):
    """Show settings for a specific server"""
    access_token = request.cookies.get('access_token')
    if not access_token:
        return redirect('/login')
        
    # Verify user has access to this server
    user_guilds = get_user_guilds(access_token)
    if not any(g['id'] == guild_id and (int(g['permissions']) & 0x20) == 0x20 for g in user_guilds):
        return "Unauthorized", 403

    # Get server settings from database
    settings = get_guild_settings(guild_id)
    
    # Initialize default values if settings is empty
    guild_info = None
    channels = []
    roles = []
    
    # Only try to get Discord API data if bot token is available
    if DISCORD_BOT_TOKEN:
        headers = {'Authorization': f'Bot {DISCORD_BOT_TOKEN}'}
        try:
            guild_response = requests.get(f'https://discord.com/api/v10/guilds/{guild_id}', headers=headers)
            channels_response = requests.get(f'https://discord.com/api/v10/guilds/{guild_id}/channels', headers=headers)
            roles_response = requests.get(f'https://discord.com/api/v10/guilds/{guild_id}/roles', headers=headers)
            
            guild_info = guild_response.json() if guild_response.ok else None
            channels = channels_response.json() if channels_response.ok else []
            roles = roles_response.json() if roles_response.ok else []
        except Exception as e:
            print(f"Error fetching Discord API data: {e}")
    else:
        print("No bot token available, using minimal guild info")
        # Use basic guild info from user's guild list
        user_guild = next((g for g in user_guilds if g['id'] == guild_id), None)
        if user_guild:
            guild_info = {
                'id': user_guild['id'],
                'name': user_guild['name'],
                'icon': user_guild.get('icon')
            }
    
    # Filter text channels only and sort by position
    text_channels = sorted(
        [c for c in channels if c.get('type') == 0],  # 0 is text channel
        key=lambda c: c.get('position', 0)
    )
    
    # Sort roles by position
    roles = sorted(roles, key=lambda r: r.get('position', 0), reverse=True)
    
    return render_template('settings.html',
        guild=guild_info,
        settings=settings,
        channels=text_channels,
        roles=roles,
        username=request.cookies.get('username', 'User'),
        mongodb_available=MONGODB_AVAILABLE
    )

@app.route('/servers/<guild_id>/settings/update', methods=['POST'])
@login_required
def update_settings(guild_id):
    """Update settings for a specific server"""
    access_token = request.cookies.get('access_token')
    if not access_token:
        return redirect('/login')
        
    # Verify user has access to this server
    user_guilds = get_user_guilds(access_token)
    if not any(g['id'] == guild_id and (int(g['permissions']) & 0x20) == 0x20 for g in user_guilds):
        return "Unauthorized", 403
    
    if not MONGODB_AVAILABLE:
        return redirect(f'/servers/{guild_id}/settings?error=database_unavailable')
        
    # Get settings from form
    settings = {
        'prefixes': [p.strip() for p in request.form.get('prefixes', '').split(',') if p.strip()],
        'welcome': {
            'enabled': bool(request.form.get('welcome_enabled')),
            'channel_id': request.form.get('welcome_channel'),
            'message': request.form.get('welcome_message')
        },
        'moderation': {
            'log_channel': request.form.get('log_channel'),
            'mute_role': request.form.get('mute_role'),
            'jail_role': request.form.get('jail_role')
        }
    }
    
    try:
        # Update database
        result = db.guild_settings.update_one(
            {"_id": str(guild_id)},
            {"$set": settings},
            upsert=True
        )
        
        if result.acknowledged:
            return redirect(f'/servers/{guild_id}/settings?success=1')
        else:
            return redirect(f'/servers/{guild_id}/settings?error=1')
    except Exception as e:
        print(f"Error updating guild settings: {e}")
        return redirect(f'/servers/{guild_id}/settings?error=1')

@app.route('/settings')
@login_required
def settings_redirect():
    """Redirect settings to servers page"""
    return redirect('/servers')

@app.route('/api/guild/<guild_id>/quick-setting', methods=['POST'])
@login_required
def update_quick_setting(guild_id):
    """API endpoint to update quick settings"""
    try:
        data = request.get_json()
        setting = data.get('setting')
        enabled = data.get('enabled', False)
        
        # Verify user has access to this server
        access_token = request.cookies.get('access_token')
        if not access_token:
            return jsonify({"success": False, "error": "No access token"}), 401
        
        user_guilds = get_user_guilds(access_token)
        user_guild = next((g for g in user_guilds if str(g['id']) == str(guild_id)), None)
        if not user_guild or not (int(user_guild['permissions']) & 0x20):
            return jsonify({"success": False, "error": "Unauthorized"}), 403
        
        # Update setting in database
        if MONGODB_AVAILABLE and db:
            update_data = {}
            if setting == 'welcome_messages':
                update_data['welcome.enabled'] = enabled
            elif setting == 'auto_moderation':
                update_data['moderation.automod_enabled'] = enabled
            
            result = db.guild_settings.update_one(
                {"_id": str(guild_id)},
                {"$set": update_data},
                upsert=True
            )
            
            return jsonify({"success": True, "message": "Setting updated successfully"})
        else:
            return jsonify({"success": False, "error": "Database not available"}), 503
            
    except Exception as e:
        print(f"Error updating quick setting: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/user/<user_id>/balance')
@login_required
def get_user_balance_api(user_id):
    """API endpoint to get user balance"""
    # Only allow the user to see their own balance or allow bot owner to see any balance
    requester_id = request.cookies.get('user_id')
    if requester_id != user_id and requester_id != DISCORD_BOT_OWNER_ID:
        return jsonify({"error": "Unauthorized"}), 403
    
    balance = get_user_balance(user_id)
    return jsonify(balance)

def is_owner(user_id):
    """Check if user is the bot owner"""
    return str(user_id) == str(DISCORD_BOT_OWNER_ID)

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard - only accessible to bot owner"""
    load_config()  # Ensure config is loaded
    
    # Check if user is logged in
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    # Check if user is the bot owner
    if not is_owner(user_id):
        return render_template('error.html',
                             error_code=403,
                             error_message="Access forbidden - Admin only",
                             username=request.cookies.get('username')), 403
    
    try:
        # Get comprehensive stats for admin view
        stats = load_stats()
        
        # Get additional admin-specific data
        admin_data = {
            'total_guilds': stats.get('guilds', {}).get('count', 0),
            'total_commands': stats.get('commands', {}).get('total_executed', 0),
            'uptime': stats.get('uptime', {}),
            'performance': stats.get('performance', {}),
            'last_updated': stats.get('last_updated', 'Never')
        }
        
        return render_template('DEVindex.html', 
                             stats=stats,
                             admin_data=admin_data,
                             is_admin=True,
                             username=request.cookies.get('username'))
    except Exception as e:
        print(f"Error loading admin dashboard: {e}")
        return render_template('error.html',
                             error_code=500,
                             error_message="Failed to load admin dashboard",
                             username=request.cookies.get('username')), 500

@app.route('/api/guild/<guild_id>/stats')
@login_required
def get_guild_stats_api(guild_id):
    """API endpoint to get guild stats"""
    access_token = request.cookies.get('access_token')
    if not access_token:
        return jsonify({"error": "No access token"}), 401
        
    # Verify user has access to this server
    user_guilds = get_user_guilds(access_token)
    if not any(g['id'] == guild_id and (int(g['permissions']) & 0x20) == 0x20 for g in user_guilds):
        return jsonify({"error": "Unauthorized"}), 403
    
    stats = get_guild_stats(guild_id)
    return jsonify(stats)

@app.route('/debug')
def debug():
    """Debug endpoint to check application status"""
    return jsonify({
        'status': 'ok',
        'env': os.environ.get('FLASK_ENV'),
        'discord_configured': load_config(),
        'mongodb_available': MONGODB_AVAILABLE,
        'bot_token_available': bool(DISCORD_BOT_TOKEN),
        'redirect_uri': DISCORD_REDIRECT_URI,
        'config_source': 'env' if any([os.environ.get('DISCORD_CLIENT_ID'),
                                     os.environ.get('DISCORD_CLIENT_SECRET'),
                                     os.environ.get('DISCORD_BOT_OWNER_ID')]) else 'config_file',
        'missing_config': [k for k in ['DISCORD_CLIENT_ID', 'DISCORD_CLIENT_SECRET', 'DISCORD_BOT_OWNER_ID']
                          if not os.environ.get(k) and not config.get(k.split('_', 1)[1])]
    })

# API Routes for Stats Management
@app.route('/api/stats')
def get_stats_api():
    """Get all statistics"""
    stats = load_stats()
    return jsonify(stats)

@app.route('/api/stats/update', methods=['POST'])
def update_stats_endpoint():
    """Dedicated endpoint for bot to update stats"""
    return api_stats()  # Reuse the existing logic

@app.route('/invite')
async def invite():
    """Redirect to bot invite page"""
    if not DISCORD_CLIENT_ID:
        return "Discord configuration not set up", 503
    return redirect(f'https://discord.com/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&permissions=10140354735863&response_type=code&redirect_uri={DISCORD_REDIRECT_URI}&integration_type=0&scope=identify+guilds+bot+applications.commands.permissions.update+applications.commands')

@app.route('/api/stats/realtime', methods=['POST'])
def realtime_stats_update():
    """Handle real-time command execution updates from bot"""
    try:
        data = request.get_json()
        print(f"Realtime stats received: {data}")  # Debug logging
        
        if not data or data.get('type') != 'command_update':
            print(f"Invalid data type: {data.get('type') if data else 'No data'}")  # Debug logging
            return jsonify({"error": "Invalid real-time update data"}), 400
        
        # Handle MongoDB direct update if available
        if MONGODB_AVAILABLE and db is not None:
            try:
                # Get the command name if provided
                command_name = data.get('command')
                
                # Update MongoDB directly for better performance
                update_data = {
                    "$inc": {
                        "command_count": 1,
                        "daily_commands": 1
                    },
                    "$set": {
                        "last_update": datetime.now().timestamp()
                    }
                }
                
                # Update command type counter if command name provided
                if command_name:
                    update_data["$inc"][f"command_types.{command_name}"] = 1
                
                # Update MongoDB
                db.bot_stats.update_one(
                    {"_id": "global_stats"},
                    update_data,
                    upsert=True
                )
                
                # Continue loading stats for the response
            except Exception as e:
                print(f"Error with direct MongoDB update: {e}")
                # Continue with regular stats loading as fallback
        
        # Load stats with error handling
        try:
            stats = load_stats()
        except Exception as e:
            print(f"Error loading stats for real-time update: {e}")
            # Return a basic response but don't fail
            return jsonify({"error": "Could not load stats", "details": str(e)}), 500
        
        # Initialize commands structure if it doesn't exist or is corrupted
        if not isinstance(stats, dict):
            print("Stats is not a dictionary, using default")
            stats = {
                "uptime": {"days": 0, "hours": 0, "minutes": 0, "total_seconds": 0, "start_time": time.time()},
                "guilds": {"count": 0, "history": [], "list": [], "detailed": []},
                "commands": {"total_executed": 0, "daily_metrics": [], "command_types": {}, "daily_count": 0},
                "performance": {"user_count": 0, "latency": 0, "shard_count": 1},
                "last_updated": datetime.now().isoformat()
            }
        
        if 'commands' not in stats or not isinstance(stats['commands'], dict):
            stats['commands'] = {
                'total_executed': 0,
                'daily_metrics': [],
                'command_types': {},
                'daily_count': 0
            }
        
        # Update total commands
        if 'total_commands' in data:
            stats['commands']['total_executed'] = data['total_commands']
        else:
            # Increment total commands if not provided
            stats['commands']['total_executed'] = stats['commands'].get('total_executed', 0) + 1
        
        # Update today's count
        today = datetime.now().strftime('%Y-%m-%d')
        daily_metrics = stats['commands'].get('daily_metrics', [])
        
        # Find today's entry or create it
        updated = False
        for metric in daily_metrics:
            if metric.get('date') == today:
                metric['count'] = metric.get('count', 0) + 1
                metric['timestamp'] = datetime.now().isoformat()
                updated = True
                break
        
        if not updated:
            daily_metrics.append({
                'date': today,
                'count': 1,
                'timestamp': datetime.now().isoformat()
            })
            stats['commands']['daily_metrics'] = daily_metrics
            
            # Update MongoDB directly with the new daily metric if available
            if MONGODB_AVAILABLE and db is not None:
                try:
                    # Add the new daily metric to MongoDB array
                    today_metric = {
                        'date': today,
                        'count': 1,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    db.bot_stats.update_one(
                        {"_id": "global_stats"},
                        {"$push": {"daily_metrics": today_metric}},
                        upsert=True
                    )
                except Exception as e:
                    print(f"Error updating daily metrics in MongoDB: {e}")
                    # Continue with regular stats saving as fallback
        
        # Update command types
        if 'command' in data:
            command_types = stats['commands'].get('command_types', {})
            command_name = data['command']
            command_types[command_name] = command_types.get(command_name, 0) + 1
            stats['commands']['command_types'] = command_types
        
        # Save stats with error handling
        try:
            save_success = save_stats(stats)
            if not save_success:
                print("Failed to save stats but continuing")
        except Exception as e:
            print(f"Error saving stats: {e}")
            # Don't fail the request, just log the error
        
        return jsonify({
            "status": "success", 
            "message": "Real-time stats updated",
            "updated_stats": {
                "total_commands": stats['commands']['total_executed'],
                "today_commands": next((m['count'] for m in daily_metrics if m.get('date') == today), 0),
                "command": data.get('command'),
                "error": data.get('error', False)
            }
        })
        
    except Exception as e:
        print(f"Error in real-time stats update: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/metrics/commands')
def get_command_metrics():
    """Get command metrics for charts"""
    try:
        # Initialize variables
        daily_metrics = []
        command_types = {}
        
        # Try to get metrics from MongoDB first
        if MONGODB_AVAILABLE and db is not None:
            try:
                stats_doc = db.bot_stats.find_one({"_id": "global_stats"})
                if stats_doc:
                    # Get daily metrics if available in MongoDB
                    if 'daily_metrics' in stats_doc:
                        daily_metrics = stats_doc['daily_metrics']
                    # Get command types from MongoDB
                    if 'command_types' in stats_doc:
                        command_types = stats_doc['command_types']
                    else:
                        # Fall back to getting command types from regular stats
                        stats = load_stats()
                        command_types = stats.get('commands', {}).get('command_types', {})
                else:
                    # MongoDB document doesn't exist, fall back to file
                    stats = load_stats()
                    daily_metrics = stats.get('commands', {}).get('daily_metrics', [])
                    command_types = stats.get('commands', {}).get('command_types', {})
            except Exception as e:
                print(f"Error loading command metrics from MongoDB: {e}")
                # Fall back to file-based storage
                stats = load_stats()
                daily_metrics = stats.get('commands', {}).get('daily_metrics', [])
                command_types = stats.get('commands', {}).get('command_types', {})
        else:
            # No MongoDB, use file-based storage
            stats = load_stats()
            daily_metrics = stats.get('commands', {}).get('daily_metrics', [])
            command_types = stats.get('commands', {}).get('command_types', {})
        
        # Get last 7 days of data
        last_7_days = daily_metrics[-7:] if len(daily_metrics) >= 7 else daily_metrics
        
        # Calculate totals and percentage change
        total_last_7_days = sum(day.get('count', 0) for day in last_7_days)
        
        # Calculate percentage change (compare to previous 7 days)
        percentage_change = 0
        if len(daily_metrics) >= 14:
            previous_7_days = daily_metrics[-14:-7]
            total_previous_7_days = sum(day.get('count', 0) for day in previous_7_days)
            if total_previous_7_days > 0:
                percentage_change = round(((total_last_7_days - total_previous_7_days) / total_previous_7_days) * 100, 1)
        
        # Ensure we have 7 days of data (fill with zeros if needed)
        while len(last_7_days) < 7:
            last_7_days.insert(0, {'date': '', 'count': 0})
        
        return jsonify({
            'daily_data': last_7_days,
            'total_last_7_days': total_last_7_days,
            'percentage_change': percentage_change,
            'command_types': command_types
        })
        
    except Exception as e:
        print(f"Error getting command metrics: {e}")
        import traceback
        traceback.print_exc()  # Print full traceback for better debugging
        # Return default data
        return jsonify({
            'daily_data': [{'date': '', 'count': 0} for _ in range(7)],
            'total_last_7_days': 0,
            'percentage_change': 0,
            'command_types': {}
        })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('error.html', 
                         error_code=404,
                         error_message="Page not found",
                         username=request.cookies.get('username')), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('error.html',
                         error_code=500,
                         error_message="Internal server error",
                         username=request.cookies.get('username')), 500

@app.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    return render_template('error.html',
                         error_code=403,
                         error_message="Access forbidden",
                         username=request.cookies.get('username')), 403

# Set app secret key
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

def sync_stats_to_mongodb():
    """Helper function to synchronize local stats with MongoDB"""
    if not MONGODB_AVAILABLE or db is None:
        return False
    
    try:
        # Get local stats
        local_stats = None
        
        # First try in-memory stats (production mode)
        if IS_PRODUCTION and GLOBAL_STATS:
            local_stats = GLOBAL_STATS
        else:
            # Try file-based storage
            with file_lock:
                try:
                    with open(stats_file, 'r') as f:
                        content = f.read().strip()
                        if content and content != '{}':
                            local_stats = json.loads(content)
                except (FileNotFoundError, json.JSONDecodeError):
                    pass
        
        if not local_stats:
            print("No local stats to sync to MongoDB")
            return False
            
        # Convert to MongoDB format
        mongo_data = {
            "command_count": local_stats.get('commands', {}).get('total_executed', 0),
            "daily_commands": local_stats.get('commands', {}).get('daily_count', 0),
            "command_types": local_stats.get('commands', {}).get('command_types', {}),
            "last_update": datetime.now().timestamp()
        }
        
        # Add daily metrics if available
        if 'daily_metrics' in local_stats.get('commands', {}):
            mongo_data['daily_metrics'] = local_stats['commands']['daily_metrics']
            
        # Add guild info if available
        if 'guilds' in local_stats:
            mongo_data['guild_count'] = local_stats['guilds'].get('count', 0)
            
        # Update MongoDB with upsert to ensure document exists
        result = db.bot_stats.update_one(
            {"_id": "global_stats"},
            {"$set": mongo_data},
            upsert=True
        )
        
        print(f"Synced local stats to MongoDB: {result.modified_count} documents modified")
        return True
    except Exception as e:
        print(f"Error syncing stats to MongoDB: {e}")
        return False

# Run sync on startup if the file exists but MongoDB might be empty
try:
    if MONGODB_AVAILABLE and db is not None:
        sync_stats_to_mongodb()
except Exception as e:
    print(f"Error during initial stats sync: {e}")

@app.route('/api/admin/sync_stats', methods=['POST'])
def admin_sync_stats():
    """Admin endpoint to manually trigger a sync of stats to MongoDB"""
    try:
        # Check for authorization (basic security)
        auth_header = request.headers.get('Authorization')
        admin_key = os.environ.get('ADMIN_KEY', 'default_admin_key')  # Set this in your environment!
        
        if not auth_header or auth_header != f"Bearer {admin_key}":
            return jsonify({"error": "Unauthorized"}), 401
            
        # Trigger the sync
        if sync_stats_to_mongodb():
            return jsonify({
                "status": "success",
                "message": "Stats synced to MongoDB"
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to sync stats. Check logs for details."
            }), 500
            
    except Exception as e:
        print(f"Error in admin sync stats endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
