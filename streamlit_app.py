import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client

# ==============================================================
# PAGE CONFIG (must be first)
# ==============================================================

st.set_page_config(
    page_title="PMAX Search Terms Explorer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add viewport meta tag for proper mobile scaling
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
""", unsafe_allow_html=True)

# ==============================================================
# CUSTOM CSS - UNOBRAVO DARK THEME (matching your HTML template)
# ==============================================================

st.markdown("""
<style>
    /* Import font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Main background - matches #0f172a from template */
    .stApp {
        background: #0f172a;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #e2e8f0;
    }
    
    /* Apply font to text elements */
    h1, h2, h3, h4, h5, h6, p, span, div, label, button, input, select {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Custom HTML Table - matching template exactly */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        border-spacing: 0;
        background: #1e293b;
        font-size: 13px;
        margin: 0 !important;
        padding: 0 !important;
        border: none;
    }
    
    .custom-table thead,
    .custom-table tbody,
    .custom-table tr {
        margin: 0;
        padding: 0;
        border-spacing: 0;
    }
    
    .custom-table tbody {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    .custom-table thead th {
        background: #1e293b;
        color: #94a3b8;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 14px 16px;
        text-align: left;
        border-bottom: 1px solid #334155;
    }
    
    .custom-table tbody td {
        padding: 12px 16px;
        color: #e2e8f0;
        border-bottom: 1px solid #334155;
    }
    
    .custom-table tbody tr:first-child td {
        border-top: none;
    }
    
    .custom-table tbody tr {
        cursor: pointer;
        transition: background 0.15s ease;
    }
    
    .custom-table tbody tr:hover {
        background: #334155;
    }
    
    .custom-table tbody tr:last-child td {
        border-bottom: none;
    }
    
    /* Right-align numbers */
    .custom-table .num {
        text-align: right;
    }
    
    /* Fixed header table wrapper */
    .table-wrapper {
        border-radius: 12px;
        margin-top: 16px;
        display: flex;
        flex-direction: column;
        gap: 0;
    }
    
    .table-wrapper .table-header {
        border-bottom: 1px solid #334155;
        margin: 0 !important;
        padding: 0 !important;
        flex-shrink: 0;
    }
    
    .table-wrapper .table-header table {
        margin: 0 !important;
        margin-bottom: 0 !important;
    }
    
    .table-wrapper .table-header thead th {
        border-bottom: none;
    }
    
    .table-wrapper .table-body {
        scrollbar-width: thin;
        scrollbar-color: #334155 #1e293b;
        margin: 0 !important;
        padding: 0 !important;
        flex: 1;
    }
    
    .table-wrapper .table-body table {
        margin: 0 !important;
        margin-top: 0 !important;
    }
    
    .table-wrapper .table-body::-webkit-scrollbar {
        width: 8px;
    }
    
    .table-wrapper .table-body::-webkit-scrollbar-track {
        background: #1e293b;
    }
    
    .table-wrapper .table-body::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 4px;
    }
    
    /* Legacy table-container for compatibility */
    .table-container {
        border-radius: 12px;
        border: 1px solid #334155;
        margin-top: 16px;
        background: #1e293b;
        overflow: auto;
        position: relative;
    }
    
    .table-container::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    .table-container::-webkit-scrollbar-track {
        background: #1e293b;
    }
    
    .table-container::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 4px;
    }
    
    /* Sidebar - matches #1e293b from template */
    [data-testid="stSidebar"] {
        background: #1e293b;
        border-right: 1px solid #334155;
        min-width: 300px !important;
    }
    
    /* Hide ALL sidebar collapse/expand buttons and controls */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="baseButton-headerNoPadding"],
    button[kind="headerNoPadding"],
    [data-testid="stSidebar"] button[kind="headerNoPadding"],
    [data-testid="stSidebarNav"] button,
    .st-emotion-cache-1gwvy71,
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }
    
    /* Hide the chevron/arrow icon */
    [data-testid="stSidebar"] svg[data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebar"] > div > button,
    [data-testid="stSidebar"] > div:first-child > button {
        display: none !important;
    }
    
    /* Ensure sidebar always stays visible and expanded */
    [data-testid="stSidebar"][aria-expanded="false"] {
        display: block !important;
        transform: none !important;
        margin-left: 0 !important;
        width: 300px !important;
    }
    
    /* Remove top padding where collapse button was */
    [data-testid="stSidebarContent"] {
        padding-top: 1rem !important;
    }
    
    /* Cards/Metrics - matches .stat-card from template */
    [data-testid="stMetric"] {
        background: #1e293b;
        border: none;
        border-radius: 12px;
        padding: 20px;
    }
    
    /* Different colors for each metric - using nth-of-type on columns */
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [data-testid="stMetric"] {
        border-left: 4px solid #22c55e; /* Green - Clusters */
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(2) [data-testid="stMetric"] {
        border-left: 4px solid #3b82f6; /* Blue - Impressions */
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(3) [data-testid="stMetric"] {
        border-left: 4px solid #f59e0b; /* Orange - Clicks */
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(4) [data-testid="stMetric"] {
        border-left: 4px solid #ec4899; /* Pink - Conversions */
    }
    
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 24px !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 12px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px;
    }
    
    /* Headers - matches template */
    h1 {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 28px !important;
        letter-spacing: -0.5px;
    }
    
    h2 {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 18px !important;
        margin-top: 32px !important;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    h3 {
        color: #94a3b8 !important;
        font-size: 14px !important;
    }
    
    /* Text */
    p, span, label {
        color: #e2e8f0 !important;
    }
    
    .subtitle {
        color: #94a3b8 !important;
        font-size: 14px !important;
    }
    
    /* Buttons - green like template badges */
    .stButton > button {
        background: #22c55e;
        color: #000000;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 25px;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: #4ade80;
        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
    }
    
    /* Download button - styled blue */
    .stDownloadButton > button {
        background: #3b82f6 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
    }
    
    .stDownloadButton > button:hover {
        background: #60a5fa !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    /* Select boxes */
    [data-testid="stSelectbox"] {
        background: #1e293b;
        border-radius: 8px;
        max-width: 400px;
    }
    
    [data-testid="stSelectbox"] > div > div {
        cursor: pointer !important;
        transition: all 0.15s ease;
    }
    
    [data-testid="stSelectbox"] > div > div:hover {
        border-color: #22c55e !important;
        box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.2);
    }
    
    /* Dropdown options hover */
    [data-testid="stSelectbox"] [role="listbox"] [role="option"] {
        cursor: pointer !important;
        transition: background 0.1s ease;
    }
    
    [data-testid="stSelectbox"] [role="listbox"] [role="option"]:hover {
        background: #334155 !important;
    }
    
    [data-testid="stSelectbox"] [role="listbox"] [role="option"][aria-selected="true"] {
        background: #22c55e !important;
        color: #000000 !important;
    }
    
    /* st.dataframe styling to match theme */
    [data-testid="stDataFrame"] {
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    
    [data-testid="stDataFrame"] > div {
        border-radius: 12px !important;
        background: #1e293b !important;
    }
    
    [data-testid="stDataFrame"] iframe {
        border-radius: 12px !important;
    }
    
    /* Dataframe container background */
    .stDataFrame {
        background: #1e293b !important;
        border-radius: 12px !important;
    }
    
    /* Better spacing for form elements */
    [data-testid="stSelectbox"] > div {
        padding: 0 !important;
    }
    
    /* Labels above inputs */
    .stSelectbox label, .stTextInput label {
        font-size: 13px !important;
        color: #94a3b8 !important;
        margin-bottom: 6px !important;
        padding-left: 12px !important;
        padding-top: 8px !important;
    }
    
    /* Expander - matches .section from template */
    .streamlit-expanderHeader {
        background: #1e293b;
        border-radius: 8px;
        color: #e2e8f0 !important;
        border: 1px solid #334155;
    }
    
    .streamlit-expanderHeader p {
        font-size: 14px !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stExpander"] summary span {
        color: #e2e8f0 !important;
    }
    
    .streamlit-expanderContent {
        background: #1e293b;
        border: 1px solid #334155;
        border-top: none;
        border-radius: 0 0 8px 8px;
    }
    
    /* Input fields */
    .stTextInput input, .stNumberInput input {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #e2e8f0 !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #22c55e !important;
        box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.2) !important;
    }
    
    /* Sidebar text */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: #e2e8f0 !important;
    }
    
    /* Insight box - matches .insight-box from template */
    .insight-box {
        background: #334155;
        border-radius: 8px;
        padding: 16px;
        margin-top: 16px;
        margin-bottom: 24px;
    }
    
    .insight-title {
        font-weight: 600;
        color: #fbbf24 !important;
        margin-bottom: 8px;
    }
    
    /* Footer */
    .footer-text {
        color: #64748b;
        text-align: center;
        padding: 20px;
        font-size: 12px;
    }
    
    /* Hide Streamlit branding and header */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Fix top padding after hiding header */
    .block-container {
        padding-top: 1rem !important;
    }
    
    /* Make sure the entire page background is dark */
    [data-testid="stHeader"] {
        background: #0f172a !important;
    }
    
    .stApp > header {
        background: #0f172a !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #22c55e !important;
    }
    
    /* Login page input styling */
    .stTextInput > div > div > input {
        font-size: 16px !important;
        padding: 14px 16px !important;
    }
    
    /* ============================================
       RESPONSIVE STYLES
       ============================================ */
    
    /* Mobile devices */
    @media (max-width: 768px) {
        /* Sidebar - slide out when collapsed on mobile */
        [data-testid="stSidebar"] {
            z-index: 999 !important;
            transition: transform 0.3s ease !important;
        }
        
        [data-testid="stSidebar"][aria-expanded="false"] {
            transform: translateX(-100%) !important;
        }
        
        /* Main content full width */
        .main .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            max-width: 100% !important;
        }
        
        /* Stack metric cards vertically - 2 per row */
        [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) {
            flex-wrap: wrap !important;
        }
        
        [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) > div {
            flex: 0 0 48% !important;
            max-width: 48% !important;
            margin-bottom: 8px !important;
        }
        
        /* Smaller metric text */
        [data-testid="stMetricValue"] {
            font-size: 18px !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 10px !important;
        }
        
        /* Table horizontal scroll */
        .table-container {
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch;
        }
        
        .custom-table {
            min-width: 500px;
            font-size: 11px !important;
        }
        
        /* Smaller headers */
        h1 {
            font-size: 20px !important;
        }
        
        h2 {
            font-size: 14px !important;
            margin-top: 16px !important;
        }
        
        /* 3D chart - smaller height */
        [data-testid="stPlotlyChart"] {
            height: 350px !important;
        }
        
        [data-testid="stPlotlyChart"] > div {
            height: 350px !important;
        }
        
        /* Full width inputs */
        [data-testid="stTextInput"], [data-testid="stSelectbox"] {
            width: 100% !important;
        }
        
        /* Caption smaller */
        .stCaption {
            font-size: 11px !important;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            font-size: 12px !important;
        }
    }
    
    /* Small mobile */
    @media (max-width: 480px) {
        /* Single column metrics */
        [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) > div {
            flex: 0 0 100% !important;
            max-width: 100% !important;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 16px !important;
        }
        
        h1 {
            font-size: 18px !important;
        }
        
        /* Smaller table text */
        .custom-table {
            font-size: 10px !important;
        }
    }
    
    /* Tablet */
    @media (min-width: 769px) and (max-width: 1024px) {
        [data-testid="stSidebar"] {
            min-width: 220px !important;
            width: 220px !important;
        }
        
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }
    
    /* Small desktop */
    @media (min-width: 1025px) and (max-width: 1280px) {
        [data-testid="stSidebar"] {
            min-width: 260px !important;
            width: 260px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================
# HELPER FUNCTION FOR CUSTOM HTML TABLES
# ==============================================================

def render_html_table(df, max_height=400):
    """Render a dataframe as a styled HTML table with fixed header."""
    
    # Minified HTML to avoid whitespace gaps
    html = f'<div class="table-wrapper" style="border:1px solid #334155;border-radius:12px;overflow:hidden;background:#1e293b;margin-top:16px;">'
    html += '<div class="table-header" style="background:#1e293b;margin:0;padding:0;border-bottom:1px solid #334155;">'
    html += '<table class="custom-table" style="table-layout:fixed;width:100%;margin:0;border-collapse:collapse;"><thead><tr>'
    
    for col in df.columns:
        html += f'<th style="border-bottom:none;">{col}</th>'
    
    html += '</tr></thead></table></div>'
    html += f'<div class="table-body" style="max-height:{max_height - 45}px;overflow-y:auto;overflow-x:hidden;margin:0;padding:0;">'
    html += '<table class="custom-table" style="table-layout:fixed;width:100%;margin:0;border-collapse:collapse;"><tbody>'
    
    for _, row in df.iterrows():
        html += '<tr>'
        for i, val in enumerate(row):
            if isinstance(val, (int, float)):
                if pd.isna(val):
                    html += '<td class="num">-</td>'
                elif isinstance(val, float):
                    html += f'<td class="num">{val:,.2f}</td>'
                else:
                    html += f'<td class="num">{val:,}</td>'
            else:
                html += f'<td>{val}</td>'
        html += '</tr>'
    
    html += '</tbody></table></div></div>'
    
    return html

# ==============================================================
# PASSWORD PROTECTION
# ==============================================================

def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            st.markdown("""
                <div style="text-align: center;">
                    <h1 style="font-size: 48px; font-weight: 700; color: #ffffff; margin-bottom: 8px;">
                        🎯 PMAX Explorer
                    </h1>
                    <p style="font-size: 18px; color: #94a3b8; margin-bottom: 40px;">
                        Explore 1.25M search terms grouped into 1,000 semantic clusters
                    </p>
                </div>
            """, unsafe_allow_html=True)
            st.text_input(
                "",
                type="password",
                on_change=password_entered,
                key="password",
                placeholder="Enter password..."
            )
        return False
    
    elif not st.session_state["password_correct"]:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            st.markdown("""
                <div style="text-align: center;">
                    <h1 style="font-size: 48px; font-weight: 700; color: #ffffff; margin-bottom: 8px;">
                        🎯 PMAX Explorer
                    </h1>
                    <p style="font-size: 18px; color: #94a3b8; margin-bottom: 40px;">
                        Explore 1.25M search terms grouped into 1,000 semantic clusters
                    </p>
                </div>
            """, unsafe_allow_html=True)
            st.text_input(
                "",
                type="password",
                on_change=password_entered,
                key="password",
                placeholder="Enter password..."
            )
            st.error("❌ Incorrect password")
        return False
    
    return True

if not check_password():
    st.stop()

# ==============================================================
# CONFIGURATION
# ==============================================================

SUPABASE_URL = st.secrets["supabase_url"]
SUPABASE_KEY = st.secrets["supabase_key"]

TABLE_CLUSTERS = "pmax_cluster_summary_2025"
TABLE_SEARCH_TERMS = "pmax_search_terms_2025"

# ==============================================================
# CONNECT TO SUPABASE
# ==============================================================

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# ==============================================================
# LOAD DATA
# ==============================================================

@st.cache_data(ttl=600)
def load_clusters():
    response = supabase.table(TABLE_CLUSTERS).select("*").execute()
    return pd.DataFrame(response.data)

@st.cache_data(ttl=600)
def load_terms_for_cluster(cluster_id):
    response = supabase.table(TABLE_SEARCH_TERMS)\
        .select("*")\
        .eq("cluster_id", cluster_id)\
        .order("impressions", desc=True)\
        .limit(500)\
        .execute()
    return pd.DataFrame(response.data)

# ==============================================================
# MAIN APP
# ==============================================================

st.title("🎯 PMAX Search Terms Explorer")
st.markdown("*Explore **1.25M** search terms grouped into **1,000** semantic clusters*")

# Introduction section
st.markdown("""
<div style="background: linear-gradient(135deg, #1e3a5f 0%, #1e293b 100%); border-radius: 16px; padding: 24px; margin: 24px 0; border: 1px solid #334155;">
    <h3 style="color: #22c55e; margin: 0 0 16px 0; font-size: 20px;">💎 Gold Data for Cross-Channel Marketing</h3>
    <p style="color: #e2e8f0; font-size: 15px; line-height: 1.7; margin: 0;">
        This is <strong>real search behavior data</strong> powered by Google's algorithms — and it cost €3.2M to generate. 
        Use these insights across all departments: <strong>SEO</strong> (discover what people actually search), 
        <strong>CRM</strong> (understand user intent), <strong>Brand</strong> (identify positioning opportunities), 
        and more. This data is invaluable for building cross-channel strategies based on actual user behavior.
    </p>
</div>
""", unsafe_allow_html=True)

# 2025 Year Header
st.markdown("""
<div style="text-align: center; margin: 24px 0 32px 0; background: #0f172a; border: 1px solid #22c55e; border-radius: 8px; padding: 20px; box-shadow: 0 0 10px rgba(34, 197, 94, 0.3);">
    <p style="color: #3b82f6; font-size: 48px; font-weight: 800; margin: 0; letter-spacing: 2px;">2025</p>
    <p style="color: #94a3b8; font-size: 16px; margin: 8px 0 0 0;">Full Year Performance Data • PMAX</p>
</div>
""", unsafe_allow_html=True)

# Stats cards in columns
col_stat1, col_stat2, col_stat3 = st.columns(3)

with col_stat1:
    st.markdown("""
    <div style="background: #0f172a; border-radius: 12px; padding: 20px; border-left: 4px solid #3b82f6; height: 100%;">
        <p style="color: #94a3b8; font-size: 12px; text-transform: uppercase; margin: 0 0 8px 0;">Total Users</p>
        <p style="color: #22c55e; font-size: 32px; font-weight: 700; margin: 0;">6.78M</p>
        <p style="color: #f59e0b; font-size: 15px; margin: 8px 0 0 0;">58.5% of all Google Ads users</p>
    </div>
    """, unsafe_allow_html=True)

with col_stat2:
    st.markdown("""
    <div style="background: #0f172a; border-radius: 12px; padding: 20px; border-left: 4px solid #f59e0b; height: 100%;">
        <p style="color: #94a3b8; font-size: 12px; text-transform: uppercase; margin: 0 0 8px 0;">Total Spend</p>
        <p style="color: #22c55e; font-size: 32px; font-weight: 700; margin: 0;">€3.2M</p>
        <p style="color: #94a3b8; font-size: 14px; margin: 8px 0 0 0;">35.9% of budget • €0.47/user</p>
    </div>
    """, unsafe_allow_html=True)

with col_stat3:
    st.markdown("""
    <div style="background: #0f172a; border-radius: 12px; padding: 20px; border-left: 4px solid #ec4899; height: 100%;">
        <p style="color: #94a3b8; font-size: 12px; text-transform: uppercase; margin: 0 0 8px 0;">Placements</p>
        <p style="color: #e2e8f0; font-size: 15px; font-weight: 500; margin: 0; line-height: 1.8;">Search • YouTube • Gmail • Display • Discover • Maps</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<p style="color: #94a3b8; font-size: 13px; margin: 16px 0 0 0;">
    📊 <strong>Metrics available:</strong> Impressions, Clicks, Conversions, CTR, CPA, Cost — all extracted from PMAX campaign search term reports.
</p>
""", unsafe_allow_html=True)

df_clusters = load_clusters()

# ==============================================================
# SIDEBAR FILTERS
# ==============================================================

with st.sidebar:
    st.markdown("## 🎯 PMAX Explorer 2025")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #334155 0%, #1e293b 100%); border-radius: 12px; padding: 16px; margin: 16px 0; border-left: 4px solid #22c55e;">
        <p style="color: #e2e8f0; font-size: 14px; line-height: 1.6; margin: 0;">
            🔍 Explore <strong style="color: #22c55e;">1.25M search terms</strong> from Google Ads 
            Performance Max campaigns (2025)
        </p>
        <p style="color: #94a3b8; font-size: 13px; margin-top: 8px; margin-bottom: 0;">
            Grouped into <strong style="color: #22c55e;">1,000 semantic clusters</strong> for easy analysis
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Metrics Guide")
    
    # Impressions
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 12px; padding: 10px; background: rgba(59, 130, 246, 0.1); border-radius: 8px; border-left: 3px solid #3b82f6;">
        <span style="font-size: 20px; margin-right: 12px;">👁️</span>
        <div>
            <p style="color: #3b82f6; font-weight: 600; margin: 0; font-size: 13px;">Impressions</p>
            <p style="color: #94a3b8; margin: 0; font-size: 12px;">Times your ad was shown</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Clicks
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 12px; padding: 10px; background: rgba(245, 158, 11, 0.1); border-radius: 8px; border-left: 3px solid #f59e0b;">
        <span style="font-size: 20px; margin-right: 12px;">👆</span>
        <div>
            <p style="color: #f59e0b; font-weight: 600; margin: 0; font-size: 13px;">Clicks</p>
            <p style="color: #94a3b8; margin: 0; font-size: 12px;">Users who clicked your ad</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Conversions
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 12px; padding: 10px; background: rgba(236, 72, 153, 0.1); border-radius: 8px; border-left: 3px solid #ec4899;">
        <span style="font-size: 20px; margin-right: 12px;">✅</span>
        <div>
            <p style="color: #ec4899; font-weight: 600; margin: 0; font-size: 13px;">Conversions</p>
            <p style="color: #94a3b8; margin: 0; font-size: 12px;">Completed goals (leads, sales)</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # CPA
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 12px; padding: 10px; background: rgba(139, 92, 246, 0.1); border-radius: 8px; border-left: 3px solid #8b5cf6;">
        <span style="font-size: 20px; margin-right: 12px;">💰</span>
        <div>
            <p style="color: #8b5cf6; font-weight: 600; margin: 0; font-size: 13px;">CPA</p>
            <p style="color: #94a3b8; margin: 0; font-size: 12px;">Cost per acquisition (€)</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # CTR
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 12px; padding: 10px; background: rgba(34, 197, 94, 0.1); border-radius: 8px; border-left: 3px solid #22c55e;">
        <span style="font-size: 20px; margin-right: 12px;">📈</span>
        <div>
            <p style="color: #22c55e; font-weight: 600; margin: 0; font-size: 13px;">CTR</p>
            <p style="color: #94a3b8; margin: 0; font-size: 12px;">Click-through rate (%)</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Pro Tip
    st.markdown("""
    <div style="background: linear-gradient(135deg, #334155 0%, #1e293b 100%); border-radius: 12px; padding: 16px; margin-top: 20px; border: 1px solid #334155;">
        <p style="color: #fbbf24; font-size: 12px; font-weight: 600; margin: 0 0 8px 0;">
            💡 PRO TIP
        </p>
        <p style="color: #94a3b8; font-size: 12px; line-height: 1.5; margin: 0;">
            Hover on clusters in the 3D map to see details. Use the tables below to explore individual search terms.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # No filters - show all clusters
    df_filtered = df_clusters.copy()

# ==============================================================
# METRICS ROW
# ==============================================================

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Clusters", f"{len(df_filtered):,}")
with col2:
    st.metric("Impressions", f"{df_filtered['impressions'].sum()/1000000:.1f}M")
with col3:
    st.metric("Clicks", f"{df_filtered['clicks'].sum()/1000000:.2f}M")
with col4:
    st.metric("Conversions", f"{df_filtered['conversions'].sum():,.0f}")

# ==============================================================
# 3D CLUSTER MAP
# ==============================================================

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<h2 style='font-size: 28px;'>🌐 3D Cluster Map</h2>", unsafe_allow_html=True)

with st.expander("View 3D Map", expanded=True):
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.markdown("✋ **Drag** to rotate")
    with col_info2:
        st.markdown("🔍 **Scroll** to zoom")
    with col_info3:
        st.markdown("👆 **Hover** for details")
    
    # Metric selector for Z-axis
    col_metric, col_empty = st.columns([1, 3])
    with col_metric:
        z_metric = st.selectbox(
            "Height (Z-axis) by",
            ["conversions", "impressions", "clicks", "ctr", "cpa"],
            index=0,
            key="z_metric"
        )
    
    # Labels for display
    metric_labels = {
        "conversions": "Conversions",
        "impressions": "Impressions", 
        "clicks": "Clicks",
        "ctr": "CTR %",
        "cpa": "CPA €"
    }
    
    df_plot = df_filtered.copy()
    df_plot['hover_text'] = df_plot.apply(
        lambda x: f"<b>Cluster {x['cluster_id']}</b><br><br>" +
                  f"📊 Terms: {x['term_count']:,}<br>" +
                  f"👁️ Impressions: {x['impressions']:,}<br>" +
                  f"👆 Clicks: {x['clicks']:,}<br>" +
                  f"✅ Conversions: {int(x['conversions'])}<br>" +
                  f"💰 CPA: €{x['cpa']:.2f}<br><br>" +
                  f"<b>🔤 Top Keywords:</b><br>• " +
                  f"{x['sample_terms'].replace(' | ', '<br>• ')[:500]}",
        axis=1
    )
    
    size_values = df_plot['impressions'].apply(lambda x: max(5, min(40, x / 2500)))
    
    # 3D scatter plot with selected metric
    fig_3d = go.Figure(data=[go.Scatter3d(
        x=df_plot['center_x'],
        y=df_plot['center_y'],
        z=df_plot[z_metric],
        mode='markers',
        marker=dict(
            size=size_values,
            color=df_plot[z_metric],
            colorscale='Viridis',
            opacity=0.9,
            showscale=True
        ),
        text=df_plot['hover_text'],
        hovertemplate='%{text}<extra></extra>'
    )])
    
    fig_3d.update_layout(
        scene=dict(
            xaxis=dict(title='Semantic X', gridcolor='#334155', backgroundcolor='#0f172a'),
            yaxis=dict(title='Semantic Y', gridcolor='#334155', backgroundcolor='#0f172a'),
            zaxis=dict(title=metric_labels[z_metric], gridcolor='#334155', backgroundcolor='#0f172a'),
            camera=dict(eye=dict(x=1.5, y=1.5, z=0.9))
        ),
        height=700,
        margin=dict(l=0, r=50, t=30, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(
            bgcolor="#1e293b",
            font_size=13,
            font_color="#e2e8f0",
            bordercolor="#334155"
        )
    )
    
    config = {'scrollZoom': True, 'displayModeBar': True, 'displaylogo': False}
    st.plotly_chart(fig_3d, use_container_width=True, config=config)
    
    # Insight box matching template style
    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-title">💡 How to read this chart</div>
        <p><strong>Height (Z-axis)</strong> = {metric_labels[z_metric]} • <strong>Size</strong> = Impressions • <strong>Color</strong> = {metric_labels[z_metric]}</p>
        <p style="margin-top:8px">The best clusters are <strong>tall</strong> (high {metric_labels[z_metric].lower()}) and <strong>colored green/yellow</strong> (high performance).</p>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================
# 2D VIEW (OPTIONAL)
# ==============================================================

st.markdown("<br>", unsafe_allow_html=True)

# Need df_plot for 2D view
df_plot = df_filtered.copy()

with st.expander("View 2D Map", expanded=False):
    color_option = st.selectbox("Color by:", ["conversions", "clicks", "cpa", "ctr"])
    
    # Create hover text like the 3D chart
    df_plot['hover_text_2d'] = df_plot.apply(
        lambda x: f"<b>Cluster {x['cluster_id']}</b><br><br>" +
                  f"📊 Terms: {x['term_count']:,}<br>" +
                  f"👁️ Impressions: {x['impressions']:,}<br>" +
                  f"👆 Clicks: {x['clicks']:,}<br>" +
                  f"✅ Conversions: {int(x['conversions'])}<br>" +
                  f"💰 CPA: €{x['cpa']:.2f}<br><br>" +
                  f"<b>🔤 Top Keywords:</b><br>• " +
                  f"{x['sample_terms'].replace(' | ', '<br>• ')[:300]}",
        axis=1
    )
    
    fig_2d = px.scatter(
        df_plot,
        x='center_x',
        y='center_y',
        size='impressions',
        color=color_option,
        custom_data=['hover_text_2d'],
        color_continuous_scale='Viridis',
        size_max=50,
        height=600
    )
    
    fig_2d.update_traces(
        hovertemplate='%{customdata[0]}<extra></extra>'
    )
    
    fig_2d.update_layout(
        xaxis_title='Semantic X',
        yaxis_title='Semantic Y',
        paper_bgcolor='#1e293b',
        plot_bgcolor='#1e293b',
        font_color='#e2e8f0',
        margin=dict(l=80, r=40, t=40, b=60),
        xaxis=dict(gridcolor='#334155', zerolinecolor='#334155'),
        yaxis=dict(gridcolor='#334155', zerolinecolor='#334155'),
        hoverlabel=dict(
            bgcolor="#1e293b",
            font_size=13,
            font_color="#e2e8f0",
            bordercolor="#334155"
        )
    )
    
    st.plotly_chart(fig_2d, use_container_width=True)

# ==============================================================
# TOP CLUSTERS TABLE WITH EXPANDABLE ROWS
# ==============================================================

st.markdown("<h2 style='font-size: 28px;'>🏆 Top Performing Clusters</h2>", unsafe_allow_html=True)

# Initialize session state for expanded cluster
if 'expanded_cluster' not in st.session_state:
    st.session_state.expanded_cluster = None

col_sort, col_empty = st.columns([1, 3])
with col_sort:
    sort_by = st.selectbox(
        "Sort by",
        ["conversions", "impressions", "clicks", "term_count", "cpa"],
        index=0
    )

ascending = sort_by == "cpa"  # Only CPA sorts ascending (lower is better)
df_sorted = df_filtered.sort_values(sort_by, ascending=ascending).head(50)  # Top 50 clusters

# Define cycling colors for clusters
cluster_colors = [
    "#22c55e",  # Green
    "#3b82f6",  # Blue
    "#f59e0b",  # Orange
    "#ec4899",  # Pink
    "#8b5cf6",  # Purple
    "#06b6d4",  # Cyan
    "#ef4444",  # Red
    "#84cc16",  # Lime
    "#f97316",  # Orange bright
    "#a855f7",  # Violet
]

# Create table with expandable rows
st.markdown("""
<style>
    /* Cluster row button - minimal styling with left alignment */
    .stButton > button {
        background: transparent !important;
        border: none !important;
        color: #e2e8f0 !important;
        font-weight: 400 !important;
        padding: 4px 0 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        align-items: flex-start !important;
        cursor: pointer !important;
        width: 100% !important;
        display: flex !important;
        outline: none !important;
        box-shadow: none !important;
        border-radius: 0 !important;
    }
    .stButton > button * {
        text-align: left !important;
        justify-content: flex-start !important;
    }
    .stButton > button:hover,
    .stButton > button:focus,
    .stButton > button:active,
    .stButton > button:focus-visible {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
        border-color: transparent !important;
    }
    /* Remove button container hover effect */
    .stButton:hover,
    .stButton:focus,
    div[data-testid="stButton"]:hover,
    div[data-testid="stButton"]:focus {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    /* Remove any Streamlit default button borders */
    button[kind="secondary"],
    button[kind="secondary"]:hover,
    button[kind="secondary"]:focus {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }
    /* Remove element container hover border */
    [data-testid="stElementContainer"]:has(.stButton):hover {
        border: none !important;
        box-shadow: none !important;
    }
    .element-container:has(.stButton):hover {
        border: none !important;
    }
    /* Remove focus ring on buttons */
    .stButton > button::after,
    .stButton > button::before {
        display: none !important;
    }
    .stButton button:focus,
    .stButton button:focus-visible {
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* Expanded section styling */
    .expanded-detail {
        background: #0f172a;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0 16px 0;
        border: 1px solid #334155;
    }
    
    /* Align search input and download button */
    [data-testid="stTextInput"] input {
        height: 42px !important;
    }
    
    [data-testid="stDownloadButton"] button {
        height: 42px !important;
    }
    
    /* Row wrapper for hover effect */
    .cluster-row {
        display: contents;
    }
</style>
""", unsafe_allow_html=True)

st.caption(f"Showing top 50 clusters (scroll to see more)")

# Scrollable container with sticky header inside
clusters_container = st.container(height=900)

with clusters_container:
    # Header row - same columns as data rows for perfect alignment
    header_col_bar, header_col_cluster, header_col_terms, header_col_imp, header_col_clicks, header_col_conv, header_col_ctr, header_col_cpa, header_col_sample = st.columns([0.08, 0.65, 0.6, 0.9, 0.7, 0.9, 0.6, 0.6, 3.5])
    
    with header_col_bar:
        st.markdown("", unsafe_allow_html=True)
    with header_col_cluster:
        st.markdown("<p style='color:#94a3b8; font-size:11px; font-weight:600; text-transform:uppercase; margin:0;'>CLUSTER</p>", unsafe_allow_html=True)
    with header_col_terms:
        st.markdown("<p style='color:#94a3b8; font-size:11px; font-weight:600; text-transform:uppercase; margin:0;'>TERMS</p>", unsafe_allow_html=True)
    with header_col_imp:
        st.markdown("<p style='color:#94a3b8; font-size:11px; font-weight:600; text-transform:uppercase; margin:0;'>IMPRESSIONS</p>", unsafe_allow_html=True)
    with header_col_clicks:
        st.markdown("<p style='color:#94a3b8; font-size:11px; font-weight:600; text-transform:uppercase; margin:0;'>CLICKS</p>", unsafe_allow_html=True)
    with header_col_conv:
        st.markdown("<p style='color:#94a3b8; font-size:11px; font-weight:600; text-transform:uppercase; margin:0;'>CONVERSIONS</p>", unsafe_allow_html=True)
    with header_col_ctr:
        st.markdown("<p style='color:#94a3b8; font-size:11px; font-weight:600; text-transform:uppercase; margin:0;'>CTR %</p>", unsafe_allow_html=True)
    with header_col_cpa:
        st.markdown("<p style='color:#94a3b8; font-size:11px; font-weight:600; text-transform:uppercase; margin:0;'>CPA €</p>", unsafe_allow_html=True)
    with header_col_sample:
        st.markdown("<p style='color:#94a3b8; font-size:11px; font-weight:600; text-transform:uppercase; margin:0;'>SAMPLE TERMS</p>", unsafe_allow_html=True)
    
    st.markdown("<hr style='border:none; border-top:1px solid #334155; margin:8px 0;'>", unsafe_allow_html=True)
    
    for row_idx, (idx, row) in enumerate(df_sorted.iterrows()):
        cluster_id = row['cluster_id']
        is_expanded = st.session_state.expanded_cluster == cluster_id
        color = cluster_colors[row_idx % len(cluster_colors)]
        arrow_char = '▼' if is_expanded else '▶'
        
        # Add CSS for this row's hover effect using unique marker class
        st.markdown(f"""
        <style>
            [data-testid="stHorizontalBlock"]:has(.row-marker-{int(cluster_id)}):hover {{
                background: {color}12 !important;
                border-radius: 8px;
                transition: background 0.15s ease;
            }}
            [data-testid="stHorizontalBlock"]:has(.row-marker-{int(cluster_id)}):hover p {{
                color: {color} !important;
                transition: color 0.15s ease;
            }}
            [data-testid="stHorizontalBlock"]:has(.row-marker-{int(cluster_id)}):hover button {{
                color: {color} !important;
            }}
        </style>
        """, unsafe_allow_html=True)
        
        # Create columns for the row
        col_bar, col_cluster, col_terms, col_imp, col_clicks, col_conv, col_ctr, col_cpa, col_sample = st.columns([0.08, 0.65, 0.6, 0.9, 0.7, 0.9, 0.6, 0.6, 3.5])
        
        # Track if any cell is clicked
        row_clicked = False
        
        with col_bar:
            # Colored indicator bar with unique marker class
            st.markdown(f"""
            <div class="row-marker-{int(cluster_id)}" style="width: 4px; height: 32px; background: {color}; border-radius: 2px; margin-top: 4px;"></div>
            """, unsafe_allow_html=True)
        
        with col_cluster:
            if st.button(f"{arrow_char}  {int(cluster_id)}", key=f"btn_{cluster_id}", use_container_width=True):
                row_clicked = True
        
        with col_terms:
            if st.button(f"{row['term_count']:,}", key=f"terms_{cluster_id}", use_container_width=True):
                row_clicked = True
        with col_imp:
            if st.button(f"{row['impressions']:,}", key=f"imp_{cluster_id}", use_container_width=True):
                row_clicked = True
        with col_clicks:
            if st.button(f"{row['clicks']:,}", key=f"clicks_{cluster_id}", use_container_width=True):
                row_clicked = True
        with col_conv:
            if st.button(f"{row['conversions']:.2f}", key=f"conv_{cluster_id}", use_container_width=True):
                row_clicked = True
        with col_ctr:
            if st.button(f"{row['ctr']:.2f}%", key=f"ctr_{cluster_id}", use_container_width=True):
                row_clicked = True
        with col_cpa:
            if st.button(f"€{row['cpa']:.2f}", key=f"cpa_{cluster_id}", use_container_width=True):
                row_clicked = True
        with col_sample:
            if st.button(f"{row['sample_terms'][:80]}...", key=f"sample_{cluster_id}", use_container_width=True):
                row_clicked = True
        
        # Handle row click
        if row_clicked:
            if is_expanded:
                st.session_state.expanded_cluster = None
            else:
                st.session_state.expanded_cluster = cluster_id
            st.rerun()
        
        # If this cluster is expanded, show the details
        if is_expanded:
            st.markdown("""
            <div style="background: #0f172a; border-radius: 12px; padding: 20px; margin: 12px 0 20px 0; border: 1px solid #22c55e;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                    <span style="color: #22c55e; font-size: 16px; font-weight: 600;">📊 Cluster {cluster_id} - All Search Terms</span>
                </div>
            </div>
            """.replace("{cluster_id}", str(int(cluster_id))), unsafe_allow_html=True)
            
            # Cluster stats row
            stat_col1, stat_col2, stat_col3, stat_col4, stat_col5, close_col = st.columns([1, 1, 1, 1, 1, 1])
            with stat_col1:
                st.metric("Terms", f"{row['term_count']:,}")
            with stat_col2:
                st.metric("Impressions", f"{row['impressions']:,}")
            with stat_col3:
                st.metric("Clicks", f"{row['clicks']:,}")
            with stat_col4:
                st.metric("Conversions", f"{int(row['conversions'])}")
            with stat_col5:
                st.metric("CPA", f"€{row['cpa']:.2f}")
            with close_col:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("✕ Close", key=f"close_{cluster_id}"):
                    st.session_state.expanded_cluster = None
                    st.rerun()
            
            # Load and display terms
            with st.spinner("Loading search terms..."):
                df_terms_expanded = load_terms_for_cluster(cluster_id)
            
            # Search and export row
            search_col, export_col = st.columns([4, 1])
            with search_col:
                search_exp = st.text_input("Search within cluster", "", key=f"search_{cluster_id}", placeholder="🔍 Filter keywords...", label_visibility="collapsed")
            with export_col:
                csv_exp = df_terms_expanded.to_csv(index=False)
                st.download_button(
                    "📥 Export CSV",
                    csv_exp,
                    f"cluster_{int(cluster_id)}_terms.csv",
                    "text/csv",
                    key=f"export_{cluster_id}",
                    use_container_width=True
                )
            
            if search_exp:
                df_terms_expanded = df_terms_expanded[df_terms_expanded['search_term'].str.contains(search_exp, case=False, na=False)]
            
            # Caption with small sort dropdown
            c1, c2 = st.columns([4, 1])
            with c1:
                st.caption(f"Showing all {len(df_terms_expanded):,} search terms")
            with c2:
                sort_opt = st.selectbox("", ["Impressions ↓", "Impressions ↑", "Clicks ↓", "Clicks ↑", "Conv ↓", "Conv ↑", "Cost ↓", "Cost ↑"], key=f"sort_{cluster_id}", label_visibility="collapsed")
            
            # Parse and sort
            col_map = {"Impressions": "impressions", "Clicks": "clicks", "Conv": "conversions", "Cost": "cost"}
            sort_col = col_map[sort_opt.split()[0]]
            sort_asc = "↑" in sort_opt
            df_terms_expanded = df_terms_expanded.sort_values(sort_col, ascending=sort_asc)
            
            # Show ALL data (no limit)
            df_terms_display_exp = df_terms_expanded[['search_term', 'impressions', 'clicks', 'conversions', 'cost']].copy()
            df_terms_display_exp.columns = ['Search Term', 'Impressions', 'Clicks', 'Conversions', 'Cost €']
            
            st.markdown(render_html_table(df_terms_display_exp, max_height=350), unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
        
        # Add a subtle divider between rows
        st.markdown("<hr style='border: none; border-top: 1px solid #334155; margin: 0;'>", unsafe_allow_html=True)

# ==============================================================
# EXPLORE ALL CLUSTERS
# ==============================================================

st.markdown("<h2 style='font-size: 28px;'>🗂️ Explore All 1,000 Clusters</h2>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Browse and search all clusters to find relevant topics</p>', unsafe_allow_html=True)

# Search box for clusters
cluster_search = st.text_input(
    "Search clusters by topic",
    "",
    key="cluster_explorer_search",
    placeholder="🔍 Type to search clusters (e.g., ansia, psicologo, terapia...)",
    label_visibility="collapsed"
)

# Filter clusters based on search
df_all_clusters = df_clusters.copy()
if cluster_search:
    df_all_clusters = df_all_clusters[
        df_all_clusters['sample_terms'].str.contains(cluster_search, case=False, na=False)
    ]

# Sort options
col_sort1, col_sort2, col_count = st.columns([1, 1, 2])
with col_sort1:
    explorer_sort = st.selectbox(
        "Sort by",
        ["conversions", "impressions", "clicks", "term_count", "cpa"],
        key="explorer_sort"
    )
with col_sort2:
    explorer_order = st.selectbox(
        "Order",
        ["Highest first", "Lowest first"],
        key="explorer_order"
    )
with col_count:
    st.markdown(f"<p style='color:#94a3b8; padding-top: 28px;'>Found <span style='color:#22c55e; font-weight:600;'>{len(df_all_clusters):,}</span> clusters</p>", unsafe_allow_html=True)

# Sort data
ascending = explorer_order == "Lowest first"
df_all_clusters = df_all_clusters.sort_values(explorer_sort, ascending=ascending)

# Create the explorer table
st.markdown("""
<style>
    /* Remove Streamlit container margins for tables */
    [data-testid="stMarkdownContainer"]:has(.explorer-wrapper),
    [data-testid="stMarkdownContainer"]:has(.table-wrapper) {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .cluster-explorer-table {
        width: 100%;
        border-collapse: collapse;
        border-spacing: 0;
        background: #1e293b;
        font-size: 13px;
        table-layout: fixed;
        margin: 0 !important;
        padding: 0 !important;
        border: none;
    }
    .cluster-explorer-table thead,
    .cluster-explorer-table tbody,
    .cluster-explorer-table tr {
        margin: 0;
        padding: 0;
    }
    .cluster-explorer-table tbody {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    .cluster-explorer-table thead th {
        background: #1e293b !important;
        color: #94a3b8;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 14px 20px;
        text-align: left;
        border-bottom: none;
        white-space: nowrap;
    }
    .cluster-explorer-table tbody td {
        padding: 14px 20px;
        color: #e2e8f0;
        border-bottom: 1px solid #334155;
        vertical-align: middle;
    }
    .cluster-explorer-table tbody tr:first-child td {
        border-top: none;
    }
    .cluster-explorer-table tbody tr:hover {
        background: #334155;
        cursor: pointer;
    }
    .cluster-explorer-table .cluster-id {
        font-weight: 600;
        color: #22c55e;
        font-size: 14px;
    }
    .cluster-explorer-table .sample-terms {
        color: #94a3b8;
        font-size: 12px;
        line-height: 1.5;
    }
    .cluster-explorer-table .metric {
        text-align: right;
        font-variant-numeric: tabular-nums;
        white-space: nowrap;
    }
    .explorer-wrapper {
        border: 1px solid #334155;
        border-radius: 12px;
        margin-top: 16px;
        overflow: hidden;
        background: #1e293b;
        display: flex;
        flex-direction: column;
        gap: 0;
    }
    .explorer-header {
        margin: 0 !important;
        padding: 0 !important;
        border-bottom: 1px solid #334155;
        flex-shrink: 0;
    }
    .explorer-header table {
        margin: 0 !important;
        margin-bottom: 0 !important;
    }
    .explorer-body {
        max-height: 550px;
        overflow-y: auto;
        margin: 0 !important;
        padding: 0 !important;
        flex: 1;
    }
    .explorer-body table {
        margin: 0 !important;
        margin-top: 0 !important;
    }
    .explorer-body table {
        margin: 0 !important;
    }
    .explorer-body::-webkit-scrollbar {
        width: 8px;
    }
    .explorer-body::-webkit-scrollbar-track {
        background: #1e293b;
    }
    .explorer-body::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Build HTML table with fixed header - using colgroup for consistent widths
col_widths = '''<colgroup>
<col style="width:80px">
<col style="width:100px">
<col style="width:130px">
<col style="width:110px">
<col style="width:100px">
<col style="width:110px">
<col>
</colgroup>'''

explorer_html = '<div class="explorer-wrapper" style="margin:0;padding:0;">'
explorer_html += f'<div class="explorer-header" style="margin:0;padding:0;"><table class="cluster-explorer-table" style="margin:0;padding:0;">{col_widths}<thead><tr>'
explorer_html += '<th>ID</th><th style="text-align:right;">TERMS</th><th style="text-align:right;">IMPRESSIONS</th><th style="text-align:right;">CLICKS</th><th style="text-align:right;">CONV</th><th style="text-align:right;">CPA €</th><th>SAMPLE SEARCH TERMS</th>'
explorer_html += '</tr></thead></table></div>'
explorer_html += f'<div class="explorer-body" style="margin:0;padding:0;"><table class="cluster-explorer-table" style="margin:0;padding:0;">{col_widths}<tbody>'

for _, row in df_all_clusters.iterrows():
    sample = row['sample_terms'][:100] + "..." if len(str(row['sample_terms'])) > 100 else row['sample_terms']
    explorer_html += f'<tr><td class="cluster-id">{int(row["cluster_id"])}</td><td class="metric">{row["term_count"]:,}</td><td class="metric">{row["impressions"]:,}</td><td class="metric">{row["clicks"]:,}</td><td class="metric">{row["conversions"]:.0f}</td><td class="metric">€{row["cpa"]:.2f}</td><td class="sample-terms">{sample}</td></tr>'

explorer_html += '</tbody></table></div></div>'

st.markdown(explorer_html, unsafe_allow_html=True)

st.caption("💡 Tip: Find a cluster you're interested in? Copy the ID and paste it in the Deep Dive section below!")

# ==============================================================
# CLUSTER DRILL-DOWN
# ==============================================================

st.markdown("<h2 style='font-size: 28px;'>🔎 Cluster Deep Dive</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#94a3b8; font-size:14px; margin-top:-8px;'>👆 Enter a cluster ID to explore all its search terms</p>", unsafe_allow_html=True)

col_input, col_empty2 = st.columns([1, 3])
with col_input:
    cluster_input_str = st.text_input(
        "Cluster ID",
        value="",
        placeholder="e.g. 410",
        help="Enter a cluster ID to view all its search terms"
    )

# Convert to int if valid
cluster_input = None
if cluster_input_str.strip():
    try:
        cluster_input = int(cluster_input_str.strip())
    except ValueError:
        st.warning("⚠️ Please enter a valid number")

if cluster_input is not None:
    # Check if cluster exists
    cluster_exists = cluster_input in df_clusters['cluster_id'].values
    
    if not cluster_exists:
        st.warning(f"⚠️ Cluster {cluster_input} not found. Please enter a valid cluster ID.")
    else:
        selected_cluster = cluster_input
        cluster_info = df_clusters[df_clusters['cluster_id'] == selected_cluster].iloc[0]
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Terms", f"{cluster_info['term_count']:,}")
        with col2:
            st.metric("Impressions", f"{cluster_info['impressions']:,}")
        with col3:
            st.metric("Clicks", f"{cluster_info['clicks']:,}")
        with col4:
            st.metric("Conversions", f"{int(cluster_info['conversions'])}")
        with col5:
            st.metric("CPA", f"€{cluster_info['cpa']:.2f}")
        
        with st.spinner("Loading all search terms..."):
            df_terms = load_terms_for_cluster(selected_cluster)
        
        # Search and export row
        col_search, col_export = st.columns([4, 1])
        
        with col_search:
            search_within = st.text_input(
                "Search within cluster",
                "",
                key="cluster_search",
                placeholder="🔍 Type to filter keywords...",
                label_visibility="collapsed"
            )
        
        with col_export:
            csv_data = df_terms.to_csv(index=False)
            st.download_button(
                label="📥 Export CSV",
                data=csv_data,
                file_name=f"cluster_{selected_cluster}_terms.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        if search_within:
            df_terms = df_terms[df_terms['search_term'].str.contains(search_within, case=False, na=False)]
        
        # Caption with small sort dropdown
        c1, c2 = st.columns([4, 1])
        with c1:
            st.caption(f"Showing all {len(df_terms):,} search terms")
        with c2:
            sort_opt = st.selectbox("", ["Impressions ↓", "Impressions ↑", "Clicks ↓", "Clicks ↑", "Conv ↓", "Conv ↑", "Cost ↓", "Cost ↑"], key="sort_deep", label_visibility="collapsed")
        
        # Parse and sort
        col_map = {"Impressions": "impressions", "Clicks": "clicks", "Conv": "conversions", "Cost": "cost"}
        sort_col = col_map[sort_opt.split()[0]]
        sort_asc = "↑" in sort_opt
        df_terms = df_terms.sort_values(sort_col, ascending=sort_asc)
        
        # Show ALL data (no limit)
        df_terms_display = df_terms[['search_term', 'impressions', 'clicks', 'conversions', 'cost']].copy()
        df_terms_display.columns = ['Search Term', 'Impressions', 'Clicks', 'Conversions', 'Cost €']
        
        # Use larger height for more data
        table_height = min(600, max(400, len(df_terms_display) * 35))
        st.markdown(render_html_table(df_terms_display, max_height=table_height), unsafe_allow_html=True)

# ==============================================================
# FOOTER
# ==============================================================

st.markdown("---")
st.markdown(
    '<p class="footer-text">Built with 🧡 by Unobravo Marketing Automation Hub • Data from Google Ads PMAX 2025</p>',
    unsafe_allow_html=True
)