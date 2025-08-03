import discord
from .calendar_service import GoogleCalendarService

class CalendarTasks:
    """Calendar-specific scheduled tasks"""
    
    def __init__(self):
        self.calendar_service = GoogleCalendarService()
    
    async def daily_schedule_notification(self, channel):
        """Send daily schedule to the specified channel"""
        if not channel:
            print("No channel specified for daily schedule notification")
            return
        
        try:
            # Get today's events
            events = await self.calendar_service.get_today_events()
            
            if not events:
                embed = discord.Embed(
                    title="📅 Today's Schedule",
                    description="No events scheduled for today! 🎉",
                    color=discord.Color.green()
                )
                await channel.send(embed=embed)
                return
            
            # Create embed for schedule
            embed = discord.Embed(
                title="📅 Today's Schedule",
                color=discord.Color.blue()
            )
            
            schedule_text = ""
            for event in events:
                schedule_text += f"🕐 **{event['time']}** - {event['title']}\n"
                if event['location']:
                    schedule_text += f"📍 {event['location']}\n"
                if event['description']:
                    # Limit description length
                    desc = event['description'][:100] + "..." if len(event['description']) > 100 else event['description']
                    schedule_text += f"📝 {desc}\n"
                schedule_text += "\n"
            
            # Split into multiple embeds if too long
            if len(schedule_text) > 4000:
                chunks = self._split_text(schedule_text, 4000)
                for i, chunk in enumerate(chunks):
                    if i == 0:
                        embed.description = chunk
                        await channel.send(embed=embed)
                    else:
                        continuation_embed = discord.Embed(
                            title="📅 Today's Schedule (continued)",
                            description=chunk,
                            color=discord.Color.blue()
                        )
                        await channel.send(embed=continuation_embed)
            else:
                embed.description = schedule_text
                await channel.send(embed=embed)
                
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Calendar Error",
                description=f"Failed to fetch today's schedule: {str(e)}",
                color=discord.Color.red()
            )
            await channel.send(embed=error_embed)
            print(f"Error in daily schedule notification: {e}")
    
    async def send_manual_schedule(self, channel, days=0):
        """Manually send schedule for today or upcoming days"""
        if not channel:
            return
        
        try:
            if days == 0:
                events = await self.calendar_service.get_today_events()
                title = "📅 Today's Schedule"
            else:
                events = await self.calendar_service.get_upcoming_events(days)
                title = f"📅 Upcoming Events (Next {days} days)"
            
            if not events:
                embed = discord.Embed(
                    title=title,
                    description="No events found! 🎉",
                    color=discord.Color.green()
                )
                await channel.send(embed=embed)
                return
            
            embed = discord.Embed(title=title, color=discord.Color.blue())
            
            schedule_text = ""
            current_date = None
            
            for event in events:
                if event['title'].startswith('🟢') or event['title'].startswith('🔵'):
                    continue
                # Parse event date for grouping
                from datetime import datetime
                start_str = event['start']
                if 'T' in start_str:
                    event_date = datetime.fromisoformat(start_str.replace('Z', '+00:00')).date()
                else:
                    event_date = datetime.fromisoformat(start_str).date()
                
                # Add date header if changed (for multi-day view)
                if days > 0 and current_date != event_date:
                    current_date = event_date
                    schedule_text += f"\n**{event_date.strftime('%Y-%m-%d (%A)')}**\n"
                
                schedule_text += f"🕐 **{event['time']}** - {event['title']}\n"
                if event['location']:
                    schedule_text += f"📍 {event['location']}\n"
                if event['description']:
                    desc = event['description'][:100] + "..." if len(event['description']) > 100 else event['description']
                    schedule_text += f"📝 {desc}\n"
                schedule_text += "\n"
            
            # Handle long messages
            if len(schedule_text) > 4000:
                chunks = self._split_text(schedule_text, 4000)
                for i, chunk in enumerate(chunks):
                    if i == 0:
                        embed.description = chunk
                        await channel.send(embed=embed)
                    else:
                        continuation_embed = discord.Embed(
                            title=f"{title} (continued)",
                            description=chunk,
                            color=discord.Color.blue()
                        )
                        await channel.send(embed=continuation_embed)
            else:
                embed.description = schedule_text
                await channel.send(embed=embed)
                
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Calendar Error",
                description=f"Error fetching calendar events: {str(e)}",
                color=discord.Color.red()
            )
            await channel.send(embed=error_embed)
            print(f"Error in manual schedule: {e}")
    
    def _split_text(self, text, max_length):
        """Split text into chunks of max_length while preserving line breaks"""
        lines = text.split('\n')
        chunks = []
        current_chunk = ""
        
        for line in lines:
            if len(current_chunk + line + '\n') > max_length:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = line + '\n'
                else:
                    # Single line is too long, force split
                    current_chunk = line[:max_length-3] + "..."
                    chunks.append(current_chunk)
                    current_chunk = ""
            else:
                current_chunk += line + '\n'
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
