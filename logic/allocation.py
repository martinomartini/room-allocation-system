"""
Allocation algorithms for Room Allocation System
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from data.models import WeeklyAllocation, OasisAllocation, ValidationHelper
from utils.helpers import get_current_week_dates, calculate_team_priority_score, parse_preferred_days_from_oasis_pref


class ProjectRoomAllocator:
    """Handles project room allocation logic"""
    
    def __init__(self):
        self.rooms = ValidationHelper.get_available_rooms()
        self.room_capacities = {
            'Room A': 6, 'Room B': 6,  # 2 rooms with 6-person capacity
            'Room C': 4, 'Room D': 4, 'Room E': 4, 'Room F': 4,  # 4 rooms with 4-person capacity
            'Room G': 4, 'Room H': 4, 'Room I': 4  # 3 more rooms with 4-person capacity
        }
    
    def allocate_rooms(self, preferences: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Allocate project rooms based on preferences
        
        Returns:
            Tuple of (allocations, unplaced_teams)
        """
        
        if not preferences:
            return [], []
        
        # Separate teams by preference
        mon_wed_teams = [p for p in preferences if p['preferred_days'] == 'Monday & Wednesday']
        tue_thu_teams = [p for p in preferences if p['preferred_days'] == 'Tuesday & Thursday']
        
        # Sort teams by priority (size first, then submission time)
        mon_wed_teams.sort(key=lambda x: calculate_team_priority_score(x['team_size'], x.get('submission_time', '')), reverse=True)
        tue_thu_teams.sort(key=lambda x: calculate_team_priority_score(x['team_size'], x.get('submission_time', '')), reverse=True)
        
        # Shuffle teams of same size for fairness
        self._shuffle_same_priority_teams(mon_wed_teams)
        self._shuffle_same_priority_teams(tue_thu_teams)
        
        allocations = []
        unplaced_teams = []
        
        # Get current week dates
        week_dates = get_current_week_dates()
        date_map = {day: date for day, date in week_dates}
        
        # Allocate Monday & Wednesday teams
        mon_wed_allocations, mon_wed_unplaced = self._allocate_teams_for_days(
            mon_wed_teams, ['Monday', 'Wednesday'], date_map
        )
        allocations.extend(mon_wed_allocations)
        
        # Allocate Tuesday & Thursday teams
        tue_thu_allocations, tue_thu_unplaced = self._allocate_teams_for_days(
            tue_thu_teams, ['Tuesday', 'Thursday'], date_map
        )
        allocations.extend(tue_thu_allocations)
        
        # Try to place unplaced teams on alternative days
        all_unplaced = mon_wed_unplaced + tue_thu_unplaced
        
        for team in all_unplaced:
            # Try alternative days
            alternative_days = ['Tuesday', 'Thursday'] if team['preferred_days'] == 'Monday & Wednesday' else ['Monday', 'Wednesday']
            
            alt_allocations, alt_unplaced = self._allocate_teams_for_days(
                [team], alternative_days, date_map, existing_allocations=allocations
            )
            
            if alt_allocations:
                allocations.extend(alt_allocations)
            else:
                unplaced_teams.append(team['team_name'])
        
        return allocations, unplaced_teams
    
    def _shuffle_same_priority_teams(self, teams: List[Dict[str, Any]]):
        """Shuffle teams with the same priority score for fairness"""
        
        if len(teams) <= 1:
            return
        
        # Group by priority score
        priority_groups = {}
        for team in teams:
            score = calculate_team_priority_score(team['team_size'], team.get('submission_time', ''))
            if score not in priority_groups:
                priority_groups[score] = []
            priority_groups[score].append(team)
        
        # Shuffle within each group
        for group in priority_groups.values():
            random.shuffle(group)
        
        # Rebuild the list
        teams.clear()
        for score in sorted(priority_groups.keys(), reverse=True):
            teams.extend(priority_groups[score])
    
    def _allocate_teams_for_days(self, teams: List[Dict[str, Any]], days: List[str], 
                                date_map: Dict[str, str], existing_allocations: List[Dict] = None) -> Tuple[List[Dict], List[Dict]]:
        """Allocate teams for specific days"""
        
        if existing_allocations is None:
            existing_allocations = []
        
        allocations = []
        unplaced_teams = []
        
        # Track room usage for each day
        room_usage = {day: {room: 0 for room in self.rooms} for day in days}
        
        # Account for existing allocations
        for allocation in existing_allocations:
            day = allocation['day_of_week']
            room = allocation['room_name']
            if day in room_usage and room in room_usage[day]:
                # Find team size from original preferences (this is a simplification)
                room_usage[day][room] = self.room_capacities[room]  # Mark as full
        
        for team in teams:
            team_size = team['team_size']
            team_name = team['team_name']
            
            # Find suitable room for both days
            suitable_room = None
            
            for room in self.rooms:
                room_capacity = self.room_capacities[room]
                
                # Check if room can accommodate team on both days
                if room_capacity >= team_size:
                    available_both_days = True
                    for day in days:
                        if room_usage[day][room] + team_size > room_capacity:
                            available_both_days = False
                            break
                    
                    if available_both_days:
                        suitable_room = room
                        break
            
            if suitable_room:
                # Allocate room for both days
                for day in days:
                    allocation = WeeklyAllocation(
                        team_name=team_name,
                        room_name=suitable_room,
                        date=date_map[day],
                        day_of_week=day,
                        confirmed=False,
                        created_at=datetime.now().isoformat()
                    )
                    allocations.append(allocation.to_dict())
                    
                    # Update room usage
                    room_usage[day][suitable_room] += team_size
            else:
                unplaced_teams.append(team)
        
        return allocations, unplaced_teams


class OasisAllocator:
    """Handles Oasis workspace allocation logic"""
    
    def __init__(self):
        self.daily_capacity = 11
        self.weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    def allocate_oasis(self, preferences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Allocate Oasis workspace based on preferences
        
        Algorithm:
        1. First pass: Ensure everyone gets at least one preferred day
        2. Additional passes: Fill remaining spots with users' other preferences
        3. Random assignment order for fairness
        """
        
        if not preferences:
            return []
        
        # Parse preferences
        parsed_preferences = []
        for pref in preferences:
            person_name = pref['person_name']
            preferred_days = parse_preferred_days_from_oasis_pref(pref)
            
            parsed_preferences.append({
                'person_name': person_name,
                'preferred_days': preferred_days,
                'submission_time': pref.get('submission_time', '')
            })
        
        # Get current week dates
        week_dates = get_current_week_dates()
        date_map = {day: date for day, date in week_dates}
        
        # Initialize daily allocations
        daily_allocations = {day: [] for day in self.weekdays}
        person_allocations = {pref['person_name']: [] for pref in parsed_preferences}
        
        # First pass: Ensure everyone gets at least one preferred day
        unallocated_people = list(parsed_preferences)
        random.shuffle(unallocated_people)  # Random order for fairness
        
        for person in unallocated_people[:]:  # Copy list to modify during iteration
            allocated = False
            
            # Try to allocate to one of their preferred days
            preferred_days = person['preferred_days'][:]
            random.shuffle(preferred_days)  # Random order for fairness
            
            for day in preferred_days:
                if len(daily_allocations[day]) < self.daily_capacity:
                    # Allocate this person to this day
                    allocation = OasisAllocation(
                        person_name=person['person_name'],
                        date=date_map[day],
                        day_of_week=day,
                        confirmed=False,
                        created_at=datetime.now().isoformat()
                    )
                    
                    daily_allocations[day].append(allocation.to_dict())
                    person_allocations[person['person_name']].append(day)
                    allocated = True
                    break
            
            if allocated:
                unallocated_people.remove(person)
        
        # Additional passes: Fill remaining spots
        max_additional_passes = 4  # Prevent infinite loops
        
        for pass_num in range(max_additional_passes):
            if not unallocated_people:
                break
            
            # Try to allocate remaining people
            for person in unallocated_people[:]:
                allocated = False
                
                # Try their preferred days again
                preferred_days = person['preferred_days'][:]
                random.shuffle(preferred_days)
                
                for day in preferred_days:
                    if len(daily_allocations[day]) < self.daily_capacity:
                        allocation = OasisAllocation(
                            person_name=person['person_name'],
                            date=date_map[day],
                            day_of_week=day,
                            confirmed=False,
                            created_at=datetime.now().isoformat()
                        )
                        
                        daily_allocations[day].append(allocation.to_dict())
                        person_allocations[person['person_name']].append(day)
                        allocated = True
                        break
                
                if allocated:
                    unallocated_people.remove(person)
        
        # Additional allocation for people who already have days (up to their preferences)
        for pass_num in range(max_additional_passes):
            made_allocation = False
            
            # Shuffle people for fairness
            all_people = list(parsed_preferences)
            random.shuffle(all_people)
            
            for person in all_people:
                person_name = person['person_name']
                current_days = person_allocations[person_name]
                preferred_days = person['preferred_days']
                
                # Skip if person already has all their preferred days
                if len(current_days) >= len(preferred_days):
                    continue
                
                # Try to allocate to additional preferred days
                for day in preferred_days:
                    if day not in current_days and len(daily_allocations[day]) < self.daily_capacity:
                        allocation = OasisAllocation(
                            person_name=person_name,
                            date=date_map[day],
                            day_of_week=day,
                            confirmed=False,
                            created_at=datetime.now().isoformat()
                        )
                        
                        daily_allocations[day].append(allocation.to_dict())
                        person_allocations[person_name].append(day)
                        made_allocation = True
                        break
            
            if not made_allocation:
                break
        
        # Flatten all allocations
        all_allocations = []
        for day_allocations in daily_allocations.values():
            all_allocations.extend(day_allocations)
        
        return all_allocations
    
    def get_daily_availability(self, existing_allocations: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get remaining capacity for each day"""
        
        # Count existing allocations per day
        daily_counts = {day: 0 for day in self.weekdays}
        
        for allocation in existing_allocations:
            day = allocation.get('day_of_week')
            if day in daily_counts:
                daily_counts[day] += 1
        
        # Calculate remaining capacity
        availability = {}
        for day in self.weekdays:
            availability[day] = max(0, self.daily_capacity - daily_counts[day])
        
        return availability
    
    def can_add_person_to_day(self, day: str, existing_allocations: List[Dict[str, Any]]) -> bool:
        """Check if a person can be added to a specific day"""
        
        if day not in self.weekdays:
            return False
        
        availability = self.get_daily_availability(existing_allocations)
        return availability[day] > 0
    
    def add_adhoc_allocation(self, person_name: str, day: str, existing_allocations: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Add an ad-hoc allocation if possible"""
        
        if not self.can_add_person_to_day(day, existing_allocations):
            return None
        
        # Check if person is already allocated for this day
        for allocation in existing_allocations:
            if (allocation.get('person_name') == person_name and 
                allocation.get('day_of_week') == day):
                return None  # Already allocated
        
        # Get date for the day
        week_dates = get_current_week_dates()
        date_map = {day_name: date for day_name, date in week_dates}
        
        if day not in date_map:
            return None
        
        # Create allocation
        allocation = OasisAllocation(
            person_name=person_name,
            date=date_map[day],
            day_of_week=day,
            confirmed=False,
            created_at=datetime.now().isoformat()
        )
        
        return allocation.to_dict()


# Utility functions for allocation management

def run_project_room_allocation(preferences: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Run project room allocation and return results"""
    
    allocator = ProjectRoomAllocator()
    return allocator.allocate_rooms(preferences)


def run_oasis_allocation(preferences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Run Oasis allocation and return results"""
    
    allocator = OasisAllocator()
    return allocator.allocate_oasis(preferences)


def validate_allocation_results(weekly_allocations: List[Dict], oasis_allocations: List[Dict]) -> Dict[str, Any]:
    """Validate allocation results and return summary"""
    
    validation_results = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'summary': {}
    }
    
    # Validate project room allocations
    room_usage = {}
    for allocation in weekly_allocations:
        room = allocation['room_name']
        day = allocation['day_of_week']
        key = f"{room}_{day}"
        
        if key not in room_usage:
            room_usage[key] = []
        room_usage[key].append(allocation['team_name'])
    
    # Check for room conflicts
    for key, teams in room_usage.items():
        if len(teams) > 1:
            validation_results['errors'].append(f"Room conflict: {key} assigned to multiple teams: {', '.join(teams)}")
            validation_results['valid'] = False
    
    # Validate Oasis allocations
    oasis_usage = {}
    for allocation in oasis_allocations:
        day = allocation['day_of_week']
        
        if day not in oasis_usage:
            oasis_usage[day] = []
        oasis_usage[day].append(allocation['person_name'])
    
    # Check for Oasis capacity violations
    for day, people in oasis_usage.items():
        if len(people) > 11:
            validation_results['errors'].append(f"Oasis capacity exceeded on {day}: {len(people)} people (max 11)")
            validation_results['valid'] = False
        
        # Check for duplicate allocations
        if len(people) != len(set(people)):
            duplicates = [p for p in people if people.count(p) > 1]
            validation_results['errors'].append(f"Duplicate Oasis allocations on {day}: {', '.join(set(duplicates))}")
            validation_results['valid'] = False
    
    # Generate summary
    validation_results['summary'] = {
        'total_project_allocations': len(weekly_allocations),
        'total_oasis_allocations': len(oasis_allocations),
        'unique_teams': len(set(a['team_name'] for a in weekly_allocations)),
        'unique_people': len(set(a['person_name'] for a in oasis_allocations)),
        'rooms_used': len(set(a['room_name'] for a in weekly_allocations)),
        'oasis_daily_usage': {day: len(people) for day, people in oasis_usage.items()}
    }
    
    return validation_results

