"""
Utility helper functions for Room Allocation System
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import re


def format_date(date_str: str, format_type: str = "display") -> str:
    """Format date string for display"""
    
    if not date_str:
        return "N/A"
    
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        
        if format_type == "display":
            return dt.strftime("%Y-%m-%d %H:%M")
        elif format_type == "date_only":
            return dt.strftime("%Y-%m-%d")
        elif format_type == "time_only":
            return dt.strftime("%H:%M")
        elif format_type == "friendly":
            return dt.strftime("%B %d, %Y at %I:%M %p")
        else:
            return dt.strftime("%Y-%m-%d %H:%M")
    
    except (ValueError, AttributeError):
        return date_str


def get_current_week_dates() -> List[Tuple[str, str]]:
    """Get current week's dates (Monday to Friday)"""
    
    today = datetime.now()
    
    # Find Monday of current week
    days_since_monday = today.weekday()
    monday = today - timedelta(days=days_since_monday)
    
    # Generate week dates
    week_dates = []
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    for i, day_name in enumerate(weekdays):
        date = monday + timedelta(days=i)
        week_dates.append((day_name, date.strftime("%Y-%m-%d")))
    
    return week_dates


def get_next_week_dates() -> List[Tuple[str, str]]:
    """Get next week's dates (Monday to Friday)"""
    
    today = datetime.now()
    
    # Find Monday of next week
    days_since_monday = today.weekday()
    next_monday = today + timedelta(days=(7 - days_since_monday))
    
    # Generate week dates
    week_dates = []
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    for i, day_name in enumerate(weekdays):
        date = next_monday + timedelta(days=i)
        week_dates.append((day_name, date.strftime("%Y-%m-%d")))
    
    return week_dates


def sanitize_text_input(text: str) -> str:
    """Sanitize text input for security"""
    
    if not text:
        return ""
    
    # Strip whitespace
    text = text.strip()
    
    # Remove potentially harmful characters
    text = re.sub(r'[<>"\']', '', text)
    
    # Limit length
    if len(text) > 100:
        text = text[:100]
    
    return text


def validate_email(email: str) -> bool:
    """Validate email format"""
    
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def calculate_allocation_stats(allocations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate allocation statistics"""
    
    if not allocations:
        return {
            'total_allocations': 0,
            'confirmed_allocations': 0,
            'pending_allocations': 0,
            'confirmation_rate': 0.0
        }
    
    total = len(allocations)
    confirmed = len([a for a in allocations if a.get('confirmed', False)])
    pending = total - confirmed
    confirmation_rate = (confirmed / total) * 100 if total > 0 else 0.0
    
    return {
        'total_allocations': total,
        'confirmed_allocations': confirmed,
        'pending_allocations': pending,
        'confirmation_rate': round(confirmation_rate, 1)
    }


def group_allocations_by_day(allocations: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group allocations by day of week"""
    
    grouped = {
        'Monday': [],
        'Tuesday': [],
        'Wednesday': [],
        'Thursday': [],
        'Friday': []
    }
    
    for allocation in allocations:
        day = allocation.get('day_of_week')
        if day in grouped:
            grouped[day].append(allocation)
    
    return grouped


def calculate_capacity_utilization(allocations: List[Dict[str, Any]], capacity_per_day: int) -> Dict[str, float]:
    """Calculate capacity utilization by day"""
    
    grouped = group_allocations_by_day(allocations)
    utilization = {}
    
    for day, day_allocations in grouped.items():
        count = len(day_allocations)
        utilization[day] = (count / capacity_per_day) * 100 if capacity_per_day > 0 else 0.0
    
    return utilization


def generate_allocation_summary(weekly_allocations: List[Dict], oasis_allocations: List[Dict]) -> Dict[str, Any]:
    """Generate comprehensive allocation summary"""
    
    # Weekly allocations stats
    weekly_stats = calculate_allocation_stats(weekly_allocations)
    
    # Oasis allocations stats
    oasis_stats = calculate_allocation_stats(oasis_allocations)
    
    # Capacity utilization
    oasis_utilization = calculate_capacity_utilization(oasis_allocations, 11)
    
    # Team size distribution
    team_sizes = {}
    for allocation in weekly_allocations:
        # This would need team size info from preferences
        pass
    
    return {
        'weekly_stats': weekly_stats,
        'oasis_stats': oasis_stats,
        'oasis_utilization': oasis_utilization,
        'generated_at': datetime.now().isoformat()
    }


def export_data_to_csv(data: List[Dict[str, Any]], filename: str) -> str:
    """Export data to CSV format (returns CSV string)"""
    
    if not data:
        return ""
    
    import csv
    import io
    
    output = io.StringIO()
    
    if data:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    return output.getvalue()


def parse_preferred_days_from_oasis_pref(pref: Dict[str, Any]) -> List[str]:
    """Parse preferred days from Oasis preference dictionary"""
    
    preferred_days = []
    
    for i in range(1, 6):
        day = pref.get(f'preferred_day_{i}')
        if day:
            preferred_days.append(day)
    
    return preferred_days


def create_backup_filename(prefix: str) -> str:
    """Create a backup filename with timestamp"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_backup_{timestamp}.json"


def is_valid_team_name(team_name: str) -> bool:
    """Validate team name format"""
    
    if not team_name or not team_name.strip():
        return False
    
    team_name = team_name.strip()
    
    # Check length
    if len(team_name) < 2 or len(team_name) > 50:
        return False
    
    # Check for valid characters
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', team_name):
        return False
    
    return True


def is_valid_person_name(person_name: str) -> bool:
    """Validate person name format"""
    
    if not person_name or not person_name.strip():
        return False
    
    person_name = person_name.strip()
    
    # Check length
    if len(person_name) < 2 or len(person_name) > 50:
        return False
    
    # Check for valid characters (letters, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-Z\s\-']+$", person_name):
        return False
    
    return True


def get_week_range_string(start_date: str = None) -> str:
    """Get a formatted week range string"""
    
    if start_date:
        try:
            start = datetime.fromisoformat(start_date)
        except ValueError:
            start = datetime.now()
    else:
        start = datetime.now()
    
    # Find Monday of the week
    days_since_monday = start.weekday()
    monday = start - timedelta(days=days_since_monday)
    friday = monday + timedelta(days=4)
    
    return f"{monday.strftime('%B %d')} - {friday.strftime('%B %d, %Y')}"


def calculate_team_priority_score(team_size: int, submission_time: str) -> float:
    """Calculate priority score for team allocation (higher = better priority)"""
    
    # Larger teams get higher priority
    size_score = team_size * 10
    
    # Earlier submissions get slight priority (but less important than size)
    try:
        submission_dt = datetime.fromisoformat(submission_time)
        # Convert to hours since epoch, then invert (earlier = higher score)
        time_score = -(submission_dt.timestamp() / 3600)
    except (ValueError, AttributeError):
        time_score = 0
    
    return size_score + (time_score * 0.001)  # Time has minimal impact compared to size

