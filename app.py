import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time

# Set page configuration
st.set_page_config(
    page_title="AI Video Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .video-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        background-color: #f9f9f9;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .card-header {
        font-size: 1.2em;
        font-weight: bold;
        color: #333;
        margin-bottom: 10px;
    }
    
    .card-subtitle {
        font-size: 0.9em;
        color: #666;
        margin-bottom: 15px;
    }
    
    .caption-text {
        background-color: #e8f4f8;
        padding: 10px;
        border-radius: 5px;
        font-style: italic;
        margin: 10px 0;
    }
    
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: bold;
        margin: 5px 0;
    }
    
    .status-done {
        background-color: #d4edda;
        color: #155724;
    }
    
    .status-pending {
        background-color: #fff3cd;
        color: #856404;
    }
    
    .video-container {
        margin: 15px 0;
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

def load_data_from_gsheets(sheet_url):
    """
    Load data from Google Sheets using a public URL
    Convert the sharing URL to CSV export format
    """
    try:
        # Convert Google Sheets URL to CSV export format
        if 'docs.google.com/spreadsheets' in sheet_url:
            # Extract the sheet ID from the URL
            sheet_id = sheet_url.split('/d/')[1].split('/')[0]
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        else:
            csv_url = sheet_url
            
        # Load the data
        df = pd.read_csv(csv_url)
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def validate_video_url(url):
    """Check if video URL is accessible"""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def display_video_card(row, index):
    """Display a single video card"""
    with st.container():
        st.markdown('<div class="video-card">', unsafe_allow_html=True)
        
        # Card header with ID and date
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f'<div class="card-header">Video #{row["Id"]} - {row["Idea"]}</div>', unsafe_allow_html=True)
        with col2:
            if pd.notna(row.get("Date")):
                st.markdown(f'<div class="card-subtitle">📅 {row["Date"]}</div>', unsafe_allow_html=True)
        
        # Status badge
        status = row.get("production", "Unknown")
        status_class = "status-done" if status.lower() == "done" else "status-pending"
        st.markdown(f'<span class="status-badge {status_class}">{status}</span>', unsafe_allow_html=True)
        
        # Caption
        if pd.notna(row.get("Caption")):
            st.markdown(f'<div class="caption-text">💬 {row["Caption"]}</div>', unsafe_allow_html=True)
        
        # Environment prompt
        if pd.notna(row.get("environment_prompt")):
            st.markdown(f"**Environment:** {row['environment_prompt']}")
        
        # Final prompt
        if pd.notna(row.get("Prompt")):
            with st.expander("View Full Prompt"):
                st.text(row["Prompt"])
        
        # Video player
        video_url = row.get("final_output", "")
        if pd.notna(video_url) and video_url.strip():
            st.markdown('<div class="video-container">', unsafe_allow_html=True)
            try:
                st.video(video_url)
            except Exception as e:
                st.error(f"Could not load video: {str(e)}")
                st.markdown(f"**Video URL:** [Click to view]({video_url})")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No video available for this entry")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")

def main():
    # Header
    st.title("🎬 AI Video Dashboard")
    st.markdown("### Live data from Google Sheets")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Default Google Sheets URL input
        default_url = "https://docs.google.com/spreadsheets/d/your-sheet-id/edit#gid=0"
        sheet_url = st.text_input(
            "Google Sheets URL:",
            value=default_url,
            help="Paste your Google Sheets URL here. Make sure it's publicly accessible (sharing settings: Anyone with the link can view)"
        )
        
        # Auto-refresh option
        auto_refresh = st.checkbox("Auto-refresh every 30 seconds", value=False)
        
        # Manual refresh button
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        # Filters
        st.header("🔍 Filters")
        show_filters = st.checkbox("Enable Filters", value=False)
    
    # Auto-refresh logic
    if auto_refresh:
        placeholder = st.empty()
        with placeholder:
            st.info("Auto-refreshing in 30 seconds...")
            time.sleep(30)
            st.rerun()
    
    # Load and display data
    if sheet_url and sheet_url != default_url:
        with st.spinner("Loading data from Google Sheets..."):
            df = load_data_from_gsheets(sheet_url)
        
        if df is not None and not df.empty:
            # Display summary stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Videos", len(df))
            with col2:
                done_count = len(df[df.get("production", "").str.lower() == "done"]) if "production" in df.columns else 0
                st.metric("Completed", done_count)
            with col3:
                pending_count = len(df) - done_count
                st.metric("Pending", pending_count)
            with col4:
                videos_with_output = len(df[df.get("final_output", "").notna() & (df.get("final_output", "") != "")])
                st.metric("With Video", videos_with_output)
            
            # Apply filters if enabled
            filtered_df = df.copy()
            
            if show_filters:
                filter_col1, filter_col2 = st.columns(2)
                
                with filter_col1:
                    if "production" in df.columns:
                        status_filter = st.selectbox(
                            "Filter by Status:",
                            options=["All"] + list(df["production"].dropna().unique()),
                            index=0
                        )
                        if status_filter != "All":
                            filtered_df = filtered_df[filtered_df["production"] == status_filter]
                
                with filter_col2:
                    # Search filter
                    search_term = st.text_input("Search in Ideas/Captions:")
                    if search_term:
                        mask = (
                            filtered_df["Idea"].str.contains(search_term, case=False, na=False) |
                            filtered_df["Caption"].str.contains(search_term, case=False, na=False)
                        )
                        filtered_df = filtered_df[mask]
            
            # Display results count
            if len(filtered_df) != len(df):
                st.info(f"Showing {len(filtered_df)} of {len(df)} videos")
            
            # Sort by Id (descending to show newest first)
            if "Id" in filtered_df.columns:
                filtered_df = filtered_df.sort_values("Id", ascending=False)
            
            # Display video cards
            if not filtered_df.empty:
                for index, row in filtered_df.iterrows():
                    display_video_card(row, index)
            else:
                st.warning("No videos match your current filters.")
                
        elif df is not None:
            st.warning("The Google Sheets appears to be empty.")
        else:
            st.error("Could not load data. Please check your Google Sheets URL and sharing settings.")
    else:
        # Instructions for setting up
        st.info("👆 Please enter your Google Sheets URL in the sidebar to get started.")
        
        st.markdown("""
        ### 📝 Setup Instructions:
        
        1. **Open your Google Sheets document**
        2. **Set sharing permissions:**
           - Click "Share" button
           - Change permissions to "Anyone with the link can view"
           - Copy the sharing URL
        3. **Paste the URL in the sidebar**
        4. **Your data should appear automatically!**
        
        ### 📋 Expected Column Names:
        - `Id` - Unique identifier
        - `Idea` - Video concept/idea
        - `Caption` - Social media caption
        - `production` - Status (Done, Pending, etc.)
        - `environment_prompt` - Environment description
        - `final_output` - Video URL
        - `Prompt` - Full generation prompt
        - `Date` - Creation date
        
        ### 🎥 Video Format Support:
        - MP4 files (recommended)
        - Direct video links
        - URLs must be publicly accessible
        """)

if __name__ == "__main__":
    main()
