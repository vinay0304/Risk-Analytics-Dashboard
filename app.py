import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import get_joined_data
from components.charts import (
    plot_risk_trend_over_time,
    plot_rule_distribution,
    plot_risk_score_distribution,
    plot_geo_distribution
)

# Page configuration
st.set_page_config(
    page_title="Risk Analytics Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1E293B;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #F8FAFC;
    }
    .metric-label {
        color: #94A3B8;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .alert-high { color: #EF4444; }
    .alert-medium { color: #F59E0B; }
    .alert-low { color: #10B981; }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ Risk Analytics & Operations Dashboard")
st.markdown("Monitor transaction trends, analyze rule triggers, and investigate operational risks.")

# --- Data Loading ---
with st.spinner("Loading Risk Data..."):
    df = get_joined_data()

if df.empty:
    st.error("No data available. Please ensure database connections are configured and data is generated.")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")

# Date range filter
min_date = df['timestamp'].min().date()
max_date = df['timestamp'].max().date()
start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Risk Score range filter
min_score, max_score = st.sidebar.slider(
    "Risk Score Range",
    min_value=0, max_value=100,
    value=(0, 100)
)

# Status text filter
statuses = df['status'].unique().tolist()
selected_status = st.sidebar.multiselect("Transaction Status", statuses, default=statuses)

# Rule triggered filter
rules = ['All'] + [r for r in df['rule_name'].dropna().unique().tolist() if r]
selected_rule = st.sidebar.selectbox("Filter by Rule Triggered", rules)

# Apply filters
filtered_df = df[
    (df['timestamp'].dt.date >= start_date) &
    (df['timestamp'].dt.date <= end_date) &
    (df['risk_score'] >= min_score) &
    (df['risk_score'] <= max_score) &
    (df['status'].isin(selected_status))
]

if selected_rule != 'All':
    filtered_df = filtered_df[filtered_df['rule_name'] == selected_rule]

# --- KPIs ---
st.markdown("### Executive Summary")
col1, col2, col3, col4 = st.columns(4)

total_tx = len(filtered_df)
flagged_tx = len(filtered_df[filtered_df['is_flagged'] == True])
flag_rate = (flagged_tx / total_tx) * 100 if total_tx > 0 else 0
avg_risk = filtered_df['risk_score'].mean() if total_tx > 0 else 0

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Transactions</div>
        <div class="metric-value">{total_tx:,}</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Flagged for Review</div>
        <div class="metric-value alert-high">{flagged_tx:,}</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Flag Rate</div>
        <div class="metric-value alert-medium">{flag_rate:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    color_class = "alert-high" if avg_risk > 50 else ("alert-medium" if avg_risk > 20 else "alert-low")
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Avg Risk Score</div>
        <div class="metric-value {color_class}">{avg_risk:.1f}</div>
    </div>
    """, unsafe_allow_html=True)


# --- Visualizations ---
st.markdown("### 📈 Analytical Trends")
row1_col1, row1_col2 = st.columns([2, 1])

with row1_col1:
    st.plotly_chart(plot_risk_trend_over_time(filtered_df), use_container_width=True)
with row1_col2:
    st.plotly_chart(plot_risk_score_distribution(filtered_df), use_container_width=True)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.plotly_chart(plot_rule_distribution(filtered_df), use_container_width=True)
with row2_col2:
    st.plotly_chart(plot_geo_distribution(filtered_df), use_container_width=True)


# --- Data Deep Dive ---
st.markdown("### 📋 Transaction Investigations")
st.write("Review flagged transactions in detail. Data table is interactive and can be downloaded as CSV.")

# Prepare a nice view for the table
display_cols = [
    'transaction_id', 'timestamp', 'user_id', 'amount', 'risk_score', 
    'status', 'rule_name', 'ip_country', 'device_os'
]
available_cols = [c for c in display_cols if c in filtered_df.columns]

# Show recent flagged items first
flagged_only = st.checkbox("Show only Flagged Transactions", value=True)
if flagged_only:
    table_df = filtered_df[filtered_df['is_flagged'] == True]
else:
    table_df = filtered_df

table_df = table_df.sort_values(by='timestamp', ascending=False)[available_cols]

# Streamlit Dataframe provides out-of-the-box sorting and searching
st.dataframe(
    table_df, 
    use_container_width=True,
    hide_index=True,
    height=400
)

st.markdown("---")
st.caption("Risk Analytics Dashboard built with Python, SQL, Plotly, Streamlit, and MongoDB.")
