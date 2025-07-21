"""
UI Components for Room Allocation System
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any


def render_capacity_info(capacity_data: Dict[str, Any]):
    """Render capacity information display"""
    
    st.markdown("### 📊 Capacity Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Project Rooms")
        
        # Create a DataFrame for project rooms
        rooms_data = []
        for room, capacity in capacity_data['project_rooms'].items():
            rooms_data.append({'Room': room, 'Capacity': capacity})
        
        df_rooms = pd.DataFrame(rooms_data)
        
        # Create bar chart
        fig = px.bar(df_rooms, x='Room', y='Capacity', 
                    title='Project Room Capacities',
                    color='Capacity',
                    color_continuous_scale='Blues')
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Oasis Workspace")
        
        # Oasis capacity visualization
        oasis_capacity = capacity_data['oasis_capacity']
        weekdays = capacity_data['weekdays']
        
        # Create gauge chart for Oasis
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = oasis_capacity,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Daily Oasis Capacity"},
            gauge = {
                'axis': {'range': [None, 15]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 5], 'color': "lightgray"},
                    {'range': [5, 10], 'color': "gray"},
                    {'range': [10, 15], 'color': "darkgray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': oasis_capacity
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)


def render_allocation_matrix(allocations: List[Dict[str, Any]]):
    """Render interactive allocation matrix"""
    
    if not allocations:
        st.info("No allocations to display")
        return
    
    # Create DataFrame from allocations
    df = pd.DataFrame(allocations)
    
    # Create pivot table for matrix view
    matrix_data = df.pivot_table(
        index='person_name',
        columns='day_of_week',
        values='confirmed',
        aggfunc='first',
        fill_value=False
    )
    
    # Ensure all weekdays are present
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    for day in weekdays:
        if day not in matrix_data.columns:
            matrix_data[day] = False
    
    # Reorder columns
    matrix_data = matrix_data[weekdays]
    
    # Create heatmap
    fig = px.imshow(
        matrix_data.astype(int),
        labels=dict(x="Day of Week", y="Person", color="Allocated"),
        x=weekdays,
        y=matrix_data.index,
        color_continuous_scale=['lightgray', 'green'],
        title="Oasis Allocation Matrix"
    )
    
    fig.update_layout(height=max(400, len(matrix_data) * 30))
    st.plotly_chart(fig, use_container_width=True)
    
    # Interactive editing (placeholder)
    st.markdown("#### ✏️ Edit Allocations")
    st.info("Interactive editing will be available in the admin panel.")


def render_status_indicator(status: str, message: str):
    """Render status indicator with appropriate styling"""
    
    if status == "success":
        st.markdown(f"""
        <div class="success-box">
            <h4>✅ Success</h4>
            <p>{message}</p>
        </div>
        """, unsafe_allow_html=True)
    
    elif status == "error":
        st.markdown(f"""
        <div class="error-box">
            <h4>❌ Error</h4>
            <p>{message}</p>
        </div>
        """, unsafe_allow_html=True)
    
    elif status == "info":
        st.markdown(f"""
        <div class="info-box">
            <h4>ℹ️ Information</h4>
            <p>{message}</p>
        </div>
        """, unsafe_allow_html=True)
    
    elif status == "warning":
        st.markdown(f"""
        <div style="background-color: #fff3cd; padding: 1rem; border-radius: 8px; border-left: 4px solid #ffc107; margin: 1rem 0;">
            <h4>⚠️ Warning</h4>
            <p>{message}</p>
        </div>
        """, unsafe_allow_html=True)


def render_data_table(data: List[Dict], title: str, columns: Dict[str, str] = None):
    """Render a formatted data table"""
    
    if not data:
        st.info(f"No {title.lower()} data available")
        return
    
    st.markdown(f"### {title}")
    
    df = pd.DataFrame(data)
    
    # Apply column configuration if provided
    if columns:
        st.dataframe(
            df,
            column_config=columns,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)


def render_metrics_row(metrics: List[Dict[str, Any]]):
    """Render a row of metrics"""
    
    cols = st.columns(len(metrics))
    
    for i, metric in enumerate(metrics):
        with cols[i]:
            st.metric(
                label=metric['label'],
                value=metric['value'],
                delta=metric.get('delta'),
                help=metric.get('help')
            )


def render_form_section(title: str, description: str = None):
    """Render a form section header"""
    
    st.markdown(f"### {title}")
    
    if description:
        st.markdown(f"""
        <div class="info-box">
            <p>{description}</p>
        </div>
        """, unsafe_allow_html=True)


def render_confirmation_dialog(title: str, message: str, confirm_text: str = "Confirm", cancel_text: str = "Cancel"):
    """Render a confirmation dialog"""
    
    st.markdown(f"### {title}")
    st.markdown(message)
    
    col1, col2 = st.columns(2)
    
    with col1:
        confirm = st.button(confirm_text, type="primary", use_container_width=True)
    
    with col2:
        cancel = st.button(cancel_text, use_container_width=True)
    
    return confirm, cancel


def render_loading_spinner(message: str = "Processing..."):
    """Render a loading spinner with message"""
    
    with st.spinner(message):
        return True


def render_progress_bar(progress: float, message: str = ""):
    """Render a progress bar"""
    
    progress_bar = st.progress(progress)
    
    if message:
        st.text(message)
    
    return progress_bar

