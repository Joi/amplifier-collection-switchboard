"""Calendar integration using AppleScript.

Fetches today's events from macOS Calendar app without requiring
Google OAuth credentials.
"""

import subprocess
import json
from datetime import datetime


def fetch_today_events() -> list[dict]:
    """Fetch today's calendar events using AppleScript.
    
    Returns:
        List of event dicts with: summary, start_time, end_time, location, notes
    """
    # AppleScript to get today's events from all calendars
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
                set evtNotes to ""
                
                try
                    set evtLocation to location of evt
                end try
                try
                    set evtNotes to description of evt
                end try
                
                -- Format times as HH:MM
                set startHour to text -2 thru -1 of ("0" & (hours of evtStart))
                set startMin to text -2 thru -1 of ("0" & (minutes of evtStart))
                set endHour to text -2 thru -1 of ("0" & (hours of evtEnd))
                set endMin to text -2 thru -1 of ("0" & (minutes of evtEnd))
                
                set eventInfo to {summary:evtSummary, startTime:(startHour & ":" & startMin), endTime:(endHour & ":" & endMin), location:evtLocation, notes:evtNotes}
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
            # Calendar access might be denied or app not running
            return []
        
        # Parse the JSON output
        output = result.stdout.strip()
        if output:
            events = json.loads(output)
            # Sort by start time
            events.sort(key=lambda x: x.get('start_time', ''))
            return events
        return []
        
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
        return []


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
        
        # Format: - 09:00-10:00 Meeting Name
        time_range = f"{start}-{end}" if start and end else start
        line = f"- {time_range} {summary}"
        
        if location:
            line += f" ({location})"
        
        lines.append(line)
    
    return '\n'.join(lines)
