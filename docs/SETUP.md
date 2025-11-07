# Setup Guide

This guide will help you set up and install the Graz Library Bulk Operations Tool.

## Prerequisites

- Python 3.9 or higher
- pip package manager
- Git (optional, for cloning the repository)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/graz-library-bulk-ops.git
cd graz-library-bulk-ops
```

### 2. Create Virtual Environment

It's recommended to use a virtual environment to isolate dependencies:

```bash
# On Linux/macOS
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

Install the required packages:

```bash
pip install -r requirements.txt
```

### 4. Install in Development Mode

For development, install the package in editable mode:

```bash
pip install -e .
```

## Configuration

### Environment Variables

Create a `.env` file in your `~/.graz-library/` directory to customize settings:

```bash
mkdir -p ~/.graz-library
cat > ~/.graz-library/.env << EOF
# Library Configuration
LIBRARY_BASE_URL=https://stadtbibliothek.graz.at

# Browser Configuration
BROWSER_HEADLESS=true

# Request Configuration
REQUEST_TIMEOUT=10
RATE_LIMIT_DELAY=2

# Logging
LOG_LEVEL=INFO

# Email Configuration (optional, for mail order notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
EOF
```

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| LIBRARY_BASE_URL | https://stadtbibliothek.graz.at | Base URL of the library |
| BROWSER_HEADLESS | true | Run browser in headless mode |
| REQUEST_TIMEOUT | 10 | HTTP request timeout in seconds |
| RATE_LIMIT_DELAY | 2 | Delay between requests in seconds |
| LOG_LEVEL | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| CACHE_TTL | 3600 | Cache time-to-live in seconds |

## Installation Verification

Verify the installation was successful:

```bash
python -c "from graz_library import __version__; print(__version__)"
```

You should see the version number (e.g., "0.1.0").

## Using the CLI

Test the CLI is working:

```bash
python -m graz_library.cli --help
```

Or if installed as a command:

```bash
graz-library --help
```

## Data Directories

The tool creates the following directories in your home directory:

- `~/.graz-library/logs/` - Application logs
- `~/.graz-library/data/` - Data storage
- `~/.graz-library/data/cache/` - Search result cache
- `~/.graz-library/config/` - Configuration files

These directories are created automatically on first run.

## Troubleshooting

### ModuleNotFoundError

If you get "ModuleNotFoundError: No module named 'graz_library'":
1. Ensure you've installed the package in development mode: `pip install -e .`
2. Verify your virtual environment is activated

### Connection Issues

If you get connection errors:
1. Check your internet connection
2. Verify the library website is accessible: https://stadtbibliothek.graz.at/
3. Check firewall/proxy settings

### Permission Errors

If you get permission errors when creating directories:
1. Ensure your home directory is writable
2. Check file permissions: `ls -la ~/.graz-library/`

## Next Steps

After installation, see [USAGE.md](USAGE.md) for how to use the tool.
