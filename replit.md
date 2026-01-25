# KittyCooker - Telegram Bot

## Overview
KittyCooker is a Telegram bot built with aiogram (Python) and MongoDB (Beanie ODM) for managing recipes.

## Tech Stack
- **Language**: Python 3.12
- **Bot Framework**: aiogram 3.24+
- **Database**: MongoDB with Beanie ODM
- **Configuration**: environs for environment variables

## Project Structure
```
├── main.py              # Entry point - bot initialization
├── env.py               # Environment variable configuration
├── commands/            # Bot command handlers
│   ├── __init__.py
│   ├── create.py
│   ├── list.py
│   └── start.py
├── models/              # Beanie document models
│   ├── __init__.py
│   ├── ingredient.py
│   ├── recipe.py
│   └── states.py
└── utils/               # Utility functions
    ├── constants.py
    └── formatting.py
```

## Required Environment Variables
- `BOT_TOKEN` - Telegram Bot API token (get from @BotFather)
- `DB_URL` - MongoDB connection string

## Running the Bot
The bot runs as a console application that polls Telegram for updates.

## Recent Changes
- January 2026: Initial import to Replit environment
