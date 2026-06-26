import json
import pandas as pd
import plotly.express as px
from dash import html, dcc, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc
from pathlib import Path
from functools import lru_cache


PROCESSED_DIR = Path(__file__).resolve().parents[3] / "data" / "processed"
GEOJSON_PATH  = Path(__file__).resolve().parents[3] / "data" / "geojson" / "mumbai_wards.geojson"
TIER_COLORS   = {"High": "#2ecc71", "Medium": "#f39c12", "Low": "#e74c3c"}


@lru_cache(maxsize=1)
def _load():
    df = pd.read_csv(PROCESSED_DIR / "ward_scores.csv")
    with open(GEOJSON_PATH) as f:
        geo = json.load(f)
    return df, geo


@lru_cache(maxsize=1)
def _build_map():
    df, geo = _load()
    fig = px.choropleth_mapbox(
        df,
        geojson=geo,
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
            "opportunity_tier":  True,
            "total_venues":      True,
            "unique_cuisines":   True,
        },
        labels={
            "opportunity_score": "Score",
            "opportunity_tier":  "Tier",
            "total_venues":      "Venues",
            "unique_cuisines":   "Cuisines",
        },
    )
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar={"title": "Score", "thickness": 12, "len": 0.5},
        paper_bgcolor="white",
    )
    return fig


def layout():
    df  = _load()[0]
    fig = _build_map()

    return html.Div([

        # Page header
        html.Div([
            html.Div([
                html.H1("Dashboard", style={
                    "fontWeight": "800", "color": "white",
                    "fontSize": "2rem", "margin": "0 0 6px",
                }),
                html.P("Mumbai ward opportunity map & analytics",
                       style={"color": "rgba(255,255,255,0.65)", "margin": "0"}),
            ], style={"maxWidth": "1200px", "margin": "0 auto", "padding": "0 24px"}),
        ], style={
            "background": "linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%)",
            "padding": "36px 0 28px",
        }),

        html.Div([

            # ── MAP ───────────────────────────────────────────────
            html.H3("Opportunity Map", style={
                "fontWeight": "700", "color": "#1a1a2e",
                "marginBottom": "6px",
            }),
            html.P("Hover any ward — green = high opportunity, red = saturated",
                   style={"color": "#888", "marginBottom": "16px", "fontSize": "0.9rem"}),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody(
                            dcc.Graph(id="ward-map", figure=fig,
                                      style={"height": "500px"},
                                      config={"displayModeBar": False}),
                            style={"padding": "0"},
                        ),
                    ], className="shadow-sm border-0 rounded-3"),
                ], width=8),

                dbc.Col([
                    html.Div(id="ward-detail-panel", children=_default_panel()),
                ], width=4),
            ], className="mb-5"),

            # ── ANALYTICS ─────────────────────────────────────────
            html.H3("Analytics", style={
                "fontWeight": "700", "color": "#1a1a2e", "marginBottom": "6px",
            }),
            html.P("Filter and compare wards by tier and data confidence",
                   style={"color": "#888", "marginBottom": "16px", "fontSize": "0.9rem"}),

            # Filters
            html.Div([
                html.Div([
                    html.Label("Opportunity Tier", style={
                        "fontWeight": "600", "fontSize": "0.83rem",
                        "color": "#555", "marginBottom": "6px", "display": "block",
                    }),
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
                    html.Label("Min Venues", style={
                        "fontWeight": "600", "fontSize": "0.83rem",
                        "color": "#555", "marginBottom": "6px", "display": "block",
                    }),
                    dcc.Slider(
                        id="min-venues-slider",
                        min=0, max=50, step=5, value=10,
                        marks={0: "0", 10: "10", 25: "25", 50: "50+"},
                        tooltip={"placement": "bottom"},
                    ),
                ], style={"width": "260px"}),
            ], style={
                "display": "flex", "gap": "40px", "alignItems": "flex-end",
                "backgroundColor": "white", "padding": "16px 20px",
                "borderRadius": "10px", "marginBottom": "20px",
                "boxShadow": "0 1px 4px rgba(0,0,0,0.06)",
            }),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Opportunity Score by Ward", style={
                            "fontWeight": "600", "backgroundColor": "white",
                            "borderBottom": "1px solid #f0f0f0",
                        }),
                        dbc.CardBody(
                            dcc.Graph(id="bar-chart", style={"height": "400px"},
                                      config={"displayModeBar": False}),
                            style={"padding": "8px"},
                        ),
                    ], className="shadow-sm border-0 rounded-3"),
                ], width=7),

                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Venues vs Score", style={
                            "fontWeight": "600", "backgroundColor": "white",
                            "borderBottom": "1px solid #f0f0f0",
                        }),
                        dbc.CardBody(
                            dcc.Graph(id="scatter-chart", style={"height": "400px"},
                                      config={"displayModeBar": False}),
                            style={"padding": "8px"},
                        ),
                    ], className="shadow-sm border-0 rounded-3"),
                ], width=5),
            ], className="mb-4"),

            html.Div([
                html.Div([
                    html.H3("Ward Data", style={
                        "fontWeight": "700", "color": "#1a1a2e",
                        "marginBottom": "0", "fontSize": "1.1rem",
                    }),
                    html.Div([
                        html.Button(
                            "⬇ Download CSV",
                            id="download-btn",
                            n_clicks=0,
                            style={
                                "backgroundColor": "#0f3460",
                                "color": "white",
                                "border": "none",
                                "borderRadius": "6px",
                                "padding": "8px 16px",
                                "fontSize": "0.85rem",
                                "fontWeight": "600",
                                "cursor": "pointer",
                                "fontFamily": "Inter, sans-serif",
                            }
                        ),
                        html.Button(
                            "⬇ Download Power BI Ready",
                            id="download-bi-btn",
                            n_clicks=0,
                            style={
                                "backgroundColor": "white",
                                "color": "#0f3460",
                                "border": "2px solid #0f3460",
                                "borderRadius": "6px",
                                "padding": "8px 16px",
                                "fontSize": "0.85rem",
                                "fontWeight": "600",
                                "cursor": "pointer",
                                "fontFamily": "Inter, sans-serif",
                                "marginLeft": "8px",
                            }
                        ),
                        dcc.Download(id="download-csv"),
                        dcc.Download(id="download-bi-csv"),
                    ]),
                ], style={
                    "display": "flex", "justifyContent": "space-between",
                    "alignItems": "center", "marginBottom": "16px",
                }),
            ]),
            dbc.Card([
                dbc.CardHeader("Ward Detail Table", style={
                    "fontWeight": "600", "backgroundColor": "white",
                    "borderBottom": "1px solid #f0f0f0",
                }),
                dbc.CardBody(html.Div(id="ward-table"), style={"padding": "0"}),
            ], className="shadow-sm border-0 rounded-3 mb-5"),

        ], style={"maxWidth": "1200px", "margin": "0 auto", "padding": "36px 24px"}),

        # Footer
        html.Footer([
            html.P("MarketLens · OpenStreetMap · scikit-learn · Plotly Dash · Groq LLaMA",
                   style={"textAlign": "center", "color": "#aaa",
                          "fontSize": "0.82rem", "margin": "0"}),
        ], style={"backgroundColor": "#1a1a2e", "padding": "20px"}),

    ])


def _default_panel():
    return html.Div([
        html.Div("🗺️", style={"fontSize": "2.5rem", "marginBottom": "8px"}),
        html.H6("Hover a ward", style={"fontWeight": "600", "color": "#555"}),
        html.P("Move your cursor over any ward on the map.",
               style={"color": "#999", "fontSize": "0.85rem", "margin": "0"}),
    ], style={
        "textAlign": "center", "padding": "40px 20px",
        "backgroundColor": "white", "borderRadius": "12px",
        "boxShadow": "0 1px 4px rgba(0,0,0,0.06)",
    })