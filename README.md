# Quant Developer Evaluation Assignment – Yash Leelani

## Overview
This project is a real-time quantitative analytics dashboard designed to ingest live tick data from
Binance WebSocket streams, store it locally, compute statistical arbitrage analytics, and visualize
results interactively.

The system demonstrates an end-to-end workflow from live market data ingestion to analytics,
alerting, and export, built with a modular and extensible design.

---

## Architecture
**Data Source**
- Binance WebSocket (BTCUSDT, ETHUSDT trades)

**Backend**
- Python asyncio WebSocket client
- SQLite for persistent tick storage

**Analytics**
- Hedge ratio estimation via OLS regression
- Spread construction
- Rolling Z-score
- Rolling correlation

**Frontend**
- Streamlit dashboard
- Plotly interactive charts

**Alerting**
- Rule-based alerts on Z-score thresholds

---

## Project Structure
Gemscap task/
│
├── app.py # WebSocket ingestion + database initialization
├── dashboard.py # Analytics computation + visualization
├── README.md
├── .gitignore


---

## Setup Instructions

### Install dependencies
```bash
pip install streamlit pandas numpy plotly statsmodels websockets

Run data ingestion
python app.py

Run dashboard
streamlit run dashboard.py


Open browser at:

http://localhost:8501
