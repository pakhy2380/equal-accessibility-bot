"""
Custom decorators for bot commands
"""

import os
from functools import wraps
from discord.ext import commands

def authorized_only():
    """
    Decorator to restrict command access to authorized users only.
    Authorized users are defined in AUTHORIZED_USERS environment variable.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            # Load authorized users from environment
            authorized_users_str = os.getenv('AUTHORIZED_USERS', '')
            authorized_users = set()
            if authorized_users_str:
                authorized_users = set(int(uid.strip()) for uid in authorized_users_str.split(',') if uid.strip().isdigit())
            
            # Check if user is authorized
            if ctx.author.id not in authorized_users:
                await ctx.send("❌ You are not authorized to use this command")
                return
            
            # Execute the original function
            return await func(self, ctx, *args, **kwargs)
        
        return wrapper
    return decorator

def require_bot_attribute(attribute_name: str, error_message: str = None):
    """
    Decorator to check if bot has a required attribute/service.
    
    Args:
        attribute_name: Name of the attribute to check (e.g., 'scheduler')
        error_message: Custom error message if attribute is missing
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            if not hasattr(self.bot, attribute_name):
                message = error_message or f"❌ {attribute_name.title()} service not available"
                await ctx.send(message)
                return
            
            return await func(self, ctx, *args, **kwargs)
        
        return wrapper
    return decorator