import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Weight Tracker",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        text-align: center;
    }
    .goal-card {
        background: linear-gradient(135deg, #38b2ac 0%, #4fd1c7 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stButton > button {
        background: linear-gradient(135deg, #38b2ac 0%, #4fd1c7 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2c7a7b 0%, #38b2ac 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(56, 178, 172, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Data storage functions
def load_data():
    """Load weight data from CSV file"""
    data_file = "weight_data.csv"
    if os.path.exists(data_file):
        df = pd.read_csv(data_file)
        df['date'] = pd.to_datetime(df['date'])
        return df
    else:
        # Create sample data if no file exists
        sample_data = {
            'date': pd.date_range(start='2024-01-01', periods=30, freq='D'),
            'weight': [85.0 + i*0.1 + np.random.normal(0, 0.3) for i in range(30)],
            'notes': ['Morning weight'] * 30
        }
        df = pd.DataFrame(sample_data)
        df.to_csv(data_file, index=False)
        return df

def save_data(df):
    """Save weight data to CSV file"""
    df.to_csv("weight_data.csv", index=False)

def load_user_profile():
    """Load user profile from JSON file"""
    profile_file = "user_profile.json"
    if os.path.exists(profile_file):
        with open(profile_file, 'r') as f:
            return json.load(f)
    else:
        # Default profile
        default_profile = {
            'name': 'User',
            'goal': 'maintenance',
            'target_weight': 85.0,
            'current_weight': 85.0
        }
        with open(profile_file, 'w') as f:
            json.dump(default_profile, f)
        return default_profile

def save_user_profile(profile):
    """Save user profile to JSON file"""
    with open("user_profile.json", 'w') as f:
        json.dump(profile, f)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.weight_data = load_data()
    st.session_state.user_profile = load_user_profile()
    st.session_state.data_loaded = True

# Sidebar navigation
st.sidebar.markdown("""
<div style="text-align: center; padding: 1rem;">
    <h2>⚖️ Weight Tracker</h2>
    <p style="color: #666;">Smart. Scientific. Sustainable.</p>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.selectbox(
    "Navigation",
    ["Dashboard", "Add Weight", "Analytics", "Profile"]
)

# User profile display in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### Your Profile")
st.sidebar.markdown(f"**Name:** {st.session_state.user_profile['name']}")
st.sidebar.markdown(f"**Goal:** {st.session_state.user_profile['goal'].title()}")
st.sidebar.markdown(f"**Target:** {st.session_state.user_profile['target_weight']} kg")

# Main content
if page == "Dashboard":
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>Your Fitness Journey</h1>
        <p>Track your progress weekly to stay on target!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Goal summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="goal-card">
            <h3>🎯 Goal</h3>
            <h2>{}</h2>
        </div>
        """.format(st.session_state.user_profile['goal'].title()), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="goal-card">
            <h3>🎯 Target</h3>
            <h2>{} kg</h2>
        </div>
        """.format(st.session_state.user_profile['target_weight']), unsafe_allow_html=True)
    
    with col3:
        current_weight = st.session_state.weight_data['weight'].iloc[-1] if len(st.session_state.weight_data) > 0 else 0
        st.markdown("""
        <div class="goal-card">
            <h3>⚖️ Current</h3>
            <h2>{:.1f} kg</h2>
        </div>
        """.format(current_weight), unsafe_allow_html=True)
    
    # Key metrics
    st.markdown("### 📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>📈 Total Entries</h4>
            <h2>{}</h2>
        </div>
        """.format(len(st.session_state.weight_data)), unsafe_allow_html=True)
    
    with col2:
        avg_weight = st.session_state.weight_data['weight'].mean() if len(st.session_state.weight_data) > 0 else 0
        st.markdown("""
        <div class="metric-card">
            <h4>📊 Average Weight</h4>
            <h2>{:.1f} kg</h2>
        </div>
        """.format(avg_weight), unsafe_allow_html=True)
    
    with col3:
        weight_range = st.session_state.weight_data['weight'].max() - st.session_state.weight_data['weight'].min() if len(st.session_state.weight_data) > 0 else 0
        st.markdown("""
        <div class="metric-card">
            <h4>📏 Weight Range</h4>
            <h2>{:.1f} kg</h2>
        </div>
        """.format(weight_range), unsafe_allow_html=True)
    
    with col4:
        if st.session_state.user_profile['target_weight'] > 0:
            progress = min(100, max(0, (1 - abs(current_weight - st.session_state.user_profile['target_weight']) / st.session_state.user_profile['target_weight']) * 100))
        else:
            progress = 0
        st.markdown("""
        <div class="metric-card">
            <h4>🎯 Goal Progress</h4>
            <h2>{:.0f}%</h2>
        </div>
        """.format(progress), unsafe_allow_html=True)
    
    # Weight trend chart
    st.markdown("### 📈 Weight Trend")
    if len(st.session_state.weight_data) > 0:
        fig = px.line(
            st.session_state.weight_data, 
            x='date', 
            y='weight',
            title="Weight Over Time",
            labels={'weight': 'Weight (kg)', 'date': 'Date'}
        )
        fig.update_layout(
            plot_bgcolor='white',
            xaxis=dict(gridcolor='lightgray'),
            yaxis=dict(gridcolor='lightgray')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent entries
    st.markdown("### 📝 Recent Entries")
    if len(st.session_state.weight_data) > 0:
        recent_data = st.session_state.weight_data.tail(5)[['date', 'weight', 'notes']].copy()
        recent_data['date'] = recent_data['date'].dt.strftime('%Y-%m-%d')
        st.dataframe(recent_data, use_container_width=True)

elif page == "Add Weight":
    st.title("📝 Add Weight Entry")
    
    # Weight entry form
    with st.form("weight_entry"):
        col1, col2 = st.columns(2)
        
        with col1:
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=85.0, step=0.1)
            date = st.date_input("Date", value=datetime.now().date())
        
        with col2:
            notes = st.text_area("Notes (optional)", placeholder="How are you feeling? Any observations?")
            goal = st.selectbox("Fitness Goal", ["maintenance", "cut", "bulk", "reverse"])
        
        submitted = st.form_submit_button("Add Weight Entry")
        
        if submitted:
            # Add new entry
            new_entry = pd.DataFrame({
                'date': [date],
                'weight': [weight],
                'notes': [notes]
            })
            
            st.session_state.weight_data = pd.concat([st.session_state.weight_data, new_entry], ignore_index=True)
            st.session_state.weight_data = st.session_state.weight_data.sort_values('date')
            save_data(st.session_state.weight_data)
            
            # Update user profile
            st.session_state.user_profile['goal'] = goal
            st.session_state.user_profile['current_weight'] = weight
            save_user_profile(st.session_state.user_profile)
            
            st.success("Weight entry added successfully! 🎉")
            st.balloons()

elif page == "Analytics":
    st.title("📊 Analytics & Insights")
    
    if len(st.session_state.weight_data) > 0:
        # Time range filter
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### Weight Trend Analysis")
        with col2:
            time_range = st.selectbox("Time Range", ["1M", "3M", "6M", "1Y", "All"])
        
        # Filter data based on time range
        if time_range == "1M":
            filtered_data = st.session_state.weight_data[st.session_state.weight_data['date'] >= datetime.now() - timedelta(days=30)]
        elif time_range == "3M":
            filtered_data = st.session_state.weight_data[st.session_state.weight_data['date'] >= datetime.now() - timedelta(days=90)]
        elif time_range == "6M":
            filtered_data = st.session_state.weight_data[st.session_state.weight_data['date'] >= datetime.now() - timedelta(days=180)]
        elif time_range == "1Y":
            filtered_data = st.session_state.weight_data[st.session_state.weight_data['date'] >= datetime.now() - timedelta(days=365)]
        else:
            filtered_data = st.session_state.weight_data
        
        # Weight trend chart
        if len(filtered_data) > 0:
            fig = px.line(
                filtered_data, 
                x='date', 
                y='weight',
                title=f"Weight Trend - {time_range}",
                labels={'weight': 'Weight (kg)', 'date': 'Date'}
            )
            fig.update_layout(
                plot_bgcolor='white',
                xaxis=dict(gridcolor='lightgray'),
                yaxis=dict(gridcolor='lightgray')
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average Weight", f"{filtered_data['weight'].mean():.1f} kg")
            with col2:
                st.metric("Weight Range", f"{filtered_data['weight'].max() - filtered_data['weight'].min():.1f} kg")
            with col3:
                st.metric("Total Entries", len(filtered_data))
            
            # Weight distribution
            st.markdown("### 📊 Weight Distribution")
            fig_hist = px.histogram(
                filtered_data, 
                x='weight',
                nbins=20,
                title="Weight Distribution",
                labels={'weight': 'Weight (kg)', 'count': 'Frequency'}
            )
            fig_hist.update_layout(
                plot_bgcolor='white',
                xaxis=dict(gridcolor='lightgray'),
                yaxis=dict(gridcolor='lightgray')
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("No data available for the selected time range.")
    else:
        st.info("No weight data available. Add some entries first!")

elif page == "Profile":
    st.title("👤 Profile & Settings")
    
    # Profile form
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name", value=st.session_state.user_profile['name'])
            goal = st.selectbox("Fitness Goal", ["maintenance", "cut", "bulk", "reverse"])
        
        with col2:
            target_weight = st.number_input("Target Weight (kg)", min_value=30.0, max_value=300.0, value=st.session_state.user_profile['target_weight'], step=0.1)
            current_weight = st.number_input("Current Weight (kg)", min_value=30.0, max_value=300.0, value=st.session_state.user_profile['current_weight'], step=0.1)
        
        submitted = st.form_submit_button("Save Profile")
        
        if submitted:
            st.session_state.user_profile.update({
                'name': name,
                'goal': goal,
                'target_weight': target_weight,
                'current_weight': current_weight
            })
            save_user_profile(st.session_state.user_profile)
            st.success("Profile updated successfully! 🎉")
    
    # Goal descriptions
    st.markdown("### 💡 Goal Descriptions")
    goal_descriptions = {
        "maintenance": "Maintain current weight and body composition",
        "cut": "Lose weight and reduce body fat",
        "bulk": "Gain weight and build muscle mass",
        "reverse": "Gradual weight gain for muscle building"
    }
    
    for g, desc in goal_descriptions.items():
        if g == st.session_state.user_profile['goal']:
            st.markdown(f"**🎯 {g.title()}**: {desc} *(Current Goal)*")
        else:
            st.markdown(f"**{g.title()}**: {desc}")
    
    # Data export
    st.markdown("### 📤 Export Data")
    if len(st.session_state.weight_data) > 0:
        csv = st.session_state.weight_data.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"weight_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>Weight Tracker - Built with Streamlit ❤️</p>
    <p>Smart. Scientific. Sustainable.</p>
</div>
""", unsafe_allow_html=True)
