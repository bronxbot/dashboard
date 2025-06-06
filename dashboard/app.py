from flask import Flask, render_template, redirect, request, make_response, url_for, jsonify, Response
import requests
import json
from functools import wraps
import time
import os
import hmac
import hashlib
import datetime
from pymongo import MongoClient
import pymongo.errors
from dotenv import load_dotenv


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


def get_guild_settings(guild_id: str):
    """Get guild settings synchronously with error handling"""
    if not MONGODB_AVAILABLE or db is None:
        print("MongoDB not available, returning default settings")
        return {
            'prefixes': ['!'],
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

def get_guild_settings(guild_id: str):
    """Get guild settings synchronously with error handling"""
    if not MONGODB_AVAILABLE or db is None:
        print("MongoDB not available, returning default settings")
        return {
            'prefixes': ['!'],
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

def get_guild_settings(guild_id: str):
    """Get guild settings synchronously with error handling"""
    if not MONGODB_AVAILABLE or db is None:
        print("MongoDB not available, returning default settings")
        return {
            'prefixes': ['!'],
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
    global bot_stats
    if request.method == 'POST':
        bot_stats.update(request.json)
        return jsonify({"status": "success"})
    return jsonify(bot_stats)

@app.route('/')
def home():
    user_id = request.cookies.get('user_id')
    # Only check bot owner ID if Discord config is loaded
    if DISCORD_BOT_OWNER_ID and user_id and user_id == DISCORD_BOT_OWNER_ID and request.host == 'localhost:5000':
        username = request.cookies.get('username', 'User')
        return render_template('DEVindex.html', username=username, stats=bot_stats) 
    elif user_id:
        username = request.cookies.get('username', 'User')
        return render_template('index.html', username=username, stats=bot_stats)
    return render_template('home.html', stats=bot_stats)

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

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'mongodb_available': MONGODB_AVAILABLE,
        'discord_configured': load_config()
    })

@app.route('/servers')
@login_required
def servers():
    """Show list of servers the user has access to"""
    access_token = request.cookies.get('access_token')
    if not access_token:
        return redirect('/login')
        
    user_guilds = get_user_guilds(access_token)
    bot_guilds = get_bot_guilds()
    
    # Filter guilds where user has manage server permission
    manage_guilds = [
        guild for guild in user_guilds 
        if (int(guild['permissions']) & 0x20) == 0x20  # Check for MANAGE_GUILD permission
    ]
    
    # Mark guilds where bot is present and add icon URLs
    for guild in manage_guilds:
        guild['bot_present'] = str(guild['id']) in bot_guilds
        guild['icon_url'] = f"https://cdn.discordapp.com/icons/{guild['id']}/{guild['icon']}.png" if guild['icon'] else None
    
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
                "$set": {"last_vote": datetime.datetime.utcnow()}
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
def settings_select():
    """Show server selection for settings"""
    access_token = request.cookies.get('access_token')
    if not access_token:
        return redirect('/login')
        
    user_guilds = get_user_guilds(access_token)
    bot_guilds = get_bot_guilds()
    
    # Filter guilds where user has manage server permission
    manage_guilds = [
        guild for guild in user_guilds 
        if (int(guild['permissions']) & 0x20) == 0x20
    ]
    
    # Add bot presence info
    for guild in manage_guilds:
        guild['bot_present'] = str(guild['id']) in bot_guilds
        guild['icon_url'] = f"https://cdn.discordapp.com/icons/{guild['id']}/{guild['icon']}.png" if guild['icon'] else None
    
    # Sort guilds to show bot-present servers first
    manage_guilds.sort(key=lambda g: (not g['bot_present'], g['name'].lower()))
    
    return render_template('settings_select.html',
        guilds=manage_guilds,
        username=request.cookies.get('username', 'User'),
        config={'CLIENT_ID': DISCORD_CLIENT_ID}
    )

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

# Error handlers
@app.errorhandler(500)
def server_error(e):
    return jsonify({
        'error': 'Internal Server Error',
        'message': str(e),
        'type': '500'
    }), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'error': 'Not Found',
        'message': str(e),
        'type': '404'
    }), 404

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    if request.headers.get('Accept', '').startswith('application/json'):
        return jsonify({"error": "Not found"}), 404
    return render_template('home.html', stats=bot_stats), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    if request.headers.get('Accept', '').startswith('application/json'):
        return jsonify({"error": "Internal server error"}), 500
    return render_template('home.html', stats=bot_stats, error="Internal server error"), 500

def get_available_port(start_port, max_port=65535):
    """Find first available port in range"""
    import socket
    for port in range(start_port, max_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                s.close()
                return port
        except OSError:
            continue
    return None

def run(as_thread=False):
    """Run the Flask application server
    
    Args:
        as_thread (bool): If True, run in a separate thread for the Discord bot
    """
    default_port = int(os.environ.get('PORT', 5000))
    port = get_available_port(default_port)
    if not port:
        port = get_available_port(8000)  # Try alternate port range
    if not port:
        raise RuntimeError("No available ports found")
        
    host = '0.0.0.0' if os.environ.get('FLASK_ENV') == 'production' else '127.0.0.1'
    
    if as_thread:
        import threading
        from werkzeug.serving import make_server
        
        server = make_server(host, port, app, threaded=True)
        print(f"Web server starting on http://{host}:{port}")
        
        def run_server():
            server.serve_forever()
            
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
    else:
        # Only use debug mode when running directly (not in thread)
        debug = os.environ.get('FLASK_ENV') != 'production'
        app.run(host=host, port=port, debug=debug)

def shutdown_server():
    """Shutdown the Flask server (placeholder for now)"""
    pass

@app.route('/api/stats/live')
def live_stats():
    def generate():
        while True:
            # Read the latest stats from the file
            try:
                with open('data/stats.json', 'r') as f:
                    stats = json.load(f)
                    data = f"data: {json.dumps(stats)}\n\n"
                    yield data
            except Exception as e:
                print(f"Error reading stats: {e}")
                yield "data: {}\n\n"
            time.sleep(1)  # Update every second

    return Response(generate(), mimetype='text/event-stream')

@app.route("/invite")
def invite():
    return redirect("https://discord.com/oauth2/authorize?client_id=828380019406929962&permissions=8&response_type=code&redirect_uri=https%3A%2F%2Fbronxbot.onrender.com%2Fcallback&integration_type=0&scope=bot+identify+guilds+applications.commands")

@app.route('/api/lastfm/unlink', methods=['POST'])
@login_required
def lastfm_unlink():
    """Unlink Last.fm account for the logged-in user."""
    user_id = request.cookies.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401

    if MONGODB_AVAILABLE and db is not None:
        try:
            result = db.users.update_one(
                {"_id": str(user_id)},
                {"$unset": {"lastfm": ""}}
            )
            if result.modified_count > 0:
                return jsonify({'success': True, 'message': 'Last.fm account unlinked.'})
            else:
                return jsonify({'success': False, 'message': 'No Last.fm account linked.'})
        except Exception as e:
            app.logger.error(f"MongoDB error unlinking Last.fm: {e}")
            return jsonify({'error': 'Failed to unlink Last.fm from database'}), 500
    else:
        # Fallback: Remove from JSON file
        fallback_dir = "data"
        fallback_path = os.path.join(fallback_dir, "lastfm_fallback.json")
        try:
            if os.path.exists(fallback_path):
                with open(fallback_path, "r", encoding="utf-8") as f:
                    fallback_data = json.load(f)
                if str(user_id) in fallback_data:
                    del fallback_data[str(user_id)]
                    with open(fallback_path, "w", encoding="utf-8") as f:
                        json.dump(fallback_data, f, indent=2)
                    return jsonify({'success': True, 'message': 'Last.fm account unlinked.'})
                else:
                    return jsonify({'success': False, 'message': 'No Last.fm account linked.'})
            else:
                return jsonify({'success': False, 'message': 'No Last.fm account linked.'})
        except Exception as e:
            app.logger.error(f"Error unlinking Last.fm from fallback JSON: {e}")
            return jsonify({'error': 'Failed to unlink Last.fm from file'}), 500

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print(f"Error starting server: {e}")
        import sys
        sys.exit(1)