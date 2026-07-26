import webbrowser
import urllib.parse
from datetime import datetime, timedelta

# Personal Assistant Features
# Email and Calendar integration
# Uses web-based intents for simplicity and security (no OAuth setup needed)

def create_email(recipient=None, subject=None, body=None):
    """
    Open default email client with pre-filled details.
    """
    if not recipient:
        recipient = ""
    if not subject:
        subject = "Message from Atlas"
    if not body:
        body = "Sent via Atlas AI Assistant"
        
    # Construct mailto link
    params = {
        "subject": subject,
        "body": body
    }
    query_string = urllib.parse.urlencode(params)
    mailto_link = f"mailto:{recipient}?{query_string}"
    
    webbrowser.open(mailto_link)
    return "Opened your email client with instructions."

def open_calendar(action="view"):
    """
    Open Google Calendar for viewing or creating events.
    action: 'view' or 'new'
    """
    if action == "new":
        url = "https://calendar.google.com/calendar/u/0/r/eventedit"
        msg = "Opened Google Calendar to create a new event."
    else:
        url = "https://calendar.google.com/calendar/u/0/r"
        msg = "Opened your Google Calendar."
        
    webbrowser.open(url)
    return msg

def get_date_time_info():
    """
    Get current date and time info for planning.
    """
    now = datetime.now()
    date_str = now.strftime("%A, %d %B %Y")
    time_str = now.strftime("%I:%M %p")
    week_num = now.isocalendar()[1]
    
    return f"Today is {date_str}. The time is {time_str}. It is week {week_num} of the year."

# Global / Helper Wrappers
def assistant_action(command):
    command = command.lower()
    
    if "email" in command:
        # Simple extraction
        # "email to boss about meeting"
        recipient = ""
        subject = "Update"
        
        if "to" in command:
            parts = command.split("to")
            if len(parts) > 1:
                recipient = parts[1].split()[0]  # First word after 'to'
                
        if "about" in command:
            subject = command.split("about")[1].strip()
            
        return create_email(recipient, subject)
        
    elif "calendar" in command or "schedule" in command or "meeting" in command:
        if "new" in command or "create" in command or "add" in command:
            return open_calendar("new")
        else:
            return open_calendar("view")
            
    elif "date" in command or "day" in command:
        return get_date_time_info()
        
    return "I couldn't identify the assistant task."
