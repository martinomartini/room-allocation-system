"""
Security utilities for Room Allocation System
"""

import hashlib
import secrets
import time
from typing import Dict, Any, Optional
import streamlit as st
import re


class SecurityManager:
    """Handles security-related operations"""
    
    def __init__(self):
        self.admin_password_hash = self._hash_password("trainee")
        self.session_timeout = 3600  # 1 hour in seconds
        self.max_login_attempts = 5
        self.lockout_duration = 900  # 15 minutes in seconds
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_admin_password(self, password: str) -> bool:
        """Verify admin password"""
        if not password:
            return False
        
        # Check for brute force attempts
        if self._is_locked_out():
            return False
        
        # Verify password
        password_hash = self._hash_password(password)
        is_valid = password_hash == self.admin_password_hash
        
        # Track login attempts
        self._track_login_attempt(is_valid)
        
        return is_valid
    
    def _is_locked_out(self) -> bool:
        """Check if admin login is locked out due to failed attempts"""
        if 'admin_lockout_until' not in st.session_state:
            return False
        
        lockout_until = st.session_state.admin_lockout_until
        return time.time() < lockout_until
    
    def _track_login_attempt(self, success: bool):
        """Track login attempts for brute force protection"""
        if 'admin_login_attempts' not in st.session_state:
            st.session_state.admin_login_attempts = 0
        
        if success:
            # Reset attempts on successful login
            st.session_state.admin_login_attempts = 0
            if 'admin_lockout_until' in st.session_state:
                del st.session_state.admin_lockout_until
        else:
            # Increment failed attempts
            st.session_state.admin_login_attempts += 1
            
            # Lock out if too many attempts
            if st.session_state.admin_login_attempts >= self.max_login_attempts:
                st.session_state.admin_lockout_until = time.time() + self.lockout_duration
    
    def get_lockout_remaining_time(self) -> int:
        """Get remaining lockout time in seconds"""
        if not self._is_locked_out():
            return 0
        
        return int(st.session_state.admin_lockout_until - time.time())
    
    def is_admin_session_valid(self) -> bool:
        """Check if admin session is still valid"""
        if not st.session_state.get('admin_authenticated', False):
            return False
        
        # Check session timeout
        if 'admin_login_time' not in st.session_state:
            return False
        
        login_time = st.session_state.admin_login_time
        return (time.time() - login_time) < self.session_timeout
    
    def start_admin_session(self):
        """Start admin session"""
        st.session_state.admin_authenticated = True
        st.session_state.admin_login_time = time.time()
    
    def end_admin_session(self):
        """End admin session"""
        if 'admin_authenticated' in st.session_state:
            del st.session_state.admin_authenticated
        if 'admin_login_time' in st.session_state:
            del st.session_state.admin_login_time


class InputValidator:
    """Validates and sanitizes user inputs"""
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 100) -> str:
        """Sanitize text input"""
        if not text:
            return ""
        
        # Strip whitespace
        text = text.strip()
        
        # Remove potentially harmful characters
        text = re.sub(r'[<>"\'\x00-\x1f\x7f-\x9f]', '', text)
        
        # Limit length
        if len(text) > max_length:
            text = text[:max_length]
        
        return text
    
    @staticmethod
    def validate_team_name(team_name: str) -> tuple[bool, str]:
        """Validate team name"""
        if not team_name or not team_name.strip():
            return False, "Team name is required"
        
        team_name = InputValidator.sanitize_text(team_name, 50)
        
        if len(team_name) < 2:
            return False, "Team name must be at least 2 characters"
        
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', team_name):
            return False, "Team name can only contain letters, numbers, spaces, hyphens, and underscores"
        
        # Check for common injection patterns
        dangerous_patterns = ['script', 'javascript', 'vbscript', 'onload', 'onerror']
        team_name_lower = team_name.lower()
        for pattern in dangerous_patterns:
            if pattern in team_name_lower:
                return False, "Team name contains invalid content"
        
        return True, team_name
    
    @staticmethod
    def validate_person_name(person_name: str) -> tuple[bool, str]:
        """Validate person name"""
        if not person_name or not person_name.strip():
            return False, "Person name is required"
        
        person_name = InputValidator.sanitize_text(person_name, 50)
        
        if len(person_name) < 2:
            return False, "Person name must be at least 2 characters"
        
        if not re.match(r"^[a-zA-Z\s\-']+$", person_name):
            return False, "Person name can only contain letters, spaces, hyphens, and apostrophes"
        
        # Check for common injection patterns
        dangerous_patterns = ['script', 'javascript', 'vbscript', 'onload', 'onerror']
        person_name_lower = person_name.lower()
        for pattern in dangerous_patterns:
            if pattern in person_name_lower:
                return False, "Person name contains invalid content"
        
        return True, person_name
    
    @staticmethod
    def validate_team_size(team_size: Any) -> tuple[bool, int]:
        """Validate team size"""
        try:
            size = int(team_size)
            if size < 3 or size > 6:
                return False, 0
            return True, size
        except (ValueError, TypeError):
            return False, 0
    
    @staticmethod
    def validate_preferred_days(preferred_days: str) -> tuple[bool, str]:
        """Validate preferred days for project rooms"""
        valid_options = ["Monday & Wednesday", "Tuesday & Thursday"]
        
        if preferred_days not in valid_options:
            return False, ""
        
        return True, preferred_days
    
    @staticmethod
    def validate_oasis_days(selected_days: list) -> tuple[bool, list]:
        """Validate selected days for Oasis"""
        valid_weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        if not selected_days:
            return False, []
        
        if len(selected_days) > 5:
            return False, []
        
        # Check all days are valid
        for day in selected_days:
            if day not in valid_weekdays:
                return False, []
        
        # Check for duplicates
        if len(selected_days) != len(set(selected_days)):
            return False, []
        
        return True, selected_days
    
    @staticmethod
    def validate_admin_setting(key: str, value: str) -> tuple[bool, str]:
        """Validate admin setting values"""
        if not key or not isinstance(key, str):
            return False, ""
        
        # Sanitize the value
        value = InputValidator.sanitize_text(value, 1000)  # Allow longer text for settings
        
        # Check for dangerous content
        dangerous_patterns = ['<script', 'javascript:', 'vbscript:', 'data:', 'file:']
        value_lower = value.lower()
        for pattern in dangerous_patterns:
            if pattern in value_lower:
                return False, ""
        
        return True, value


class RateLimiter:
    """Simple rate limiting for form submissions"""
    
    def __init__(self):
        self.submission_window = 60  # 1 minute
        self.max_submissions = 5  # Max 5 submissions per minute
    
    def is_rate_limited(self, identifier: str) -> bool:
        """Check if identifier is rate limited"""
        current_time = time.time()
        
        # Initialize session state for rate limiting
        if 'rate_limit_data' not in st.session_state:
            st.session_state.rate_limit_data = {}
        
        rate_data = st.session_state.rate_limit_data
        
        # Clean old entries
        if identifier in rate_data:
            rate_data[identifier] = [
                timestamp for timestamp in rate_data[identifier]
                if current_time - timestamp < self.submission_window
            ]
        else:
            rate_data[identifier] = []
        
        # Check if rate limited
        if len(rate_data[identifier]) >= self.max_submissions:
            return True
        
        # Record this attempt
        rate_data[identifier].append(current_time)
        return False
    
    def get_remaining_time(self, identifier: str) -> int:
        """Get remaining time until rate limit resets"""
        if 'rate_limit_data' not in st.session_state:
            return 0
        
        rate_data = st.session_state.rate_limit_data
        
        if identifier not in rate_data or not rate_data[identifier]:
            return 0
        
        oldest_submission = min(rate_data[identifier])
        remaining = self.submission_window - (time.time() - oldest_submission)
        
        return max(0, int(remaining))


class SessionManager:
    """Manages user sessions and state"""
    
    @staticmethod
    def initialize_session():
        """Initialize session state variables"""
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
            st.session_state.admin_authenticated = False
            st.session_state.page_visits = {}
            st.session_state.form_data = {}
    
    @staticmethod
    def track_page_visit(page_name: str):
        """Track page visits for analytics"""
        if 'page_visits' not in st.session_state:
            st.session_state.page_visits = {}
        
        if page_name not in st.session_state.page_visits:
            st.session_state.page_visits[page_name] = 0
        
        st.session_state.page_visits[page_name] += 1
    
    @staticmethod
    def clear_form_data():
        """Clear stored form data"""
        if 'form_data' in st.session_state:
            st.session_state.form_data = {}
    
    @staticmethod
    def store_form_data(form_name: str, data: Dict[str, Any]):
        """Store form data temporarily"""
        if 'form_data' not in st.session_state:
            st.session_state.form_data = {}
        
        st.session_state.form_data[form_name] = data
    
    @staticmethod
    def get_form_data(form_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve stored form data"""
        if 'form_data' not in st.session_state:
            return None
        
        return st.session_state.form_data.get(form_name)


# Global instances
security_manager = SecurityManager()
input_validator = InputValidator()
rate_limiter = RateLimiter()
session_manager = SessionManager()

