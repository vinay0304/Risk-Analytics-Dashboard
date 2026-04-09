import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def plot_risk_trend_over_time(df):
    """Line chart showing count of transactions over time by risk status."""
    if df.empty:
        return go.Figure()
        
    df['date'] = df['timestamp'].dt.date
    daily_stats = df.groupby(['date', 'is_flagged']).size().reset_index(name='count')
    daily_stats['is_flagged'] = daily_stats['is_flagged'].map({True: 'Flagged (Risky)', False: 'Normal'})
    
    fig = px.line(
        daily_stats,
        x='date', 
        y='count', 
        color='is_flagged',
        title='Transaction Volume Trend over Time',
        color_discrete_map={'Flagged (Risky)': '#EF4444', 'Normal': '#10B981'},
        labels={'date': 'Date', 'count': 'Transaction Count', 'is_flagged': 'Status'}
    )
    fig.update_layout(template='plotly_dark', margin=dict(l=20, r=20, t=50, b=20))
    return fig

def plot_rule_distribution(df):
    """Bar chart for rule triggers."""
    if df.empty or 'rule_name' not in df.columns:
        return go.Figure()
        
    rule_counts = df[df['is_flagged'] == True]['rule_name'].value_counts().reset_index()
    rule_counts.columns = ['rule_name', 'count']
    
    fig = px.bar(
        rule_counts,
        x='count',
        y='rule_name',
        orientation='h',
        title='Top Triggered Rules',
        color='count',
        color_continuous_scale='Reds'
    )
    fig.update_layout(
        template='plotly_dark', 
        yaxis={'categoryorder':'total ascending'},
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

def plot_risk_score_distribution(df):
    """Histogram of risk scores."""
    if df.empty:
        return go.Figure()
        
    fig = px.histogram(
        df,
        x='risk_score',
        color='status',
        nbins=20,
        title='Risk Score Distribution by Status',
        color_discrete_map={'Completed': '#10B981', 'Pending Review': '#F59E0B', 'Blocked': '#EF4444'},
        barmode='stack'
    )
    fig.update_layout(template='plotly_dark', margin=dict(l=20, r=20, t=50, b=20))
    return fig

def plot_geo_distribution(df):
    """Simple bar or map representing IP locations of flagged tx."""
    if df.empty or 'ip_country' not in df.columns:
        return go.Figure()
        
    geo_counts = df[df['is_flagged'] == True]['ip_country'].value_counts().reset_index()
    geo_counts.columns = ['ip_country', 'count']
    
    fig = px.choropleth(
        geo_counts,
        locations='ip_country',
        color='count',
        color_continuous_scale='Reds',
        title='Flagged Transactions by Region'
    )
    fig.update_layout(template='plotly_dark', geo=dict(bgcolor='rgba(0,0,0,0)'), margin=dict(l=0, r=0, t=50, b=0))
    return fig
