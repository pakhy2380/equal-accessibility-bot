import asyncio
import os
from datetime import datetime, time
from collections.abc import Callable
from typing import Any
import pytz
from discord.ext import tasks

class ScheduledTask:
    """Represents a scheduled task"""
    def __init__(self, name: str, func: Callable, hour: int, minute: int = 0, enabled: bool = True):
        self.name = name
        self.func = func
        self.hour = hour
        self.minute = minute
        self.enabled = enabled
        self.task = None
    
    def start(self):
        """Start this scheduled task"""
        if self.task and not self.task.is_running():
            self.task.start()
    
    def stop(self):
        """Stop this scheduled task"""
        if self.task and self.task.is_running():
            self.task.cancel()

class SchedulerService:
    """Generic scheduler service for managing multiple scheduled tasks"""
    
    def __init__(self, bot):
        self.bot = bot
        self.timezone = pytz.timezone(os.getenv('TIMEZONE', 'Asia/Seoul'))
        self.tasks: dict[str, ScheduledTask] = {}
        self.notification_channels: dict[str, int] = {}  # task_name -> channel_id
    
    def add_task(self, name: str, func: Callable, hour: int, minute: int = 0, enabled: bool = True):
        """Add a new scheduled task"""
        if name in self.tasks:
            print(f"Task '{name}' already exists. Replacing...")
            self.remove_task(name)
        
        scheduled_task = ScheduledTask(name, func, hour, minute, enabled)
        
        # Create the discord.py task loop
        @tasks.loop(time=time(hour=hour, minute=minute))
        async def task_loop():
            if scheduled_task.enabled:
                try:
                    channel_id = self.notification_channels.get(name)
                    if channel_id:
                        channel = self.bot.get_channel(channel_id)
                        await func(channel)
                    else:
                        await func(None)
                except Exception as e:
                    print(f"Error in scheduled task '{name}': {e}")
        
        @task_loop.before_loop
        async def before_task():
            await self.bot.wait_until_ready()
        
        scheduled_task.task = task_loop
        self.tasks[name] = scheduled_task
        
        print(f"Added scheduled task: {name} at {hour:02d}:{minute:02d}")
        return scheduled_task
    
    def remove_task(self, name: str):
        """Remove a scheduled task"""
        if name in self.tasks:
            self.tasks[name].stop()
            del self.tasks[name]
            print(f"Removed scheduled task: {name}")
    
    def start_task(self, name: str):
        """Start a specific task"""
        if name in self.tasks:
            self.tasks[name].enabled = True
            self.tasks[name].start()
            print(f"Started task: {name}")
    
    def stop_task(self, name: str):
        """Stop a specific task"""
        if name in self.tasks:
            self.tasks[name].enabled = False
            self.tasks[name].stop()
            print(f"Stopped task: {name}")
    
    def start_all(self):
        """Start all scheduled tasks"""
        for task in self.tasks.values():
            if task.enabled:
                task.start()
        print(f"Started {len(self.tasks)} scheduled tasks")
    
    def stop_all(self):
        """Stop all scheduled tasks"""
        for task in self.tasks.values():
            task.stop()
        print("Stopped all scheduled tasks")
    
    def set_notification_channel(self, task_name: str, channel_id: int):
        """Set notification channel for a specific task"""
        self.notification_channels[task_name] = channel_id
        print(f"Set notification channel for '{task_name}': {channel_id}")
    
    def list_tasks(self) -> list[dict[str, Any]]:
        """Get list of all scheduled tasks"""
        task_list = []
        for name, task in self.tasks.items():
            task_list.append({
                'name': name,
                'time': f"{task.hour:02d}:{task.minute:02d}",
                'enabled': task.enabled,
                'running': task.task.is_running() if task.task else False,
                'channel_id': self.notification_channels.get(name)
            })
        return task_list
    
    def update_task_time(self, name: str, hour: int, minute: int):
        """Update the time for a specific task"""
        if name not in self.tasks:
            print(f"Task '{name}' not found")
            return False
        
        task = self.tasks[name]
        was_running = task.task.is_running() if task.task else False
        
        # Stop current task
        if was_running:
            task.stop()
        
        # Update time
        task.hour = hour
        task.minute = minute
        
        # Recreate the task with new time
        func = task.func
        self.remove_task(name)
        new_task = self.add_task(name, func, hour, minute, task.enabled)
        
        # Start if it was running before
        if was_running:
            new_task.start()
        
        print(f"Updated task '{name}' time to {hour:02d}:{minute:02d}")
        return True