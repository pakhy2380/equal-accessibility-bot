"""
Schedule configuration module
Centralized configuration for all scheduled tasks
"""

from collections.abc import Callable
import os
from .calendar_tasks import CalendarTasks

class ScheduleConfig:
    """Configuration for scheduled tasks"""
    
    def __init__(self):
        self.calendar_tasks = CalendarTasks()
    
    def get_scheduled_tasks(self) -> list[dict[str, any]]:
        """
        Get all scheduled tasks configuration
        
        Returns:
        List of task configurations with format:
        {
            'name': 'task_name',
            'func': callable_function,
            'hour': int,
            'minute': int,
            'enabled': bool,
            'description': 'Task description'
        }
        """
        
        # Default schedule times from environment
        default_hour = int(os.getenv('DAILY_SCHEDULE_HOUR', '8'))
        default_minute = int(os.getenv('DAILY_SCHEDULE_MINUTE', '0'))
        
        tasks = [
            {
                'name': 'daily_calendar',
                'func': self.calendar_tasks.daily_schedule_notification,
                'hour': default_hour,
                'minute': default_minute,
                'enabled': True,
                'description': 'Send daily calendar schedule notification'
            },
            # Add more tasks here as needed
            # {
            #     'name': 'weekly_report',
            #     'func': self.some_other_service.weekly_report,
            #     'hour': 9,
            #     'minute': 0,
            #     'enabled': False,
            #     'description': 'Send weekly report'
            # },
        ]
        
        return tasks
    
    def get_task_by_name(self, name: str) -> dict[str, any] | None:
        """Get a specific task configuration by name"""
        tasks = self.get_scheduled_tasks()
        return next((task for task in tasks if task['name'] == name), None)
    
    def get_enabled_tasks(self) -> list[dict[str, any]]:
        """Get only enabled tasks"""
        return [task for task in self.get_scheduled_tasks() if task['enabled']]
    
    def add_custom_task(self, name: str, func: Callable, hour: int, minute: int = 0, 
                       enabled: bool = True, description: str = "") -> dict[str, any]:
        """
        Add a custom task configuration (for dynamic task creation)
        Note: This creates a runtime task config, not persistent
        """
        return {
            'name': name,
            'func': func,
            'hour': hour,
            'minute': minute,
            'enabled': enabled,
            'description': description or f"Custom task: {name}"
        }