"""Calendar integration with Google Calendar API and AppleScript fallback.

Primary: Google Calendar API (uses existing obs-dailynotes credentials)
Fallback: macOS Calendar via AppleScript
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path


def get_rfc3339_day_bounds() -> dict:
    """Get RFC3339 strings for start and end of local day with timezone offset."""
    now = datetime.now()
    year = now.year
    month = f"{now.month:02d}"
    day = f"{now.day:02d}"
    
    # Calculate timezone offset
    import time
    offset_seconds = -time.timezone if time.daylight == 0 else -time.altzone
    sign = '+' if offset_seconds >= 0 else '-'
    abs_offset = abs(offset_seconds)
    hours = abs_offset // 3600
    minutes = (abs_offset % 3600) // 60
    tz = f"{sign}{hours:02d}:{minutes:02d}"
    
    return {
        'start': f"{year}-{month}-{day}T00:00:00{tz}",
        'end': f"{year}-{month}-{day}T23:59:59{tz}",
    }


def fetch_google_calendar_events(creds_path: str, token_path: str) -> list[dict]:
    """Fetch today's events from Google Calendar API.
    
    Args:
        creds_path: Path to Google OAuth credentials JSON
        token_path: Path to stored OAuth token
        
    Returns:
        List of event dicts with: summary, start_time, end_time, location
    """
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError:
        return None  # Google API not installed, signal to use fallback
    
    # Resolve ~ in paths
    creds_path = os.path.expanduser(creds_path)
    token_path = os.path.expanduser(token_path)
    
    if not os.path.exists(token_path):
        return None  # No token, signal to use fallback
    
    try:
        # Load credentials
        creds = Credentials.from_authorized_user_file(token_path)
        
        # Refresh if expired
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save refreshed token
            with open(token_path, 'w') as f:
                f.write(creds.to_json())
        
        if not creds or not creds.valid:
            return None
        
        # Build calendar service
        service = build('calendar', 'v3', credentials=creds)
        
        # Get today's bounds
        bounds = get_rfc3339_day_bounds()
        
        # Fetch events
        events_result = service.events().list(
            calendarId='primary',
            timeMin=bounds['start'],
            timeMax=bounds['end'],
            maxResults=100,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        items = events_result.get('items', [])
        
        # Convert to our format
        events = []
        for item in items:
            start = item.get('start', {})
            end = item.get('end', {})
            
            # Get start time (dateTime for timed events, date for all-day)
            start_str = start.get('dateTime', start.get('date', ''))
            end_str = end.get('dateTime', end.get('date', ''))
            
            # Format times as HH:MM
            start_time = ''
            end_time = ''
            if 'T' in start_str:
                start_time = start_str.split('T')[1][:5]
            if 'T' in end_str:
                end_time = end_str.split('T')[1][:5]
            
            events.append({
                'summary': item.get('summary', 'Untitled'),
                'start_time': start_time,
                'end_time': end_time,
                'location': item.get('location', ''),
                'all_day': 'T' not in start_str,
            })
        
        return events
        
    except Exception as e:
        # Any error, signal to use fallback
        return None


def fetch_applescript_events() -> list[dict]:
    """Fetch today's calendar events using macOS AppleScript (fallback).
    
    Returns:
        List of event dicts with: summary, start_time, end_time, location
    """
    script = '''
    use AppleScript version "2.4"
    use scripting additions
    use framework "Foundation"

    set today to current date
    set todayStart to today - (time of today)
    set todayEnd to todayStart + (24 * 60 * 60) - 1

    set eventList to {}
    
    tell application "Calendar"
        repeat with cal in calendars
            set calEvents to (every event of cal whose start date >= todayStart and start date < todayEnd)
            repeat with evt in calEvents
                set evtStart to start date of evt
                set evtEnd to end date of evt
                set evtSummary to summary of evt
                set evtLocation to ""
                
                try
                    set evtLocation to location of evt
                end try
                
                -- Format times as HH:MM
                set startHour to text -2 thru -1 of ("0" & (hours of evtStart))
                set startMin to text -2 thru -1 of ("0" & (minutes of evtStart))
                set endHour to text -2 thru -1 of ("0" & (hours of evtEnd))
                set endMin to text -2 thru -1 of ("0" & (minutes of evtEnd))
                
                set eventInfo to {summary:evtSummary, startTime:(startHour & ":" & startMin), endTime:(endHour & ":" & endMin), location:evtLocation}
                set end of eventList to eventInfo
            end repeat
        end repeat
    end tell

    -- Convert to JSON-like output
    set output to "["
    set isFirst to true
    repeat with evt in eventList
        if not isFirst then
            set output to output & ","
        end if
        set isFirst to false
        set output to output & "{\\"summary\\":\\"" & (summary of evt) & "\\",\\"start_time\\":\\"" & (startTime of evt) & "\\",\\"end_time\\":\\"" & (endTime of evt) & "\\",\\"location\\":\\"" & (location of evt) & "\\"}"
    end repeat
    set output to output & "]"
    return output
    '''
    
    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return []
        
        output = result.stdout.strip()
        if output:
            events = json.loads(output)
            events.sort(key=lambda x: x.get('start_time', ''))
            return events
        return []
        
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
        return []


def fetch_today_events(
    google_creds_path: str | None = None,
    google_token_path: str | None = None,
) -> list[dict]:
    """Fetch today's calendar events.
    
    Tries Google Calendar API first (if credentials provided), falls back to AppleScript.
    
    Args:
        google_creds_path: Path to Google OAuth credentials (or GCAL_CREDS_PATH env var)
        google_token_path: Path to Google OAuth token (or GCAL_TOKEN_PATH env var)
        
    Returns:
        List of event dicts with: summary, start_time, end_time, location
    """
    # Get paths from env if not provided
    creds_path = google_creds_path or os.environ.get('GCAL_CREDS_PATH')
    token_path = google_token_path or os.environ.get('GCAL_TOKEN_PATH')
    
    # Try Google Calendar first
    if creds_path and token_path:
        events = fetch_google_calendar_events(creds_path, token_path)
        if events is not None:
            return events
    
    # Fall back to AppleScript
    return fetch_applescript_events()


def format_events_markdown(events: list[dict]) -> str:
    """Format calendar events as markdown.
    
    Args:
        events: List of event dicts
        
    Returns:
        Markdown formatted string
    """
    if not events:
        return "*No calendar events today*"
    
    lines = []
    for event in events:
        start = event.get('start_time', '')
        end = event.get('end_time', '')
        summary = event.get('summary', 'Untitled')
        location = event.get('location', '')
        all_day = event.get('all_day', False)
        
        if all_day:
            line = f"- (All day) {summary}"
        else:
            time_range = f"{start}-{end}" if start and end else start
            line = f"- {time_range} {summary}"
        
        if location:
            line += f" ({location})"
        
        lines.append(line)
    
    return '\n'.join(lines)
