"""
Data storage module for Room Allocation System
Uses JSON-based persistence with file locking for multi-user access
"""

import json
import os
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import fcntl
import tempfile
import shutil


class DataStorage:
    """Thread-safe JSON-based data storage with file locking"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.lock = threading.Lock()
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Define data files
        self.files = {
            'weekly_preferences': os.path.join(data_dir, 'weekly_preferences.json'),
            'oasis_preferences': os.path.join(data_dir, 'oasis_preferences.json'),
            'weekly_allocations': os.path.join(data_dir, 'weekly_allocations.json'),
            'oasis_allocations': os.path.join(data_dir, 'oasis_allocations.json'),
            'admin_settings': os.path.join(data_dir, 'admin_settings.json'),
            'weekly_preferences_archive': os.path.join(data_dir, 'weekly_preferences_archive.json'),
            'oasis_preferences_archive': os.path.join(data_dir, 'oasis_preferences_archive.json'),
            'weekly_allocations_archive': os.path.join(data_dir, 'weekly_allocations_archive.json'),
            'oasis_allocations_archive': os.path.join(data_dir, 'oasis_allocations_archive.json')
        }
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize JSON files with empty structures"""
        default_structures = {
            'weekly_preferences': [],
            'oasis_preferences': [],
            'weekly_allocations': [],
            'oasis_allocations': [],
            'admin_settings': {
                'welcome_text': 'Welcome to the Room Allocation System',
                'project_room_instructions': 'Please submit your team preferences for project rooms.',
                'oasis_instructions': 'Please select your preferred days for Oasis workspace.',
                'allocation_period': 'Current Week',
                'last_reset': None
            },
            'weekly_preferences_archive': [],
            'oasis_preferences_archive': [],
            'weekly_allocations_archive': [],
            'oasis_allocations_archive': []
        }
        
        for file_key, file_path in self.files.items():
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump(default_structures[file_key], f, indent=2)
    
    def _read_file_with_lock(self, file_path: str) -> Any:
        """Read JSON file with file locking"""
        try:
            with open(file_path, 'r') as f:
                # Apply shared lock for reading
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    data = json.load(f)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return [] if file_path.endswith('preferences.json') or file_path.endswith('allocations.json') or file_path.endswith('archive.json') else {}
    
    def _write_file_with_lock(self, file_path: str, data: Any):
        """Write JSON file with file locking and atomic operation"""
        # Create temporary file in the same directory
        temp_dir = os.path.dirname(file_path)
        with tempfile.NamedTemporaryFile(mode='w', dir=temp_dir, delete=False, suffix='.tmp') as temp_f:
            temp_path = temp_f.name
            
            # Apply exclusive lock for writing
            fcntl.flock(temp_f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(data, temp_f, indent=2, default=str)
                temp_f.flush()
                os.fsync(temp_f.fileno())
            finally:
                fcntl.flock(temp_f.fileno(), fcntl.LOCK_UN)
        
        # Atomically replace the original file
        shutil.move(temp_path, file_path)
    
    def get_weekly_preferences(self) -> List[Dict]:
        """Get all weekly preferences"""
        with self.lock:
            return self._read_file_with_lock(self.files['weekly_preferences'])
    
    def add_weekly_preference(self, preference: Dict) -> bool:
        """Add a new weekly preference"""
        with self.lock:
            preferences = self._read_file_with_lock(self.files['weekly_preferences'])
            
            # Check if team already submitted
            team_name = preference.get('team_name', '').strip().lower()
            for existing in preferences:
                if existing.get('team_name', '').strip().lower() == team_name:
                    return False  # Team already submitted
            
            # Add timestamp
            preference['submission_time'] = datetime.now().isoformat()
            preferences.append(preference)
            
            self._write_file_with_lock(self.files['weekly_preferences'], preferences)
            return True
    
    def get_oasis_preferences(self) -> List[Dict]:
        """Get all oasis preferences"""
        with self.lock:
            return self._read_file_with_lock(self.files['oasis_preferences'])
    
    def add_oasis_preference(self, preference: Dict) -> bool:
        """Add a new oasis preference"""
        with self.lock:
            preferences = self._read_file_with_lock(self.files['oasis_preferences'])
            
            # Check if person already submitted
            person_name = preference.get('person_name', '').strip().lower()
            for existing in preferences:
                if existing.get('person_name', '').strip().lower() == person_name:
                    return False  # Person already submitted
            
            # Add timestamp
            preference['submission_time'] = datetime.now().isoformat()
            preferences.append(preference)
            
            self._write_file_with_lock(self.files['oasis_preferences'], preferences)
            return True
    
    def get_weekly_allocations(self) -> List[Dict]:
        """Get all weekly allocations"""
        with self.lock:
            return self._read_file_with_lock(self.files['weekly_allocations'])
    
    def set_weekly_allocations(self, allocations: List[Dict]):
        """Set weekly allocations"""
        with self.lock:
            # Add timestamps to allocations
            for allocation in allocations:
                if 'created_at' not in allocation:
                    allocation['created_at'] = datetime.now().isoformat()
            
            self._write_file_with_lock(self.files['weekly_allocations'], allocations)
    
    def get_oasis_allocations(self) -> List[Dict]:
        """Get all oasis allocations"""
        with self.lock:
            return self._read_file_with_lock(self.files['oasis_allocations'])
    
    def set_oasis_allocations(self, allocations: List[Dict]):
        """Set oasis allocations"""
        with self.lock:
            # Add timestamps to allocations
            for allocation in allocations:
                if 'created_at' not in allocation:
                    allocation['created_at'] = datetime.now().isoformat()
            
            self._write_file_with_lock(self.files['oasis_allocations'], allocations)
    
    def get_admin_settings(self) -> Dict:
        """Get admin settings"""
        with self.lock:
            return self._read_file_with_lock(self.files['admin_settings'])
    
    def update_admin_setting(self, key: str, value: Any):
        """Update a specific admin setting"""
        with self.lock:
            settings = self._read_file_with_lock(self.files['admin_settings'])
            settings[key] = value
            settings['updated_at'] = datetime.now().isoformat()
            self._write_file_with_lock(self.files['admin_settings'], settings)
    
    def archive_and_reset(self):
        """Archive current data and reset for new allocation period"""
        with self.lock:
            timestamp = datetime.now().isoformat()
            
            # Archive current data
            for data_type in ['weekly_preferences', 'oasis_preferences', 'weekly_allocations', 'oasis_allocations']:
                current_data = self._read_file_with_lock(self.files[data_type])
                archive_data = self._read_file_with_lock(self.files[f'{data_type}_archive'])
                
                # Add archive timestamp to each record
                for record in current_data:
                    record['archived_at'] = timestamp
                
                # Append to archive
                archive_data.extend(current_data)
                self._write_file_with_lock(self.files[f'{data_type}_archive'], archive_data)
                
                # Clear current data
                self._write_file_with_lock(self.files[data_type], [])
            
            # Update admin settings
            self.update_admin_setting('last_reset', timestamp)
    
    def get_archive_data(self, data_type: str) -> List[Dict]:
        """Get archived data for analytics"""
        with self.lock:
            archive_file = self.files.get(f'{data_type}_archive')
            if archive_file:
                return self._read_file_with_lock(archive_file)
            return []
    
    def backup_data(self, backup_dir: str):
        """Create a backup of all data files"""
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        with self.lock:
            for file_key, file_path in self.files.items():
                if os.path.exists(file_path):
                    backup_path = os.path.join(backup_dir, f'{file_key}_{timestamp}.json')
                    shutil.copy2(file_path, backup_path)
    
    def get_capacity_info(self) -> Dict:
        """Get current capacity information"""
        # Project room capacities
        project_rooms = {
            'Room A': 6, 'Room B': 6,  # 2 rooms with 6-person capacity
            'Room C': 4, 'Room D': 4, 'Room E': 4, 'Room F': 4,  # 4 rooms with 4-person capacity
            'Room G': 4, 'Room H': 4, 'Room I': 4  # 3 more rooms with 4-person capacity
        }
        
        # Oasis capacity: 11 people per day
        oasis_capacity = 11
        
        return {
            'project_rooms': project_rooms,
            'oasis_capacity': oasis_capacity,
            'total_project_room_capacity': sum(project_rooms.values()),
            'weekdays': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        }


# Global storage instance
storage = DataStorage()

