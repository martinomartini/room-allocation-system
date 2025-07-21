"""
Data models and validation for Room Allocation System
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
import re


@dataclass
class TeamPreference:
    """Model for team project room preferences"""
    team_name: str
    contact_person: str
    team_size: int
    preferred_days: str  # "Monday & Wednesday" or "Tuesday & Thursday"
    submission_time: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate team preference data"""
        errors = []
        
        # Team name validation
        if not self.team_name or not self.team_name.strip():
            errors.append("Team name is required")
        elif len(self.team_name.strip()) < 2:
            errors.append("Team name must be at least 2 characters")
        elif len(self.team_name.strip()) > 50:
            errors.append("Team name must be less than 50 characters")
        
        # Contact person validation
        if not self.contact_person or not self.contact_person.strip():
            errors.append("Contact person is required")
        elif len(self.contact_person.strip()) < 2:
            errors.append("Contact person name must be at least 2 characters")
        elif len(self.contact_person.strip()) > 50:
            errors.append("Contact person name must be less than 50 characters")
        
        # Team size validation
        if not isinstance(self.team_size, int) or self.team_size < 3 or self.team_size > 6:
            errors.append("Team size must be between 3 and 6 people")
        
        # Preferred days validation
        valid_days = ["Monday & Wednesday", "Tuesday & Thursday"]
        if self.preferred_days not in valid_days:
            errors.append("Preferred days must be either 'Monday & Wednesday' or 'Tuesday & Thursday'")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'team_name': self.team_name.strip(),
            'contact_person': self.contact_person.strip(),
            'team_size': self.team_size,
            'preferred_days': self.preferred_days,
            'submission_time': self.submission_time
        }


@dataclass
class OasisPreference:
    """Model for individual Oasis preferences"""
    person_name: str
    preferred_days: List[str]  # Up to 5 weekdays
    submission_time: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate oasis preference data"""
        errors = []
        
        # Person name validation
        if not self.person_name or not self.person_name.strip():
            errors.append("Person name is required")
        elif len(self.person_name.strip()) < 2:
            errors.append("Person name must be at least 2 characters")
        elif len(self.person_name.strip()) > 50:
            errors.append("Person name must be less than 50 characters")
        
        # Preferred days validation
        valid_weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        if not self.preferred_days:
            errors.append("At least one preferred day must be selected")
        elif len(self.preferred_days) > 5:
            errors.append("Maximum 5 preferred days can be selected")
        else:
            for day in self.preferred_days:
                if day not in valid_weekdays:
                    errors.append(f"Invalid day: {day}")
            
            # Check for duplicates
            if len(self.preferred_days) != len(set(self.preferred_days)):
                errors.append("Duplicate days are not allowed")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        # Store as individual day fields for easier processing
        result = {
            'person_name': self.person_name.strip(),
            'submission_time': self.submission_time
        }
        
        # Add preferred days as separate fields
        for i in range(5):
            day_key = f'preferred_day_{i+1}'
            result[day_key] = self.preferred_days[i] if i < len(self.preferred_days) else None
        
        return result


@dataclass
class WeeklyAllocation:
    """Model for weekly project room allocation"""
    team_name: str
    room_name: str
    date: str  # ISO format date
    day_of_week: str  # Monday, Tuesday, etc.
    confirmed: bool = False
    confirmed_at: Optional[str] = None
    created_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'team_name': self.team_name,
            'room_name': self.room_name,
            'date': self.date,
            'day_of_week': self.day_of_week,
            'confirmed': self.confirmed,
            'confirmed_at': self.confirmed_at,
            'created_at': self.created_at
        }


@dataclass
class OasisAllocation:
    """Model for Oasis allocation"""
    person_name: str
    date: str  # ISO format date
    day_of_week: str  # Monday, Tuesday, etc.
    confirmed: bool = False
    confirmed_at: Optional[str] = None
    created_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'person_name': self.person_name,
            'date': self.date,
            'day_of_week': self.day_of_week,
            'confirmed': self.confirmed,
            'confirmed_at': self.confirmed_at,
            'created_at': self.created_at
        }


class ValidationHelper:
    """Helper class for common validation functions"""
    
    @staticmethod
    def validate_name(name: str, field_name: str = "Name") -> List[str]:
        """Validate name fields"""
        errors = []
        
        if not name or not name.strip():
            errors.append(f"{field_name} is required")
            return errors
        
        name = name.strip()
        
        if len(name) < 2:
            errors.append(f"{field_name} must be at least 2 characters")
        elif len(name) > 50:
            errors.append(f"{field_name} must be less than 50 characters")
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-']+$", name):
            errors.append(f"{field_name} can only contain letters, spaces, hyphens, and apostrophes")
        
        return errors
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize text input"""
        if not text:
            return ""
        
        # Strip whitespace and normalize
        text = text.strip()
        
        # Remove any potentially harmful characters
        text = re.sub(r'[<>"\']', '', text)
        
        return text
    
    @staticmethod
    def validate_team_size(size: Any) -> List[str]:
        """Validate team size"""
        errors = []
        
        try:
            size = int(size)
            if size < 3 or size > 6:
                errors.append("Team size must be between 3 and 6 people")
        except (ValueError, TypeError):
            errors.append("Team size must be a valid number")
        
        return errors
    
    @staticmethod
    def get_room_capacity(room_name: str) -> int:
        """Get capacity for a specific room"""
        room_capacities = {
            'Room A': 6, 'Room B': 6,  # 2 rooms with 6-person capacity
            'Room C': 4, 'Room D': 4, 'Room E': 4, 'Room F': 4,  # 4 rooms with 4-person capacity
            'Room G': 4, 'Room H': 4, 'Room I': 4  # 3 more rooms with 4-person capacity
        }
        return room_capacities.get(room_name, 4)  # Default to 4 if room not found
    
    @staticmethod
    def get_available_rooms() -> List[str]:
        """Get list of available room names"""
        return ['Room A', 'Room B', 'Room C', 'Room D', 'Room E', 'Room F', 'Room G', 'Room H', 'Room I']
    
    @staticmethod
    def get_weekdays() -> List[str]:
        """Get list of weekdays"""
        return ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

