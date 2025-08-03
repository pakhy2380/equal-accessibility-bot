import discord
from discord.ext import commands
import os
import signal
import sys
import asyncio
from dotenv import load_dotenv
from services.scheduler_service import SchedulerService
from services.schedule_config import ScheduleConfig

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=os.getenv('COMMAND_PREFIX', '!'), intents=intents, help_command=None)

# Initialize services
bot.scheduler = SchedulerService(bot)
schedule_config = ScheduleConfig()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    
    # Load command extensions
    await load_extensions()
    
    # Setup scheduler
    await setup_scheduler()
    
    print('🚀 Bot is ready!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Handle DM vs Guild channel names
    if isinstance(message.channel, discord.DMChannel):
        channel_name = "DM"
    else:
        channel_name = f"#{message.channel.name}"
    
    print(f'Message received from {message.author} in {channel_name}: {message.content}')
    await bot.process_commands(message)

async def load_extensions():
    """Load all command extensions"""
    extensions = ['commands.basic', 'commands.calendar', 'commands.scheduler']
    
    for extension in extensions:
        try:
            await bot.load_extension(extension)
            print(f'✅ Loaded {extension}')
        except Exception as e:
            print(f'❌ Failed to load {extension}: {e}')

async def setup_scheduler():
    """Setup scheduled tasks from configuration"""
    
    # Get all enabled tasks from configuration
    enabled_tasks = schedule_config.get_enabled_tasks()
    
    # Add each task to the scheduler
    for task_config in enabled_tasks:
        bot.scheduler.add_task(
            name=task_config['name'],
            func=task_config['func'],
            hour=task_config['hour'],
            minute=task_config['minute'],
            enabled=task_config['enabled']
        )
        print(f"Added scheduled task: {task_config['name']} at {task_config['hour']:02d}:{task_config['minute']:02d} - {task_config['description']}")
    
    # Start all scheduled tasks
    bot.scheduler.start_all()
    print(f'✅ Scheduler initialized with {len(enabled_tasks)} tasks')

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ Unknown command. Use `!help` to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument. Use `!help` for command usage.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏰ Command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
    else:
        print(f"Unhandled error: {error}")

def signal_handler(sig, frame):
    print('\nReceived shutdown signal. Closing bot...')
    sys.exit(0)

if __name__ == '__main__':
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN not found in environment variables")
        print("Please set your Discord bot token in the .env file")
        exit(1)
    
    try:
        bot.run(token)
    except KeyboardInterrupt:
        print('\nBot stopped by user.')
    except Exception as e:
        print(f'Bot encountered an error: {e}')
    finally:
        print('Bot shutdown complete.')
