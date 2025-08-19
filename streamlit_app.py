import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import io

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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    .main-header {
        background: linear-gradient(135deg, #38b2ac 0%, #4fd1c7 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 25px rgba(56, 178, 172, 0.3);
    }
    
    .main-header h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 3rem;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .main-header p {
        font-family: 'Inter', sans-serif;
        font-weight: 400;
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .metric-value {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 2.5rem;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .metric-label {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    .goal-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(240, 147, 251, 0.3);
    }
    
    .csv-import-section {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 2rem;
        border-radius: 16px;
        color: white;
        margin: 2rem 0;
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #38b2ac 0%, #4fd1c7 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(56, 178, 172, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2c7a7b 0%, #38b2ac 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(56, 178, 172, 0.4);
    }
    
    .export-button {
        background: linear-gradient(135deg, #38b2ac 0%, #4fd1c7 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 1rem 3rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(56, 178, 172, 0.3);
        margin: 2rem auto;
        display: block;
    }
    
    .export-button:hover {
        background: linear-gradient(135deg, #2c7a7b 0%, #38b2ac 100%);
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(56, 178, 172, 0.4);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%);
    }
    
    .stSelectbox > div > div > select {
        background: white;
        border-radius: 8px;
        border: 2px solid #e2e8f0;
    }
    
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
    }
    
    .stDateInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# Data storage functions
def load_data():
    """Load weight data from CSV file"""
    csv_path = Path("weight_data.csv")
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        df['date'] = pd.to_datetime(df['date'])
        return df
    else:
        # Create sample data if file doesn't exist
        sample_data = {
            'date': pd.date_range(start='2024-01-01', periods=20, freq='W'),
            'weight': np.random.normal(85, 2, 20).round(2),
            'notes': ['Feeling good', 'Great week', 'On track', 'Need to focus', 'Excellent progress'] * 4,
            'goal': ['maintenance'] * 20
        }
        df = pd.DataFrame(sample_data)
        df.to_csv(csv_path, index=False)
        return df

def save_data(df):
    """Save weight data to CSV file"""
    df.to_csv("weight_data.csv", index=False)

def load_user_profile():
    """Load user profile from JSON file"""
    json_path = Path("user_profile.json")
    if json_path.exists():
        with open(json_path, 'r') as f:
            return json.load(f)
    else:
        # Default profile
        default_profile = {
            'name': 'User',
            'goal': 'maintenance',
            'target_weight': 85.0,
            'current_weight': 85.0
        }
        with open(json_path, 'w') as f:
            json.dump(default_profile, f)
        return default_profile

def save_user_profile(profile):
    """Save user profile to JSON file"""
    with open("user_profile.json", 'w') as f:
        json.dump(profile, f)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'Dashboard'

# Load data
weight_data = load_data()
user_profile = load_user_profile()

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <h1 style="color: white; font-family: 'Inter', sans-serif; font-weight: 800;">⚖️ Weight Tracker</h1>
        <p style="color: #a0aec0; font-family: 'Inter', sans-serif; font-weight: 400;">Smart. Scientific. Sustainable.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Navigation")
    page = st.selectbox(
        "Choose a page",
        ['Dashboard', 'Add Weight', 'Analytics', 'Profile'],
        key='page_selector'
    )
    
    st.markdown("### Your Profile")
    st.markdown(f"**Name:** {user_profile['name']}")
    st.markdown(f"**Goal:** {user_profile['goal'].title()}")
    st.markdown(f"**Target:** {user_profile['target_weight']:.1f} kg")
    
    # Profile click to access profile page
    if st.button("Edit Profile", key="edit_profile_btn"):
        st.session_state.page = 'Profile'

# Main content
if page == "Dashboard":
    st.markdown("""
    <div class="main-header">
        <h1>Your Fitness Journey</h1>
        <p>Track your progress weekly to stay on target!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{len(weight_data)}</p>
            <p class="metric-label">Total Entries</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_weight = weight_data['weight'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{avg_weight:.1f}</p>
            <p class="metric-label">Avg Weight (kg)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        weight_range = weight_data['weight'].max() - weight_data['weight'].min()
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{weight_range:.1f}</p>
            <p class="metric-label">Weight Range (kg)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        recent_trend = weight_data.tail(2)['weight'].diff().iloc[-1] if len(weight_data) > 1 else 0
        trend_icon = "📈" if recent_trend > 0 else "📉" if recent_trend < 0 else "➡️"
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{trend_icon}</p>
            <p class="metric-label">Recent Trend</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Goal summary
    st.markdown(f"""
    <div class="goal-card">
        <h2 style="margin: 0 0 1rem 0; font-family: 'Inter', sans-serif; font-weight: 700;">Current Goal: {user_profile['goal'].title()}</h2>
        <p style="margin: 0; font-family: 'Inter', sans-serif; font-weight: 400; opacity: 0.9;">
            Target Weight: {user_profile['target_weight']:.1f} kg | Current Weight: {user_profile['current_weight']:.1f} kg
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Weight trend chart
    st.markdown("### Weight Trend")
    fig = px.line(
        weight_data, 
        x='date', 
        y='weight',
        title="",
        labels={'date': 'Date', 'weight': 'Weight (kg)'}
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=12),
        height=400
    )
    fig.update_traces(line=dict(color='#38b2ac', width=3))
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent entries
    st.markdown("### Recent Entries")
    recent_data = weight_data.tail(5).sort_values('date', ascending=False)
    st.dataframe(
        recent_data[['date', 'weight', 'notes']].rename(
            columns={'date': 'Date', 'weight': 'Weight (kg)', 'notes': 'Notes'}
        ),
        use_container_width=True,
        hide_index=True
    )

elif page == "Add Weight":
    st.markdown("""
    <div class="main-header">
        <h1>Add Weight Entry</h1>
        <p>Track your weekly progress with detailed notes</p>
    </div>
    """, unsafe_allow_html=True)
    
    # CSV Import Section
    st.markdown("""
    <div class="csv-import-section">
        <h2 style="margin: 0 0 1rem 0; font-family: 'Inter', sans-serif; font-weight: 700;">📁 Import CSV Data</h2>
        <p style="margin: 0; font-family: 'Inter', sans-serif; font-weight: 400; opacity: 0.9;">
            Upload a CSV file with your weight data
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show expected CSV format
    with st.expander("📋 **Expected CSV Format**"):
        st.markdown("""
        Your CSV should have these columns (column names are flexible):
        
        | **Required** | **Optional** | **Example** |
        |--------------|--------------|-------------|
        | `date` (or `Date`, `Date_Time`) | `notes` (or `Notes`, `Comments`) | `2025-08-19, 85.5, "Feeling great"` |
        | `weight` (or `Weight`, `Weight_kg`, `Weight_lbs`) | `goal` (or `Goal`, `Fitness_Goal`) | `2025-08-20, 85.3, "On track", "maintenance"` |
        
        **Date formats:** YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY, etc.
        **Weight formats:** Any number (kg or lbs)
        """)
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload a CSV file with columns: date, weight, notes, goal"
    )
    
    if uploaded_file is not None:
        try:
            # Read CSV content
            csv_content = uploaded_file.read().decode('utf-8')
            df_upload = pd.read_csv(io.StringIO(csv_content))
            
            # Show what columns we found
            st.info(f"📋 **CSV Columns Found:** {list(df_upload.columns)}")
            
            # Show first few rows for debugging
            st.markdown("**📊 First few rows of your CSV:**")
            st.dataframe(df_upload.head(3), use_container_width=True)
            
            # Try to map common column variations
            column_mapping = {}
            date_col = None
            weight_col = None
            
            # Look for date columns (case insensitive)
            for col in df_upload.columns:
                col_lower = col.lower()
                if 'date' in col_lower or 'time' in col_lower:
                    date_col = col
                    column_mapping['date'] = col
                elif 'weight' in col_lower or 'kg' in col_lower or 'lbs' in col_lower:
                    weight_col = col
                    column_mapping['weight'] = col
            
            # Validate we have the essential columns
            if date_col and weight_col:
                # Rename columns to standard format
                df_upload = df_upload.rename(columns={
                    date_col: 'date',
                    weight_col: 'weight'
                })
                
                # Convert date column
                df_upload['date'] = pd.to_datetime(df_upload['date'])
                
                # Add missing columns with defaults
                if 'notes' not in df_upload.columns:
                    df_upload['notes'] = ''
                if 'goal' not in df_upload.columns:
                    df_upload['goal'] = user_profile['goal']
                
                # Show preview
                st.success(f"✅ Successfully loaded {len(df_upload)} entries!")
                st.markdown("**Preview of uploaded data:**")
                st.dataframe(df_upload.head(), use_container_width=True)
                
                # Confirm import
                if st.button("Import Data", key="import_btn"):
                    # Append to existing data
                    weight_data = pd.concat([weight_data, df_upload], ignore_index=True)
                    weight_data = weight_data.drop_duplicates(subset=['date']).sort_values('date')
                    save_data(weight_data)
                    st.success(f"✅ Imported {len(df_upload)} entries successfully!")
                    st.rerun()
                    
            else:
                st.error(f"❌ **CSV Import Failed**")
                st.error(f"**Required columns not found:**")
                st.error(f"• Date column (found: {date_col if date_col else 'None'})")
                st.error(f"• Weight column (found: {weight_col if weight_col else 'None'})")
                st.error(f"**Your CSV has:** {list(df_upload.columns)}")
                st.error(f"**Tip:** Make sure your CSV has columns with 'date' or 'time' in the name, and 'weight', 'kg', or 'lbs' in the name.")
                
        except Exception as e:
            st.error(f"❌ Error reading CSV: {str(e)}")
    
    st.markdown("---")
    
    # Manual entry form
    st.markdown("### 📝 Manual Entry")
    
    col1, col2 = st.columns(2)
    
    with col1:
        weight = st.number_input(
            "Weight (kg)",
            min_value=30.0,
            max_value=300.0,
            value=float(user_profile['current_weight']),
            step=0.1,
            format="%.2f"
        )
        
        date = st.date_input(
            "Date",
            value=datetime.now().date()
        )
    
    with col2:
        notes = st.text_area(
            "Notes (optional)",
            placeholder="How are you feeling? Any observations?",
            height=100
        )
        
        goal = st.selectbox(
            "Fitness Goal",
            ['maintenance', 'cut', 'bulk', 'reverse'],
            index=['maintenance', 'cut', 'bulk', 'reverse'].index(user_profile['goal'])
        )
    
    if st.button("Add Weight Entry", key="add_weight_btn"):
        # Add new entry
        new_entry = pd.DataFrame({
            'date': [pd.to_datetime(date)],
            'weight': [weight],
            'notes': [notes],
            'goal': [goal]
        })
        
        weight_data = pd.concat([weight_data, new_entry], ignore_index=True)
        weight_data = weight_data.drop_duplicates(subset=['date']).sort_values('date')
        save_data(weight_data)
        
        # Update user profile
        user_profile['current_weight'] = weight
        user_profile['goal'] = goal
        save_user_profile(user_profile)
        
        st.success("✅ Weight entry added successfully!")
        st.rerun()
    
    # Goal-specific tips
    st.markdown("### 🎯 Goal-Specific Tracking Tips")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        **Bulk/Reverse:**  
        • Expect 0.2-0.5 kg weekly gain  
        • Focus on protein and strength training
        """)
    
    with col2:
        st.markdown("""
        **Cut:**  
        • Expect 0.2-0.5 kg weekly loss  
        • Maintain protein, reduce calories
        """)
    
    with col3:
        st.markdown("""
        **Maintenance:**  
        • Expect ±0.2 kg weekly variation  
        • Balance calories and activity
        """)
    
    with col4:
        st.markdown("""
        **Weekly Tracking:**  
        • Weigh at same time each week  
        • Track trends, not daily fluctuations
        """)

elif page == "Analytics":
    st.markdown("""
    <div class="main-header">
        <h1>Analytics & Insights</h1>
        <p>Deep dive into your weight tracking data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Time range filter
    col1, col2 = st.columns([1, 3])
    with col1:
        time_range = st.selectbox(
            "Time Range",
            ['1M', '3M', '6M', '1Y', 'All'],
            index=4
        )
    
    # Filter data based on time range
    if time_range != 'All':
        months = {'1M': 1, '3M': 3, '6M': 6, '1Y': 12}
        cutoff_date = datetime.now() - timedelta(days=months[time_range] * 30)
        filtered_data = weight_data[weight_data['date'] >= cutoff_date]
    else:
        filtered_data = weight_data
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{len(filtered_data)}</p>
            <p class="metric-label">Entries</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_weight = filtered_data['weight'].mean() if len(filtered_data) > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{avg_weight:.1f}</p>
            <p class="metric-label">Avg Weight</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        min_weight = filtered_data['weight'].min() if len(filtered_data) > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{min_weight:.1f}</p>
            <p class="metric-label">Min Weight</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        max_weight = filtered_data['weight'].max() if len(filtered_data) > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{max_weight:.1f}</p>
            <p class="metric-label">Max Weight</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Weight Trend")
        if len(filtered_data) > 0:
            fig_trend = px.line(
                filtered_data, 
                x='date', 
                y='weight',
                title="",
                labels={'date': 'Date', 'weight': 'Weight (kg)'}
            )
            fig_trend.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', size=12),
                height=300
            )
            fig_trend.update_traces(line=dict(color='#38b2ac', width=3))
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No data available for selected time range")
    
    with col2:
        st.markdown("### Weight Distribution")
        if len(filtered_data) > 0:
            fig_dist = px.histogram(
                filtered_data,
                x='weight',
                nbins=10,
                title="",
                labels={'weight': 'Weight (kg)', 'count': 'Frequency'}
            )
            fig_dist.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', size=12),
                height=300
            )
            fig_dist.update_traces(marker_color='#667eea')
            st.plotly_chart(fig_dist, use_container_width=True)
        else:
            st.info("No data available for selected time range")
    
    # Goal progress
    st.markdown("### Goal Progress")
    if user_profile['goal'] != 'maintenance':
        target = user_profile['target_weight']
        current = user_profile['current_weight']
        
        if user_profile['goal'] in ['cut', 'reverse']:
            if user_profile['goal'] == 'cut':
                progress = max(0, min(100, (target - current) / (weight_data['weight'].max() - target) * 100))
                direction = "losing"
            else:  # reverse
                progress = max(0, min(100, (current - target) / (target - weight_data['weight'].min()) * 100))
                direction = "gaining"
            
            st.progress(progress / 100)
            st.markdown(f"**Progress towards {direction} weight:** {progress:.1f}%")
        else:  # bulk
            progress = max(0, min(100, (current - target) / (target - weight_data['weight'].min()) * 100))
            st.progress(progress / 100)
            st.markdown(f"**Progress towards gaining weight:** {progress:.1f}%")
    else:
        st.info("Maintenance goal - focus on staying within your target range")
    
    # Export CSV
    st.markdown("---")
    st.markdown("### Export Data")
    
    # Create CSV for download
    csv = weight_data.to_csv(index=False)
    
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"weight_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        key="export_csv_btn"
    )

elif page == "Profile":
    st.markdown("""
    <div class="main-header">
        <h1>Profile & Settings</h1>
        <p>Manage your fitness goals and preferences</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Personal Information")
        
        name = st.text_input(
            "Name",
            value=user_profile['name'],
            key="profile_name"
        )
        
        goal = st.selectbox(
            "Fitness Goal",
            ['maintenance', 'cut', 'bulk', 'reverse'],
            index=['maintenance', 'cut', 'bulk', 'reverse'].index(user_profile['goal']),
            key="profile_goal"
        )
        
        target_weight = st.number_input(
            "Target Weight (kg)",
            min_value=30.0,
            max_value=300.0,
            value=float(user_profile['target_weight']),
            step=0.1,
            format="%.1f",
            key="profile_target"
        )
        
        current_weight = st.number_input(
            "Current Weight (kg)",
            min_value=30.0,
            max_value=300.0,
            value=float(user_profile['current_weight']),
            step=0.1,
            format="%.1f",
            key="profile_current"
        )
        
        if st.button("Save Changes", key="save_profile_btn"):
            user_profile.update({
                'name': name,
                'goal': goal,
                'target_weight': target_weight,
                'current_weight': current_weight
            })
            save_user_profile(user_profile)
            st.success("✅ Profile updated successfully!")
            st.rerun()
    
    with col2:
        st.markdown("### Goal Descriptions")
        
        goal_descriptions = {
            'maintenance': {
                'title': 'Maintenance',
                'description': 'Maintain your current weight and body composition',
                'tips': ['Eat at maintenance calories', 'Regular exercise', 'Monitor trends']
            },
            'cut': {
                'title': 'Cut',
                'description': 'Gradually reduce body fat while preserving muscle',
                'tips': ['Caloric deficit (200-500 calories)', 'High protein diet', 'Strength training']
            },
            'bulk': {
                'title': 'Bulk',
                'description': 'Build muscle mass with controlled weight gain',
                'tips': ['Caloric surplus (200-500 calories)', 'High protein diet', 'Progressive overload']
            },
            'reverse': {
                'title': 'Reverse (Gradual Gain)',
                'description': 'Very gradual weight gain for muscle building',
                'tips': ['Small surplus (100-200 calories)', 'Lean protein focus', 'Progressive training']
            }
        }
        
        selected_goal = goal_descriptions[goal]
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1.5rem; border-radius: 16px; color: white;">
            <h3 style="margin: 0 0 1rem 0; font-family: 'Inter', sans-serif; font-weight: 700;">
                {selected_goal['title']}
            </h3>
            <p style="margin: 0 0 1rem 0; opacity: 0.9;">
                {selected_goal['description']}
            </p>
            <ul style="margin: 0; padding-left: 1rem;">
                {''.join([f'<li>{tip}</li>' for tip in selected_goal['tips']])}
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Data export
    st.markdown("---")
    st.markdown("### Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Export your data:**")
        csv = weight_data.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"weight_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            key="profile_export_csv"
        )
    
    with col2:
        st.markdown("**Reset data:**")
        if st.button("🗑️ Clear All Data", key="clear_data_btn"):
            if st.checkbox("I understand this will delete all my data permanently"):
                # Remove data files
                if Path("weight_data.csv").exists():
                    os.remove("weight_data.csv")
                if Path("user_profile.json").exists():
                    os.remove("user_profile.json")
                st.success("✅ Data cleared successfully!")
                st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #718096;">
    <p style="font-family: 'Inter', sans-serif; font-weight: 400;">
        Weight Tracker - Built with Streamlit ❤️
    </p>
    <p style="font-family: 'Inter', sans-serif; font-weight: 600; color: #38b2ac;">
        Smart. Scientific. Sustainable.
    </p>
</div>
""", unsafe_allow_html=True)
