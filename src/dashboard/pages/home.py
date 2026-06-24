from dash import html, dcc, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc
import pandas as pd
from pathlib import Path
from functools import lru_cache

PROCESSED_DIR = Path(__file__).resolve().parents[3] / "data" / "processed"

BUSINESS_TYPES = {
    "cafe":          {"label": "☕ Cafe",           "weight_fast_food": -0.1, "weight_cafe": 0.4,  "weight_restaurant": 0.1},
    "pizza":         {"label": "🍕 Pizza Place",     "weight_fast_food": 0.2,  "weight_cafe": -0.1, "weight_restaurant": 0.2},
    "cloud_kitchen": {"label": "📦 Cloud Kitchen",   "weight_fast_food": 0.3,  "weight_cafe": 0.1,  "weight_restaurant": 0.2},
    "bakery":        {"label": "🥐 Bakery",          "weight_fast_food": -0.1, "weight_cafe": 0.3,  "weight_restaurant": 0.0},
    "south_indian":  {"label": "🍛 South Indian",    "weight_fast_food": 0.1,  "weight_cafe": 0.0,  "weight_restaurant": 0.3},
    "chinese":       {"label": "🥡 Chinese",         "weight_fast_food": 0.2,  "weight_cafe": -0.1, "weight_restaurant": 0.2},
}

BUDGETS = ["₹5 lakh", "₹10 lakh", "₹15 lakh", "₹20 lakh+"]


@lru_cache(maxsize=1)
def load_scores():
    return pd.read_csv(PROCESSED_DIR / "ward_scores.csv")


def layout():
    df = load_scores()
    top3 = df.sort_values("opportunity_score", ascending=False).head(3)

    return html.Div([

        # ── HERO ────────────────────────────────────────────────
        html.Div([
            html.Div(className="hero-glow"),
            html.Div([

                # Left column
                html.Div([
                    html.Div("MARKET INTELLIGENCE PLATFORM", style={
                        "fontSize": "0.72rem", "fontWeight": "700",
                        "color": "rgba(255,255,255,0.5)",
                        "letterSpacing": "3px", "marginBottom": "16px",
                    }),
                    html.H1(
                        "Find underserved food markets before your competitors do.",
                        className="hero-content",
                        style={
                            "fontSize": "2.6rem", "fontWeight": "800",
                            "color": "white", "margin": "0 0 16px",
                            "lineHeight": "1.15", "letterSpacing": "-1px",
                        }
                    ),
                    html.P(
                        "Analyze Mumbai's 24 wards using venue density, cuisine gaps, "
                        "delivery penetration and AI-generated market insights.",
                        className="hero-content-delay-1",
                        style={
                            "color": "rgba(255,255,255,0.65)",
                            "fontSize": "1rem", "lineHeight": "1.6",
                            "margin": "0 0 32px", "maxWidth": "420px",
                        }
                    ),
                    html.Div([
                        dcc.Link(
                            html.Button("Start Analysis →",
                                        className="ml-btn-primary btn-hero"),
                            href="/dashboard",
                        ),
                        dcc.Link(
                            html.Button("Talk to AI Analyst",
                                        className="ml-btn-outline btn-hero"),
                            href="/chat",
                        ),
                    ], className="hero-content-delay-2",
                       style={"display": "flex", "gap": "12px",
                              "flexWrap": "wrap", "marginBottom": "40px"}),

                    # KPI pills
                    html.Div([
                        _kpi_pill("1,038", "Venues"),
                        _kpi_pill("24",    "Wards"),
                        _kpi_pill("5",     "High Opportunity"),
                        _kpi_pill("3.2%",  "Avg Delivery"),
                    ], className="hero-content-delay-2",
                       style={"display": "flex", "gap": "10px", "flexWrap": "wrap"}),

                ], style={"flex": "1", "minWidth": "300px"}),

                # Right column — live opportunity preview
                html.Div([
                    html.Div([
                        html.Div("🗺️  Live Opportunity Scores", style={
                            "fontSize": "0.78rem", "fontWeight": "700",
                            "color": "rgba(255,255,255,0.5)",
                            "letterSpacing": "1px", "marginBottom": "16px",
                        }),
                        *[_score_row(row) for _, row in top3.iterrows()],
                        html.Div([
                            html.Span("·  ·  ·", style={
                                "color": "rgba(255,255,255,0.2)",
                                "fontSize": "1.2rem", "letterSpacing": "4px",
                            }),
                            html.Span("21 more wards", style={
                                "color": "rgba(255,255,255,0.3)",
                                "fontSize": "0.8rem", "marginLeft": "10px",
                            }),
                        ], style={"marginTop": "12px"}),
                    ], style={
                        "backgroundColor": "rgba(255,255,255,0.06)",
                        "border": "1px solid rgba(255,255,255,0.12)",
                        "borderRadius": "16px", "padding": "24px",
                        "backdropFilter": "blur(10px)",
                    }),
                ], style={
                    "flex": "0 0 300px",
                    "animation": "fadeSlideUp 0.9s cubic-bezier(0.22,1,0.36,1) 0.3s both",
                }),

            ], style={
                "display": "flex", "gap": "48px", "alignItems": "center",
                "flexWrap": "wrap",
                "maxWidth": "1100px", "margin": "0 auto",
                "padding": "72px 32px 64px",
                "position": "relative", "zIndex": "1",
            }),
        ], style={
            "background": "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)",
            "position": "relative", "overflow": "hidden",
        }),

        # ── WHO IT'S FOR ────────────────────────────────────────
        html.Div([
            html.Div([
                html.H2("Built for food entrepreneurs", style={
                    "fontWeight": "700", "color": "#1a1a2e",
                    "marginBottom": "8px", "fontSize": "1.7rem",
                }),
                html.P("Whether you're opening your first outlet or your tenth,\n"
                       "MarketLens tells you where the real opportunity is.",
                       style={"color": "#888", "marginBottom": "40px",
                              "fontSize": "0.95rem"}),
                html.Div([
                    _persona("🍽️", "Restaurant Owners",
                             "Find wards with low competition and high footfall potential."),
                    _persona("📦", "Cloud Kitchen Founders",
                             "Identify delivery gaps — wards where almost no one delivers."),
                    _persona("💰", "Investors & Franchisors",
                             "Spot underserved markets before they get crowded."),
                    _persona("☕", "Cafe & QSR Operators",
                             "Match your format to the ward that needs it most."),
                ], style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fill, minmax(220px, 1fr))",
                    "gap": "20px",
                }),
            ], style={"maxWidth": "1000px", "margin": "0 auto"}),
        ], style={"padding": "72px 24px", "backgroundColor": "white"}),

        # ── OPPORTUNITY SIMULATOR ────────────────────────────────
        html.Div([
            html.Div([
                html.H2("Opportunity Simulator", style={
                    "fontWeight": "700", "color": "white",
                    "marginBottom": "6px", "fontSize": "1.7rem",
                }),
                html.P("Tell us what you want to open — we'll find the best ward for it.",
                       style={"color": "rgba(255,255,255,0.6)", "marginBottom": "32px"}),

                # Simulator inputs
                html.Div([
                    html.Div([
                        html.Label("Business Type", style={
                            "color": "rgba(255,255,255,0.7)",
                            "fontSize": "0.83rem", "fontWeight": "600",
                            "marginBottom": "8px", "display": "block",
                        }),
                        dcc.Dropdown(
                            id="sim-business",
                            options=[{"label": v["label"], "value": k}
                                     for k, v in BUSINESS_TYPES.items()],
                            value="cafe",
                            clearable=False,
                            style={"borderRadius": "8px", "fontSize": "0.9rem"},
                        ),
                    ], style={"flex": "1", "minWidth": "180px"}),

                    html.Div([
                        html.Label("Budget", style={
                            "color": "rgba(255,255,255,0.7)",
                            "fontSize": "0.83rem", "fontWeight": "600",
                            "marginBottom": "8px", "display": "block",
                        }),
                        dcc.Dropdown(
                            id="sim-budget",
                            options=[{"label": b, "value": b} for b in BUDGETS],
                            value="₹10 lakh",
                            clearable=False,
                            style={"borderRadius": "8px", "fontSize": "0.9rem"},
                        ),
                    ], style={"flex": "0 0 160px"}),

                    html.Div([
                        html.Label("\u00a0", style={
                            "display": "block", "marginBottom": "8px",
                            "fontSize": "0.83rem",
                        }),
                        html.Button(
                            "Analyse Market →",
                            id="sim-submit", n_clicks=0,
                            style={
                                "width": "100%", "height": "38px",
                                "padding": "0 20px",
                                "backgroundColor": "white",
                                "color": "#0f3460",
                                "border": "none", "borderRadius": "6px",
                                "fontWeight": "700", "fontSize": "0.9rem",
                                "cursor": "pointer",
                                "fontFamily": "Inter, sans-serif",
                            },
                        ),
                    ], style={"flex": "0 0 180px"}),

                ], style={
                    "display": "flex", "gap": "16px",
                    "flexWrap": "wrap", "alignItems": "flex-end",
                    "marginBottom": "28px",
                }),

                # Result panel
                html.Div(id="sim-result", children=_sim_placeholder()),

            ], style={"maxWidth": "860px", "margin": "0 auto"}),
        ], style={
            "background": "linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%)",
            "padding": "72px 24px",
        }),

        # ── HOW IT WORKS ────────────────────────────────────────
        html.Div([
            html.Div([
                html.H2("How It Works", style={
                    "fontWeight": "700", "color": "#1a1a2e",
                    "marginBottom": "8px", "fontSize": "1.7rem",
                }),
                html.P("From raw data to actionable market intelligence in three steps.",
                       style={"color": "#888", "marginBottom": "40px"}),
                html.Div([
                    _step("01", "Data Collection", "🗂️",
                          "1,038 food & beverage venues collected from OpenStreetMap "
                          "across Mumbai's 24 administrative wards."),
                    _step("02", "ML Scoring", "🧠",
                          "A weighted opportunity model scores each ward on scarcity, "
                          "delivery gaps, cuisine diversity, and chain saturation."),
                    _step("03", "AI Insights", "🤖",
                          "Groq LLaMA generates plain-English market briefs and answers "
                          "your questions using real ward data."),
                ], style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(3, 1fr)",
                    "gap": "24px",
                }),
            ], style={"maxWidth": "1000px", "margin": "0 auto"}),
        ], style={"padding": "72px 24px", "backgroundColor": "#f8f9fa"}),

        # ── FOOTER ──────────────────────────────────────────────
        html.Footer([
            html.P(
                "MarketLens · OpenStreetMap · scikit-learn · Plotly Dash · Groq LLaMA",
                style={"textAlign": "center", "color": "#aaa",
                       "fontSize": "0.82rem", "margin": "0"},
            ),
        ], style={"backgroundColor": "#1a1a2e", "padding": "24px"}),

    ])


# ── Helper components ────────────────────────────────────────────────────────

def _sim_placeholder():
    return html.Div([
        html.Div("⬆️", style={"fontSize": "2rem", "marginBottom": "8px"}),
        html.P("Select a business type and budget, then click Analyse Market.",
               style={"color": "rgba(255,255,255,0.4)", "margin": "0",
                      "fontSize": "0.9rem"}),
    ], style={"textAlign": "center", "padding": "32px 0"})


def _sim_stat(label, value):
    return html.Div([
        html.Div(label, style={
            "fontSize": "0.72rem", "color": "rgba(255,255,255,0.4)",
            "fontWeight": "600", "letterSpacing": "1px", "marginBottom": "2px",
        }),
        html.Div(value, style={
            "fontSize": "1rem", "color": "white", "fontWeight": "700",
        }),
    ], style={
        "backgroundColor": "rgba(255,255,255,0.06)",
        "borderRadius": "8px", "padding": "10px 12px",
    })


def _score_row(row):
    colors = {"High": "#2ecc71", "Medium": "#f39c12", "Low": "#e74c3c"}
    color  = colors.get(row["opportunity_tier"], "#888")
    bar_w  = f"{row['opportunity_score']}%"
    return html.Div([
        html.Div([
            html.Span(row["ward_name"], style={
                "color": "white", "fontWeight": "600", "fontSize": "0.88rem",
            }),
            html.Span(f"{row['opportunity_score']:.0f}", style={
                "color": color, "fontWeight": "800", "fontSize": "0.95rem",
            }),
        ], style={"display": "flex", "justifyContent": "space-between",
                  "marginBottom": "6px"}),
        html.Div([
            html.Div(style={
                "width": bar_w, "height": "4px",
                "backgroundColor": color, "borderRadius": "2px",
                "transition": "width 0.6s ease",
            }),
        ], style={
            "backgroundColor": "rgba(255,255,255,0.08)",
            "borderRadius": "2px", "marginBottom": "14px",
        }),
    ])


def _kpi_pill(value, label):
    return html.Div([
        html.Span(value, style={
            "fontWeight": "800", "fontSize": "1rem", "color": "white",
        }),
        html.Span(f" {label}", style={
            "fontSize": "0.78rem", "color": "rgba(255,255,255,0.55)",
        }),
    ], style={
        "backgroundColor": "rgba(255,255,255,0.08)",
        "border": "1px solid rgba(255,255,255,0.15)",
        "borderRadius": "20px", "padding": "5px 14px",
        "display": "inline-flex", "alignItems": "center", "gap": "3px",
    })


def _persona(icon, title, desc):
    return html.Div([
        html.Div(icon, style={"fontSize": "1.8rem", "marginBottom": "10px"}),
        html.H5(title, style={
            "fontWeight": "700", "color": "#1a1a2e",
            "marginBottom": "6px", "fontSize": "1rem",
        }),
        html.P(desc, style={
            "color": "#777", "fontSize": "0.88rem",
            "lineHeight": "1.5", "margin": "0",
        }),
    ], style={
        "padding": "22px", "borderRadius": "12px",
        "border": "1px solid #f0f0f0",
        "transition": "transform 0.2s ease, box-shadow 0.2s ease",
    }, className="step-card")


def _step(num, title, icon, desc):
    return html.Div([
        html.Div(icon, style={"fontSize": "1.8rem", "marginBottom": "10px"}),
        html.Div(num, style={
            "fontSize": "0.72rem", "fontWeight": "800", "color": "#0f3460",
            "letterSpacing": "2px", "marginBottom": "6px",
        }),
        html.H4(title, style={
            "fontWeight": "700", "color": "#1a1a2e",
            "marginBottom": "8px", "fontSize": "1rem",
        }),
        html.P(desc, style={
            "color": "#777", "lineHeight": "1.6",
            "fontSize": "0.88rem", "margin": "0",
        }),
    ], style={
        "padding": "24px", "borderRadius": "12px",
        "border": "1px solid #e8e8e8",
        "transition": "transform 0.2s ease",
    }, className="step-card")


def _ward_card(name, score, tier, meta):
    colors = {"High": "#2ecc71", "Medium": "#f39c12", "Low": "#e74c3c"}
    return html.Div([
        html.Span(tier, style={
            "backgroundColor": colors[tier], "color": "white",
            "fontSize": "0.72rem", "fontWeight": "700",
            "padding": "2px 10px", "borderRadius": "20px",
        }),
        html.H3(name, style={
            "color": "white", "fontWeight": "700",
            "margin": "10px 0 4px", "fontSize": "1.2rem",
        }),
        html.Div([
            html.Span(score, style={
                "fontSize": "1.8rem", "fontWeight": "800",
                "color": colors[tier],
            }),
            html.Span(" / 100", style={"color": "#888", "fontSize": "0.9rem"}),
        ]),
        html.P(meta, style={
            "color": "rgba(255,255,255,0.4)",
            "fontSize": "0.78rem", "margin": "8px 0 0",
        }),
    ], className="ward-card-hover", style={
        "backgroundColor": "rgba(255,255,255,0.07)",
        "borderRadius": "12px", "padding": "20px",
        "border": "1px solid rgba(255,255,255,0.12)",
    })