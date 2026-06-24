import json
import pandas as pd
import plotly.express as px
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
from pathlib import Path
from functools import lru_cache

PROCESSED_DIR = Path(__file__).resolve().parents[2] / "data" / "processed"
GEOJSON_PATH  = Path(__file__).resolve().parents[2] / "data" / "geojson" / "mumbai_wards.geojson"
TIER_COLORS   = {"High": "#2ecc71", "Medium": "#f39c12", "Low": "#e74c3c"}

EXAMPLE_QUESTIONS = [
    "Where should I open a cafe in Mumbai?",
    "Which ward has the least competition?",
    "Best area for a pizza place under ₹15 lakh?",
    "Which wards have zero delivery penetration?",
]


@lru_cache(maxsize=1)
def load_scores():
    return pd.read_csv(PROCESSED_DIR / "ward_scores.csv")


@lru_cache(maxsize=1)
def load_geojson():
    with open(GEOJSON_PATH) as f:
        return json.load(f)


@lru_cache(maxsize=1)
def build_map():
    df      = load_scores()
    geojson = load_geojson()
    fig = px.choropleth_mapbox(
        df,
        geojson=geojson,
        locations="ward_name",
        featureidkey="properties.name",
        color="opportunity_score",
        color_continuous_scale=["#e74c3c", "#f39c12", "#2ecc71"],
        range_color=[0, 100],
        mapbox_style="carto-positron",
        zoom=10.5,
        center={"lat": 19.076, "lon": 72.877},
        opacity=0.75,
        hover_name="ward_name",
        hover_data={
            "opportunity_score": True,
            "opportunity_tier": True,
            "total_venues": True,
            "unique_cuisines": True,
        },
        labels={
            "opportunity_score": "Score",
            "opportunity_tier": "Tier",
            "total_venues": "Venues",
            "unique_cuisines": "Cuisines",
        },
    )
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar={"title": "Score", "thickness": 12, "len": 0.5},
        paper_bgcolor="white",
    )
    return fig


def create_layout():
    df  = load_scores()
    fig = build_map()

    return html.Div(
        style={"fontFamily": "Inter, sans-serif"},
        children=[
            # ── NAVBAR ──────────────────────────────────────────────
            html.Nav([
                html.Div([
                    html.Span("🗺️ MarketLens", style={
                        "fontWeight": "800", "fontSize": "1.2rem",
                        "color": "white", "letterSpacing": "-0.5px",
                    }),
                    html.Div([
                        html.A("Map",       href="#section-map",       className="nav-link-ml"),
                        html.A("Analytics", href="#section-analytics", className="nav-link-ml"),
                        html.A("AI Chat",   href="#section-chat",      className="nav-link-ml"),
                    ], style={"display": "flex", "gap": "4px"}),
                ], style={
                    "maxWidth": "1200px", "margin": "0 auto",
                    "display": "flex", "justifyContent": "space-between",
                    "alignItems": "center", "padding": "0 24px",
                }),
            ], className="ml-navbar", style={
                "height": "56px", "display": "flex", "alignItems": "center",
                "position": "sticky", "top": "0", "zIndex": "1000",
            }),

            # ── HERO ────────────────────────────────────────────────
            html.Div([
                html.Div(className="hero-glow"),
                html.Div([
                    html.H1("MarketLens", className="hero-content", style={
                        "fontSize": "3.5rem", "fontWeight": "800",
                        "color": "white", "margin": "0",
                        "letterSpacing": "-2px", "lineHeight": "1",
                    }),
                    html.P(
                        "Hyperlocal market intelligence for Mumbai's 24 wards",
                        className="hero-content-delay-1",
                        style={
                            "color": "rgba(255,255,255,0.7)",
                            "fontSize": "1.1rem", "margin": "12px 0 32px",
                        }
                    ),
                    # KPI pills
                    html.Div([
                        _kpi_pill("1,038", "Venues Mapped"),
                        _kpi_pill("24",    "Wards"),
                        _kpi_pill("5",     "High Opportunity"),
                        _kpi_pill("3.2%",  "Avg Delivery"),
                    ], className="hero-content-delay-2", style={
                        "display": "flex", "gap": "12px", "flexWrap": "wrap",
                    }),
                ], style={
                    "textAlign": "center", "padding": "60px 24px 50px",
                    "position": "relative", "zIndex": "1",
                    "maxWidth": "700px", "margin": "0 auto",
                }),
            ], style={
                "background": "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)",
                "position": "relative", "overflow": "hidden",
            }),

            # ── SECTION 1: MAP ──────────────────────────────────────
            html.Div(
                id="section-map", 
                style={"padding": "48px 24px 32px", "maxWidth": "1200px", "margin": "0 auto"},
                children=[
                    html.H2(
                        "Mumbai Opportunity Map", 
                        style={
                            "fontWeight": "700", 
                            "color": "#1a1a2e",
                            "marginBottom": "6px", 
                            "fontSize": "1.6rem",
                        }
                    ),
                    html.P(
                        "Hover any ward to see detailed market data",
                        style={"color": "#888", "marginBottom": "20px"}
                    ),

                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody(
                                    dcc.Graph(
                                        id="ward-map",
                                        figure=fig,
                                        style={"height": "520px"},
                                        config={"displayModeBar": False},
                                    ),
                                    style={"padding": "0"},
                                ),
                            ], className="shadow-sm border-0 rounded-3"),
                        ], width=8),

                        dbc.Col([
                            html.Div(id="ward-detail-panel", children=_default_panel()),
                        ], width=4),
                    ]),
                ]
            ),

            # ── SECTION 2: ANALYTICS ────────────────────────────────
            html.Div(id="section-analytics", style={
                "backgroundColor": "#f8f9fa",
                "padding": "48px 24px",
            }, children=[
                html.Div(style={"maxWidth": "1200px", "margin": "0 auto"}, children=[

                    html.H2("Analytics", style={
                        "fontWeight": "700", "color": "#1a1a2e",
                        "marginBottom": "6px", "fontSize": "1.6rem",
                    }),
                    html.P("Filter and compare wards by opportunity tier",
                           style={"color": "#888", "marginBottom": "24px"}),

                    # Filters
                    html.Div([
                        html.Div([
                            html.Label("Tier", style={"fontWeight": "600",
                                                       "fontSize": "0.85rem",
                                                       "color": "#555",
                                                       "marginBottom": "6px",
                                                       "display": "block"}),
                            dcc.Checklist(
                                id="tier-filter",
                                options=[
                                    {"label": "  High",   "value": "High"},
                                    {"label": "  Medium", "value": "Medium"},
                                    {"label": "  Low",    "value": "Low"},
                                ],
                                value=["High", "Medium", "Low"],
                                inline=True,
                                inputStyle={"marginRight": "4px", "marginLeft": "12px"},
                            ),
                        ]),
                        html.Div([
                            html.Label("Min Venues", style={"fontWeight": "600",
                                                              "fontSize": "0.85rem",
                                                              "color": "#555",
                                                              "marginBottom": "6px",
                                                              "display": "block"}),
                            dcc.Slider(
                                id="min-venues-slider",
                                min=0, max=50, step=5, value=10,
                                marks={0: "0", 10: "10", 25: "25", 50: "50+"},
                                tooltip={"placement": "bottom"},
                            ),
                        ], style={"width": "280px"}),
                    ], style={
                        "display": "flex", "gap": "40px", "alignItems": "flex-end",
                        "backgroundColor": "white", "padding": "16px 20px",
                        "borderRadius": "10px", "marginBottom": "24px",
                        "boxShadow": "0 1px 4px rgba(0,0,0,0.06)",
                    }),

                    # Charts row
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Opportunity Score by Ward",
                                               style={"fontWeight": "600",
                                                      "backgroundColor": "white",
                                                      "borderBottom": "1px solid #f0f0f0"}),
                                dbc.CardBody(
                                    dcc.Graph(id="bar-chart", style={"height": "400px"},
                                              config={"displayModeBar": False}),
                                    style={"padding": "8px"},
                                ),
                            ], className="shadow-sm border-0 rounded-3"),
                        ], width=7),

                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Venues vs Score",
                                               style={"fontWeight": "600",
                                                      "backgroundColor": "white",
                                                      "borderBottom": "1px solid #f0f0f0"}),
                                dbc.CardBody(
                                    dcc.Graph(id="scatter-chart", style={"height": "400px"},
                                              config={"displayModeBar": False}),
                                    style={"padding": "8px"},
                                ),
                            ], className="shadow-sm border-0 rounded-3"),
                        ], width=5),
                    ], className="mb-4"),

                    # Table
                    dbc.Card([
                        dbc.CardHeader("Ward Detail Table",
                                       style={"fontWeight": "600",
                                              "backgroundColor": "white",
                                              "borderBottom": "1px solid #f0f0f0"}),
                        dbc.CardBody(
                            html.Div(id="ward-table"),
                            style={"padding": "0"},
                        ),
                    ], className="shadow-sm border-0 rounded-3"),

                ]),
            ]),

            # ── SECTION 3: AI CHAT ──────────────────────────────────
            html.Div(id="section-chat", style={
                "padding": "48px 24px",
                "maxWidth": "900px", "margin": "0 auto",
            }, children=[

                html.H2("AI Market Consultant", style={
                    "fontWeight": "700", "color": "#1a1a2e",
                    "marginBottom": "6px", "fontSize": "1.6rem",
                }),
                html.P("Ask about Mumbai market opportunities using real ward data",
                       style={"color": "#888", "marginBottom": "24px"}),

                # Chips
                html.Div([
                    html.Button(
                        q,
                        id={"type": "chip", "index": i},
                        n_clicks=0,
                        className="chip-btn",
                    )
                    for i, q in enumerate(EXAMPLE_QUESTIONS)
                ], style={"display": "flex", "flexWrap": "wrap",
                          "gap": "8px", "marginBottom": "16px"}),

                # Chat history
                html.Div(
                    id="chat-history",
                    children=[_welcome_message()],
                    style={
                        "minHeight": "320px", "maxHeight": "440px",
                        "overflowY": "auto", "padding": "16px",
                        "backgroundColor": "#f8f9fa", "borderRadius": "12px",
                        "marginBottom": "12px", "border": "1px solid #e9ecef",
                    },
                ),

                # Input row
                html.Div([
                    dcc.Input(
                        id="chat-input",
                        placeholder="Ask about Mumbai market opportunities...",
                        type="text",
                        debounce=False,
                        n_submit=0,
                        style={
                            "flex": "1", "padding": "12px 16px",
                            "borderRadius": "8px 0 0 8px",
                            "border": "2px solid #0f3460", "borderRight": "none",
                            "fontSize": "0.95rem", "fontFamily": "Inter, sans-serif",
                            "outline": "none",
                        },
                    ),
                    html.Button(
                        "Ask →", id="chat-submit", n_clicks=0,
                        style={
                            "padding": "12px 24px",
                            "borderRadius": "0 8px 8px 0",
                            "backgroundColor": "#0f3460", "color": "white",
                            "border": "2px solid #0f3460", "fontWeight": "700",
                            "fontSize": "0.95rem", "cursor": "pointer",
                            "fontFamily": "Inter, sans-serif",
                        },
                    ),
                ], style={"display": "flex"}),
            ]),

            # ── FOOTER ──────────────────────────────────────────────
            html.Footer([
                html.P(
                    "MarketLens · OpenStreetMap · scikit-learn · Plotly Dash · Groq LLaMA",
                    style={"textAlign": "center", "color": "#aaa",
                           "fontSize": "0.82rem", "margin": "0"},
                ),
            ], style={
                "backgroundColor": "#1a1a2e", "padding": "24px",
            }),
        ]
    )


def _kpi_pill(value, label):
    return html.Div([
        html.Span(value, style={"fontWeight": "800", "fontSize": "1.1rem", "color": "white"}),
        html.Span(f"  {label}", style={"fontSize": "0.8rem",
                                        "color": "rgba(255,255,255,0.6)"}),
    ], style={
        "backgroundColor": "rgba(255,255,255,0.1)",
        "border": "1px solid rgba(255,255,255,0.2)",
        "borderRadius": "20px", "padding": "6px 16px",
        "display": "inline-flex", "alignItems": "center", "gap": "6px",
    })


def _default_panel():
    return html.Div([
        html.Div("🗺️", style={"fontSize": "2.5rem", "marginBottom": "8px"}),
        html.H6("Hover a ward", style={"fontWeight": "600", "color": "#555"}),
        html.P("Move your mouse over any ward on the map.",
               style={"color": "#999", "fontSize": "0.85rem"}),
    ], style={
        "textAlign": "center", "padding": "40px 20px",
        "backgroundColor": "white", "borderRadius": "12px",
        "boxShadow": "0 1px 4px rgba(0,0,0,0.06)",
    })


def _welcome_message():
    return html.Div([
        html.Span("🤖 ", style={"fontSize": "1.2rem"}),
        html.Span(
            "Hi! I have data on all 24 Mumbai wards. Ask me where to open "
            "your next restaurant, which ward has the least competition, or "
            "anything about Mumbai's food market.",
            style={"fontSize": "0.9rem", "color": "#444"},
        ),
    ], style={
        "backgroundColor": "white", "borderRadius": "12px",
        "padding": "14px 16px", "marginBottom": "10px",
        "border": "1px solid #e9ecef", "maxWidth": "85%",
    })