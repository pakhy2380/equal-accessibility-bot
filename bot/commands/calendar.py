import discord
from discord.ext import commands
import sys
sys.path.append('..')
from services.calendar_tasks import CalendarTasks
from utils.decorators import authorized_only, require_bot_attribute

class CalendarCommands(commands.Cog):
    """Calendar-related commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.calendar_tasks = CalendarTasks()
    
    @commands.command(name='today')
    async def today_schedule(self, ctx):
        """Show today's schedule"""
        await self.calendar_tasks.send_manual_schedule(ctx.channel, days=0)
    
    @commands.command(name='week')
    async def week_schedule(self, ctx):
        """Show this week's schedule"""
        await self.calendar_tasks.send_manual_schedule(ctx.channel, days=7)
    
    @commands.command(name='upcoming')
    async def upcoming_schedule(self, ctx, days: int = 3):
        """Show upcoming events for specified days (default: 3)"""
        if days < 1 or days > 30:
            await ctx.send("❌ Days must be between 1 and 30")
            return
        
        await self.calendar_tasks.send_manual_schedule(ctx.channel, days=days)
    
    @commands.command(name='schedule_channel')
    @authorized_only()
    @require_bot_attribute('scheduler')
    async def set_schedule_channel(self, ctx, channel: discord.TextChannel = None):
        """Set the channel for daily schedule notifications"""
        target_channel = channel or ctx.channel
        
        self.bot.scheduler.set_notification_channel('daily_calendar', target_channel.id)
        
        embed = discord.Embed(
            title="✅ Schedule Channel Set",
            description=f"Daily schedule notifications will be sent to {target_channel.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='schedule_time')
    @authorized_only()
    @require_bot_attribute('scheduler')
    async def set_schedule_time(self, ctx, hour: int, minute: int = 0):
        """Set the time for daily schedule notifications (24-hour format)"""
        if not (0 <= hour <= 23) or not (0 <= minute <= 59):
            await ctx.send("❌ Invalid time format. Hour: 0-23, Minute: 0-59")
            return
        
        success = self.bot.scheduler.update_task_time('daily_calendar', hour, minute)
        
        if success:
            embed = discord.Embed(
                title="✅ Schedule Time Updated",
                description=f"Daily schedule will be sent at {hour:02d}:{minute:02d}",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ Failed to Update",
                description="Could not update schedule time",
                color=discord.Color.red()
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='schedule_status')
    @require_bot_attribute('scheduler')
    async def schedule_status(self, ctx):
        """Show current schedule settings and status"""
        
        tasks = self.bot.scheduler.list_tasks()
        calendar_task = next((task for task in tasks if task['name'] == 'daily_calendar'), None)
        
        embed = discord.Embed(
            title="📊 Schedule Status",
            color=discord.Color.blue()
        )
        
        if calendar_task:
            status = "🟢 Enabled" if calendar_task['enabled'] else "🔴 Disabled"
            running = "▶️ Running" if calendar_task['running'] else "⏸️ Stopped"
            
            embed.add_field(
                name="Daily Calendar Notification",
                value=f"**Status:** {status} ({running})\n**Time:** {calendar_task['time']}\n**Channel:** <#{calendar_task['channel_id']}>" if calendar_task['channel_id'] else "**Channel:** Not set",
                inline=False
            )
        else:
            embed.add_field(
                name="Daily Calendar Notification",
                value="❌ Not configured",
                inline=False
            )
        
        # Add environment settings
        schedule_hour = os.getenv('DAILY_SCHEDULE_HOUR', '8')
        schedule_minute = os.getenv('DAILY_SCHEDULE_MINUTE', '0')
        timezone = os.getenv('TIMEZONE', 'Asia/Seoul')
        
        embed.add_field(
            name="Environment Settings",
            value=f"**Default Time:** {schedule_hour}:{schedule_minute}\n**Timezone:** {timezone}",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='enable_schedule')
    @commands.has_permissions(manage_guild=True)
    async def enable_schedule(self, ctx):
        """Enable daily schedule notifications"""
        if hasattr(self.bot, 'scheduler'):
            self.bot.scheduler.start_task('daily_calendar')
            
            embed = discord.Embed(
                title="✅ Schedule Enabled",
                description="Daily calendar notifications are now enabled",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Scheduler service not available")
    
    @commands.command(name='disable_schedule')
    @commands.has_permissions(manage_guild=True)
    async def disable_schedule(self, ctx):
        """Disable daily schedule notifications"""
        if hasattr(self.bot, 'scheduler'):
            self.bot.scheduler.stop_task('daily_calendar')
            
            embed = discord.Embed(
                title="⏸️ Schedule Disabled",
                description="Daily calendar notifications are now disabled",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Scheduler service not available")

async def setup(bot):
    await bot.add_cog(CalendarCommands(bot))