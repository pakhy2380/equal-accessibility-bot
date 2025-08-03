import discord
from discord.ext import commands
from utils.decorators import authorized_only, require_bot_attribute

class SchedulerCommands(commands.Cog):
    """Scheduler management commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='schedule_list')
    @require_bot_attribute('scheduler')
    async def list_schedules(self, ctx):
        """List all scheduled tasks and their status"""
        
        tasks = self.bot.scheduler.list_tasks()
        
        if not tasks:
            embed = discord.Embed(
                title="📋 Scheduled Tasks",
                description="No scheduled tasks configured",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="📋 Scheduled Tasks",
            color=discord.Color.blue()
        )
        
        for task in tasks:
            status_icon = "🟢" if task['enabled'] else "🔴"
            running_icon = "▶️" if task['running'] else "⏸️"
            
            field_value = f"**Time:** {task['time']}\n"
            field_value += f"**Status:** {status_icon} {'Enabled' if task['enabled'] else 'Disabled'}\n"
            field_value += f"**Running:** {running_icon} {'Yes' if task['running'] else 'No'}\n"
            
            if task['channel_id']:
                field_value += f"**Channel:** <#{task['channel_id']}>\n"
            else:
                field_value += "**Channel:** Not set\n"
            
            embed.add_field(
                name=f"📅 {task['name']}",
                value=field_value,
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='schedule_enable')
    @authorized_only()
    @require_bot_attribute('scheduler')
    async def enable_task(self, ctx, task_name: str):
        """Enable a specific scheduled task"""
        
        # Check if task exists
        tasks = self.bot.scheduler.list_tasks()
        if not any(task['name'] == task_name for task in tasks):
            available_tasks = [task['name'] for task in tasks]
            await ctx.send(f"❌ Task '{task_name}' not found. Available tasks: {', '.join(available_tasks)}")
            return
        
        self.bot.scheduler.start_task(task_name)
        
        embed = discord.Embed(
            title="✅ Task Enabled",
            description=f"Task '{task_name}' has been enabled",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='schedule_disable')
    @authorized_only()
    @require_bot_attribute('scheduler')
    async def disable_task(self, ctx, task_name: str):
        """Disable a specific scheduled task"""
        
        # Check if task exists
        tasks = self.bot.scheduler.list_tasks()
        if not any(task['name'] == task_name for task in tasks):
            available_tasks = [task['name'] for task in tasks]
            await ctx.send(f"❌ Task '{task_name}' not found. Available tasks: {', '.join(available_tasks)}")
            return
        
        self.bot.scheduler.stop_task(task_name)
        
        embed = discord.Embed(
            title="⏸️ Task Disabled",
            description=f"Task '{task_name}' has been disabled",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='schedule_set_channel')
    @authorized_only()
    @require_bot_attribute('scheduler')
    async def set_task_channel(self, ctx, task_name: str, channel: discord.TextChannel = None):
        """Set notification channel for a specific task"""
        
        target_channel = channel or ctx.channel
        
        # Check if task exists
        tasks = self.bot.scheduler.list_tasks()
        if not any(task['name'] == task_name for task in tasks):
            available_tasks = [task['name'] for task in tasks]
            await ctx.send(f"❌ Task '{task_name}' not found. Available tasks: {', '.join(available_tasks)}")
            return
        
        self.bot.scheduler.set_notification_channel(task_name, target_channel.id)
        
        embed = discord.Embed(
            title="📍 Channel Set",
            description=f"Task '{task_name}' will now send notifications to {target_channel.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='schedule_set_time')
    @authorized_only()
    @require_bot_attribute('scheduler')
    async def set_task_time(self, ctx, task_name: str, hour: int, minute: int = 0):
        """Set execution time for a specific task (24-hour format)"""
        
        if not (0 <= hour <= 23) or not (0 <= minute <= 59):
            await ctx.send("❌ Invalid time format. Hour: 0-23, Minute: 0-59")
            return
        
        # Check if task exists
        tasks = self.bot.scheduler.list_tasks()
        if not any(task['name'] == task_name for task in tasks):
            available_tasks = [task['name'] for task in tasks]
            await ctx.send(f"❌ Task '{task_name}' not found. Available tasks: {', '.join(available_tasks)}")
            return
        
        success = self.bot.scheduler.update_task_time(task_name, hour, minute)
        
        if success:
            embed = discord.Embed(
                title="🕐 Time Updated",
                description=f"Task '{task_name}' will now run at {hour:02d}:{minute:02d}",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ Update Failed",
                description=f"Could not update time for task '{task_name}'",
                color=discord.Color.red()
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SchedulerCommands(bot))