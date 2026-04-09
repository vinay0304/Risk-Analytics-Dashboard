# Risk Analytics Dashboard

An interactive analytics dashboard built to surface trends, support rule-style monitoring workflows, and improve transparency for operational decision-making. 

This project demonstrates a robust data pipeline utilizing **Python, SQL, Plotly, Streamlit, and MongoDB** to automate reporting, reduce manual effort, and support scalable analysis across evolving datasets.

## Features
- **Data Integration**: Connects to both document-based (MongoDB) and relational (SQLite) data stores, mimicking real-world production data lakes where metadata (users, rules) sits in SQL and high-volume logs (transactions) sit in NoSQL.
- **Resilient Fallbacks**: If MongoDB is unavailable, the system automatically falls back to an in-memory JSON document cache.
- **Interactive Visualizations**: Built with Plotly and integrated into a modern `plotly_dark` aesthetic layout. Modules include trendlines, distribution analytics, and geographic mapping.
- **Rule Monitoring**: Interactive sidebars and deep-dive tables allow security and operations teams to drill into which risk rules triggered high-risk scores.

## Prerequisites
- Python 3.9+
- MongoDB (Optional, but recommended)

## Installation

1. Clone or navigate to the repository:
```bash
cd risk-analytics-dashboard
```

2. Install dependencies via pip:
```bash
pip3 install -r requirements.txt
```

3. Configure your Environment Variables:
Copy `.env.example` to `.env` and adjust the configuration as you see fit.
```bash
cp .env.example .env
```

## Running the Application

This dashboard is divided into two primary scripts:

**1. Data Generator**
If this is your first time starting the project, or you need fresh data, run the generator script. It seeds an underlying SQLite database and MongoDB collection:
```bash
python3 data_generator.py
```

**2. Streamlit Dashboard**
To start the web application, run:
```bash
streamlit run app.py
```

The application will launch on your local network (e.g., `http://localhost:8501`).

## Tech Stack
- **Python**: Core logic and runtime.
- **Streamlit**: Web framework for rapid dashboard deployment.
- **Plotly**: Rich charting library.
- **SQLite / SQLAlchemy**: Relational data modeling for users and risk rules.
- **MongoDB / PyMongo**: Document database modeling for high-velocity transaction data.
- **Pandas**: In-memory analytical data shaping and aggregation.
