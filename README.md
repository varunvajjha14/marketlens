# MarketLens 🗺️
### Hyperlocal Market Intelligence for Mumbai's Food & Beverage Sector

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![Plotly Dash](https://img.shields.io/badge/Plotly-Dash-purple)](https://dash.plotly.com)
[![Groq](https://img.shields.io/badge/AI-Groq%20LLaMA-orange)](https://groq.com)
[![Railway](https://img.shields.io/badge/Deployed-Railway-blueviolet)](https://railway.app)

> **Find underserved food markets before your competitors do.**

MarketLens is a full-stack data intelligence platform that identifies high-opportunity micro-markets across Mumbai's 24 administrative wards by combining real venue data, machine learning scoring, and AI-generated market insights.

---

## 🎯 Who It's For

| User | Use Case |
|------|----------|
| 🍽️ Restaurant Owners | Find wards with low competition and high demand |
| 📦 Cloud Kitchen Founders | Identify wards with near-zero delivery penetration |
| 💰 Investors & Franchisors | Spot underserved markets before they get crowded |
| ☕ Cafe & QSR Operators | Match your format to the ward that needs it most |

---

## ✨ Features

### 🗺️ Mumbai Ward Opportunity Map
Interactive choropleth heatmap of all 24 Mumbai wards. Green = high opportunity, red = saturated. Hover any ward for instant market data.

### 📊 Analytics Dashboard
- Opportunity score bar chart across all wards
- Venues vs score scatter plot
- Filterable ward detail table by tier and data confidence

### 🎯 Opportunity Simulator
Select your business type (Cafe, Pizza, Cloud Kitchen, Bakery, South Indian, Chinese) and budget — MarketLens recalculates the best ward specifically for your format using a weighted ML model.

### 🤖 AI Market Consultant
Conversational AI powered by Groq LLaMA 3.1. Ask natural language questions like *"Where should I open a pizza place under ₹15 lakh?"* and get data-grounded answers in seconds.

### 📤 BI Export *(v1.1)*
Export ward scores as Power BI / Tableau-ready `.csv` for deeper custom analysis. Pre-built Power BI template included.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Data Collection | OpenStreetMap · Overpass API |
| Data Processing | Python · pandas · NumPy |
| ML Scoring | scikit-learn · KMeans · MinMaxScaler |
| Dashboard | Plotly Dash · Dash Bootstrap Components |
| AI | Groq API · LLaMA 3.1 8B Instant |
| Deployment | Railway |

---

## 📐 How the ML Model Works

The opportunity score is a weighted composite of five signals:
opportunity_score =

0.30 × scarcity_signal          (fewer venues = more room to enter)

0.25 × delivery_gap_signal      (low delivery % = unmet demand)
0.20 × cuisine_gap_signal       (fewer cuisine types = more gaps)
0.15 × quality_gap_signal       (fast food heavy = demand for better)
0.10 × fragmentation_signal     (independent-heavy = weaker incumbents)


Wards are then clustered into High / Medium / Low tiers using KMeans.

---

## 🚀 Local Setup

```bash
git clone https://github.com/varunvajjha14/marketlens.git
cd marketlens

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env          # add your GROQ_API_KEY

# Run the data pipeline
python src/ingestion/places_collector.py
python src/pipeline/etl.py
python src/ml/opportunity_scorer.py

# Launch dashboard
python src/dashboard/app.py
# Open http://localhost:8050
```

---

## 📁 Project Structure
marketlens/

├── data/

│   ├── raw/              ← OSM venue data (24 ward JSON files)

│   ├── processed/        ← Cleaned CSVs, ward feature table, scores

│   └── geojson/          ← Mumbai ward boundary polygons

├── src/

│   ├── ingestion/        ← Overpass API data collection

│   ├── pipeline/         ← ETL + ward aggregation

│   ├── ml/               ← Opportunity scoring model

│   ├── dashboard/        ← Plotly Dash app (pages, callbacks, layouts)

│   └── ai/               ← Groq LLaMA insight generator

├── notebooks/            ← EDA notebooks

└── config/               ← Settings, ward coordinates

---

## 🗺️ Data Coverage

| Metric | Value |
|--------|-------|
| Wards Analysed | 24 |
| Total Venues Mapped | 1,038 |
| High Opportunity Wards | 5 |
| Avg Delivery Penetration | 3.2% |
| Data Source | OpenStreetMap via Overpass API |
| Last Updated | June 2026 |

---

## 🔮 Roadmap

### v1.1 — Data & Export
- [ ] Power BI / Tableau export template
- [ ] CSV download button in dashboard
- [ ] Ward data confidence score indicator

### v1.2 — Richer Data
- [ ] BMC census data integration (population density, income proxy)
- [ ] Zomato / Swiggy restaurant count as supplementary signal
- [ ] Historical venue growth tracking

### v1.3 — Product
- [ ] User accounts + saved ward watchlists
- [ ] Email alerts for ward score changes
- [ ] API endpoint for ward scores

---

## 🔗 Links

- **Live Demo**: https://marketlens-production-62ae.up.railway.app/chat
- **Portfolio**: [FleetPulse](https://fleetpulse-beta.vercel.app) — B2B SaaS delivery management platform
- **GitHub**: [github.com/varunvajjha14](https://github.com/varunvajjha14)

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

*Built with OpenStreetMap data © OpenStreetMap contributors*