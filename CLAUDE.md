# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a Discord bot project designed to improve accessibility. The bot is built using Python 3.11+ with discord.py and uses uv for dependency management.

## Development Setup
- Uses `uv` for Python package management and virtual environments
- Python 3.11+ required
- Environment variables stored in `.env` file (copy from `.env.example`)
- Virtual environment is automatically managed by uv

## Common Commands

### Environment Setup
```bash
# Install dependencies (creates venv automatically)
uv sync

# Add new dependency
uv add package_name

# Run with uv
uv run python bot/main.py
```

### Running the Bot
```bash
# Development mode
uv run python bot/main.py

# Alternative: activate venv and run directly  
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
python bot/main.py
```

### Testing
```bash
# Run basic connection test
uv run python bot/main.py
```

## Project Structure
```
├── bot/
│   └── main.py          # Main bot entry point
├── .env                 # Environment variables (not committed)
├── .env.example         # Environment variables template
├── pyproject.toml       # Project configuration and dependencies
└── uv.lock             # Dependency lock file
```

## Environment Variables
Required environment variables (set in `.env`):
- `DISCORD_TOKEN`: Discord bot token from Discord Developer Portal
- `CLIENT_ID`: Discord application client ID
- `COMMAND_PREFIX`: Bot command prefix (default: "!")
- `DEBUG`: Enable debug mode (default: True)
- `GOOGLE_CALENDAR_ID`: Public Google Calendar ID
- `GOOGLE_API_KEY`: Google API key for Calendar API
- `DAILY_SCHEDULE_HOUR`: Hour for daily notifications (default: 8)
- `DAILY_SCHEDULE_MINUTE`: Minute for daily notifications (default: 0)
- `TIMEZONE`: Timezone for scheduling (default: Asia/Seoul)

## Bot Features
- Basic ping/pong commands for testing connectivity
- Hello command for user interaction
- Google Calendar integration (public calendars)
- Extensible scheduler system for automated tasks
- Modular command structure using discord.py cogs

### Available Commands
**Basic Commands:**
- `!hello` - Greet the user
- `!ping` - Check bot latency
- `!help` - Show available commands

**Calendar Commands:**
- `!today` - Show today's schedule
- `!week` - Show this week's schedule
- `!upcoming [days]` - Show upcoming events

**Schedule Management:**
- `!schedule_list` - List all scheduled tasks
- `!schedule_enable <task_name>` - Enable a task
- `!schedule_disable <task_name>` - Disable a task
- `!schedule_set_channel <task_name> [#channel]` - Set notification channel
- `!schedule_set_time <task_name> <hour> [minute]` - Set task time

## Deployment Notes
- Designed to be deployed on Replit
- Uses python-dotenv for environment variable management
- All sensitive tokens should be set via environment variables, never committed to git

## Coding Guidelines

### Type Hints
- **ALWAYS use built-in type hints instead of typing library** (Python 3.11+)
  - Use `list[str]` instead of `typing.List[str]`
  - Use `dict[str, int]` instead of `typing.Dict[str, int]`
  - Use `int | None` instead of `typing.Optional[int]`
  - Only import from typing when absolutely necessary (e.g., `Callable`, `Any`)

### Testing and Code Quality
- **ALWAYS test code after implementation**
- Write temporary test code to verify functionality
- **DELETE one-time test code after verification** - keep codebase clean
- Only keep test code that serves ongoing maintenance purposes
- Test all new commands and features before considering them complete

### Code Organization
- Follow existing modular structure (commands/, services/)
- Use type hints on all function parameters and return values
- Handle errors gracefully with appropriate user feedback