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
import hashlib

# Page configuration
st.set_page_config(
    page_title="Weight Tracker",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Utility functions
def calculate_bmi(weight_kg, height_cm):
    """Calculate BMI from weight and height"""
    if height_cm > 0:
        height_m = height_cm / 100
        return weight_kg / (height_m ** 2)
    return 0

def get_bmi_category(bmi):
    """Get BMI category and color"""
    if bmi < 18.5:
        return "Underweight", "#ff6b6b"
    elif bmi < 25:
        return "Normal", "#51cf66"
    elif bmi < 30:
        return "Overweight", "#ffd43b"
    else:
        return "Obese", "#ff6b6b"

def calculate_progress_to_goal(current_weight, target_weight, start_weight=None):
    """Calculate progress toward goal as percentage"""
    if start_weight is None or start_weight == target_weight:
        return 0

    total_change_needed = abs(target_weight - start_weight)
    current_change = abs(current_weight - start_weight)

    if total_change_needed == 0:
        return 100

    progress = (current_change / total_change_needed) * 100
    return min(progress, 100)

def calculate_streak(weight_data):
    """Calculate days since last entry"""
    if len(weight_data) == 0:
        return 0

    last_entry = weight_data['date'].max()
    today = pd.Timestamp.now().normalize()
    days_since = (today - last_entry.normalize()).days
    return days_since

def calculate_weekly_change(weight_data):
    """Calculate weekly weight change rate"""
    if len(weight_data) < 2:
        return 0

    # Get data from last 4 weeks
    recent_data = weight_data.tail(28)  # Assuming roughly daily entries
    if len(recent_data) < 2:
        return 0

    first_weight = recent_data.iloc[0]['weight']
    last_weight = recent_data.iloc[-1]['weight']
    days_diff = (recent_data.iloc[-1]['date'] - recent_data.iloc[0]['date']).days

    if days_diff == 0:
        return 0

    weekly_change = ((last_weight - first_weight) / days_diff) * 7
    return weekly_change

def get_motivational_message(progress, goal, weekly_change):
    """Get motivational message based on progress"""
    messages = {
        'weight_loss': {
            'good': ["🔥 Amazing progress! Keep it up!", "💪 You're crushing your goals!", "⭐ Fantastic work this week!"],
            'ok': ["👍 Steady progress! Stay consistent!", "💫 You're on the right track!", "🎯 Keep pushing forward!"],
            'bad': ["💪 Every step counts! Don't give up!", "🌟 Tomorrow is a new day!", "🎯 Refocus and restart!"]
        },
        'weight_gain': {
            'good': ["💪 Excellent gains! Keep eating!", "🔥 Building that muscle!", "⭐ Great progress this week!"],
            'ok': ["👍 Steady gains! Stay consistent!", "💫 You're making progress!", "🎯 Keep up the good work!"],
            'bad': ["💪 Consistency is key! You've got this!", "🌟 Small gains add up!", "🎯 Stay focused on your goals!"]
        },
        'maintenance': {
            'good': ["⚖️ Perfect balance! Well maintained!", "✨ Consistency champion!", "🎯 Nailing your maintenance!"],
            'ok': ["👍 Staying steady! Good job!", "💫 Maintaining well!", "⚖️ Balanced approach!"],
            'bad': ["💪 Maintenance takes discipline too!", "🌟 Get back to your routine!", "🎯 You know what works!"]
        }
    }

    # Determine performance level
    if goal == 'weight_loss':
        if weekly_change < -0.3:
            level = 'good'
        elif weekly_change < 0:
            level = 'ok'
        else:
            level = 'bad'
    elif goal == 'weight_gain':
        if weekly_change > 0.3:
            level = 'good'
        elif weekly_change > 0:
            level = 'ok'
        else:
            level = 'bad'
    else:  # maintenance
        if abs(weekly_change) < 0.2:
            level = 'good'
        elif abs(weekly_change) < 0.5:
            level = 'ok'
        else:
            level = 'bad'

    import random
    goal_type = 'weight_loss' if goal == 'weight_loss' else 'weight_gain' if goal in ['weight_gain', 'reverse_goal'] else 'maintenance'
    return random.choice(messages[goal_type][level])

# Data storage functions
def load_data(username):
    """Load weight data from user-specific CSV file"""
    csv_path = Path(f"weight_data_{username}.csv")
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        df['date'] = pd.to_datetime(df['date'])
        return df
    else:
        # Return empty DataFrame for new users
        return pd.DataFrame(columns=['date', 'weight', 'notes', 'goal'])

def save_data(df, username):
    """Save weight data to user-specific CSV file"""
    csv_path = Path(f"weight_data_{username}.csv")
    df.to_csv(csv_path, index=False)

def load_user_profile(username):
    """Load user profile from user-specific JSON file"""
    json_path = Path(f"user_profile_{username}.json")
    if json_path.exists():
        with open(json_path, 'r') as f:
            return json.load(f)
    else:
        # Default profile for new users
        default_profile = {
            'name': username.title(),
            'goal': 'maintenance',
            'target_weight': 85.0,
            'current_weight': 85.0,
            'height': 175.0  # cm
        }
        with open(json_path, 'w') as f:
            json.dump(default_profile, f)
        return default_profile

def save_user_profile(profile, username):
    """Save user profile to user-specific JSON file"""
    json_path = Path(f"user_profile_{username}.json")
    with open(json_path, 'w') as f:
        json.dump(profile, f)

# Authentication functions
def hash_password(password):
    """Hash password for security"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_credentials(username, password):
    """Check if username and password are correct"""
    users = load_users()
    
    if username in users:
        return users[username]['password'] == hash_password(password)
    return False

def load_users():
    """Load users from file or return empty dict if no users exist"""
    users_file = Path("users.json")
    if users_file.exists():
        try:
            with open(users_file, 'r') as f:
                return json.load(f)
        except:
            pass
    
    # Return empty dict - no default users
    return {}

def save_users(users):
    """Save users to file"""
    with open("users.json", 'w') as f:
        json.dump(users, f, indent=2)

def create_user(username, password, security_question, security_answer):
    """Create a new user account"""
    users = load_users()
    
    if username in users:
        return False, "Username already exists"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    # Create new user
    users[username] = {
        'password': hash_password(password),
        'security_question': security_question,
        'security_answer': security_answer
    }
    
    save_users(users)
    
    # Create user profile and data files
    user_profile = {
        'name': username.title(),
        'goal': 'maintenance',
        'target_weight': 85.0,
        'current_weight': 85.0,
        'height': 175.0  # cm
    }
    save_user_profile(user_profile, username)
    
    # Create empty weight data file
    empty_df = pd.DataFrame(columns=['date', 'weight', 'notes', 'goal'])
    save_data(empty_df, username)
    
    return True, f"Account created successfully for {username}!"

def change_user_password(username, new_password):
    """Change user password"""
    users = load_users()
    if username in users:
        users[username]['password'] = hash_password(new_password)
        save_users(users)
        return True
    return False

def get_security_question(username):
    """Get security question for password reset"""
    users = load_users()
    if username in users:
        return users[username]['security_question']
    return None

def check_security_answer(username, answer):
    """Check if security answer is correct"""
    users = load_users()
    if username in users:
        return users[username]['security_answer'].lower() == answer.lower()
    return False

# Initialize authentication
def init_auth():
    """Initialize authentication state"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None

# Initialize authentication
init_auth()

# Quick Access Option
if st.sidebar.button("🚀 Quick Access (Bypass Login)", use_container_width=True):
    st.session_state.authenticated = True
    st.session_state.username = "demo_user"
    st.rerun()

# Login page
if not st.session_state.authenticated:
    st.markdown("""
    <div style="text-align: center; padding: 4rem;">
        <h1 style="font-family: 'Inter', sans-serif; font-weight: 800; color: #38b2ac;">⚖️ Weight Tracker</h1>
        <p style="font-family: 'Inter', sans-serif; font-weight: 400; color: #718096; font-size: 1.2rem;">
            Smart. Scientific. Sustainable.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Login form
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #38b2ac 0%, #4fd1c7 100%); 
                        padding: 2rem; border-radius: 16px; color: white; text-align: center;">
                <h2 style="margin: 0 0 1rem 0; font-family: 'Inter', sans-serif; font-weight: 700;">
                    🔐 Login Required
                </h2>
                <p style="margin: 0; opacity: 0.9;">
                    Please login to access your weight tracking data
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    submit_button = st.form_submit_button("Login", use_container_width=True)
                with col2:
                    if st.form_submit_button("🔑 Forgot Password?", use_container_width=True):
                        st.session_state.show_forgot_password = True
                with col3:
                    if st.form_submit_button("📝 Sign Up", use_container_width=True):
                        st.session_state.show_signup = True
                
                if submit_button:
                    if check_credentials(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.success("✅ Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
            
            # Forgot Password Section
            if st.session_state.get('show_forgot_password', False):
                st.markdown("---")
                st.markdown("### 🔑 Password Reset")
                
                with st.form("forgot_password_form"):
                    reset_username = st.text_input("Username", placeholder="Enter your username", key="reset_username")
                    security_question = get_security_question(reset_username) if reset_username else ""
                    
                    if security_question:
                        st.markdown(f"**Security Question:** {security_question}")
                        security_answer = st.text_input("Answer", placeholder="Enter your answer", key="security_answer")
                        new_password = st.text_input("New Password", type="password", placeholder="Enter new password", key="new_password")
                        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm new password", key="confirm_password")
                        
                        reset_button = st.form_submit_button("Reset Password", use_container_width=True)
                        
                        if reset_button:
                            if not reset_username or not security_answer or not new_password:
                                st.error("❌ Please fill in all fields")
                            elif new_password != confirm_password:
                                st.error("❌ Passwords don't match")
                            elif len(new_password) < 8:
                                st.error("❌ Password must be at least 8 characters")
                            elif check_security_answer(reset_username, security_answer):
                                if change_user_password(reset_username, new_password):
                                    st.success("✅ Password updated successfully! You can now login with your new password.")
                                    st.session_state.show_forgot_password = False
                                else:
                                    st.error("❌ Failed to update password")
                            else:
                                st.error("❌ Incorrect security answer")
                    elif reset_username:
                        st.error("❌ Username not found. Please check your username or create a new account.")
                
                # Back to login button
                if st.button("← Back to Login", key="back_to_login"):
                    st.session_state.show_forgot_password = False
                    st.rerun()
            
            # Sign Up Section
            if st.session_state.get('show_signup', False):
                st.markdown("---")
                st.markdown("### 📝 Create New Account")
                
                with st.form("signup_form"):
                    new_username = st.text_input("Username", placeholder="Choose a username", key="signup_username")
                    new_password = st.text_input("Password", type="password", placeholder="Choose a password (8+ chars)", key="signup_password")
                    confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password", key="signup_confirm")
                    
                    # Security question selection
                    security_questions = [
                        "What was your first pet's name?",
                        "What city were you born in?",
                        "What was your mother's maiden name?",
                        "What was the name of your first school?",
                        "What is your favorite movie?",
                        "What is your dream job?",
                        "What is the name of the street you grew up on?",
                        "What is your favorite book?"
                    ]
                    selected_question = st.selectbox("Security Question", security_questions, key="signup_question")
                    security_answer = st.text_input("Security Answer", placeholder="Your answer", key="signup_answer")
                    
                    signup_button = st.form_submit_button("Create Account", use_container_width=True)
                    
                    if signup_button:
                        if not new_username or not new_password or not confirm_password or not security_answer:
                            st.error("❌ Please fill in all fields")
                        elif new_password != confirm_password:
                            st.error("❌ Passwords don't match")
                        elif len(new_password) < 8:
                            st.error("❌ Password must be at least 8 characters")
                        elif len(new_username) < 3:
                            st.error("❌ Username must be at least 3 characters")
                        else:
                            success, message = create_user(new_username, new_password, selected_question, security_answer)
                            if success:
                                st.success(f"✅ {message}")
                                st.info("You can now login with your new account!")
                                st.session_state.show_signup = False
                            else:
                                st.error(f"❌ {message}")
                
                # Back to login button
                if st.button("← Back to Login", key="back_to_signup"):
                    st.session_state.show_signup = False
                    st.rerun()
            
            # Quick access for personal use
            st.markdown("---")
            st.markdown("### 🚀 Quick Access")
            if st.button("Skip Login (Personal Use)", use_container_width=True, type="secondary"):
                st.session_state.authenticated = True
                st.session_state.username = "demo_user"
                st.success("✅ Quick access enabled! Redirecting...")
                st.rerun()

            st.info("💡 **Personal Use Mode:** Skip login for quick access to your weight tracker")

            # No default users message
            if not load_users():
                st.info("ℹ️ **Multi-User Setup:** Create your first account using the Sign Up button above for secure access!")

    st.stop()  # Stop execution here if not authenticated

# If we get here, user is authenticated
# Ensure username is set before loading data
if st.session_state.username:
    # Load user-specific data
    weight_data = load_data(st.session_state.username)
    user_profile = load_user_profile(st.session_state.username)
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'Dashboard'
    
    # Sidebar (only shown when authenticated)
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
        # Update session state when page changes
        if 'page' not in st.session_state or page != st.session_state.page:
            st.session_state.page = page
        
        st.markdown("### Your Profile")
        st.markdown(f"**Name:** {user_profile['name']}")
        st.markdown(f"**Goal:** {user_profile['goal'].title()}")
        st.markdown(f"**Target:** {user_profile['target_weight']:.1f} kg")
        
        # Profile click to access profile page
        if st.button("Edit Profile", key="edit_profile_btn"):
            st.session_state.page = 'Profile'
            st.rerun()
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", key="sidebar_logout_btn", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()
    
    # Main content (outside sidebar)
    if st.session_state.page == "Dashboard":
        st.markdown("""
        <div class="main-header">
            <h1>Your Fitness Journey</h1>
            <p>Track your progress weekly to stay on target!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Key metrics
        if len(weight_data) > 0:
            # Calculate enhanced metrics
            current_weight = weight_data.iloc[-1]['weight'] if len(weight_data) > 0 else user_profile['current_weight']
            height = user_profile.get('height', 175.0)
            bmi = calculate_bmi(current_weight, height)
            bmi_category, bmi_color = get_bmi_category(bmi)
            days_since_last = calculate_streak(weight_data)
            weekly_change = calculate_weekly_change(weight_data)

            # Progress to goal
            start_weight = weight_data.iloc[0]['weight'] if len(weight_data) > 0 else current_weight
            progress = calculate_progress_to_goal(current_weight, user_profile['target_weight'], start_weight)

            # Quick Add Weight button
            col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
            with col_btn2:
                if st.button("➕ Add Weight", use_container_width=True, type="primary"):
                    st.session_state.page = 'Add Weight'
                    st.rerun()

            # Motivational message
            motivation = get_motivational_message(progress, user_profile['goal'], weekly_change)
            last_entry_date = weight_data.iloc[-1]['date'].strftime('%B %d, %Y') if len(weight_data) > 0 else "No entries yet"

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 1.5rem; border-radius: 16px; color: white; text-align: center; margin: 1rem 0;">
                <h3 style="margin: 0 0 0.5rem 0; font-family: 'Inter', sans-serif; font-weight: 700;">
                    {motivation}
                </h3>
                <p style="margin: 0; opacity: 0.9; font-size: 1.1rem;">
                    Last weigh-in: {last_entry_date} • {days_since_last} days ago
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Enhanced metrics grid
            col1, col2, col3, col4, col5, col6 = st.columns(6)

            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="metric-value">{len(weight_data)}</p>
                    <p class="metric-label">Total Entries</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, {bmi_color}aa 0%, {bmi_color}dd 100%);">
                    <p class="metric-value">{bmi:.1f}</p>
                    <p class="metric-label">BMI ({bmi_category})</p>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                progress_color = "#51cf66" if progress > 75 else "#ffd43b" if progress > 50 else "#ff6b6b"
                st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, {progress_color}aa 0%, {progress_color}dd 100%);">
                    <p class="metric-value">{progress:.0f}%</p>
                    <p class="metric-label">Goal Progress</p>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                change_icon = "📈" if weekly_change > 0 else "📉" if weekly_change < 0 else "➡️"
                change_color = "#ff6b6b" if abs(weekly_change) > 0.5 else "#ffd43b" if abs(weekly_change) > 0.2 else "#51cf66"
                st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, {change_color}aa 0%, {change_color}dd 100%);">
                    <p class="metric-value">{change_icon}</p>
                    <p class="metric-label">{weekly_change:+.2f} kg/week</p>
                </div>
                """, unsafe_allow_html=True)

            with col5:
                streak_color = "#51cf66" if days_since_last <= 3 else "#ffd43b" if days_since_last <= 7 else "#ff6b6b"
                st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, {streak_color}aa 0%, {streak_color}dd 100%);">
                    <p class="metric-value">{days_since_last}</p>
                    <p class="metric-label">Days Since Entry</p>
                </div>
                """, unsafe_allow_html=True)

            with col6:
                weight_range = weight_data['weight'].max() - weight_data['weight'].min()
                st.markdown(f"""
                <div class="metric-card">
                    <p class="metric-value">{weight_range:.1f}</p>
                    <p class="metric-label">Weight Range (kg)</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Show empty state for new users
            st.markdown("""
            <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%); border-radius: 16px; margin: 2rem 0;">
                <h2 style="color: #4a5568; margin-bottom: 1rem;">🎯 Welcome to Your Weight Tracker!</h2>
                <p style="color: #718096; margin-bottom: 2rem;">You don't have any weight entries yet. Start tracking your progress!</p>
                <div style="display: flex; justify-content: center; gap: 1rem;">
                    <a href="#add-weight" style="text-decoration: none;">
                        <button style="background: linear-gradient(135deg, #38b2ac 0%, #4fd1c7 100%); color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; cursor: pointer;">
                            📝 Add Your First Entry
                        </button>
                    </a>
                    <a href="#csv-import" style="text-decoration: none;">
                        <button style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; cursor: pointer;">
                            📁 Import CSV Data
                        </button>
                    </a>
                </div>
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
        
        # Weight trend chart and recent entries (only if data exists)
        if len(weight_data) > 0:
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
        else:
            st.markdown("### 📊 No Data Yet")
            st.info("Start adding weight entries to see your progress charts and recent activity!")
    
    elif st.session_state.page == "Add Weight":
        st.markdown("""
        <div class="main-header">
            <h1>Add Weight Entry</h1>
            <p>Track your weekly progress!</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("add_weight_form"):
            col1, col2 = st.columns(2)
            with col1:
                weight = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=float(user_profile['current_weight']), step=0.1)
            with col2:
                date = st.date_input("Date", value=datetime.now().date(), max_value=datetime.now().date())

            notes = st.text_area("Notes (optional)", placeholder="How are you feeling? Any observations?")

            # Show predicted BMI
            height = user_profile.get('height', 175.0)
            predicted_bmi = calculate_bmi(weight, height)
            bmi_category, bmi_color = get_bmi_category(predicted_bmi)

            st.markdown(f"""
            <div style="background: {bmi_color}22; padding: 1rem; border-radius: 8px; border-left: 4px solid {bmi_color};">
                <strong>Predicted BMI:</strong> {predicted_bmi:.1f} ({bmi_category})
            </div>
            """, unsafe_allow_html=True)

            if st.form_submit_button("Add Entry", use_container_width=True):
                # Validation
                validation_errors = []

                # Check for reasonable weight changes
                if len(weight_data) > 0:
                    last_weight = weight_data.iloc[-1]['weight']
                    weight_diff = abs(weight - last_weight)
                    if weight_diff > 5.0:  # More than 5kg change
                        validation_errors.append(f"⚠️ Large weight change detected: {weight_diff:.1f}kg from last entry")

                # Check for future dates
                if date > datetime.now().date():
                    validation_errors.append("⚠️ Cannot add entries for future dates")

                # Check for duplicate dates
                if len(weight_data) > 0 and date in weight_data['date'].dt.date.values:
                    validation_errors.append("⚠️ Entry for this date already exists")

                if validation_errors:
                    for error in validation_errors:
                        st.error(error)
                    st.info("💡 If this is correct, please double-check your input")
                else:
                    new_entry = pd.DataFrame({
                        'date': [date],
                        'weight': [weight],
                        'notes': [notes],
                        'goal': [user_profile['goal']]
                    })

                    weight_data = pd.concat([weight_data, new_entry], ignore_index=True)
                    weight_data = weight_data.sort_values('date')  # Keep sorted by date
                    save_data(weight_data, st.session_state.username)

                    # Update current weight in profile
                    user_profile['current_weight'] = weight
                    save_user_profile(user_profile, st.session_state.username)

                    st.success("✅ Weight entry added successfully!")
                    st.rerun()

        # Bulk entry section
        st.markdown("### 📊 Bulk Data Entry")
        with st.expander("📋 Quick Multi-Entry (Coming Soon)"):
            st.info("💡 Feature in development: Upload CSV files or enter multiple entries at once.")

            # CSV upload placeholder
            uploaded_file = st.file_uploader("Upload Weight Data CSV", type="csv", disabled=True)
            st.markdown("""
            **Expected CSV format:**
            ```
            date,weight,notes
            2024-01-01,75.5,Feeling good
            2024-01-02,75.3,Morning workout
            ```
            """)

            if st.button("📤 Export Template CSV", disabled=True):
                pass
    
    elif st.session_state.page == "Analytics":
        st.markdown("""
        <div class="main-header">
            <h1>Analytics & Insights</h1>
            <p>Deep dive into your weight tracking data</p>
        </div>
        """, unsafe_allow_html=True)
        
        if len(weight_data) > 0:
            # Time range selector
            col1, col2 = st.columns([1, 3])
            with col1:
                time_range = st.selectbox("Time Range", ["All Time", "Last 3 Months", "Last 6 Months", "Last Year"], key="time_range")
            
            # Filter data based on time range
            if time_range == "Last 3 Months":
                filtered_data = weight_data[weight_data['date'] >= (datetime.now() - timedelta(days=90)).date()]
            elif time_range == "Last 6 Months":
                filtered_data = weight_data[weight_data['date'] >= (datetime.now() - timedelta(days=180)).date()]
            elif time_range == "Last Year":
                filtered_data = weight_data[weight_data['date'] >= (datetime.now() - timedelta(days=365)).date()]
            else:
                filtered_data = weight_data
            
            # Enhanced analytics
            st.markdown("### 📈 Advanced Weight Analysis")

            # Calculate moving averages
            filtered_data = filtered_data.sort_values('date')
            if len(filtered_data) >= 7:
                filtered_data['7_day_avg'] = filtered_data['weight'].rolling(window=7, min_periods=1).mean()
            if len(filtered_data) >= 30:
                filtered_data['30_day_avg'] = filtered_data['weight'].rolling(window=30, min_periods=1).mean()

            # Weight trend chart with moving averages
            fig = go.Figure()

            # Main weight line
            fig.add_trace(go.Scatter(
                x=filtered_data['date'],
                y=filtered_data['weight'],
                mode='lines+markers',
                name='Actual Weight',
                line=dict(color='#38b2ac', width=3),
                marker=dict(size=6)
            ))

            # 7-day moving average
            if '7_day_avg' in filtered_data.columns:
                fig.add_trace(go.Scatter(
                    x=filtered_data['date'],
                    y=filtered_data['7_day_avg'],
                    mode='lines',
                    name='7-Day Average',
                    line=dict(color='#667eea', width=2, dash='dash'),
                    opacity=0.8
                ))

            # 30-day moving average
            if '30_day_avg' in filtered_data.columns:
                fig.add_trace(go.Scatter(
                    x=filtered_data['date'],
                    y=filtered_data['30_day_avg'],
                    mode='lines',
                    name='30-Day Average',
                    line=dict(color='#f093fb', width=2, dash='dot'),
                    opacity=0.7
                ))

            # Goal line
            fig.add_hline(
                y=user_profile['target_weight'],
                line_dash="dash",
                line_color="#ff6b6b",
                annotation_text="Target Weight",
                annotation_position="bottom right"
            )

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', size=12),
                height=500,
                showlegend=True,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                )
            )
            fig.update_xaxes(title_text="Date")
            fig.update_yaxes(title_text="Weight (kg)")

            st.plotly_chart(fig, use_container_width=True)

            # Statistics summary
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_change = filtered_data.iloc[-1]['weight'] - filtered_data.iloc[0]['weight'] if len(filtered_data) > 1 else 0
                st.metric("Total Change", f"{total_change:+.1f} kg")
            with col2:
                avg_weekly_change = calculate_weekly_change(filtered_data)
                st.metric("Weekly Rate", f"{avg_weekly_change:+.2f} kg/week")
            with col3:
                volatility = filtered_data['weight'].std() if len(filtered_data) > 1 else 0
                st.metric("Weight Volatility", f"{volatility:.2f} kg")
            with col4:
                days_tracking = (filtered_data['date'].max() - filtered_data['date'].min()).days if len(filtered_data) > 1 else 0
                st.metric("Days Tracked", f"{days_tracking} days")

            # Simple trend prediction
            if len(filtered_data) >= 7:
                st.markdown("### 🔮 Trend Prediction")

                # Calculate trend over last 4 weeks
                recent_weeks = filtered_data.tail(28)
                if len(recent_weeks) >= 7:
                    weekly_rate = calculate_weekly_change(recent_weeks)

                    # Predict 4 weeks ahead
                    current_weight = filtered_data.iloc[-1]['weight']
                    predicted_4weeks = current_weight + (weekly_rate * 4)

                    # Time to goal
                    target = user_profile['target_weight']
                    if abs(weekly_rate) > 0.1:  # Only if meaningful change
                        weeks_to_goal = abs(target - current_weight) / abs(weekly_rate)
                        months_to_goal = weeks_to_goal / 4.33

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Predicted Weight (4 weeks)", f"{predicted_4weeks:.1f} kg")
                        with col2:
                            if months_to_goal < 24:  # Only show if reasonable
                                st.metric("Estimated Time to Goal", f"{months_to_goal:.1f} months")
                            else:
                                st.metric("Estimated Time to Goal", "Adjust rate")
                        with col3:
                            weekly_needed = (target - current_weight) / 12  # 3 months
                            st.metric("Weekly Rate Needed", f"{weekly_needed:+.2f} kg/week")

                        # Progress visualization
                        progress_data = pd.DataFrame({
                            'weeks': [0, 4, 8, 12],
                            'predicted': [current_weight,
                                        current_weight + weekly_rate * 4,
                                        current_weight + weekly_rate * 8,
                                        current_weight + weekly_rate * 12],
                            'target': [target] * 4
                        })

                        fig_pred = px.line(progress_data, x='weeks', y=['predicted', 'target'],
                                         title="12-Week Projection",
                                         labels={'weeks': 'Weeks Ahead', 'value': 'Weight (kg)'})
                        fig_pred.update_layout(height=300)
                        st.plotly_chart(fig_pred, use_container_width=True)
                else:
                    st.info("📈 Add more data points for trend predictions")
            
            # Enhanced Export Options
            st.markdown("### 📤 Export Data")
            col1, col2, col3 = st.columns(3)

            with col1:
                # CSV Export
                csv_data = weight_data.to_csv(index=False)
                st.download_button(
                    label="📄 Download CSV",
                    data=csv_data,
                    file_name=f"weight_data_{st.session_state.username}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            with col2:
                # JSON Export
                json_data = weight_data.to_json(orient='records', date_format='iso')
                st.download_button(
                    label="🗂️ Download JSON",
                    data=json_data,
                    file_name=f"weight_data_{st.session_state.username}_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True
                )

            with col3:
                # Excel-compatible CSV Export
                excel_data = weight_data.copy()
                excel_data['date'] = excel_data['date'].dt.strftime('%Y-%m-%d')
                excel_csv = excel_data.to_csv(index=False, sep=';')  # Excel likes semicolons
                st.download_button(
                    label="📊 Download Excel CSV",
                    data=excel_csv,
                    file_name=f"weight_data_excel_{st.session_state.username}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.info("📊 No data to analyze yet. Add some weight entries first!")
    
    elif st.session_state.page == "Profile":
        st.markdown("""
        <div class="main-header">
            <h1>Your Profile</h1>
            <p>Manage your account and preferences</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Personal Information")
            with st.form("profile_form"):
                name = st.text_input("Name", value=user_profile['name'])

                col1a, col1b = st.columns(2)
                with col1a:
                    height = st.number_input("Height (cm)", min_value=120.0, max_value=250.0,
                                           value=float(user_profile.get('height', 175.0)), step=0.5)
                with col1b:
                    target_weight = st.number_input("Target Weight (kg)", min_value=30.0, max_value=300.0,
                                                   value=float(user_profile['target_weight']), step=0.1)

                goal = st.selectbox(
                    "Fitness Goal",
                    ['maintenance', 'weight_loss', 'weight_gain', 'reverse_goal'],
                    index=['maintenance', 'weight_loss', 'weight_gain', 'reverse_goal'].index(user_profile['goal']),
                    format_func=lambda x: {
                        'maintenance': '⚖️ Maintenance - Maintain current weight',
                        'weight_loss': '📉 Weight Loss - Lose weight gradually',
                        'weight_gain': '📈 Weight Gain - Gain weight for muscle',
                        'reverse_goal': '🔄 Reverse Diet - Gradual weight gain'
                    }[x]
                )

                # Show current BMI
                if len(weight_data) > 0:
                    current_weight = weight_data.iloc[-1]['weight']
                    current_bmi = calculate_bmi(current_weight, height)
                    target_bmi = calculate_bmi(target_weight, height)

                    st.markdown(f"""
                    **Current BMI:** {current_bmi:.1f} | **Target BMI:** {target_bmi:.1f}
                    """)

                if st.form_submit_button("Update Profile", use_container_width=True):
                    user_profile['name'] = name
                    user_profile['goal'] = goal
                    user_profile['target_weight'] = target_weight
                    user_profile['height'] = height
                    save_user_profile(user_profile, st.session_state.username)
                    st.success("✅ Profile updated successfully!")
                    st.rerun()
        
        with col2:
            st.markdown("### Change Password")
            with st.form("change_password_form"):
                current_password = st.text_input("Current Password", type="password")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
                
                if st.form_submit_button("Change Password", use_container_width=True):
                    if new_password != confirm_password:
                        st.error("❌ New passwords don't match")
                    elif len(new_password) < 8:
                        st.error("❌ Password must be at least 8 characters")
                    elif check_credentials(st.session_state.username, current_password):
                        if change_user_password(st.session_state.username, new_password):
                            st.success("✅ Password changed successfully!")
                        else:
                            st.error("❌ Failed to change password")
                    else:
                        st.error("❌ Current password is incorrect")
            
            st.markdown("### Data Management")
            if st.button("🗑️ Clear All Data", use_container_width=True, type="secondary"):
                if st.button("⚠️ Confirm Deletion", key="confirm_delete"):
                    # Delete user-specific files
                    try:
                        os.remove(f"weight_data_{st.session_state.username}.csv")
                        os.remove(f"user_profile_{st.session_state.username}.json")
                        st.success("✅ All data cleared successfully!")
                        st.rerun()
                    except FileNotFoundError:
                        st.info("ℹ️ No data files to delete")
            
            # CSV Export
            if len(weight_data) > 0:
                csv_data = weight_data.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=f"weight_data_{st.session_state.username}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
else:
    # This shouldn't happen, but just in case
    st.error("❌ Authentication error. Please login again.")
    st.session_state.authenticated = False
    st.rerun()

# Logout button in top right
col1, col2 = st.columns([4, 1])
with col2:
    if st.button("🚪 Logout", key="top_logout_btn"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()

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
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(56, 178, 172, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(56, 178, 172, 0.4);
    }
    
    .stSelectbox > div > div {
        background: white;
        border: 2px solid #e2e8f0;
    }

    /* Mobile responsiveness */
    @media screen and (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem !important;
        }

        .metric-card {
            margin-bottom: 1rem;
        }

        .metric-value {
            font-size: 1.8rem !important;
        }

        .metric-label {
            font-size: 0.9rem !important;
        }

        /* Stack columns on mobile */
        .stColumns > div {
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }
    }

    @media screen and (max-width: 480px) {
        .main-header {
            padding: 1rem !important;
        }

        .main-header h1 {
            font-size: 1.5rem !important;
        }

        .metric-value {
            font-size: 1.5rem !important;
        }
    }

    /* Improve form styling */
    .stNumberInput > div > div > input {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
    }

    .stTextInput > div > div > input {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
    }

    .stTextArea > div > div > textarea {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
    }

    /* Enhance buttons */
    .stButton > button {
        transition: all 0.3s ease !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(56, 178, 172, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)
