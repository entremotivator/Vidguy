import streamlit as st
import pandas as pd
import requests
import json
import base64
from datetime import datetime
import time

# Set page configuration
st.set_page_config(
    page_title="AI Video Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced custom CSS for colorful and modern styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .video-card {
        border: none;
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .video-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }
    
    .video-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #ffd93d);
        background-size: 200% 100%;
        animation: rainbow 3s linear infinite;
    }
    
    @keyframes rainbow {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }
    
    .card-header {
        font-size: 1.4em;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 12px;
        font-family: 'Inter', sans-serif;
    }
    
    .card-id {
        display: inline-block;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: 600;
        margin-right: 10px;
    }
    
    .card-subtitle {
        font-size: 0.9em;
        color: #718096;
        margin-bottom: 15px;
        font-weight: 500;
    }
    
    .caption-text {
        background: linear-gradient(135deg, #e8f8ff 0%, #f0f8ff 100%);
        border-left: 4px solid #4ecdc4;
        padding: 15px;
        border-radius: 10px;
        font-style: italic;
        margin: 15px 0;
        color: #2d3748;
        position: relative;
    }
    
    .caption-text::before {
        content: '💬';
        position: absolute;
        top: 10px;
        right: 15px;
        font-size: 1.2em;
    }
    
    .status-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 25px;
        font-size: 0.8em;
        font-weight: 600;
        margin: 8px 5px 8px 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-done {
        background: linear-gradient(135deg, #48bb78, #38a169);
        color: white;
        box-shadow: 0 4px 15px rgba(72, 187, 120, 0.3);
    }
    
    .status-pending {
        background: linear-gradient(135deg, #ed8936, #dd6b20);
        color: white;
        box-shadow: 0 4px 15px rgba(237, 137, 54, 0.3);
    }
    
    .status-in-progress {
        background: linear-gradient(135deg, #4299e1, #3182ce);
        color: white;
        box-shadow: 0 4px 15px rgba(66, 153, 225, 0.3);
    }
    
    .video-container {
        margin: 20px 0;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .environment-tag {
        background: linear-gradient(135deg, #f093fb, #f5576c);
        color: white;
        padding: 8px 15px;
        border-radius: 20px;
        font-size: 0.9em;
        margin: 10px 0;
        display: inline-block;
        font-weight: 500;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        margin: 10px 0;
    }
    
    .metric-number {
        font-size: 2.5em;
        font-weight: 700;
        margin-bottom: 5px;
    }
    
    .metric-label {
        font-size: 0.9em;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .chat-container {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border: 1px solid #e2e8f0;
    }
    
    .image-container {
        background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border: 2px dashed #e53e3e;
        text-align: center;
    }
    
    .upload-zone {
        border: 2px dashed #4299e1;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        background: linear-gradient(135deg, #ebf8ff 0%, #bee3f8 100%);
        transition: all 0.3s ease;
    }
    
    .upload-zone:hover {
        border-color: #3182ce;
        background: linear-gradient(135deg, #bee3f8 0%, #90cdf4 100%);
    }
    
    .uploaded-image {
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 10px 0;
        max-width: 100%;
        height: auto;
    }
    
    .chat-message {
        background: white;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .chat-user {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        margin-left: 20px;
    }
    
    .chat-bot {
        background: linear-gradient(135deg, #4ecdc4, #44a08d);
        color: white;
        margin-right: 20px;
    }
    
    .navigation-pills {
        display: flex;
        gap: 10px;
        margin: 20px 0;
        flex-wrap: wrap;
    }
    
    .nav-pill {
        padding: 8px 16px;
        background: linear-gradient(135deg, #e2e8f0, #cbd5e0);
        border-radius: 20px;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
    }
    
    .nav-pill:hover, .nav-pill.active {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
    }
    
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Default configuration
DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/13EGSQYUva5jutqW0hGmiPh_b1qIVsqGLcCwzoFNsj5g/edit?usp=drivesdk"
WEBHOOK_URL = "https://agentonline-u29564.vm.elestio.app/webhook-test/98b5cc62-767d-484a-99cf-09c0ad616e92"
IMAGE_WEBHOOK_URL = "https://agentonline-u29564.vm.elestio.app/webhook-test/57b4f824-85f3-46eb-91eb-3e95e022e1fc"

def load_data_from_gsheets(sheet_url):
    """Load data from Google Sheets using a public URL"""
    try:
        if 'docs.google.com/spreadsheets' in sheet_url:
            sheet_id = sheet_url.split('/d/')[1].split('/')[0]
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        else:
            csv_url = sheet_url
            
        df = pd.read_csv(csv_url)
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def send_to_webhook(message):
    """Send message to webhook and get response"""
    try:
        payload = {"message": message, "user": "streamlit_user"}
        response = requests.post(
            WEBHOOK_URL, 
            json=payload, 
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json().get('response', 'No response received')
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error sending message: {str(e)}"

def send_image_to_webhook(image_data, filename, prompt="Analyze this image and suggest creative video ideas"):
    """Send image to image webhook and get response"""
    try:
        # Convert image to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        payload = {
            "image": image_base64,
            "filename": filename,
            "prompt": prompt,
            "user": "streamlit_user"
        }
        
        response = requests.post(
            IMAGE_WEBHOOK_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60  # Longer timeout for image processing
        )
        
        if response.status_code == 200:
            return response.json().get('response', 'No response received')
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error sending image: {str(e)}"

def get_status_class(status):
    """Get CSS class for status badge"""
    if pd.isna(status):
        return "status-pending"
    status_lower = str(status).lower()
    if status_lower == "done":
        return "status-done"
    elif status_lower in ["pending", "todo", "waiting"]:
        return "status-pending"
    elif status_lower in ["in progress", "working", "processing"]:
        return "status-in-progress"
    else:
        return "status-pending"

def display_video_card(row, index):
    """Display a single enhanced video card"""
    with st.container():
        st.markdown('<div class="video-card">', unsafe_allow_html=True)
        
        # Card header with ID and title
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f'''
                <div class="card-header">
                    <span class="card-id">#{row["Id"]}</span>
                    {row["Idea"]}
                </div>
            ''', unsafe_allow_html=True)
        with col2:
            if pd.notna(row.get("Date")):
                st.markdown(f'<div class="card-subtitle">📅 {row["Date"]}</div>', unsafe_allow_html=True)
        
        # Status badge
        status = row.get("production", "Pending")
        status_class = get_status_class(status)
        st.markdown(f'<span class="status-badge {status_class}">{status}</span>', unsafe_allow_html=True)
        
        # Caption with enhanced styling
        if pd.notna(row.get("Caption")):
            st.markdown(f'<div class="caption-text">{row["Caption"]}</div>', unsafe_allow_html=True)
        
        # Environment prompt with colorful tag
        if pd.notna(row.get("environment_prompt")):
            st.markdown(f'<div class="environment-tag">🎬 {row["environment_prompt"]}</div>', unsafe_allow_html=True)
        
        # Full prompt in expander
        if pd.notna(row.get("Prompt")):
            with st.expander("🔍 View Full Prompt", expanded=False):
                st.markdown(f"```\n{row['Prompt']}\n```")
        
        # Video player with enhanced container
        video_url = row.get("final_output", "")
        if pd.notna(video_url) and video_url.strip():
            st.markdown('<div class="video-container">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                try:
                    st.video(video_url)
                except Exception as e:
                    st.error(f"Could not load video: {str(e)}")
                    st.markdown(f"**🔗 Direct Link:** [Open Video]({video_url})")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("🎬 Video coming soon...")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(f"👍 Like #{row['Id']}", key=f"like_{index}"):
                st.success("Liked!")
        with col2:
            if st.button(f"📤 Share #{row['Id']}", key=f"share_{index}"):
                st.info(f"Share this video: {video_url}")
        with col3:
            if st.button(f"💬 Comment #{row['Id']}", key=f"comment_{index}"):
                st.info("Comment feature coming soon!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")

def chat_sidebar():
    """Enhanced chat sidebar for video ideas"""
    st.sidebar.markdown("## 💭 AI Video Ideas Chat")
    st.sidebar.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Initialize loading states
    if 'is_loading_chat' not in st.session_state:
        st.session_state.is_loading_chat = False
    
    if 'pending_message' not in st.session_state:
        st.session_state.pending_message = ""
    
    if 'pending_suggestion' not in st.session_state:
        st.session_state.pending_suggestion = ""
    
    # Process pending chat message
    if st.session_state.pending_message:
        st.sidebar.info("🤖 AI is thinking...")
        try:
            response = send_to_webhook(st.session_state.pending_message)
            st.session_state.chat_history.append((st.session_state.pending_message, response))
        except Exception as e:
            st.sidebar.error(f"Error: {str(e)}")
        st.session_state.pending_message = ""
        st.rerun()
    
    # Process pending suggestion
    if st.session_state.pending_suggestion:
        st.sidebar.info("🤖 AI is thinking...")
        try:
            message = f"Give me creative video ideas about: {st.session_state.pending_suggestion}"
            response = send_to_webhook(message)
            st.session_state.chat_history.append((st.session_state.pending_suggestion, response))
        except Exception as e:
            st.sidebar.error(f"Error: {str(e)}")
        st.session_state.pending_suggestion = ""
        st.rerun()
    
    # Display chat history
    if st.session_state.chat_history:
        for i, (user_msg, bot_msg) in enumerate(st.session_state.chat_history[-5:]):  # Show last 5
            st.sidebar.markdown(f'<div class="chat-message chat-user">You: {user_msg}</div>', unsafe_allow_html=True)
            st.sidebar.markdown(f'<div class="chat-message chat-bot">AI: {bot_msg}</div>', unsafe_allow_html=True)
    
    # Chat input (don't disable, let user type while processing)
    user_input = st.sidebar.text_area(
        "Ask for video ideas:", 
        placeholder="e.g., 'Give me ideas for AI robot videos'", 
        height=80,
        key="chat_input"
    )
    
    # Button controls
    col1, col2 = st.sidebar.columns(2)
    with col1:
        send_disabled = bool(st.session_state.pending_message or st.session_state.pending_suggestion)
        if st.button("🚀 Send", key="send_chat", disabled=send_disabled):
            if user_input.strip():
                st.session_state.pending_message = user_input
                st.rerun()
    
    with col2:
        clear_disabled = bool(st.session_state.pending_message or st.session_state.pending_suggestion)
        if st.button("🗑️ Clear", key="clear_chat", disabled=clear_disabled):
            st.session_state.chat_history = []
            st.rerun()
    
    # Quick suggestion buttons
    st.sidebar.markdown("### 💡 Quick Ideas")
    suggestions = [
        "Futuristic robot scenes",
        "AI in daily life",
        "Cyberpunk cityscapes",
        "Robot emotions",
        "Tech workplace"
    ]
    
    buttons_disabled = bool(st.session_state.pending_message or st.session_state.pending_suggestion)
    for i, suggestion in enumerate(suggestions):
        if st.sidebar.button(suggestion, key=f"suggest_{i}", disabled=buttons_disabled):
            st.session_state.pending_suggestion = suggestion
            st.rerun()
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

def image_upload_sidebar():
    """Enhanced image upload sidebar for AI analysis"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🖼️ AI Image Analysis")
    st.sidebar.markdown('<div class="image-container">', unsafe_allow_html=True)
    
    # Initialize image states
    if 'image_history' not in st.session_state:
        st.session_state.image_history = []
    
    if 'pending_image' not in st.session_state:
        st.session_state.pending_image = None
    
    if 'pending_image_prompt' not in st.session_state:
        st.session_state.pending_image_prompt = ""
    
    # Process pending image
    if st.session_state.pending_image:
        st.sidebar.info("🔍 AI is analyzing your image...")
        try:
            image_data, filename, prompt = st.session_state.pending_image
            response = send_image_to_webhook(image_data, filename, prompt)
            st.session_state.image_history.append((filename, prompt, response))
        except Exception as e:
            st.sidebar.error(f"Error: {str(e)}")
        st.session_state.pending_image = None
        st.rerun()
    
    # Image upload section
    st.sidebar.markdown("### 📤 Upload Image")
    uploaded_file = st.sidebar.file_uploader(
        "Choose an image...",
        type=['png', 'jpg', 'jpeg', 'gif', 'webp'],
        key="image_uploader",
        help="Upload an image to get AI-generated video ideas based on it"
    )
    
    # Custom prompt for image analysis
    image_prompt = st.sidebar.text_area(
        "Custom analysis prompt:",
        placeholder="Analyze this image and suggest creative video ideas",
        height=60,
        key="image_prompt_input"
    )
    
    # Show uploaded image preview
    if uploaded_file is not None:
        st.sidebar.markdown('<div class="upload-zone">', unsafe_allow_html=True)
        st.sidebar.image(uploaded_file, caption=f"📸 {uploaded_file.name}", use_column_width=True)
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            analyze_disabled = bool(st.session_state.pending_image)
            if st.sidebar.button("🔍 Analyze", key="analyze_image", disabled=analyze_disabled):
                # Read image data
                image_data = uploaded_file.getvalue()
                prompt = image_prompt.strip() if image_prompt.strip() else "Analyze this image and suggest creative video ideas"
                st.session_state.pending_image = (image_data, uploaded_file.name, prompt)
                st.rerun()
        
        with col2:
            if st.sidebar.button("🗑️ Remove", key="remove_image"):
                # Force a rerun to clear the uploader
                st.rerun()
        
        st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Quick analysis prompts
    if uploaded_file is not None:
        st.sidebar.markdown("### ⚡ Quick Analysis")
        quick_prompts = [
            "Video ideas from this image",
            "Create story scenarios",
            "Describe visual elements",
            "Suggest camera angles",
            "Mood and atmosphere ideas"
        ]
        
        for i, prompt in enumerate(quick_prompts):
            if st.sidebar.button(prompt, key=f"quick_prompt_{i}"):
                image_data = uploaded_file.getvalue()
                st.session_state.pending_image = (image_data, uploaded_file.name, prompt)
                st.rerun()
    
    # Display image analysis history
    if st.session_state.image_history:
        st.sidebar.markdown("### 📋 Recent Analysis")
        for i, (filename, prompt, response) in enumerate(st.session_state.image_history[-3:]):  # Show last 3
            with st.sidebar.expander(f"🖼️ {filename[:20]}...", expanded=False):
                st.markdown(f"**Prompt:** {prompt}")
                st.markdown(f"**Response:** {response[:200]}...")
    
    # Clear history button
    if st.session_state.image_history:
        if st.sidebar.button("🗑️ Clear Image History", key="clear_image_history"):
            st.session_state.image_history = []
            st.rerun()
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

def main():
    # Enhanced header
    st.markdown('''
        <div class="main-header">
            <h1>🎬 AI Video Dashboard</h1>
            <p>Create, manage, and showcase your AI-generated video content</p>
        </div>
    ''', unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("## ⚙️ Dashboard Settings")
        
        # Sheet URL input with default
        sheet_url = st.text_input(
            "📊 Google Sheets URL:",
            value=DEFAULT_SHEET_URL,
            help="Your Google Sheets URL (publicly accessible)"
        )
        
        # Auto-refresh and manual refresh
        col1, col2 = st.columns(2)
        with col1:
            auto_refresh = st.checkbox("🔄 Auto-refresh", value=False)
        with col2:
            if st.button("↻ Refresh"):
                st.session_state.data_loading = True
                st.rerun()
        
        st.markdown("---")
        
        # Chat sidebar
        chat_sidebar()
        
        # Image upload sidebar  
        image_upload_sidebar()
        
        st.markdown("---")
        
        # Filters section
        st.markdown("## 🔍 Filters & Navigation")
    
    # Load and display data
    if sheet_url:
        # Initialize loading state for data
        if 'data_loading' not in st.session_state:
            st.session_state.data_loading = False
        
        if st.session_state.data_loading:
            st.info("🔄 Loading your awesome videos...")
            df = load_data_from_gsheets(sheet_url)
            st.session_state.data_loading = False
        else:
            df = load_data_from_gsheets(sheet_url)
        
        if df is not None and not df.empty:
            # Navigation pills for quick filtering
            st.markdown("### 🎯 Quick Navigation")
            nav_cols = st.columns(5)
            nav_options = ["All Videos", "Completed", "Pending", "With Video", "Recent"]
            
            selected_nav = None
            for i, option in enumerate(nav_options):
                with nav_cols[i]:
                    if st.button(option, key=f"nav_{option}"):
                        selected_nav = option
            
            # Enhanced metrics with colorful cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f'''
                    <div class="metric-card">
                        <div class="metric-number">{len(df)}</div>
                        <div class="metric-label">Total Videos</div>
                    </div>
                ''', unsafe_allow_html=True)
            
            with col2:
                done_count = len(df[df.get("production", "").str.lower() == "done"]) if "production" in df.columns else 0
                st.markdown(f'''
                    <div class="metric-card" style="background: linear-gradient(135deg, #48bb78, #38a169);">
                        <div class="metric-number">{done_count}</div>
                        <div class="metric-label">Completed</div>
                    </div>
                ''', unsafe_allow_html=True)
            
            with col3:
                pending_count = len(df) - done_count
                st.markdown(f'''
                    <div class="metric-card" style="background: linear-gradient(135deg, #ed8936, #dd6b20);">
                        <div class="metric-number">{pending_count}</div>
                        <div class="metric-label">Pending</div>
                    </div>
                ''', unsafe_allow_html=True)
            
            with col4:
                videos_with_output = len(df[df.get("final_output", "").notna() & (df.get("final_output", "") != "")])
                st.markdown(f'''
                    <div class="metric-card" style="background: linear-gradient(135deg, #4ecdc4, #44a08d);">
                        <div class="metric-number">{videos_with_output}</div>
                        <div class="metric-label">With Video</div>
                    </div>
                ''', unsafe_allow_html=True)
            
            # Advanced filters
            with st.sidebar:
                show_advanced = st.checkbox("🔧 Advanced Filters", value=False)
                
                filtered_df = df.copy()
                
                if show_advanced:
                    # Status filter
                    if "production" in df.columns:
                        status_options = ["All"] + sorted(df["production"].dropna().unique().tolist())
                        status_filter = st.selectbox("📊 Status Filter:", status_options)
                        if status_filter != "All":
                            filtered_df = filtered_df[filtered_df["production"] == status_filter]
                    
                    # Search filter
                    search_term = st.text_input("🔍 Search Videos:", placeholder="Search ideas, captions...")
                    if search_term:
                        mask = (
                            filtered_df.get("Idea", "").str.contains(search_term, case=False, na=False) |
                            filtered_df.get("Caption", "").str.contains(search_term, case=False, na=False)
                        )
                        filtered_df = filtered_df[mask]
                    
                    # Date range filter
                    if "Date" in df.columns and not df["Date"].isna().all():
                        date_filter = st.checkbox("📅 Filter by Date")
                        if date_filter:
                            st.date_input("From Date:", key="start_date")
                            st.date_input("To Date:", key="end_date")
            
            # Apply navigation filter
            if selected_nav == "Completed":
                filtered_df = filtered_df[filtered_df.get("production", "").str.lower() == "done"]
            elif selected_nav == "Pending":
                filtered_df = filtered_df[filtered_df.get("production", "").str.lower() != "done"]
            elif selected_nav == "With Video":
                filtered_df = filtered_df[filtered_df.get("final_output", "").notna() & (filtered_df.get("final_output", "") != "")]
            elif selected_nav == "Recent":
                if "Id" in filtered_df.columns:
                    filtered_df = filtered_df.nlargest(10, "Id")
            
            # Sort options
            sort_col1, sort_col2 = st.columns(2)
            with sort_col1:
                sort_by = st.selectbox("🔄 Sort by:", ["Id (Newest)", "Id (Oldest)", "Status", "Date"])
            with sort_col2:
                items_per_page = st.selectbox("📄 Items per page:", [5, 10, 20, 50], index=1)
            
            # Apply sorting
            if "Id" in filtered_df.columns:
                if sort_by == "Id (Newest)":
                    filtered_df = filtered_df.sort_values("Id", ascending=False)
                elif sort_by == "Id (Oldest)":
                    filtered_df = filtered_df.sort_values("Id", ascending=True)
                elif sort_by == "Status":
                    filtered_df = filtered_df.sort_values("production", ascending=True, na_position='last')
            
            # Pagination
            total_items = len(filtered_df)
            if total_items > items_per_page:
                total_pages = (total_items - 1) // items_per_page + 1
                page = st.selectbox(f"📄 Page (1-{total_pages}):", range(1, total_pages + 1))
                start_idx = (page - 1) * items_per_page
                end_idx = start_idx + items_per_page
                filtered_df = filtered_df.iloc[start_idx:end_idx]
            
            # Display results info
            if len(filtered_df) != len(df):
                st.info(f"📊 Showing {len(filtered_df)} of {len(df)} videos")
            
            # Display video cards
            if not filtered_df.empty:
                st.markdown("### 🎬 Your Video Collection")
                for index, row in filtered_df.iterrows():
                    display_video_card(row, index)
            else:
                st.warning("🔍 No videos match your current filters. Try adjusting your search criteria!")
                
        elif df is not None:
            st.warning("📭 The Google Sheets appears to be empty. Add some video data to get started!")
        else:
            st.error("❌ Could not load data. Please check your Google Sheets URL and sharing settings.")
    
    # Auto-refresh logic (simplified to avoid conflicts)
    if auto_refresh:
        # Use a more controlled auto-refresh approach
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = time.time()
        
        current_time = time.time()
        if current_time - st.session_state.last_refresh > 30:  # 30 seconds
            st.session_state.last_refresh = current_time
            st.session_state.data_loading = True
            st.rerun()

if __name__ == "__main__":
    main()
