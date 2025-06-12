# BronxBot Dashboard

> The web interface for managing your BronxBot Discord server settings

A clean, modern dashboard for configuring BronxBot across your Discord servers. Built with Flask and designed for ease of use.

## Features

- **Server Management**: Configure settings for all your Discord servers
- **User Authentication**: Secure Discord OAuth integration  
- **Real-time Stats**: Live bot statistics and server information
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Easy Configuration**: Intuitive interface for all bot settings

## Quick Start

### For Render Deployment

1. Fork this repository
2. Connect to Render and deploy as a web service
3. Set your environment variables:
   - `MONGO_URI`: Your MongoDB connection string
   - `DISCORD_CLIENT_ID`: Your bot's client ID
   - `DISCORD_CLIENT_SECRET`: Your bot's client secret
   - `DISCORD_BOT_OWNER_ID`: Your Discord user ID

### For Local Development

1. Clone this repository
2. Install dependencies: `pip install -r requirements.web.txt`
3. Set up your environment variables
4. Run: `python wsgi.py` or `gunicorn -c gunicorn_config.py wsgi:app`

## ⚙️ Configuration

Set these environment variables:

```bash
MONGO_URI=your_mongodb_connection_string
DISCORD_CLIENT_ID=your_bot_client_id
DISCORD_CLIENT_SECRET=your_bot_client_secret
DISCORD_BOT_OWNER_ID=your_discord_user_id
SECRET_KEY=your_flask_secret_key
```

## Built With

- **Flask** - Web framework
- **MongoDB** - Database
- **Discord OAuth** - Authentication
- **Gunicorn** - WSGI HTTP Server
- **Bootstrap/CSS** - Frontend styling

## Project Structure

```
dashboard/
├── app.py              # Main Flask application
├── config.py           # Configuration management
├── utils/              # Utility modules
├── templates/          # HTML templates
├── static/             # CSS, JS, images
└── api/                # API endpoints
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Links

- [Live Dashboard](https://bronxbot.onrender.com/)
- [Support Server](https://discord.gg/jENm4phpgv)
- [Bot Repository](https://github.com/BronxBot/BronxBot)

---

> Made with 💖
