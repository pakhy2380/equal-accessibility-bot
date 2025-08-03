import os
from datetime import datetime, timedelta
from googleapiclient.discovery import build
import pytz

class GoogleCalendarService:
    def __init__(self):
        self.service = None
        self.calendar_id = os.getenv('GOOGLE_CALENDAR_ID')
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.timezone = pytz.timezone(os.getenv('TIMEZONE', 'Asia/Seoul'))
    
    async def authenticate(self):
        """Initialize Google Calendar API service for public calendar access"""
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        if not self.calendar_id:
            raise ValueError("GOOGLE_CALENDAR_ID not found in environment variables")
        
        # Build service with API key (no OAuth needed for public calendars)
        self.service = build('calendar', 'v3', developerKey=self.api_key)
        return True
    
    async def get_today_events(self):
        """Get today's events from calendar"""
        if not self.service:
            await self.authenticate()
        
        # Get today's date range
        now = datetime.now(self.timezone)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        # Convert to UTC for API call
        time_min = today_start.astimezone(pytz.UTC).isoformat()
        time_max = today_end.astimezone(pytz.UTC).isoformat()
        
        try:
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return self._format_events(events)
            
        except Exception as e:
            print(f"Error fetching calendar events: {e}")
            return []
    
    async def get_upcoming_events(self, days=7):
        """Get upcoming events for next N days"""
        if not self.service:
            await self.authenticate()
        
        now = datetime.now(self.timezone)
        time_min = now.isoformat()
        time_max = (now + timedelta(days=days)).isoformat()
        
        try:
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return self._format_events(events)
            
        except Exception as e:
            print(f"Error fetching upcoming events: {e}")
            return []
    
    def _format_events(self, events):
        """Format events for display"""
        formatted_events = []
        
        for event in events:
            title = event.get('summary', 'No title')
            
            # Handle all-day events
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            # Parse datetime
            if 'T' in start:  # Has time
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                
                # Convert to local timezone
                start_local = start_dt.astimezone(self.timezone)
                end_local = end_dt.astimezone(self.timezone)
                
                time_str = f"{start_local.strftime('%H:%M')} - {end_local.strftime('%H:%M')}"
            else:  # All-day event
                time_str = "All day"
            
            location = event.get('location', '')
            description = event.get('description', '')
            
            formatted_events.append({
                'title': title,
                'time': time_str,
                'location': location,
                'description': description,
                'start': start,
                'end': end
            })
        
        return formatted_events