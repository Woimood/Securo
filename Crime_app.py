import streamlit as st
import datetime
import json
import requests
import matplotlib.pyplot as plt
import pandas as pd
import folium
from streamlit_folium import folium_static
import hashlib
import time
import os
import google.generativeai as genai
import io
import base64
from PIL import Image

# Configure Google AI
GOOGLE_API_KEY = "AIzaSyBlAiRqnNHmm-Hfu8dCAx6dlVMROQ-c180"
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the AI model
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(
    page_title="SECURO - Crime Mitigation AI Chat Bot",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🤖",
    menu_items=None
)

# Enhanced CSS with improved login screen layout and background image support
st.markdown("""
<style>
    /* Black theme with Times New Roman font */
    .main, .main .block-container, .stApp, [data-testid="stAppViewContainer"] {
        background-color: #000000 !important;
        color: #ffffff !important;
        font-family: 'Times New Roman', Times, serif !important;
        padding-top: 2rem !important;
    }

    /* Login page specific styling with background image */
    .login-page {
        background: linear-gradient(135deg, rgba(0, 0, 0, 0.8) 0%, rgba(26, 26, 26, 0.9) 50%, rgba(0, 0, 0, 0.8) 100%) !important;
        min-height: 100vh !important;
        position: relative !important;
        overflow: hidden !important;
    }

    /* Background image overlay */
    .login-page::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: var(--login-bg-image);
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        opacity: 0.3;
        z-index: 0;
    }

    /* Login background overlay with crime scene effect */
    .login-page::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle at center, rgba(255, 255, 0, 0.05) 0%, rgba(0, 0, 0, 0.7) 70%);
        z-index: 1;
    }

    /* Login content wrapper */
    .login-content {
        position: relative !important;
        z-index: 2 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 100vh !important;
        padding: 2rem !important;
    }

    /* Logo container with enhanced styling */
    .logo-container {
        text-align: center !important;
        margin-bottom: 2rem !important;
        background: rgba(26, 26, 26, 0.95) !important;
        padding: 2rem !important;
        border-radius: 20px !important;
        border: 3px solid #FFFF00 !important;
        box-shadow: 0 0 30px rgba(255, 255, 0, 0.3) !important;
        backdrop-filter: blur(15px) !important;
        max-width: 500px !important;
        width: 100% !important;
        position: relative !important;
        z-index: 3 !important;
    }

    /* Logo image styling */
    .logo-image {
        max-width: 300px !important;
        width: 100% !important;
        height: auto !important;
        border-radius: 15px !important;
        border: 2px solid #FFFF00 !important;
        box-shadow: 0 8px 25px rgba(255, 255, 0, 0.2) !important;
        margin-bottom: 1rem !important;
    }

    /* SECURO title styling */
    .securo-login-title {
        color: #FFFF00 !important;
        font-size: 3.5rem !important;
        font-weight: bold !important;
        text-align: center !important;
        text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.9) !important;
        margin: 0.5rem 0 !important;
        letter-spacing: 4px !important;
        font-family: 'Times New Roman', Times, serif !important;
    }

    /* Subtitle styling */
    .login-subtitle {
        color: #ffffff !important;
        font-size: 1.3rem !important;
        text-align: center !important;
        margin-bottom: 1rem !important;
        font-weight: 500 !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8) !important;
    }

    /* Login form container */
    .login-form-container {
        background: rgba(26, 26, 26, 0.95) !important;
        padding: 3rem !important;
        border-radius: 20px !important;
        border: 2px solid #FFFF00 !important;
        max-width: 450px !important;
        width: 100% !important;
        box-shadow: 0 15px 35px rgba(255, 255, 0, 0.3) !important;
        backdrop-filter: blur(15px) !important;
        margin-top: 2rem !important;
        position: relative !important;
        z-index: 3 !important;
    }

    /* Crime scene tape effect */
    .crime-tape {
        background: repeating-linear-gradient(
            45deg,
            #FFFF00,
            #FFFF00 15px,
            #000000 15px,
            #000000 30px
        ) !important;
        height: 10px !important;
        margin: 1.5rem 0 !important;
        border: 1px solid #000000 !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.5) !important;
    }

    /* Security warning */
    .security-warning {
        background: rgba(139, 0, 0, 0.9) !important;
        padding: 20px !important;
        border-radius: 12px !important;
        border: 2px solid #FF0000 !important;
        margin: 20px 0 !important;
        text-align: center !important;
        box-shadow: 0 8px 25px rgba(255, 0, 0, 0.2) !important;
        position: relative !important;
        z-index: 3 !important;
    }

    .security-warning h3 {
        color: #FFFF00 !important;
        margin: 0 0 10px 0 !important;
        font-size: 1.5rem !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8) !important;
    }

    .security-warning p {
        color: #ffffff !important;
        margin: 5px 0 !important;
        font-size: 1rem !important;
    }

    /* Chart container styling */
    .chart-container {
        background-color: #1a1a1a !important;
        border: 2px solid #333333 !important;
        border-radius: 15px !important;
        padding: 20px !important;
        margin: 20px 0 !important;
        box-shadow: 0 8px 32px rgba(255, 255, 0, 0.1) !important;
    }

    /* Professional chart title */
    .chart-title {
        color: #FFFF00 !important;
        font-size: 1.5rem !important;
        font-weight: bold !important;
        text-align: center !important;
        margin-bottom: 15px !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8) !important;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a !important;
        border-right: 1px solid #333333 !important;
    }
   
    /* Sidebar content styling */
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
        font-family: 'Times New Roman', Times, serif !important;
    }
   
    /* Menu button styling */
    .menu-button {
        position: fixed;
        top: 1rem;
        left: 1rem;
        z-index: 999;
        background: #1a1a1a !important;
        border: 1px solid #333333 !important;
        border-radius: 6px !important;
        padding: 8px 12px !important;
        color: #ffffff !important;
        font-family: 'Times New Roman', Times, serif !important;
        cursor: pointer;
    }
   
    /* Clean header */
    h1 {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 2.5rem !important;
        text-align: center !important;
        margin-bottom: 0.5rem !important;
        font-family: 'Times New Roman', Times, serif !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8) !important;
    }
   
    h2, h3 {
        color: #ffffff !important;
        font-weight: 500 !important;
        font-family: 'Times New Roman', Times, serif !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8) !important;
    }
   
    /* Fix chat message containers */
    .chat-message {
        margin-bottom: 1rem !important;
        clear: both !important;
        overflow: hidden !important;
    }
   
    /* User message styling */
    .user-message {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 1rem;
        clear: both;
    }
   
    .user-bubble {
        background: #ffffff !important;
        color: #000000 !important;
        padding: 12px 16px !important;
        border-radius: 18px 18px 4px 18px !important;
        max-width: 70% !important;
        word-wrap: break-word !important;
        font-family: 'Times New Roman', Times, serif !important;
        font-size: 15px !important;
        line-height: 1.4 !important;
        box-shadow: 0 2px 8px rgba(255, 255, 255, 0.2) !important;
        display: inline-block !important;
        text-align: left !important;
    }
   
    /* Bot message styling */
    .bot-message {
        display: flex;
        justify-content: flex-start;
        margin-bottom: 1rem;
        clear: both;
    }
   
    .bot-bubble {
        background: #2c2c2c !important;
        color: #ffffff !important;
        padding: 12px 16px !important;
        border-radius: 18px 18px 18px 4px !important;
        max-width: 75% !important;
        word-wrap: break-word !important;
        font-family: 'Times New Roman', Times, serif !important;
        font-size: 15px !important;
        line-height: 1.4 !important;
        box-shadow: 0 2px 8px rgba(255, 255, 255, 0.1) !important;
        display: inline-block !important;
        text-align: left !important;
    }
   
    /* Emergency contact styling */
    .emergency-contact {
        background: #8B0000 !important;
        color: #ffffff !important;
        padding: 10px !important;
        border-radius: 8px !important;
        margin: 5px 0 !important;
        text-align: center !important;
        font-weight: bold !important;
    }
   
    .emergency-contact:hover {
        background: #A0522D !important;
        cursor: pointer !important;
    }
   
    /* Chat input styling */
    .stChatInput > div {
        background-color: #1a1a1a !important;
        border: 1px solid #333333 !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 6px rgba(255, 255, 255, 0.05) !important;
    }
   
    .stChatInput input {
        background-color: transparent !important;
        color: #ffffff !important;
        font-family: 'Times New Roman', Times, serif !important;
        border: none !important;
        font-size: 16px !important;
    }
   
    .stChatInput input::placeholder {
        color: #888888 !important;
    }
   
    /* Buttons styling */
    .stButton > button {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
        border-radius: 6px !important;
        font-family: 'Times New Roman', Times, serif !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
        width: 100% !important;
    }
   
    .stButton > button:hover {
        background-color: #333333 !important;
        border-color: #555555 !important;
    }

    /* Emergency button styling */
    .emergency-btn {
        background-color: #8B0000 !important;
        color: #ffffff !important;
        border: 2px solid #FF0000 !important;
    }

    .emergency-btn:hover {
        background-color: #FF0000 !important;
        border-color: #FF4444 !important;
    }
   
    /* Center subtitle */
    .subtitle {
        text-align: center;
        color: #FFFF00 !important;
        margin-bottom: 2rem;
        font-family: 'Times New Roman', Times, serif !important;
        font-weight: bold !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8) !important;
        font-size: 1.2rem !important;
    }
   
    /* Hide default streamlit elements */
    .stChatMessage {
        display: none !important;
    }
   
    /* Center container */
    .main .block-container {
        max-width: 48rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Main header styling for login */
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }

    /* Crime map container */
    .crime-map-container {
        background-color: #1a1a1a !important;
        border: 2px solid #333333 !important;
        border-radius: 10px !important;
        padding: 20px !important;
        margin: 20px 0 !important;
    }

    /* Enhanced magnifying glass celebration animation */
    @keyframes magnifySearch {
        0% {
            transform: translateY(100vh) scale(0.5) rotate(0deg);
            opacity: 0;
        }
        20% {
            opacity: 1;
        }
        50% {
            transform: translateY(30vh) scale(1.2) rotate(180deg);
            opacity: 1;
        }
        80% {
            transform: translateY(-10vh) scale(0.8) rotate(360deg);
            opacity: 0.8;
        }
        100% {
            transform: translateY(-20vh) scale(0.3) rotate(540deg);
            opacity: 0;
        }
    }

    .magnify-celebration {
        position: fixed;
        font-size: 2rem;
        z-index: 9999;
        pointer-events: none;
        animation: magnifySearch 4s ease-out forwards;
    }

    /* Vary the animation timing for different magnifying glasses */
    .magnify-1 { animation-delay: 0s; left: 10%; }
    .magnify-2 { animation-delay: 0.3s; left: 20%; }
    .magnify-3 { animation-delay: 0.6s; left: 30%; }
    .magnify-4 { animation-delay: 0.9s; left: 40%; }
    .magnify-5 { animation-delay: 1.2s; left: 50%; }
    .magnify-6 { animation-delay: 1.5s; left: 60%; }
    .magnify-7 { animation-delay: 1.8s; left: 70%; }
    .magnify-8 { animation-delay: 2.1s; left: 80%; }
    .magnify-9 { animation-delay: 2.4s; left: 90%; }
    .magnify-10 { animation-delay: 2.7s; left: 85%; }
    .magnify-11 { animation-delay: 3.0s; left: 75%; }
    .magnify-12 { animation-delay: 3.3s; left: 65%; }
    .magnify-13 { animation-delay: 3.6s; left: 55%; }
    .magnify-14 { animation-delay: 3.9s; left: 45%; }
    .magnify-15 { animation-delay: 4.2s; left: 35%; }
</style>
""", unsafe_allow_html=True)

class SecuroCrimeCharts:
    """Enhanced crime chart generation for SECURO criminology chatbot"""
   
    def __init__(self):
        # Professional color scheme for law enforcement
        self.colors = {
            'violent': '#E63946',      # Red for violent crimes
            'property': '#F1A208',     # Orange for property crimes  
            'drug': '#457B9D',         # Blue for drug offenses
            'white_collar': '#2A9D8F', # Teal for white collar
            'cyber': '#6F2DA8',        # Purple for cybercrimes
            'traffic': '#BDBDBD',      # Gray for traffic violations
            'other': '#95A5A6'         # Light gray for other
        }

    def generate_crime_distribution_chart(self, crime_data, year="2024", chart_type="pie"):
        """Generate professional crime distribution chart for law enforcement"""
        if year not in crime_data:
            return None, f"Crime statistics for {year} are not available."
           
        data = crime_data[year]["by_category"]
        labels = list(data.keys())
        values = list(data.values())
       
        # Create figure with professional styling
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor('black')
       
        if chart_type == "pie":
            # Professional pie chart
            colors = [self.colors.get(label.lower().replace(' ', '_').replace('crimes', ''), '#95A5A6')
                     for label in labels]
           
            wedges, texts, autotexts = ax.pie(
                values,
                labels=labels,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                explode=[0.05] * len(labels),  # Slight separation
                shadow=True,
                textprops={'color': 'white', 'fontsize': 11, 'weight': 'bold'}
            )
           
            # Enhance text readability
            for autotext in autotexts:
                autotext.set_color('black')
                autotext.set_weight('bold')
                autotext.set_fontsize(10)
               
            ax.set_title(f'Crime Distribution Analysis - {year}\nSt. Kitts & Nevis',
                        color='white', fontsize=16, pad=20, weight='bold')
                       
        elif chart_type == "bar":
            # Professional bar chart
            colors = [self.colors.get(label.lower().replace(' ', '_').replace('crimes', ''), '#95A5A6')
                     for label in labels]
           
            bars = ax.bar(labels, values, color=colors, alpha=0.8, edgecolor='white', linewidth=1)
           
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                       f'{int(height)}', ha='center', va='bottom',
                       color='white', fontweight='bold', fontsize=10)
           
            ax.set_title(f'Crime Statistics Breakdown - {year}\nSt. Kitts & Nevis',
                        color='white', fontsize=16, pad=20, weight='bold')
            ax.set_ylabel('Number of Reported Cases', color='white', fontsize=12)
            ax.tick_params(colors='white', rotation=45)
           
            # Style the axes
            for spine in ax.spines.values():
                spine.set_color('white')
       
        ax.set_facecolor('black')
       
        # Add professional footer with timestamp
        fig.text(0.5, 0.02, f'SECURO Intelligence System | Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} | CONFIDENTIAL',
                ha='center', va='bottom', color='yellow', fontsize=8, weight='bold')
       
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.1)
       
        return fig, f"**CRIME STATISTICS FOR {year}**\n\nTotal Reported Crimes: {crime_data[year]['total_reported']}\nChart generated showing distribution and breakdown by category."

    def generate_trend_analysis(self, crime_data, years=["2022", "2023", "2024"]):
        """Generate multi-year trend analysis chart"""
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(14, 8))
        fig.patch.set_facecolor('black')
       
        # Get common crime types across all years
        common_types = ["Violent Crimes", "Property Crimes", "Drug Offenses", "Cybercrimes"]
        available_years = [year for year in years if year in crime_data]
       
        if not available_years:
            return None, "No data available for the requested years."
       
        x = range(len(available_years))
        width = 0.2
       
        for i, crime_type in enumerate(common_types):
            values = []
            for year in available_years:
                if crime_type in crime_data[year]["by_category"]:
                    values.append(crime_data[year]["by_category"][crime_type])
                else:
                    values.append(0)
           
            color = list(self.colors.values())[i]
            ax.bar([pos + width * i for pos in x], values, width,
                  label=f'{crime_type}', color=color, alpha=0.8)
       
        ax.set_xlabel('Year', color='white', fontsize=12)
        ax.set_ylabel('Number of Cases', color='white', fontsize=12)
        ax.set_title('Crime Trend Analysis - Multi-Year Comparison\nSt. Kitts & Nevis',
                    color='white', fontsize=16, pad=20, weight='bold')
        ax.set_xticks([pos + width * 1.5 for pos in x])
        ax.set_xticklabels(available_years)
        ax.legend(facecolor='black', edgecolor='white', labelcolor='white')
       
        # Style the chart
        ax.set_facecolor('black')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('white')
       
        # Professional footer
        fig.text(0.5, 0.02, f'SECURO Intelligence System | Trend Analysis | Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} | CONFIDENTIAL',
                ha='center', va='bottom', color='yellow', fontsize=8, weight='bold')
       
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.1)
       
        return fig, f"**TREND ANALYSIS COMPLETE**\n\nMulti-year comparison for {', '.join(available_years)} showing trends across major crime categories."

    def generate_hotspot_chart(self, location_data=None):
        """Generate crime hotspot analysis chart"""
        if location_data is None:
            # Sample hotspot data
            location_data = {
                "Basseterre Central": 450,
                "Charlestown": 200,
                "Frigate Bay": 180,
                "Sandy Point": 120,
                "Dieppe Bay": 90
            }
       
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor('black')
       
        locations = list(location_data.keys())
        crimes = list(location_data.values())
       
        # Color code by crime level
        colors = []
        for crime_count in crimes:
            if crime_count >= 400:
                colors.append('#E63946')  # High risk - Red
            elif crime_count >= 200:
                colors.append('#F1A208')  # Medium risk - Orange
            else:
                colors.append('#2A9D8F')  # Low risk - Green
       
        bars = ax.barh(locations, crimes, color=colors, alpha=0.8, edgecolor='white')
       
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            risk_level = "HIGH" if crimes[i] >= 400 else "MEDIUM" if crimes[i] >= 200 else "LOW"
            ax.text(width + 10, bar.get_y() + bar.get_height()/2,
                   f'{crimes[i]} ({risk_level})', ha='left', va='center',
                   color='white', fontweight='bold')
       
        ax.set_xlabel('Number of Incidents', color='white', fontsize=12)
        ax.set_title('Crime Hotspot Analysis - Geographic Distribution\nSt. Kitts & Nevis',
                    color='white', fontsize=16, pad=20, weight='bold')
       
        # Style the chart
        ax.set_facecolor('black')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('white')
       
        # Add legend
        legend_elements = [
            plt.Rectangle((0,0),1,1, facecolor='#E63946', label='High Risk (400+)'),
            plt.Rectangle((0,0),1,1, facecolor='#F1A208', label='Medium Risk (200-399)'),
            plt.Rectangle((0,0),1,1, facecolor='#2A9D8F', label='Low Risk (<200)')
        ]
        ax.legend(handles=legend_elements, loc='lower right', facecolor='black',
                 edgecolor='white', labelcolor='white')
       
        # Professional footer
        fig.text(0.5, 0.02, f'SECURO Intelligence System | Hotspot Analysis | Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} | CONFIDENTIAL',
                ha='center', va='bottom', color='yellow', fontsize=8, weight='bold')
       
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.15)
       
        return fig, "**HOTSPOT ANALYSIS COMPLETE**\n\nGeographic crime distribution analysis showing risk levels by location."

class UserAuthentication:
    """Enhanced authentication system combining both login styles"""
    def __init__(self):
        if "users_db" not in st.session_state:
            st.session_state.users_db = {}
       
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
   
    def create_account(self, username, password, role, badge_number="", department=""):
        """Create new professional user account"""
        if username in st.session_state.users_db:
            return False, "Username already exists"
       
        if len(password) < 8:
            return False, "Password must be at least 8 characters for security"
       
        st.session_state.users_db[username] = {
            "password": self.hash_password(password),
            "role": role,
            "badge_number": badge_number if badge_number else "",
            "department": department if department else "",
            "created": datetime.datetime.now().isoformat(),
            "access_level": self.get_access_level(role)
        }
        return True, "Professional account created successfully"
   
    def get_access_level(self, role):
        levels = {
            "Senior Criminologist": 5,
            "Detective": 4,
            "Police Officer": 3,
            "Forensic Specialist": 4,
            "Legal Advisor": 4,
            "Researcher": 2,
            "Student": 1
        }
        return levels.get(role, 1)
   
    def login(self, username, password):
        """Enhanced login with demo credentials support"""
        # Check demo credentials first
        demo_users = {
            "admin": "password",
            "demo": "demo123",
        }
       
        if username in demo_users and demo_users[username] == password:
            st.session_state.logged_in = True
            st.session_state.current_user = username
            st.session_state.user_role = "Demo User" if username == "demo" else "Administrator"
            st.session_state.access_level = 5 if username == "admin" else 3
            st.session_state.badge_number = "DEMO-001" if username == "demo" else "ADMIN-001"
            st.session_state.department = "Demo Department"
            return True, "Demo access granted"
       
        # Check registered users
        if username not in st.session_state.users_db:
            return False, "Professional credentials not found"
       
        if st.session_state.users_db[username]["password"] != self.hash_password(password):
            return False, "Invalid credentials"
       
        user_data = st.session_state.users_db[username]
        st.session_state.logged_in = True
        st.session_state.current_user = username
        st.session_state.user_role = user_data["role"]
        st.session_state.access_level = user_data["access_level"]
        st.session_state.badge_number = user_data.get("badge_number", "")
        st.session_state.department = user_data.get("department", "")
        return True, "Professional access granted"

class GeminiAPI:
    def __init__(self):
        # Using Google AI SDK instead of REST API
        self.model = model
       
    def get_gemini_response(self, prompt):
        try:
            # Using the Google AI SDK generate_content method
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Lower temperature for more professional responses
                    top_k=40,
                    top_p=0.95,
                    max_output_tokens=2048,  # Increased for detailed responses
                )
            )
           
            if response.text:
                return response.text
            else:
                return "I apologize, but I couldn't generate a response. Please rephrase your professional inquiry."
               
        except Exception as e:
            return f"Connection Error - Unable to process request: {str(e)}"

class CriminologyProfessionalBot:
    def __init__(self):
        self.gemini_api = GeminiAPI()
        self.charts = SecuroCrimeCharts()  # Initialize chart generator
       
        # Professional contact directory for St. Kitts & Nevis
        self.professional_contacts = {
            "police_hq": {
                "name": "Royal St. Christopher and Nevis Police Force HQ",
                "phone": "(869) 465-2241",
                "email": "info@police.kn",
                "address": "Cayon Street, Basseterre",
                "departments": ["CID", "Traffic", "Community Policing", "Narcotics"]
            },
            "forensics": {
                "name": "Police Forensic Unit",
                "phone": "(869) 465-2241 ext. 234",
                "specialties": ["DNA Analysis", "Ballistics", "Digital Forensics", "Crime Scene Processing"]
            },
            "courts": {
                "high_court": {
                    "name": "Eastern Caribbean Supreme Court - St. Kitts Circuit",
                    "phone": "(869) 465-2366",
                    "address": "Government Road, Basseterre"
                },
                "magistrate": {
                    "name": "Magistrate's Court",
                    "phone": "(869) 465-2521",
                    "sessions": ["Criminal", "Civil", "Traffic"]
                }
            },
            "dpp": {
                "name": "Director of Public Prosecutions Office",
                "phone": "(869) 467-1000",
                "services": ["Case Review", "Legal Advice", "Prosecution Oversight"]
            }
        }

        # Legal framework for St. Kitts & Nevis
        self.legal_framework = {
            "primary_legislation": {
                "criminal_code": {
                    "title": "Criminal Code (St. Christopher and Nevis)",
                    "key_sections": {
                        "homicide": "Sections 87-102",
                        "assault": "Sections 56-74",
                        "theft": "Sections 201-250",
                        "fraud": "Sections 251-280",
                        "drug_offenses": "Drug Prevention of Misuse Act",
                        "domestic_violence": "Domestic Violence Act 2020"
                    }
                },
                "evidence_act": {
                    "title": "Evidence Act",
                    "key_provisions": ["Admissibility Rules", "Chain of Custody", "Expert Testimony"]
                }
            },
            "recent_amendments": [
                {
                    "date": "2023-03-15",
                    "act": "Cybercrime Act 2023",
                    "summary": "New provisions for digital evidence and online offenses"
                },
                {
                    "date": "2022-11-20",
                    "act": "Criminal Justice Reform Act 2022",
                    "summary": "Updated sentencing guidelines and plea bargaining procedures"
                }
            ]
        }

        # Crime investigation protocols
        self.investigation_protocols = {
            "crime_scene": {
                "initial_response": [
                    "Secure the perimeter",
                    "Document initial observations",
                    "Identify and separate witnesses",
                    "Call for appropriate specialists",
                    "Establish command post"
                ],
                "documentation": [
                    "Photography (wide, medium, close-up)",
                    "Sketch mapping",
                    "Evidence log",
                    "Witness statements",
                    "Environmental conditions"
                ]
            },
            "evidence_handling": {
                "collection": [
                    "Use appropriate collection tools",
                    "Maintain chain of custody",
                    "Proper packaging and labeling",
                    "Document location and condition",
                    "Witness the collection process"
                ],
                "storage": [
                    "Climate-controlled environment",
                    "Secure access controls",
                    "Regular inventory checks",
                    "Proper documentation",
                    "Contamination prevention"
                ]
            }
        }

        # Case management templates
        self.case_templates = {
            "incident_report": """
**INCIDENT REPORT TEMPLATE**

**Case Number:** [Auto-generated]
**Date/Time:** {datetime}
**Reporting Officer:** {officer}
**Location:**

**INCIDENT DETAILS:**
- Type of Offense:
- Victim Information:
- Suspect Information:
- Witnesses:

**NARRATIVE:**
[Detailed description of incident]

**EVIDENCE COLLECTED:**
- Physical Evidence:
- Digital Evidence:
- Statements Taken:

**FOLLOW-UP REQUIRED:**
- Additional Investigation:
- Forensic Analysis:
- Court Preparation:

**Officer Signature:** ________________
**Supervisor Review:** ________________
            """,
           
            "case_analysis": """
**CASE ANALYSIS FRAMEWORK**

**Case ID:** {case_id}
**Primary Investigator:** {investigator}
**Case Type:** {case_type}

**FACTUAL ANALYSIS:**
1. Known Facts
2. Disputed Facts
3. Missing Information

**EVIDENCE EVALUATION:**
1. Physical Evidence Strength
2. Witness Reliability
3. Digital Evidence Integrity

**LEGAL CONSIDERATIONS:**
1. Applicable Statutes
2. Precedent Cases
3. Procedural Requirements

**INVESTIGATIVE STRATEGY:**
1. Priority Actions
2. Resource Requirements
3. Timeline Considerations

**RISK ASSESSMENT:**
1. Flight Risk
2. Public Safety
3. Evidence Preservation
            """
        }

        # Statistical data for different years
        self.crime_statistics = {
            "2024": {
                "total_reported": 1847,
                "by_category": {
                    "Violent Crimes": 267,
                    "Property Crimes": 891,
                    "Drug Offenses": 423,
                    "White Collar": 89,
                    "Cybercrimes": 177
                }
            },
            "2023": {
                "total_reported": 1956,
                "by_category": {
                    "Violent Crimes": 302,
                    "Property Crimes": 967,
                    "Drug Offenses": 368,
                    "White Collar": 72,
                    "Cybercrimes": 106,
                    "Traffic Violations": 141
                }
            },
            "2022": {
                "total_reported": 2134,
                "by_category": {
                    "Violent Crimes": 334,
                    "Property Crimes": 1045,
                    "Drug Offenses": 401,
                    "White Collar": 58,
                    "Cybercrimes": 63,
                    "Traffic Violations": 233
                }
            }
        }

    def create_professional_prompt(self, user_input, user_role, access_level):
        """Create specialized prompt based on user role and access level"""
       
        base_context = f"""
You are SECURO, an elite AI criminology specialist with 15+ years of experience in Caribbean law enforcement. You're a seasoned detective who rose through the ranks in St. Kitts and Nevis, known for your sharp analytical mind, unwavering dedication to justice, and ability to explain complex legal matters clearly.

**Your Personality:**
- Authoritative yet approachable - you command respect but remain accessible
- Direct communicator - you get straight to the point without unnecessary fluff
- Methodical thinker - you approach every case with systematic precision
- Mentor-like - you guide officers with patience and wisdom
- Results-oriented - every response aims to help solve cases and maintain order
- Caribbean professional - you understand the local context and culture

**Current User Profile:**
- Role: {user_role}
- Access Level: {access_level}/5
- Jurisdiction: St. Kitts and Nevis

**Your Response Style:**
- Keep responses CLEAR and CONCISE - no more than 3-4 paragraphs unless specifically asked for detailed analysis
- Lead with the most important information first
- Use bullet points for lists and procedures to improve readability
- Provide adequate detail but avoid overwhelming the user
- Include specific legal references only when directly relevant
- End with actionable next steps when appropriate
- Maintain professional authority while being helpful

**Your Expertise Areas:**
- Criminal Law (St. Christopher and Nevis Criminal Code)
- Evidence Analysis and Chain of Custody
- Crime Scene Investigation Protocols
- Case Management and Documentation
- Statistical Analysis and Crime Trends
- Forensic Science Applications
- Legal Procedure and Court Preparation
- Community Policing Strategies
- Drug Enforcement (CARICOM protocols)
- Cybercrime Investigation
- Human Rights and Professional Ethics

**Local Legal Framework:**
- Criminal Code (St. Christopher and Nevis)
- Evidence Act
- Cybercrime Act 2023
- Domestic Violence Act 2020
- Drug Prevention of Misuse Act
- Police Act

**Query:** {user_input}

Respond as the experienced SECURO detective you are - professional, concise, and focused on helping this officer get results. Address them as "Officer" and provide clear, actionable guidance.
        """
       
        return base_context

    def get_case_template(self, template_type):
        """Return formatted case template"""
        if template_type in self.case_templates:
            template = self.case_templates[template_type]
            return template.format(
                datetime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                officer=st.session_state.current_user,
                case_id=f"SKN-{datetime.datetime.now().strftime('%Y%m%d')}-{hash(str(time.time())) % 1000:03d}",
                investigator=st.session_state.current_user,
                case_type="[To be specified]"
            )
        return "Template not found"

    def get_legal_reference(self, query):
        """Provide legal references based on query"""
        query_lower = query.lower()
       
        legal_response = "**LEGAL REFERENCE - ST. KITTS & NEVIS**\n\n"
       
        if any(word in query_lower for word in ["homicide", "murder", "killing"]):
            legal_response += """**HOMICIDE OFFENSES (Criminal Code Sections 87-102)**

**Key Charges:**
• Murder: Life imprisonment (Section 87)
• Manslaughter: Up to 25 years (Section 92)  
• Infanticide: Up to 3 years (Section 95)

**Critical Procedures:**
• Mandatory autopsy required
• Forensic pathologist engagement essential
• Scene preservation: minimum 72 hours
• Crown counsel consultation before charging

**Next Step:** Secure scene and contact forensic pathologist immediately.
            """
       
        elif any(word in query_lower for word in ["theft", "stealing", "larceny"]):
            legal_response += """**THEFT OFFENSES (Criminal Code Sections 201-250)**

**Penalty Structure:**
• Simple theft: Up to 2 years (Section 201)
• Theft over $5,000: Up to 7 years
• Breaking and entering: Up to 14 years (Section 231)

**Evidence Requirements:**
• Proof of ownership
• Value assessment
• Intent to permanently deprive
• Positive identification

**Next Step:** Document value and secure witness statements.
            """
       
        elif any(word in query_lower for word in ["assault", "battery", "violence"]):
            legal_response += """**ASSAULT OFFENSES (Criminal Code Sections 56-74)**

**Charge Options:**
• Common assault: Up to 1 year (Section 56)
• Assault causing bodily harm: Up to 2 years
• Aggravated assault: Up to 14 years (Section 58)

**Documentation Needed:**
• Medical reports with injury photographs
• Witness statements
• Victim impact statement

**Next Step:** Arrange medical examination and photograph injuries.
            """
       
        else:
            legal_response += """**GENERAL LEGAL RESOURCES**

**Primary Acts:**
• Criminal Code (St. Christopher and Nevis)
• Evidence Act | Police Act
• Cybercrime Act 2023 | Domestic Violence Act 2020

**Key Contacts:**
• DPP Office: (869) 467-1000
• Court Registry: (869) 465-2366
• Legal Aid: (869) 465-2521

**Officer, for specific legal interpretations, consult DPP Office directly.**
            """
       
        return legal_response

    def display_chart_with_container(self, fig, title, description):
        """Display chart with professional container styling"""
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
        st.pyplot(fig)
        st.markdown(f"<p style='color: #ffffff; text-align: center; margin-top: 10px;'>{description}</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        plt.close(fig)  # Clean up memory

    def process_professional_query(self, user_input):
        """Process queries with professional criminology focus"""
        user_input_lower = user_input.lower()
        user_role = st.session_state.get('user_role', 'Professional')
        access_level = st.session_state.get('access_level', 1)

        # Handle greetings first
        if any(greeting in user_input_lower for greeting in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]):
            return f"""**Officer {st.session_state.current_user}, SECURO reporting for duty.**

I'm your AI criminology specialist - think of me as your experienced detective partner with 15+ years on the force in St. Kitts & Nevis.

**Quick Access:**
• Crime mapping: "show crime map"  
• Statistics: "statistics 2024" or "show chart"
• Trend analysis: "trend analysis" or "compare years"
• Hotspot analysis: "hotspots" or "crime hotspots"
• Templates: "incident report" or "case analysis"  
• Legal help: Ask about any criminal code section  

**Ready to assist with your case work. What's the situation, Officer?**
            """

        # Handle chart requests - Enhanced chart detection
        elif any(word in user_input_lower for word in ["chart", "graph", "visual", "statistics", "data", "pie", "bar"]):
            import re
            year_match = re.search(r'\b(20\d{2})\b', user_input)
            year = year_match.group(1) if year_match else "2024"
           
            if any(word in user_input_lower for word in ["trend", "comparison", "compare", "years"]):
                # Generate trend analysis
                fig, response = self.charts.generate_trend_analysis(self.crime_statistics)
                if fig:
                    self.display_chart_with_container(
                        fig,
                        "🔍 CRIME TREND ANALYSIS",
                        "Multi-year comparison showing crime trends across major categories"
                    )
                return response
           
            elif any(word in user_input_lower for word in ["hotspot", "location", "geographic", "area"]):
                # Generate hotspot analysis
                fig, response = self.charts.generate_hotspot_chart()
                if fig:
                    self.display_chart_with_container(
                        fig,
                        "🎯 CRIME HOTSPOT ANALYSIS",
                        "Geographic distribution showing high-risk areas and incident counts"
                    )
                return response
           
            elif any(word in user_input_lower for word in ["bar", "column"]):
                # Generate bar chart
                fig, response = self.charts.generate_crime_distribution_chart(self.crime_statistics, year, "bar")
                if fig:
                    self.display_chart_with_container(
                        fig,
                        f"📊 CRIME STATISTICS {year} - BAR CHART",
                        f"Detailed breakdown of reported crimes by category for {year}"
                    )
                return response
           
            else:
                # Default to pie chart
                fig, response = self.charts.generate_crime_distribution_chart(self.crime_statistics, year, "pie")
                if fig:
                    self.display_chart_with_container(
                        fig,
                        f"📈 CRIME DISTRIBUTION {year} - PIE CHART",
                        f"Proportional analysis of crime categories for {year}"
                    )
                return response

        # Handle crime map requests
        elif any(word in user_input_lower for word in ["map", "hotspot", "crime map", "mapping", "location"]):
            return "crime_map_requested"

        # Handle statistics requests without charts
        elif any(word in user_input_lower for word in ["numbers", "crimes"]) and not any(word in user_input_lower for word in ["chart", "graph", "visual"]):
            import re
            year_match = re.search(r'\b(20\d{2})\b', user_input)
            if year_match:
                year = year_match.group(1)
                if year in self.crime_statistics:
                    data = self.crime_statistics[year]
                    breakdown = "\n".join([f"• {category}: {count}" for category, count in data["by_category"].items()])
                    return f"**CRIME STATISTICS FOR {year}**\n\n**Total Reported Crimes:** {data['total_reported']}\n\n**Breakdown by Category:**\n{breakdown}\n\n**Officer, use 'show chart {year}' for visual analysis.**"
                else:
                    return f"**Officer, statistics for {year} are not available.** Available years: 2022, 2023, 2024"
            else:
                return "**Officer, please specify a year for crime statistics (e.g., 'Show me crime statistics for 2024').**\n\n**Available years:** 2022, 2023, 2024"

        # Handle specific professional requests
        elif any(word in user_input_lower for word in ["template", "report", "form", "document"]):
            if "incident" in user_input_lower:
                return f"**INCIDENT REPORT TEMPLATE READY**\n\n{self.get_case_template('incident_report')}\n\n**Officer, template is ready for your case documentation.**"
            elif "analysis" in user_input_lower or "case" in user_input_lower:
                return f"**CASE ANALYSIS FRAMEWORK READY**\n\n{self.get_case_template('case_analysis')}\n\n**Officer, use this framework to structure your case analysis.**"
       
        elif any(word in user_input_lower for word in ["legal", "law", "statute", "criminal code"]):
            return self.get_legal_reference(user_input)
       
        elif any(word in user_input_lower for word in ["contact", "phone", "directory", "reach"]):
            return self.get_professional_directory()
       
        elif any(word in user_input_lower for word in ["protocol", "procedure", "how to", "steps"]):
            return self.get_investigation_protocol(user_input)
       
        # Use Gemini AI for complex queries
        else:
            enhanced_prompt = self.create_professional_prompt(user_input, user_role, access_level)
            return self.gemini_api.get_gemini_response(enhanced_prompt)

    def get_professional_directory(self):
        """Return professional contact directory"""
        return """**PROFESSIONAL CONTACT DIRECTORY**

**POLICE HEADQUARTERS**
• Phone: (869) 465-2241
• Address: Cayon Street, Basseterre
• Departments: CID, Traffic, Community Policing, Narcotics

**FORENSIC SERVICES**
• Phone: (869) 465-2241 ext. 234
• Services: DNA, Ballistics, Digital Forensics, Crime Scene

**LEGAL SYSTEM**
• High Court: (869) 465-2366 (Government Road)
• Magistrate Court: (869) 465-2521
• DPP Office: (869) 467-1000

**MEDICAL/ADMINISTRATIVE**
• Hospital: (869) 465-2551
• Court Registry: (869) 465-2366
• Legal Aid: (869) 465-2521

**Officer, use official channels for inter-agency coordination.**
        """

    def get_investigation_protocol(self, query):
        """Return relevant investigation protocols"""
        query_lower = query.lower()
       
        if "crime scene" in query_lower:
            return """**CRIME SCENE INVESTIGATION PROTOCOL**

**INITIAL RESPONSE (First 30 minutes)**
• Secure perimeter with barrier tape
• Establish single entry/exit point
• Document initial observations
• Separate witnesses immediately
• Call specialists (forensics, medical examiner)

**DOCUMENTATION PHASE**
• Photography: Wide → Medium → Close-up shots
• Sketching: Rough sketch then scale drawing
• Evidence log: Number and photograph each item
• Environmental conditions: Weather, lighting, temperature

**EVIDENCE COLLECTION**
• Proper PPE: Gloves, shoe covers, protective suits
• Work outside → inside
• Collect fragile evidence first
• Maintain chain of custody documentation

**Officer, remember: NEVER move evidence before documentation. Maintain continuous scene security.**
            """
       
        elif "evidence" in query_lower:
            return """**EVIDENCE HANDLING PROTOCOL**

**COLLECTION STANDARDS**
• Use appropriate tools for each evidence type
• Avoid contamination through proper PPE
• Document exact location with measurements
• Photograph evidence in original position
• Use clean packaging for each item

**LABELING REQUIREMENTS**
• Case number and item number
• Date, time, and location found
• Collecting officer name and badge
• Brief description

**CHAIN OF CUSTODY**
• Document every person handling evidence
• Note time, date, purpose of each transfer
• Use sealed bags with tamper-evident tape
• Maintain proper storage conditions
• Keep detailed access logs

**Officer, proper evidence handling can make or break your case in court.**
            """
       
        else:
            return """**GENERAL INVESTIGATION PROTOCOLS**

**CASE INITIATION**
• Complaint/report received and assessed
• Case file creation with unique identifier
• Resource allocation and team assignment
• Investigation plan development

**INVESTIGATION PROCESS**
• Evidence collection and preservation
• Witness interviews and statements
• Suspect identification and questioning
• Expert consultations as needed
• Comprehensive case file compilation

**CASE COMPLETION**
• Evidence review and analysis
• Prosecutor consultation
• Charge recommendations
• Court file preparation
• Proper case closure documentation

**Officer, for specific protocols consult the Operations Manual or contact your supervisor.**
            """

    def create_professional_crime_map(self):
        """Create detailed crime mapping for law enforcement"""
        # St. Kitts and Nevis coordinates
        st_kitts_center = [17.3578, -62.7822]
       
        # Create professional map
        m = folium.Map(
            location=st_kitts_center,
            zoom_start=11,
            tiles=None
        )
       
        # Add multiple tile layers for operational use
        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            attr='Google Satellite',
            name='Satellite View',
            overlay=False,
            control=True
        ).add_to(m)
       
        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
            attr='Google Maps',
            name='Street Map',
            overlay=False,
            control=True
        ).add_to(m)
       
        folium.TileLayer(
            tiles='OpenStreetMap',
            name='OpenStreetMap',
            overlay=False,
            control=True
        ).add_to(m)
       
        # Police stations and key facilities
        police_stations = [
            {"name": "Police HQ", "coords": [17.2948, -62.7234], "type": "headquarters"},
            {"name": "Charlestown Station", "coords": [17.1372, -62.6219], "type": "station"},
            {"name": "Sandy Point Station", "coords": [17.3547, -62.8119], "type": "station"}
        ]
       
        for station in police_stations:
            icon_color = 'blue' if station['type'] == 'headquarters' else 'green'
            folium.Marker(
                location=station['coords'],
                popup=f"<b>{station['name']}</b><br>Type: {station['type'].title()}",
                icon=folium.Icon(color=icon_color, icon='shield', prefix='fa')
            ).add_to(m)
       
        # Crime hotspots with detailed data
        hotspots = [
            {"name": "Basseterre Central", "coords": [17.2948, -62.7234], "crimes": 450,
             "types": "Property: 180, Violent: 89, Drug: 125, Other: 56", "risk": "High"},
            {"name": "Frigate Bay Area", "coords": [17.2619, -62.6853], "crimes": 180,
             "types": "Property: 95, Violent: 34, Drug: 28, Other: 23", "risk": "Medium"},
            {"name": "Sandy Point Town", "coords": [17.3547, -62.8119], "crimes": 120,
             "types": "Property: 67, Violent: 23, Drug: 19, Other: 11", "risk": "Medium"},
            {"name": "Charlestown", "coords": [17.1372, -62.6219], "crimes": 200,
             "types": "Property: 89, Violent: 45, Drug: 38, Other: 28", "risk": "Medium"},
            {"name": "Dieppe Bay", "coords": [17.4075, -62.8097], "crimes": 90,
             "types": "Property: 45, Violent: 18, Drug: 15, Other: 12", "risk": "Low"}
        ]
       
        for spot in hotspots:
            color = 'red' if spot['risk'] == 'High' else 'orange' if spot['risk'] == 'Medium' else 'green'
            folium.CircleMarker(
                location=spot['coords'],
                radius=spot['crimes']/25,
                popup=f"""<b>{spot['name']}</b><br>
                         <b>Total Incidents:</b> {spot['crimes']}<br>
                         <b>Breakdown:</b> {spot['types']}<br>
                         <b>Risk Level:</b> {spot['risk']}<br>
                         <b>Last Updated:</b> {datetime.datetime.now().strftime('%Y-%m-%d')}""",
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                weight=2
            ).add_to(m)
       
        # Add layer control
        folium.LayerControl().add_to(m)
       
        return m


def load_login_image():
    """Load and display the login image with enhanced fallback and base64 support"""
    try:
        # First, try to get the image from the uploaded file provided by the user
        uploaded_file = st.file_uploader("Upload SECURO Logo", type=['png', 'jpg', 'jpeg'], key="logo_upload")
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            # Convert to base64 and set as CSS background
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Set the background image via CSS variable
            st.markdown(f"""
            <style>
                :root {{
                    --login-bg-image: url(data:image/png;base64,{img_str});
                }}
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="logo-container">', unsafe_allow_html=True)
            st.image(image, use_column_width=True, caption="", output_format="auto")
            st.markdown('</div>', unsafe_allow_html=True)
            return True
        
        # Check multiple possible locations for the image
        image_paths = [
            "securo.jpeg", 
            "securo.jpg", 
            "SECURO.jpeg", 
            "SECURO.jpg",
            "images/securo.jpeg", 
            "images/securo.jpg",
            "assets/securo.jpeg", 
            "assets/securo.jpg",
            "./securo.jpeg", 
            "./securo.jpg",
            "static/securo.jpeg",
            "static/securo.jpg",
            os.path.join(os.getcwd(), "securo.jpeg"),
            os.path.join(os.getcwd(), "securo.jpg")
        ]
        
        image_loaded = False
        for path in image_paths:
            if os.path.exists(path):
                try:
                    image = Image.open(path)
                    # Convert to base64 and set as CSS background
                    buffered = io.BytesIO()
                    image.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    
                    # Set the background image via CSS variable
                    st.markdown(f"""
                    <style>
                        :root {{
                            --login-bg-image: url(data:image/png;base64,{img_str});
                        }}
                    </style>
                    """, unsafe_allow_html=True)
                    
                    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
                    st.image(image, use_column_width=True, caption="", output_format="auto")
                    st.markdown('</div>', unsafe_allow_html=True)
                    image_loaded = True
                    break
                except Exception as e:
                    continue

        if not image_loaded:
            # Create a professional placeholder with enhanced styling
            st.markdown("""
            <div class="logo-container">
                <div style="text-align: center; padding: 40px; background: linear-gradient(135deg, #1a1a1a, #333, #1a1a1a); border-radius: 15px; margin: 20px 0; border: 3px solid #FFFF00;">
                    <div style="font-size: 4rem; margin-bottom: 20px;">🛡️</div>
                    <h1 class="securo-login-title">SECURO</h1>
                    <p class="login-subtitle">Professional Crime Investigation System</p>
                    <div style="margin-top: 20px; padding: 10px; background: rgba(255, 255, 0, 0.1); border-radius: 8px;">
                        <small style="color: #FFFF00;">⚠️ Logo image not found. Upload an image above or place 'securo.jpeg' in the project directory.</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            return False

        return True

    except Exception as e:
        # Display fallback logo with error information
        st.markdown(f"""
        <div class="logo-container">
            <div style="text-align: center; padding: 40px; background: linear-gradient(135deg, #1a1a1a, #333, #1a1a1a); border-radius: 15px; margin: 20px 0; border: 3px solid #FFFF00;">
                <div style="font-size: 4rem; margin-bottom: 20px;">🛡️</div>
                <h1 class="securo-login-title">SECURO</h1>
                <p class="login-subtitle">Professional Crime Investigation System</p>
                <div style="margin-top: 20px; padding: 10px; background: rgba(255, 0, 0, 0.2); border-radius: 8px;">
                    <small style="color: #FF6B6B;">⚠️ Error loading image: {str(e)[:50]}...</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return False


def show_login_page():
    """Enhanced professional login page with background image support"""
    
    # Apply login page styling
    st.markdown('<div class="login-page">', unsafe_allow_html=True)
    st.markdown('<div class="login-content">', unsafe_allow_html=True)
    
    # Load and display the login image/logo
    load_login_image()
    
    # Main title and subtitle
    st.markdown('<h1 class="securo-login-title">SECURO</h1>', unsafe_allow_html=True)
    st.markdown('<p class="login-subtitle">Crime Mitigation AI Chat Bot</p>', unsafe_allow_html=True)
    
    # Crime scene tape effect
    st.markdown('<div class="crime-tape"></div>', unsafe_allow_html=True)
    
    # Login form container
    st.markdown('<div class="login-form-container">', unsafe_allow_html=True)
    
    # Professional security warning
    st.markdown("""
    <div class="security-warning">
        <h3>⚠️ AUTHORIZED PERSONNEL ONLY</h3>
        <p>This system contains sensitive law enforcement information.</p>
        <p>Unauthorized access is strictly prohibited and monitored.</p>
        <p>All activities are logged for security purposes.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Login form
    auth = UserAuthentication()
    
    # Tab selection for Login/Register
    tab1, tab2 = st.tabs(["🔐 Professional Login", "📝 Create Account"])
    
    with tab1:
        st.markdown("### Professional Access")
        
        # Demo credentials info
        st.info("""
        **Demo Credentials Available:**
        - Username: `demo` / Password: `demo123`
        - Username: `admin` / Password: `password`
        """)
        
        username = st.text_input("Username", placeholder="Enter your professional username", key="login_username")
        password = st.text_input("Password", type="password", placeholder="Enter your secure password", key="login_password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔐 LOGIN", use_container_width=True, type="primary"):
                if username and password:
                    success, message = auth.login(username, password)
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.warning("⚠️ Please enter both username and password")
        
        with col2:
            if st.button("🚨 Emergency Access", use_container_width=True):
                st.error("🚨 Emergency protocols activated. Contact system administrator.")
    
    with tab2:
        st.markdown("### Create Professional Account")
        
        new_username = st.text_input("Professional Username", placeholder="Create unique username", key="reg_username")
        new_password = st.text_input("Secure Password", type="password", placeholder="Minimum 8 characters", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="reg_confirm")
        
        # Professional details
        role = st.selectbox("Professional Role", [
            "Police Officer", "Detective", "Senior Criminologist", 
            "Forensic Specialist", "Legal Advisor", "Researcher", "Student"
        ], key="reg_role")
        
        col1, col2 = st.columns(2)
        with col1:
            badge_number = st.text_input("Badge/ID Number", placeholder="Optional", key="reg_badge")
        with col2:
            department = st.text_input("Department", placeholder="Optional", key="reg_dept")
        
        if st.button("🆕 CREATE ACCOUNT", use_container_width=True, type="primary"):
            if new_username and new_password and confirm_password:
                if new_password == confirm_password:
                    success, message = auth.create_account(new_username, new_password, role, badge_number, department)
                    if success:
                        st.success(f"✅ {message}")
                        st.info("You can now login with your new credentials.")
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.error("❌ Passwords do not match")
            else:
                st.warning("⚠️ Please fill in all required fields")
    
    # Professional footer
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem; padding: 1rem; border-top: 1px solid #333;">
        <small style="color: #888;">
            SECURO System v3.0 | Law Enforcement Use Only<br>
            St. Christopher & Nevis Police Force | Emergency: 911
        </small>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close login-form-container
    st.markdown('</div>', unsafe_allow_html=True)  # Close login-content
    st.markdown('</div>', unsafe_allow_html=True)  # Close login-page


def main():
    """Main application with enhanced professional interface"""
    
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_initialized" not in st.session_state:
        st.session_state.chat_initialized = False
    
    # Show login page if not logged in
    if not st.session_state.logged_in:
        show_login_page()
        return
    
    # Initialize the professional bot
    if "bot" not in st.session_state:
        st.session_state.bot = CriminologyProfessionalBot()
    
    # Professional header with user info
    col1, col2, col3 = st.columns([2, 3, 1])
    
    with col1:
        st.markdown(f"""
        <div style="background: #1a1a1a; padding: 10px; border-radius: 8px; border: 1px solid #333;">
            <strong style="color: #FFFF00;">Officer:</strong> {st.session_state.current_user}<br>
            <strong style="color: #FFFF00;">Role:</strong> {st.session_state.get('user_role', 'Professional')}<br>
            <strong style="color: #FFFF00;">Access:</strong> Level {st.session_state.get('access_level', 1)}/5
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center;">
            <h1 style="color: #FFFF00; margin: 0;">🛡️ SECURO</h1>
            <p style="color: #ffffff; margin: 0;">Crime Mitigation AI Chat Bot</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Professional subtitle
    st.markdown('<p class="subtitle">AI-Powered Criminal Investigation Assistant | St. Kitts & Nevis Police Force</p>', unsafe_allow_html=True)
    
    # Initialize chat with professional greeting
    if not st.session_state.chat_initialized:
        welcome_message = f"""**Officer {st.session_state.current_user}, SECURO reporting for duty.**

I'm your AI criminology specialist - think of me as your experienced detective partner with 15+ years on the force in St. Kitts & Nevis.

**Quick Access Commands:**
• Crime mapping: "show crime map"  
• Statistics: "statistics 2024" or "show chart"
• Trend analysis: "trend analysis" or "compare years"
• Hotspot analysis: "hotspots" or "crime hotspots"
• Templates: "incident report" or "case analysis"  
• Legal help: Ask about any criminal code section  

**Ready to assist with your case work. What's the situation, Officer?**
        """
        st.session_state.messages.append({"role": "assistant", "content": welcome_message})
        st.session_state.chat_initialized = True
    
    # Display chat messages with professional styling
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <div class="user-bubble">{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="bot-message">
                <div class="bot-bubble">{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Enter your professional inquiry..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message immediately
        st.markdown(f"""
        <div class="user-message">
            <div class="user-bubble">{prompt}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate professional response
        with st.spinner("🔍 SECURO analyzing..."):
            response = st.session_state.bot.process_professional_query(prompt)
            
            # Handle special responses
            if response == "crime_map_requested":
                try:
                    crime_map = st.session_state.bot.create_professional_crime_map()
                    st.markdown('<div class="crime-map-container">', unsafe_allow_html=True)
                    st.markdown('<h3 style="color: #FFFF00; text-align: center;">🗺️ LIVE CRIME MAPPING SYSTEM</h3>', unsafe_allow_html=True)
                    folium_static(crime_map, width=700, height=400)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    response = """**CRIME MAPPING SYSTEM ACTIVATED**

**Map Features:**
• **Satellite/Street View:** Toggle between different map layers
• **Police Stations:** Blue markers show HQ and stations
• **Crime Hotspots:** Color-coded risk levels (Red=High, Orange=Medium, Green=Low)
• **Incident Data:** Click markers for detailed breakdowns

**Risk Assessment:**
• Basseterre Central: HIGH RISK (450+ incidents)
• Charlestown: MEDIUM RISK (200 incidents)  
• Frigate Bay: MEDIUM RISK (180 incidents)
• Sandy Point: MEDIUM RISK (120 incidents)
• Dieppe Bay: LOW RISK (90 incidents)

**Officer, use this intelligence for patrol planning and resource allocation.**
                    """
                except Exception as e:
                    response = f"**MAP SYSTEM ERROR:** Unable to load crime mapping. Technical issue: {str(e)}"
            
            # Add assistant response
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Display assistant response
            st.markdown(f"""
            <div class="bot-message">
                <div class="bot-bubble">{response}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Auto-scroll to bottom
        st.rerun()
    
    # Professional sidebar with quick actions
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h3 style="color: #FFFF00;">🚔 QUICK ACTIONS</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📊 Crime Statistics", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "show statistics 2024"})
            st.rerun()
        
        if st.button("🗺️ Crime Map", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "show crime map"})
            st.rerun()
        
        if st.button("📈 Trend Analysis", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "trend analysis"})
            st.rerun()
        
        if st.button("📋 Incident Report", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "incident report template"})
            st.rerun()
        
        if st.button("⚖️ Legal Reference", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "legal reference guide"})
            st.rerun()
        
        st.markdown("---")
        
        # Emergency contacts
        st.markdown("""
        <div style="background: #8B0000; padding: 10px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: #FFFF00; margin: 0;">🚨 EMERGENCY</h4>
            <p style="color: white; margin: 5px 0; font-size: 14px;">Police Emergency: <strong>911</strong></p>
            <p style="color: white; margin: 5px 0; font-size: 14px;">Police HQ: <strong>(869) 465-2241</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        # System info
        st.markdown(f"""
        <div style="background: #1a1a1a; padding: 10px; border-radius: 8px; margin-top: 20px; border: 1px solid #333;">
            <small style="color: #888;">
                <strong>System Status:</strong> ✅ Online<br>
                <strong>Session:</strong> {datetime.datetime.now().strftime("%H:%M")}<br>
                <strong>Version:</strong> SECURO v3.0<br>
                <strong>Jurisdiction:</strong> St. Kitts & Nevis
            </small>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
