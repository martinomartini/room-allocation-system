"""
Room Allocation System - Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any

# Import our modules
from data.storage import storage
from data.models import TeamPreference, OasisPreference, ValidationHelper
from logic.allocation import ProjectRoomAllocator, OasisAllocator
from ui.components import render_capacity_info, render_allocation_matrix
from utils.helpers import format_date, get_current_week_dates, parse_preferred_days_from_oasis_pref
from utils.security import security_manager, input_validator, rate_limiter, session_manager

# Railway deployment support
PORT = int(os.environ.get("PORT", 8501))


# Page configuration
st.set_page_config(
    page_title="Room Allocation System",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    
    .capacity-indicator {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .capacity-available {
        background-color: #d4edda;
        color: #155724;
    }
    
    .capacity-full {
        background-color: #f8d7da;
        color: #721c24;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #5a6fd8 0%, #6a4190 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application function"""
    
    # Initialize session state and security
    session_manager.initialize_session()
    
    # Check admin session validity
    if st.session_state.get('admin_authenticated', False):
        if not security_manager.is_admin_session_valid():
            st.session_state.admin_authenticated = False
            st.warning("⚠️ Admin session expired. Please log in again.")
    
    # Sidebar navigation
    st.sidebar.title("🏢 Navigation")
    
    pages = {
        "🏠 Home": "home",
        "📋 Project Rooms": "project_rooms", 
        "🌴 Oasis Workspace": "oasis",
        "📊 Current Allocations": "allocations",
        "📈 Analytics": "analytics",
        "⚙️ Admin Panel": "admin"
    }
    
    selected_page = st.sidebar.selectbox("Select Page", list(pages.keys()))
    page_key = pages[selected_page]
    
    # Check if page was changed via button
    if 'selected_page' in st.session_state:
        page_key = st.session_state.selected_page
        # Update selectbox to match
        for page_name, key in pages.items():
            if key == page_key:
                selected_page = page_name
                break
        # Clear the session state
        del st.session_state.selected_page
    
    # Track page visit
    session_manager.track_page_visit(page_key)
    
    # Display admin status
    if st.session_state.admin_authenticated:
        st.sidebar.success("🔓 Admin Access Granted")
        if st.sidebar.button("🔒 Logout Admin"):
            security_manager.end_admin_session()
            st.rerun()
    
    # Load admin settings
    admin_settings = storage.get_admin_settings()
    
    # Main content area
    if page_key == "home":
        render_home_page(admin_settings)
    elif page_key == "project_rooms":
        render_project_rooms_page()
    elif page_key == "oasis":
        render_oasis_page()
    elif page_key == "allocations":
        render_allocations_page()
    elif page_key == "analytics":
        render_analytics_page()
    elif page_key == "admin":
        render_admin_page()


def render_home_page(admin_settings: Dict):
    """Render the home page"""
    
    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1>🏢 Room Allocation System</h1>
        <p>{admin_settings.get('welcome_text', 'Welcome to the Room Allocation System')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Current allocation period info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-box">
            <h3>📅 Current Period</h3>
            <p>{}</p>
        </div>
        """.format(admin_settings.get('allocation_period', 'Current Week')), unsafe_allow_html=True)
    
    with col2:
        # Get capacity info
        capacity_info = storage.get_capacity_info()
        weekly_prefs = storage.get_weekly_preferences()
        oasis_prefs = storage.get_oasis_preferences()
        
        st.markdown(f"""
        <div class="info-box">
            <h3>📊 Submissions</h3>
            <p>Teams: {len(weekly_prefs)}<br>
            Oasis: {len(oasis_prefs)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        last_reset = admin_settings.get('last_reset')
        reset_text = "Never" if not last_reset else format_date(last_reset)
        
        st.markdown(f"""
        <div class="info-box">
            <h3>🔄 Last Reset</h3>
            <p>{reset_text}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick actions
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📋 Submit Team Preference", use_container_width=True):
            st.session_state.selected_page = "project_rooms"
            st.rerun()
    
    with col2:
        if st.button("🌴 Submit Oasis Preference", use_container_width=True):
            st.session_state.selected_page = "oasis"
            st.rerun()
    
    with col3:
        if st.button("📊 View Allocations", use_container_width=True):
            st.session_state.selected_page = "allocations"
            st.rerun()
    
    with col4:
        if st.button("📈 View Analytics", use_container_width=True):
            st.session_state.selected_page = "analytics"
            st.rerun()
    
    # System status
    st.markdown("### 📋 System Status")
    
    # Display current capacity
    render_capacity_overview()


def render_project_rooms_page():
    """Render the project rooms page"""
    
    st.markdown("""
    <div class="main-header">
        <h1>📋 Project Room Allocation</h1>
        <p>Submit your team preferences for project rooms</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Instructions
    admin_settings = storage.get_admin_settings()
    instructions = admin_settings.get('project_room_instructions', 'Please submit your team preferences for project rooms.')
    
    st.markdown(f"""
    <div class="info-box">
        <h3>📝 Instructions</h3>
        <p>{instructions}</p>
        <ul>
            <li>Teams must have 3-6 members</li>
            <li>Choose either "Monday & Wednesday" OR "Tuesday & Thursday"</li>
            <li>Each team can only submit once per allocation period</li>
            <li>Larger teams get priority in allocation</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Submission form
    st.markdown("### 📝 Submit Team Preference")
    
    with st.form("team_preference_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            team_name = st.text_input("Team Name *", placeholder="Enter your team name")
            contact_person = st.text_input("Contact Person *", placeholder="Enter contact person name")
        
        with col2:
            team_size = st.selectbox("Team Size *", options=[3, 4, 5, 6])
            preferred_days = st.selectbox("Preferred Days *", 
                                        options=["Monday & Wednesday", "Tuesday & Thursday"])
        
        submitted = st.form_submit_button("🚀 Submit Preference", use_container_width=True)
        
        if submitted:
            # Rate limiting check
            user_identifier = f"team_{team_name.strip().lower()}" if team_name else "anonymous"
            
            if rate_limiter.is_rate_limited(user_identifier):
                remaining_time = rate_limiter.get_remaining_time(user_identifier)
                st.error(f"❌ Too many submissions. Please wait {remaining_time} seconds before trying again.")
                return
            
            # Enhanced validation
            validation_errors = []
            
            # Validate team name
            team_name_valid, validated_team_name = input_validator.validate_team_name(team_name)
            if not team_name_valid:
                validation_errors.append(validated_team_name)  # Error message
            
            # Validate contact person
            contact_valid, validated_contact = input_validator.validate_person_name(contact_person)
            if not contact_valid:
                validation_errors.append(validated_contact)  # Error message
            
            # Validate team size
            size_valid, validated_size = input_validator.validate_team_size(team_size)
            if not size_valid:
                validation_errors.append("Team size must be between 3 and 6 people")
            
            # Validate preferred days
            days_valid, validated_days = input_validator.validate_preferred_days(preferred_days)
            if not days_valid:
                validation_errors.append("Please select valid preferred days")
            
            if validation_errors:
                for error in validation_errors:
                    st.error(f"❌ {error}")
            else:
                # Create preference with validated data
                team_pref = TeamPreference(
                    team_name=validated_team_name,
                    contact_person=validated_contact,
                    team_size=validated_size,
                    preferred_days=validated_days
                )
                
                # Try to save
                success = storage.add_weekly_preference(team_pref.to_dict())
                
                if success:
                    st.markdown("""
                    <div class="success-box">
                        <h4>✅ Preference Submitted Successfully!</h4>
                        <p>Your team preference has been recorded. You will be notified once allocations are made.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                    
                    # Clear form data
                    session_manager.clear_form_data()
                else:
                    st.markdown("""
                    <div class="error-box">
                        <h4>❌ Submission Failed</h4>
                        <p>This team has already submitted a preference for the current allocation period.</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Display current submissions
    st.markdown("### 📊 Current Submissions")
    
    weekly_prefs = storage.get_weekly_preferences()
    
    if weekly_prefs:
        df = pd.DataFrame(weekly_prefs)
        df['submission_time'] = pd.to_datetime(df['submission_time']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Display as a nice table
        st.dataframe(
            df[['team_name', 'contact_person', 'team_size', 'preferred_days', 'submission_time']],
            column_config={
                'team_name': 'Team Name',
                'contact_person': 'Contact Person',
                'team_size': 'Team Size',
                'preferred_days': 'Preferred Days',
                'submission_time': 'Submitted At'
            },
            use_container_width=True,
            hide_index=True
        )
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Teams", len(weekly_prefs))
        
        with col2:
            mon_wed_count = len([p for p in weekly_prefs if p['preferred_days'] == 'Monday & Wednesday'])
            st.metric("Monday & Wednesday", mon_wed_count)
        
        with col3:
            tue_thu_count = len([p for p in weekly_prefs if p['preferred_days'] == 'Tuesday & Thursday'])
            st.metric("Tuesday & Thursday", tue_thu_count)
    
    else:
        st.info("📝 No team preferences submitted yet.")


def render_oasis_page():
    """Render the Oasis workspace page"""
    
    st.markdown("""
    <div class="main-header">
        <h1>🌴 Oasis Workspace</h1>
        <p>Submit your preferences for flexible workspace</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Instructions
    admin_settings = storage.get_admin_settings()
    instructions = admin_settings.get('oasis_instructions', 'Please select your preferred days for Oasis workspace.')
    
    st.markdown(f"""
    <div class="info-box">
        <h3>📝 Instructions</h3>
        <p>{instructions}</p>
        <ul>
            <li>Select up to 5 preferred weekdays</li>
            <li>11 people maximum per day</li>
            <li>Each person can only submit once per allocation period</li>
            <li>Fair allocation ensures everyone gets at least one preferred day when possible</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Show current capacity
    render_oasis_capacity_info()
    
    # Submission form
    st.markdown("### 📝 Submit Oasis Preference")
    
    with st.form("oasis_preference_form"):
        person_name = st.text_input("Your Name *", placeholder="Enter your full name")
        
        st.markdown("**Select Your Preferred Days (up to 5):**")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            monday = st.checkbox("Monday")
        with col2:
            tuesday = st.checkbox("Tuesday")
        with col3:
            wednesday = st.checkbox("Wednesday")
        with col4:
            thursday = st.checkbox("Thursday")
        with col5:
            friday = st.checkbox("Friday")
        
        submitted = st.form_submit_button("🚀 Submit Preference", use_container_width=True)
        
        if submitted:
            # Rate limiting check
            user_identifier = f"oasis_{person_name.strip().lower()}" if person_name else "anonymous"
            
            if rate_limiter.is_rate_limited(user_identifier):
                remaining_time = rate_limiter.get_remaining_time(user_identifier)
                st.error(f"❌ Too many submissions. Please wait {remaining_time} seconds before trying again.")
                return
            
            # Collect selected days
            selected_days = []
            if monday: selected_days.append("Monday")
            if tuesday: selected_days.append("Tuesday")
            if wednesday: selected_days.append("Wednesday")
            if thursday: selected_days.append("Thursday")
            if friday: selected_days.append("Friday")
            
            # Enhanced validation
            validation_errors = []
            
            # Validate person name
            name_valid, validated_name = input_validator.validate_person_name(person_name)
            if not name_valid:
                validation_errors.append(validated_name)  # Error message
            
            # Validate selected days
            days_valid, validated_days = input_validator.validate_oasis_days(selected_days)
            if not days_valid:
                validation_errors.append("Please select 1-5 valid weekdays")
            
            if validation_errors:
                for error in validation_errors:
                    st.error(f"❌ {error}")
            else:
                # Create preference with validated data
                oasis_pref = OasisPreference(
                    person_name=validated_name,
                    preferred_days=validated_days
                )
                
                # Try to save
                success = storage.add_oasis_preference(oasis_pref.to_dict())
                
                if success:
                    st.markdown("""
                    <div class="success-box">
                        <h4>✅ Preference Submitted Successfully!</h4>
                        <p>Your Oasis preference has been recorded. You will be notified once allocations are made.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                    
                    # Clear form data
                    session_manager.clear_form_data()
                else:
                    st.markdown("""
                    <div class="error-box">
                        <h4>❌ Submission Failed</h4>
                        <p>You have already submitted a preference for the current allocation period.</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Ad-hoc addition section
    st.markdown("### ➕ Ad-hoc Addition")
    
    st.markdown("""
    <div class="info-box">
        <h4>Last-minute Request</h4>
        <p>Need to add yourself to Oasis for today or tomorrow? Check availability and add yourself if spots are available.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # This would be implemented with real-time availability checking
    if st.button("🔍 Check Ad-hoc Availability"):
        st.info("🚧 Ad-hoc addition feature will be available after allocations are made.")
    
    # Display current submissions
    st.markdown("### 📊 Current Submissions")
    
    oasis_prefs = storage.get_oasis_preferences()
    
    if oasis_prefs:
        # Process preferences for display
        display_data = []
        for pref in oasis_prefs:
            preferred_days = []
            for i in range(1, 6):
                day = pref.get(f'preferred_day_{i}')
                if day:
                    preferred_days.append(day)
            
            display_data.append({
                'person_name': pref['person_name'],
                'preferred_days': ', '.join(preferred_days),
                'submission_time': pd.to_datetime(pref['submission_time']).strftime('%Y-%m-%d %H:%M')
            })
        
        df = pd.DataFrame(display_data)
        
        st.dataframe(
            df,
            column_config={
                'person_name': 'Name',
                'preferred_days': 'Preferred Days',
                'submission_time': 'Submitted At'
            },
            use_container_width=True,
            hide_index=True
        )
        
        st.metric("Total Submissions", len(oasis_prefs))
    
    else:
        st.info("📝 No Oasis preferences submitted yet.")


def render_allocations_page():
    """Render the current allocations page"""
    
    st.markdown("""
    <div class="main-header">
        <h1>📊 Current Allocations</h1>
        <p>View all current room and workspace allocations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for different allocation types
    tab1, tab2, tab3 = st.tabs(["📋 Project Rooms", "🌴 Oasis Workspace", "📅 Interactive Matrix"])
    
    with tab1:
        render_project_room_allocations()
    
    with tab2:
        render_oasis_allocations()
    
    with tab3:
        render_interactive_matrix()


def render_analytics_page():
    """Render the analytics dashboard"""
    
    st.markdown("""
    <div class="main-header">
        <h1>📈 Analytics Dashboard</h1>
        <p>Historical data and usage statistics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get all data for analytics
    weekly_prefs = storage.get_weekly_preferences()
    oasis_prefs = storage.get_oasis_preferences()
    weekly_allocations = storage.get_weekly_allocations()
    oasis_allocations = storage.get_oasis_allocations()
    
    # Get archive data
    archive_weekly_prefs = storage.get_archive_data('weekly_preferences')
    archive_oasis_prefs = storage.get_archive_data('oasis_preferences')
    archive_weekly_allocs = storage.get_archive_data('weekly_allocations')
    archive_oasis_allocs = storage.get_archive_data('oasis_allocations')
    
    # Combine current and archive data
    all_weekly_prefs = weekly_prefs + archive_weekly_prefs
    all_oasis_prefs = oasis_prefs + archive_oasis_prefs
    all_weekly_allocs = weekly_allocations + archive_weekly_allocs
    all_oasis_allocs = oasis_allocations + archive_oasis_allocs
    
    # Tabs for different analytics views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "📋 Project Rooms", "🌴 Oasis", "📈 Trends", "📥 Export"])
    
    with tab1:
        render_analytics_overview(all_weekly_prefs, all_oasis_prefs, all_weekly_allocs, all_oasis_allocs)
    
    with tab2:
        render_project_room_analytics(all_weekly_prefs, all_weekly_allocs)
    
    with tab3:
        render_oasis_analytics(all_oasis_prefs, all_oasis_allocs)
    
    with tab4:
        render_trends_analytics(all_weekly_prefs, all_oasis_prefs, all_weekly_allocs, all_oasis_allocs)
    
    with tab5:
        render_export_analytics(all_weekly_prefs, all_oasis_prefs, all_weekly_allocs, all_oasis_allocs)


def render_analytics_overview(weekly_prefs, oasis_prefs, weekly_allocs, oasis_allocs):
    """Render analytics overview"""
    
    st.markdown("#### 📊 System Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Team Submissions", len(weekly_prefs))
    
    with col2:
        st.metric("Total Oasis Submissions", len(oasis_prefs))
    
    with col3:
        st.metric("Total Project Allocations", len(weekly_allocs))
    
    with col4:
        st.metric("Total Oasis Allocations", len(oasis_allocs))
    
    # Allocation success rates
    st.markdown("#### 🎯 Allocation Success Rates")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if weekly_prefs:
            unique_teams_submitted = len(set(p['team_name'] for p in weekly_prefs))
            unique_teams_allocated = len(set(a['team_name'] for a in weekly_allocs))
            team_success_rate = (unique_teams_allocated / unique_teams_submitted) * 100 if unique_teams_submitted > 0 else 0
            
            st.metric("Team Allocation Success Rate", f"{team_success_rate:.1f}%")
            
            # Create gauge chart for team success rate
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = team_success_rate,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Team Success Rate (%)"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No team data available")
    
    with col2:
        if oasis_prefs:
            unique_people_submitted = len(set(p['person_name'] for p in oasis_prefs))
            unique_people_allocated = len(set(a['person_name'] for a in oasis_allocs))
            oasis_success_rate = (unique_people_allocated / unique_people_submitted) * 100 if unique_people_submitted > 0 else 0
            
            st.metric("Oasis Allocation Success Rate", f"{oasis_success_rate:.1f}%")
            
            # Create gauge chart for Oasis success rate
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = oasis_success_rate,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Oasis Success Rate (%)"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkgreen"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No Oasis data available")
    
    # Capacity utilization overview
    st.markdown("#### 🏢 Capacity Utilization")
    
    if weekly_allocs or oasis_allocs:
        col1, col2 = st.columns(2)
        
        with col1:
            # Project room utilization
            if weekly_allocs:
                room_usage = {}
                for allocation in weekly_allocs:
                    room = allocation['room_name']
                    room_usage[room] = room_usage.get(room, 0) + 1
                
                rooms = list(room_usage.keys())
                usage_counts = list(room_usage.values())
                
                fig = px.bar(
                    x=rooms, 
                    y=usage_counts,
                    title="Project Room Usage",
                    labels={'x': 'Room', 'y': 'Allocations'},
                    color=usage_counts,
                    color_continuous_scale='Blues'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Oasis daily utilization
            if oasis_allocs:
                daily_usage = {}
                for allocation in oasis_allocs:
                    day = allocation['day_of_week']
                    daily_usage[day] = daily_usage.get(day, 0) + 1
                
                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
                usage_counts = [daily_usage.get(day, 0) for day in days]
                
                fig = px.bar(
                    x=days,
                    y=usage_counts,
                    title="Oasis Daily Usage",
                    labels={'x': 'Day', 'y': 'Allocations'},
                    color=usage_counts,
                    color_continuous_scale='Greens'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No allocation data available for capacity analysis")


def render_project_room_analytics(weekly_prefs, weekly_allocs):
    """Render project room analytics"""
    
    st.markdown("#### 📋 Project Room Analytics")
    
    if not weekly_prefs and not weekly_allocs:
        st.info("No project room data available")
        return
    
    # Team size distribution
    if weekly_prefs:
        st.markdown("##### 👥 Team Size Distribution")
        
        team_sizes = [p['team_size'] for p in weekly_prefs]
        size_counts = {}
        for size in team_sizes:
            size_counts[size] = size_counts.get(size, 0) + 1
        
        fig = px.pie(
            values=list(size_counts.values()),
            names=[f"{size} people" for size in size_counts.keys()],
            title="Team Size Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Day preference analysis
    if weekly_prefs:
        st.markdown("##### 📅 Day Preference Analysis")
        
        day_prefs = {}
        for pref in weekly_prefs:
            days = pref['preferred_days']
            day_prefs[days] = day_prefs.get(days, 0) + 1
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                x=list(day_prefs.keys()),
                y=list(day_prefs.values()),
                title="Day Preference Distribution",
                labels={'x': 'Preferred Days', 'y': 'Number of Teams'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Show detailed breakdown
            st.markdown("**Preference Breakdown:**")
            for days, count in day_prefs.items():
                percentage = (count / len(weekly_prefs)) * 100
                st.write(f"• {days}: {count} teams ({percentage:.1f}%)")
    
    # Room allocation efficiency
    if weekly_allocs:
        st.markdown("##### 🏢 Room Allocation Efficiency")
        
        # Calculate room utilization
        room_data = []
        room_capacities = ValidationHelper.get_room_capacity
        
        for room in ValidationHelper.get_available_rooms():
            allocations = [a for a in weekly_allocs if a['room_name'] == room]
            capacity = ValidationHelper.get_room_capacity(room)
            utilization = len(allocations)
            efficiency = (utilization / capacity) * 100 if capacity > 0 else 0
            
            room_data.append({
                'Room': room,
                'Capacity': capacity,
                'Allocated': utilization,
                'Efficiency': efficiency
            })
        
        df_rooms = pd.DataFrame(room_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                df_rooms,
                x='Room',
                y='Efficiency',
                title="Room Efficiency (%)",
                color='Efficiency',
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.dataframe(df_rooms, use_container_width=True, hide_index=True)


def render_oasis_analytics(oasis_prefs, oasis_allocs):
    """Render Oasis analytics"""
    
    st.markdown("#### 🌴 Oasis Analytics")
    
    if not oasis_prefs and not oasis_allocs:
        st.info("No Oasis data available")
        return
    
    # Preference analysis
    if oasis_prefs:
        st.markdown("##### 📊 Preference Analysis")
        
        # Count preferences by day
        day_preference_counts = {
            'Monday': 0, 'Tuesday': 0, 'Wednesday': 0, 'Thursday': 0, 'Friday': 0
        }
        
        for pref in oasis_prefs:
            preferred_days = parse_preferred_days_from_oasis_pref(pref)
            for day in preferred_days:
                if day in day_preference_counts:
                    day_preference_counts[day] += 1
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                x=list(day_preference_counts.keys()),
                y=list(day_preference_counts.values()),
                title="Day Preference Popularity",
                labels={'x': 'Day', 'y': 'Number of Preferences'},
                color=list(day_preference_counts.values()),
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Preference distribution
            pref_counts = {}
            for pref in oasis_prefs:
                preferred_days = parse_preferred_days_from_oasis_pref(pref)
                count = len(preferred_days)
                pref_counts[count] = pref_counts.get(count, 0) + 1
            
            fig = px.pie(
                values=list(pref_counts.values()),
                names=[f"{count} days" for count in pref_counts.keys()],
                title="Number of Preferred Days"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Allocation success by day
    if oasis_allocs:
        st.markdown("##### 🎯 Daily Allocation Success")
        
        daily_allocs = {}
        for allocation in oasis_allocs:
            day = allocation['day_of_week']
            daily_allocs[day] = daily_allocs.get(day, 0) + 1
        
        # Calculate success rates
        success_data = []
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            allocated = daily_allocs.get(day, 0)
            requested = day_preference_counts.get(day, 0) if oasis_prefs else 0
            success_rate = (allocated / requested) * 100 if requested > 0 else 0
            
            success_data.append({
                'Day': day,
                'Requested': requested,
                'Allocated': allocated,
                'Success Rate': success_rate,
                'Capacity': 11,
                'Utilization': (allocated / 11) * 100
            })
        
        df_success = pd.DataFrame(success_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                df_success,
                x='Day',
                y='Success Rate',
                title="Allocation Success Rate by Day (%)",
                color='Success Rate',
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                df_success,
                x='Day',
                y='Utilization',
                title="Capacity Utilization by Day (%)",
                color='Utilization',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed table
        st.dataframe(df_success, use_container_width=True, hide_index=True)


def render_trends_analytics(weekly_prefs, oasis_prefs, weekly_allocs, oasis_allocs):
    """Render trends analytics"""
    
    st.markdown("#### 📈 Trends Analysis")
    
    # Time-based analysis (if we have timestamps)
    if weekly_prefs or oasis_prefs:
        st.markdown("##### ⏰ Submission Timeline")
        
        # Combine all submissions with timestamps
        submissions = []
        
        for pref in weekly_prefs:
            if 'submission_time' in pref:
                submissions.append({
                    'timestamp': pref['submission_time'],
                    'type': 'Team Preference',
                    'date': pd.to_datetime(pref['submission_time']).date()
                })
        
        for pref in oasis_prefs:
            if 'submission_time' in pref:
                submissions.append({
                    'timestamp': pref['submission_time'],
                    'type': 'Oasis Preference',
                    'date': pd.to_datetime(pref['submission_time']).date()
                })
        
        if submissions:
            df_submissions = pd.DataFrame(submissions)
            df_submissions['date'] = pd.to_datetime(df_submissions['date'])
            
            # Group by date and type
            daily_submissions = df_submissions.groupby(['date', 'type']).size().reset_index(name='count')
            
            fig = px.line(
                daily_submissions,
                x='date',
                y='count',
                color='type',
                title="Daily Submission Trends",
                labels={'date': 'Date', 'count': 'Number of Submissions'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No timestamp data available for trend analysis")
    
    # Demand vs Capacity Analysis
    st.markdown("##### ⚖️ Demand vs Capacity Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Project room demand vs capacity
        if weekly_prefs:
            total_people_demand = sum(p['team_size'] for p in weekly_prefs)
            total_room_capacity = sum(ValidationHelper.get_room_capacity(room) for room in ValidationHelper.get_available_rooms())
            
            demand_data = pd.DataFrame({
                'Category': ['Demand', 'Capacity'],
                'People': [total_people_demand, total_room_capacity]
            })
            
            fig = px.bar(
                demand_data,
                x='Category',
                y='People',
                title="Project Room: Demand vs Capacity",
                color='Category',
                color_discrete_map={'Demand': 'red', 'Capacity': 'blue'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show utilization percentage
            utilization = (total_people_demand / total_room_capacity) * 100 if total_room_capacity > 0 else 0
            st.metric("Project Room Utilization", f"{utilization:.1f}%")
    
    with col2:
        # Oasis demand vs capacity
        if oasis_prefs:
            total_oasis_demand = len(oasis_prefs)
            total_oasis_capacity = 11 * 5  # 11 people × 5 days
            
            demand_data = pd.DataFrame({
                'Category': ['Demand', 'Weekly Capacity'],
                'People': [total_oasis_demand, total_oasis_capacity]
            })
            
            fig = px.bar(
                demand_data,
                x='Category',
                y='People',
                title="Oasis: Demand vs Weekly Capacity",
                color='Category',
                color_discrete_map={'Demand': 'orange', 'Weekly Capacity': 'green'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show utilization percentage
            utilization = (total_oasis_demand / total_oasis_capacity) * 100 if total_oasis_capacity > 0 else 0
            st.metric("Oasis Weekly Utilization", f"{utilization:.1f}%")


def render_export_analytics(weekly_prefs, oasis_prefs, weekly_allocs, oasis_allocs):
    """Render export analytics"""
    
    st.markdown("#### 📥 Data Export")
    
    st.markdown("Export data for external analysis or reporting.")
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 📋 Project Room Data")
        
        if weekly_prefs:
            # Export team preferences
            df_prefs = pd.DataFrame(weekly_prefs)
            csv_prefs = df_prefs.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Team Preferences (CSV)",
                data=csv_prefs,
                file_name=f"team_preferences_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        if weekly_allocs:
            # Export project allocations
            df_allocs = pd.DataFrame(weekly_allocs)
            csv_allocs = df_allocs.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Project Allocations (CSV)",
                data=csv_allocs,
                file_name=f"project_allocations_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        st.markdown("##### 🌴 Oasis Data")
        
        if oasis_prefs:
            # Export Oasis preferences
            df_oasis_prefs = pd.DataFrame(oasis_prefs)
            csv_oasis_prefs = df_oasis_prefs.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Oasis Preferences (CSV)",
                data=csv_oasis_prefs,
                file_name=f"oasis_preferences_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        if oasis_allocs:
            # Export Oasis allocations
            df_oasis_allocs = pd.DataFrame(oasis_allocs)
            csv_oasis_allocs = df_oasis_allocs.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Oasis Allocations (CSV)",
                data=csv_oasis_allocs,
                file_name=f"oasis_allocations_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # Summary report
    st.markdown("##### 📊 Summary Report")
    
    if st.button("📄 Generate Summary Report"):
        # Create comprehensive summary
        summary_data = {
            'Report Generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Total Team Preferences': len(weekly_prefs),
            'Total Oasis Preferences': len(oasis_prefs),
            'Total Project Allocations': len(weekly_allocs),
            'Total Oasis Allocations': len(oasis_allocs),
        }
        
        if weekly_prefs:
            unique_teams = len(set(p['team_name'] for p in weekly_prefs))
            avg_team_size = sum(p['team_size'] for p in weekly_prefs) / len(weekly_prefs)
            summary_data.update({
                'Unique Teams': unique_teams,
                'Average Team Size': f"{avg_team_size:.1f}",
                'Team Success Rate': f"{(len(set(a['team_name'] for a in weekly_allocs)) / unique_teams * 100):.1f}%" if unique_teams > 0 else "N/A"
            })
        
        if oasis_prefs:
            unique_people = len(set(p['person_name'] for p in oasis_prefs))
            summary_data.update({
                'Unique Oasis Applicants': unique_people,
                'Oasis Success Rate': f"{(len(set(a['person_name'] for a in oasis_allocs)) / unique_people * 100):.1f}%" if unique_people > 0 else "N/A"
            })
        
        # Convert to DataFrame and display
        df_summary = pd.DataFrame(list(summary_data.items()), columns=['Metric', 'Value'])
        st.dataframe(df_summary, use_container_width=True, hide_index=True)
        
        # Provide download
        csv_summary = df_summary.to_csv(index=False)
        st.download_button(
            label="📥 Download Summary Report (CSV)",
            data=csv_summary,
            file_name=f"allocation_summary_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )


def render_admin_page():
    """Render the admin control panel"""
    
    st.markdown("""
    <div class="main-header">
        <h1>⚙️ Admin Control Panel</h1>
        <p>Administrative functions and system management</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Authentication
    if not st.session_state.admin_authenticated:
        st.markdown("### 🔐 Admin Authentication")
        
        # Check if locked out
        if security_manager._is_locked_out():
            remaining_time = security_manager.get_lockout_remaining_time()
            st.error(f"🔒 Account locked due to too many failed attempts. Try again in {remaining_time} seconds.")
            return
        
        # Show failed attempts warning
        failed_attempts = st.session_state.get('admin_login_attempts', 0)
        if failed_attempts > 0:
            remaining_attempts = security_manager.max_login_attempts - failed_attempts
            st.warning(f"⚠️ {failed_attempts} failed login attempts. {remaining_attempts} attempts remaining before lockout.")
        
        password = st.text_input("Enter Admin Password", type="password")
        
        if st.button("🔓 Login"):
            if security_manager.verify_admin_password(password):
                security_manager.start_admin_session()
                st.success("✅ Admin access granted!")
                st.rerun()
            else:
                if security_manager._is_locked_out():
                    st.error("🔒 Account locked due to too many failed attempts!")
                else:
                    st.error("❌ Invalid password!")
        
        return
    
    # Admin functions
    st.markdown("### 🎛️ Admin Functions")
    
    # Tabs for different admin functions
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚀 Run Allocations", "✏️ Manual Editing", "🗑️ Data Management", "⚙️ Settings", "📊 System Status"])
    
    with tab1:
        render_allocation_runner()
    
    with tab2:
        render_manual_editing()
    
    with tab3:
        render_data_management()
    
    with tab4:
        render_admin_settings()
    
    with tab5:
        render_system_status()


def render_allocation_runner():
    """Render allocation runner interface"""
    
    st.markdown("#### 🚀 Automated Allocation")
    
    # Get current data
    weekly_prefs = storage.get_weekly_preferences()
    oasis_prefs = storage.get_oasis_preferences()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 📋 Project Room Allocation")
        
        st.metric("Teams Submitted", len(weekly_prefs))
        
        if weekly_prefs:
            # Show preview of teams
            df_preview = pd.DataFrame(weekly_prefs)[['team_name', 'team_size', 'preferred_days']]
            st.dataframe(df_preview, use_container_width=True, hide_index=True)
            
            if st.button("🚀 Run Project Room Allocation", type="primary", use_container_width=True):
                with st.spinner("Running project room allocation..."):
                    from logic.allocation import run_project_room_allocation
                    
                    allocations, unplaced_teams = run_project_room_allocation(weekly_prefs)
                    
                    if allocations:
                        storage.set_weekly_allocations(allocations)
                        
                        st.success(f"✅ Allocated {len(set(a['team_name'] for a in allocations))} teams to rooms!")
                        
                        if unplaced_teams:
                            st.warning(f"⚠️ Could not place {len(unplaced_teams)} teams: {', '.join(unplaced_teams)}")
                        
                        # Show results
                        df_results = pd.DataFrame(allocations)
                        st.dataframe(df_results[['team_name', 'room_name', 'day_of_week', 'date']], 
                                   use_container_width=True, hide_index=True)
                    else:
                        st.error("❌ No allocations could be made. Check team preferences and room availability.")
        else:
            st.info("📝 No team preferences submitted yet.")
    
    with col2:
        st.markdown("##### 🌴 Oasis Allocation")
        
        st.metric("People Submitted", len(oasis_prefs))
        
        if oasis_prefs:
            # Show preview of preferences
            preview_data = []
            for pref in oasis_prefs[:5]:  # Show first 5
                preferred_days = parse_preferred_days_from_oasis_pref(pref)
                preview_data.append({
                    'person_name': pref['person_name'],
                    'preferred_days': ', '.join(preferred_days)
                })
            
            df_preview = pd.DataFrame(preview_data)
            st.dataframe(df_preview, use_container_width=True, hide_index=True)
            
            if len(oasis_prefs) > 5:
                st.caption(f"... and {len(oasis_prefs) - 5} more")
            
            if st.button("🚀 Run Oasis Allocation", type="primary", use_container_width=True):
                with st.spinner("Running Oasis allocation..."):
                    from logic.allocation import run_oasis_allocation
                    
                    allocations = run_oasis_allocation(oasis_prefs)
                    
                    if allocations:
                        storage.set_oasis_allocations(allocations)
                        
                        st.success(f"✅ Allocated {len(set(a['person_name'] for a in allocations))} people to Oasis!")
                        
                        # Show results summary
                        daily_counts = {}
                        for allocation in allocations:
                            day = allocation['day_of_week']
                            daily_counts[day] = daily_counts.get(day, 0) + 1
                        
                        st.markdown("**Daily Allocation Summary:**")
                        for day, count in daily_counts.items():
                            st.write(f"- {day}: {count} people")
                        
                        # Show detailed results
                        df_results = pd.DataFrame(allocations)
                        st.dataframe(df_results[['person_name', 'day_of_week', 'date']], 
                                   use_container_width=True, hide_index=True)
                    else:
                        st.error("❌ No allocations could be made. Check preferences and capacity.")
        else:
            st.info("📝 No Oasis preferences submitted yet.")
    
    # Validation section
    st.markdown("#### 🔍 Allocation Validation")
    
    weekly_allocations = storage.get_weekly_allocations()
    oasis_allocations = storage.get_oasis_allocations()
    
    if weekly_allocations or oasis_allocations:
        if st.button("🔍 Validate Current Allocations"):
            from logic.allocation import validate_allocation_results
            
            validation = validate_allocation_results(weekly_allocations, oasis_allocations)
            
            if validation['valid']:
                st.success("✅ All allocations are valid!")
            else:
                st.error("❌ Validation errors found:")
                for error in validation['errors']:
                    st.error(f"• {error}")
            
            if validation['warnings']:
                for warning in validation['warnings']:
                    st.warning(f"⚠️ {warning}")
            
            # Show summary
            st.markdown("**Allocation Summary:**")
            summary = validation['summary']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Project Allocations", summary['total_project_allocations'])
                st.metric("Unique Teams", summary['unique_teams'])
            
            with col2:
                st.metric("Oasis Allocations", summary['total_oasis_allocations'])
                st.metric("Unique People", summary['unique_people'])
            
            with col3:
                st.metric("Rooms Used", summary['rooms_used'])
                
                # Show daily Oasis usage
                st.markdown("**Daily Oasis Usage:**")
                for day, count in summary.get('oasis_daily_usage', {}).items():
                    st.write(f"{day}: {count}/11")


def render_manual_editing():
    """Render manual editing interface"""
    
    st.markdown("#### ✏️ Manual Allocation Editing")
    
    # Choose what to edit
    edit_type = st.selectbox("Select Data to Edit", ["Project Room Allocations", "Oasis Allocations"])
    
    if edit_type == "Project Room Allocations":
        render_project_room_editor()
    else:
        render_oasis_editor()


def render_project_room_editor():
    """Render project room allocation editor"""
    
    weekly_allocations = storage.get_weekly_allocations()
    
    if not weekly_allocations:
        st.info("📝 No project room allocations to edit. Run allocation first.")
        return
    
    st.markdown("##### 📋 Edit Project Room Allocations")
    
    # Convert to DataFrame for editing
    df = pd.DataFrame(weekly_allocations)
    
    # Create editable dataframe
    edited_df = st.data_editor(
        df[['team_name', 'room_name', 'day_of_week', 'date', 'confirmed']],
        column_config={
            'team_name': st.column_config.TextColumn('Team Name', disabled=True),
            'room_name': st.column_config.SelectboxColumn(
                'Room',
                options=ValidationHelper.get_available_rooms()
            ),
            'day_of_week': st.column_config.SelectboxColumn(
                'Day',
                options=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            ),
            'date': st.column_config.DateColumn('Date'),
            'confirmed': st.column_config.CheckboxColumn('Confirmed')
        },
        use_container_width=True,
        num_rows="dynamic"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Changes", type="primary"):
            # Convert back to list of dicts
            updated_allocations = []
            for _, row in edited_df.iterrows():
                allocation = {
                    'team_name': row['team_name'],
                    'room_name': row['room_name'],
                    'day_of_week': row['day_of_week'],
                    'date': str(row['date']),
                    'confirmed': row['confirmed'],
                    'created_at': datetime.now().isoformat()
                }
                updated_allocations.append(allocation)
            
            storage.set_weekly_allocations(updated_allocations)
            st.success("✅ Project room allocations updated!")
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset to Original"):
            st.rerun()


def render_oasis_editor():
    """Render Oasis allocation editor"""
    
    oasis_allocations = storage.get_oasis_allocations()
    
    if not oasis_allocations:
        st.info("📝 No Oasis allocations to edit. Run allocation first.")
        return
    
    st.markdown("##### 🌴 Edit Oasis Allocations")
    
    # Convert to DataFrame for editing
    df = pd.DataFrame(oasis_allocations)
    
    # Create editable dataframe
    edited_df = st.data_editor(
        df[['person_name', 'day_of_week', 'date', 'confirmed']],
        column_config={
            'person_name': st.column_config.TextColumn('Person Name', disabled=True),
            'day_of_week': st.column_config.SelectboxColumn(
                'Day',
                options=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            ),
            'date': st.column_config.DateColumn('Date'),
            'confirmed': st.column_config.CheckboxColumn('Confirmed')
        },
        use_container_width=True,
        num_rows="dynamic"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Changes", type="primary"):
            # Convert back to list of dicts
            updated_allocations = []
            for _, row in edited_df.iterrows():
                allocation = {
                    'person_name': row['person_name'],
                    'day_of_week': row['day_of_week'],
                    'date': str(row['date']),
                    'confirmed': row['confirmed'],
                    'created_at': datetime.now().isoformat()
                }
                updated_allocations.append(allocation)
            
            storage.set_oasis_allocations(updated_allocations)
            st.success("✅ Oasis allocations updated!")
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset to Original"):
            st.rerun()
    
    # Ad-hoc addition section
    st.markdown("##### ➕ Add Ad-hoc Allocation")
    
    with st.form("adhoc_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            person_name = st.text_input("Person Name")
        
        with col2:
            day = st.selectbox("Day", ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
        
        if st.form_submit_button("➕ Add Allocation"):
            if person_name:
                from logic.allocation import OasisAllocator
                
                allocator = OasisAllocator()
                new_allocation = allocator.add_adhoc_allocation(person_name, day, oasis_allocations)
                
                if new_allocation:
                    oasis_allocations.append(new_allocation)
                    storage.set_oasis_allocations(oasis_allocations)
                    st.success(f"✅ Added {person_name} to {day}!")
                    st.rerun()
                else:
                    st.error("❌ Could not add allocation. Check capacity and duplicates.")
            else:
                st.error("❌ Person name is required.")


def render_data_management():
    """Render data management interface"""
    
    st.markdown("#### 🗑️ Data Management")
    
    # Archive and reset section
    st.markdown("##### 🔄 Archive & Reset")
    
    st.markdown("""
    <div class="info-box">
        <h4>⚠️ Archive Current Data</h4>
        <p>This will move all current preferences and allocations to the archive and reset the system for a new allocation period.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Archive & Reset System", type="secondary"):
        if st.button("⚠️ Confirm Archive & Reset", type="primary"):
            storage.archive_and_reset()
            st.success("✅ System has been archived and reset!")
            st.balloons()
            st.rerun()
    
    # Backup section
    st.markdown("##### 💾 Data Backup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Create Backup"):
            import tempfile
            import zipfile
            import os
            
            # Create backup
            backup_dir = tempfile.mkdtemp()
            storage.backup_data(backup_dir)
            
            # Create zip file
            zip_path = os.path.join(backup_dir, "room_allocation_backup.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for root, dirs, files in os.walk(backup_dir):
                    for file in files:
                        if file.endswith('.json'):
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, file)
            
            st.success("✅ Backup created successfully!")
            
            # Provide download link
            with open(zip_path, 'rb') as f:
                st.download_button(
                    label="📥 Download Backup",
                    data=f.read(),
                    file_name=f"room_allocation_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip"
                )
    
    with col2:
        st.markdown("**Backup includes:**")
        st.write("• All preferences and allocations")
        st.write("• Archive data")
        st.write("• Admin settings")
        st.write("• System configuration")
    
    # Bulk deletion section
    st.markdown("##### 🗑️ Bulk Deletion")
    
    deletion_type = st.selectbox("Select Data to Delete", [
        "All Team Preferences",
        "All Oasis Preferences", 
        "All Project Room Allocations",
        "All Oasis Allocations"
    ])
    
    if st.button(f"🗑️ Delete {deletion_type}", type="secondary"):
        st.warning(f"⚠️ This will permanently delete {deletion_type.lower()}!")
        
        if st.button("⚠️ Confirm Deletion", type="primary"):
            # Archive before deletion
            timestamp = datetime.now().isoformat()
            
            if deletion_type == "All Team Preferences":
                current_data = storage.get_weekly_preferences()
                archive_data = storage.get_archive_data('weekly_preferences')
                for record in current_data:
                    record['archived_at'] = timestamp
                archive_data.extend(current_data)
                storage._write_file_with_lock(storage.files['weekly_preferences_archive'], archive_data)
                storage._write_file_with_lock(storage.files['weekly_preferences'], [])
                
            elif deletion_type == "All Oasis Preferences":
                current_data = storage.get_oasis_preferences()
                archive_data = storage.get_archive_data('oasis_preferences')
                for record in current_data:
                    record['archived_at'] = timestamp
                archive_data.extend(current_data)
                storage._write_file_with_lock(storage.files['oasis_preferences_archive'], archive_data)
                storage._write_file_with_lock(storage.files['oasis_preferences'], [])
                
            elif deletion_type == "All Project Room Allocations":
                current_data = storage.get_weekly_allocations()
                archive_data = storage.get_archive_data('weekly_allocations')
                for record in current_data:
                    record['archived_at'] = timestamp
                archive_data.extend(current_data)
                storage._write_file_with_lock(storage.files['weekly_allocations_archive'], archive_data)
                storage._write_file_with_lock(storage.files['weekly_allocations'], [])
                
            elif deletion_type == "All Oasis Allocations":
                current_data = storage.get_oasis_allocations()
                archive_data = storage.get_archive_data('oasis_allocations')
                for record in current_data:
                    record['archived_at'] = timestamp
                archive_data.extend(current_data)
                storage._write_file_with_lock(storage.files['oasis_allocations_archive'], archive_data)
                storage._write_file_with_lock(storage.files['oasis_allocations'], [])
            
            st.success(f"✅ {deletion_type} deleted and archived!")
            st.rerun()


def render_admin_settings():
    """Render admin settings interface"""
    
    st.markdown("#### ⚙️ System Settings")
    
    # Get current settings
    admin_settings = storage.get_admin_settings()
    
    # Configurable display texts
    st.markdown("##### 📝 Display Text Configuration")
    
    with st.form("settings_form"):
        welcome_text = st.text_area(
            "Welcome Text",
            value=admin_settings.get('welcome_text', ''),
            help="Text displayed on the home page"
        )
        
        project_room_instructions = st.text_area(
            "Project Room Instructions",
            value=admin_settings.get('project_room_instructions', ''),
            help="Instructions for project room submissions"
        )
        
        oasis_instructions = st.text_area(
            "Oasis Instructions", 
            value=admin_settings.get('oasis_instructions', ''),
            help="Instructions for Oasis submissions"
        )
        
        allocation_period = st.text_input(
            "Allocation Period Name",
            value=admin_settings.get('allocation_period', ''),
            help="Name of the current allocation period"
        )
        
        if st.form_submit_button("💾 Save Settings", type="primary"):
            # Validate all settings
            validation_errors = []
            
            welcome_valid, validated_welcome = input_validator.validate_admin_setting('welcome_text', welcome_text)
            if not welcome_valid:
                validation_errors.append("Welcome text contains invalid content")
            
            instructions_valid, validated_instructions = input_validator.validate_admin_setting('project_room_instructions', project_room_instructions)
            if not instructions_valid:
                validation_errors.append("Project room instructions contain invalid content")
            
            oasis_valid, validated_oasis = input_validator.validate_admin_setting('oasis_instructions', oasis_instructions)
            if not oasis_valid:
                validation_errors.append("Oasis instructions contain invalid content")
            
            period_valid, validated_period = input_validator.validate_admin_setting('allocation_period', allocation_period)
            if not period_valid:
                validation_errors.append("Allocation period name contains invalid content")
            
            if validation_errors:
                for error in validation_errors:
                    st.error(f"❌ {error}")
            else:
                # Save validated settings
                storage.update_admin_setting('welcome_text', validated_welcome)
                storage.update_admin_setting('project_room_instructions', validated_instructions)
                storage.update_admin_setting('oasis_instructions', validated_oasis)
                storage.update_admin_setting('allocation_period', validated_period)
                
                st.success("✅ Settings updated successfully!")
                st.rerun()
    
    # System configuration
    st.markdown("##### 🔧 System Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Current Configuration:**")
        st.write(f"• Project Rooms: {len(ValidationHelper.get_available_rooms())}")
        st.write("• Room Capacities: 2×6 people, 7×4 people")
        st.write("• Oasis Capacity: 11 people/day")
        st.write("• Weekdays: Monday-Friday")
    
    with col2:
        st.markdown("**System Status:**")
        last_reset = admin_settings.get('last_reset')
        if last_reset:
            st.write(f"• Last Reset: {format_date(last_reset)}")
        else:
            st.write("• Last Reset: Never")
        
        updated_at = admin_settings.get('updated_at')
        if updated_at:
            st.write(f"• Settings Updated: {format_date(updated_at)}")


def render_system_status():
    """Render system status interface"""
    
    st.markdown("#### 📊 System Status")
    
    # Get all data
    weekly_prefs = storage.get_weekly_preferences()
    oasis_prefs = storage.get_oasis_preferences()
    weekly_allocations = storage.get_weekly_allocations()
    oasis_allocations = storage.get_oasis_allocations()
    
    # Current data metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Team Preferences", len(weekly_prefs))
    
    with col2:
        st.metric("Oasis Preferences", len(oasis_prefs))
    
    with col3:
        st.metric("Project Allocations", len(weekly_allocations))
    
    with col4:
        st.metric("Oasis Allocations", len(oasis_allocations))
    
    # Capacity utilization
    st.markdown("##### 📊 Capacity Utilization")
    
    # Project room utilization
    if weekly_allocations:
        room_usage = {}
        for allocation in weekly_allocations:
            room = allocation['room_name']
            room_usage[room] = room_usage.get(room, 0) + 1
        
        st.markdown("**Project Room Usage:**")
        for room in ValidationHelper.get_available_rooms():
            usage = room_usage.get(room, 0)
            capacity = ValidationHelper.get_room_capacity(room)
            utilization = (usage / capacity) * 100 if capacity > 0 else 0
            
            st.progress(utilization / 100, text=f"{room}: {usage}/{capacity} ({utilization:.1f}%)")
    
    # Oasis utilization
    if oasis_allocations:
        daily_usage = {}
        for allocation in oasis_allocations:
            day = allocation['day_of_week']
            daily_usage[day] = daily_usage.get(day, 0) + 1
        
        st.markdown("**Oasis Daily Usage:**")
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            usage = daily_usage.get(day, 0)
            capacity = 11
            utilization = (usage / capacity) * 100
            
            st.progress(utilization / 100, text=f"{day}: {usage}/{capacity} ({utilization:.1f}%)")
    
    # Archive data summary
    st.markdown("##### 📚 Archive Summary")
    
    archive_weekly_prefs = storage.get_archive_data('weekly_preferences')
    archive_oasis_prefs = storage.get_archive_data('oasis_preferences')
    archive_weekly_allocs = storage.get_archive_data('weekly_allocations')
    archive_oasis_allocs = storage.get_archive_data('oasis_allocations')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Archived Team Prefs", len(archive_weekly_prefs))
    
    with col2:
        st.metric("Archived Oasis Prefs", len(archive_oasis_prefs))
    
    with col3:
        st.metric("Archived Project Allocs", len(archive_weekly_allocs))
    
    with col4:
        st.metric("Archived Oasis Allocs", len(archive_oasis_allocs))


def render_capacity_overview():
    """Render system capacity overview"""
    
    capacity_info = storage.get_capacity_info()
    weekly_prefs = storage.get_weekly_preferences()
    oasis_prefs = storage.get_oasis_preferences()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 Project Rooms")
        
        total_capacity = capacity_info['total_project_room_capacity']
        total_demand = sum(pref['team_size'] for pref in weekly_prefs)
        
        st.metric("Total Capacity", f"{total_capacity} people")
        st.metric("Current Demand", f"{total_demand} people")
        
        if total_demand > total_capacity:
            st.warning(f"⚠️ Demand exceeds capacity by {total_demand - total_capacity} people")
        else:
            st.success(f"✅ {total_capacity - total_demand} spots available")
    
    with col2:
        st.markdown("#### 🌴 Oasis Workspace")
        
        oasis_capacity = capacity_info['oasis_capacity']
        oasis_demand = len(oasis_prefs)
        
        st.metric("Daily Capacity", f"{oasis_capacity} people")
        st.metric("Total Applicants", f"{oasis_demand} people")
        
        if oasis_demand > oasis_capacity:
            st.info(f"📊 {oasis_demand} people competing for {oasis_capacity * 5} total weekly spots")
        else:
            st.success(f"✅ Sufficient capacity for all applicants")


def render_oasis_capacity_info():
    """Render Oasis capacity information"""
    
    oasis_allocations = storage.get_oasis_allocations()
    capacity_info = storage.get_capacity_info()
    
    st.markdown("#### 📊 Current Oasis Capacity")
    
    # Count allocations per day
    day_counts = {}
    for day in capacity_info['weekdays']:
        day_counts[day] = len([a for a in oasis_allocations if a['day_of_week'] == day])
    
    cols = st.columns(5)
    
    for i, day in enumerate(capacity_info['weekdays']):
        with cols[i]:
            count = day_counts[day]
            capacity = capacity_info['oasis_capacity']
            
            if count >= capacity:
                st.markdown(f"""
                <div class="capacity-indicator capacity-full">
                    {day}<br>{count}/{capacity}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="capacity-indicator capacity-available">
                    {day}<br>{count}/{capacity}
                </div>
                """, unsafe_allow_html=True)


def render_project_room_allocations():
    """Render project room allocations"""
    
    weekly_allocations = storage.get_weekly_allocations()
    
    if weekly_allocations:
        df = pd.DataFrame(weekly_allocations)
        
        st.dataframe(
            df[['team_name', 'room_name', 'day_of_week', 'date', 'confirmed']],
            column_config={
                'team_name': 'Team Name',
                'room_name': 'Room',
                'day_of_week': 'Day',
                'date': 'Date',
                'confirmed': 'Confirmed'
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("📝 No project room allocations yet. Run allocation from admin panel.")


def render_oasis_allocations():
    """Render Oasis allocations"""
    
    oasis_allocations = storage.get_oasis_allocations()
    
    if oasis_allocations:
        df = pd.DataFrame(oasis_allocations)
        
        st.dataframe(
            df[['person_name', 'day_of_week', 'date', 'confirmed']],
            column_config={
                'person_name': 'Name',
                'day_of_week': 'Day',
                'date': 'Date',
                'confirmed': 'Confirmed'
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("📝 No Oasis allocations yet. Run allocation from admin panel.")


def render_interactive_matrix():
    """Render interactive allocation matrix"""
    
    st.markdown("#### 🗓️ Interactive Oasis Matrix")
    
    oasis_allocations = storage.get_oasis_allocations()
    
    if oasis_allocations:
        # Create matrix view
        render_allocation_matrix(oasis_allocations)
    else:
        st.info("📝 No allocations to display in matrix view.")


if __name__ == "__main__":
    main()

