# 🚀 Dashboard Local Setup - README

## Quick Start (First Time Users)

Run this single command to set up everything automatically:

```bash
python3 setup.py
```

That's it! The setup script will:
- Check your system requirements
- Create a local development environment
- Install all dependencies
- Set up MongoDB (with Docker or locally)
- Configure environment variables
- Create helper scripts for running and testing

## What the Setup Script Does

### 1. System Check
- Verifies Python 3.8+ is installed
- Checks for required tools (pip, git)
- Validates system compatibility

### 2. Local Environment Setup
- Creates `local/` directory for all development files
- Sets up Python virtual environment
- Installs all required dependencies

### 3. Configuration
- Generates secure secret keys
- Helps you configure MongoDB connection
- Sets up Discord OAuth credentials
- Creates `.env` file with all settings

### 4. MongoDB Setup Options
- **Docker** (Recommended): Automatically starts MongoDB container
- **Local Install**: Provides installation instructions
- **MongoDB Atlas**: Guides you through cloud setup
- **Skip**: For manual setup later

### 5. Helper Scripts Created
After setup, you'll have these scripts in `local/`:

- `local/run.sh` - Start the dashboard locally
- `local/test.sh` - Run comprehensive tests
- `local/docker_test.sh` - Test with Docker
- `local/stop_mongodb.sh` - Stop MongoDB container (if using Docker)

## File Organization

After running `setup.py`, your project structure will be:

```
dashboard/
├── setup.py                 # 🔧 One-command setup script
├── local/                   # 📁 All local development files
│   ├── .env                 # ⚙️ Your environment configuration
│   ├── .env.example         # 📋 Environment template
│   ├── docker-compose.test.yml  # 🐳 Docker testing setup
│   ├── test_deployment.py   # 🧪 Comprehensive test suite
│   ├── run.sh              # 🚀 Start dashboard locally
│   ├── test.sh             # 🧪 Run tests
│   ├── docker_test.sh      # 🐳 Docker testing
│   ├── venv/               # 🐍 Python virtual environment
│   └── docs/               # 📚 Documentation
└── dashboard/              # 💻 Main application code
    ├── app.py
    ├── templates/
    ├── static/
    └── ...
```

## After Setup - Running the Dashboard

1. **Start the dashboard:**
   ```bash
   ./local/run.sh
   ```

2. **Run tests:**
   ```bash
   ./local/test.sh
   ```

3. **Test with Docker:**
   ```bash
   ./local/docker_test.sh
   ```

4. **Open in browser:**
   ```
   http://localhost:5000
   ```

## Requirements

- **Python 3.8+** (checked automatically)
- **pip** (checked automatically)
- **MongoDB** (set up automatically via Docker or instructions provided)
- **Discord Application** (you'll be guided through setup)

## Common Issues & Solutions

### "Python not found"
Install Python 3.8+ from https://python.org

### "Docker not found" 
Install Docker from https://docker.com (only needed for Docker MongoDB option)

### "MongoDB connection failed"
- If using Docker: Run `docker ps` to check if MongoDB container is running
- If using local: Run `sudo systemctl status mongod` to check MongoDB service
- If using Atlas: Verify connection string and network access

### "Discord OAuth not working"
- Check your Discord application settings
- Verify redirect URI is set to `http://localhost:5000/callback`
- Ensure client ID and secret are correct

## Manual Setup (Advanced Users)

If you prefer manual setup:

1. Create virtual environment:
   ```bash
   python3 -m venv local/venv
   source local/venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.web.txt
   pip install -r local/requirements.test.txt
   ```

3. Copy and edit environment file:
   ```bash
   cp local/.env.example local/.env
   # Edit local/.env with your settings
   ```

4. Start MongoDB (choose one):
   ```bash
   # Docker
   docker run -d -p 27017:27017 --name mongodb mongo:7.0
   
   # Local service
   sudo systemctl start mongod
   ```

5. Run the application:
   ```bash
   source local/.env
   python wsgi.py
   ```

## Getting Help

- 📚 Check `local/SETUP_GUIDE.md` for detailed instructions
- 📋 Use `local/TESTING_CHECKLIST.md` for troubleshooting
- 🧪 Run `local/test.sh` to diagnose issues
- 🔍 Check logs in terminal output

## Development Workflow

1. **First time:** Run `python3 setup.py`
2. **Daily development:** Run `./local/run.sh`
3. **Before deploying:** Run `./local/test.sh`
4. **Troubleshooting:** Check the documentation in `local/`

---

**Made setup too easy? You're welcome! 😉**
