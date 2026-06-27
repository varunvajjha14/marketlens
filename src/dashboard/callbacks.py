import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from dash import Input, Output, State, dash_table, html, ctx, dcc
import os

PROCESSED_DIR = Path(__file__).resolve().parents[2] / "data" / "processed"
TIER_COLORS   = {"High": "#2ecc71", "Medium": "#f39c12", "Low": "#e74c3c"}

EXAMPLE_QUESTIONS = [
    "Where should I open a cafe in Mumbai?",
    "Which ward has the least competition?",
    "Best area for a pizza place under ₹15 lakh?",
    "Which wards have zero delivery penetration?",
    "Where is the biggest fast food gap?",
]

BUSINESS_TYPES = {
    "cafe":          {"label": "☕ Cafe",          "weight_fast_food": -0.1, "weight_cafe": 0.4,  "weight_restaurant": 0.1},
    "pizza":         {"label": "🍕 Pizza Place",   "weight_fast_food": 0.2,  "weight_cafe": -0.1, "weight_restaurant": 0.2},
    "cloud_kitchen": {"label": "📦 Cloud Kitchen", "weight_fast_food": 0.3,  "weight_cafe": 0.1,  "weight_restaurant": 0.2},
    "bakery":        {"label": "🥐 Bakery",        "weight_fast_food": -0.1, "weight_cafe": 0.3,  "weight_restaurant": 0.0},
    "south_indian":  {"label": "🍛 South Indian",  "weight_fast_food": 0.1,  "weight_cafe": 0.0,  "weight_restaurant": 0.3},
    "chinese":       {"label": "🥡 Chinese",       "weight_fast_food": 0.2,  "weight_cafe": -0.1, "weight_restaurant": 0.2},
}


def load_scores():
    return pd.read_csv(PROCESSED_DIR / "ward_scores.csv")


def register_callbacks(app):

    # ── Ward map hover ───────────────────────────────────────────
    @app.callback(
        Output("ward-detail-panel", "children"),
        Input("ward-map", "hoverData"),
        prevent_initial_call=True,
    )
    def update_ward_panel(hover_data):
        if not hover_data:
            return _default_panel()
        ward_name = hover_data["points"][0]["hovertext"]
        df  = load_scores()
        row = df[df["ward_name"] == ward_name]
        if row.empty:
            return _default_panel()
        r     = row.iloc[0]
        color = TIER_COLORS.get(r["opportunity_tier"], "#888")
        return html.Div([
            html.Div([
                html.Span(r["opportunity_tier"], style={
                    "backgroundColor": color, "color": "white",
                    "padding": "2px 10px", "borderRadius": "20px",
                    "fontSize": "0.78rem", "fontWeight": "700",
                }),
            ], style={"marginBottom": "10px"}),
            html.H4(ward_name, style={
                "fontWeight": "800", "color": "#1a1a2e", "margin": "0 0 4px",
            }),
            html.Div([
                html.Span(f"{r['opportunity_score']}", style={
                    "fontSize": "2.8rem", "fontWeight": "800",
                    "color": color, "lineHeight": "1",
                }),
                html.Span(" / 100", style={"color": "#aaa", "fontSize": "0.9rem"}),
            ], style={"marginBottom": "16px"}),
            html.Hr(style={"margin": "12px 0"}),
            *[_row(l, v) for l, v in [
                ("🏪 Venues",      str(int(r["total_venues"]))),
                ("🍽️ Restaurants", str(int(r["restaurant_count"]))),
                ("⚡ Fast Food",   str(int(r["fast_food_count"]))),
                ("☕ Cafes",       str(int(r["cafe_count"]))),
                ("🔗 Chains",      str(int(r["chain_count"]))),
                ("🛵 Delivery",    f"{r['delivery_ratio']*100:.1f}%"),
                ("🍜 Cuisines",    str(int(r["unique_cuisines"]))),
                ("👥 Population",  f"{int(r['population']):,}"),
                ("📍 Density",     f"{int(r['population_density']):,}/km²"),
                ("💰 Income Zone", r["avg_income_proxy"]),
                ("🏪 Venues/1k",   f"{r['venues_per_1000']:.2f}"),
            ]],
        ], style={
            "backgroundColor": "white", "borderRadius": "12px",
            "padding": "20px", "boxShadow": "0 1px 4px rgba(0,0,0,0.08)",
            "position": "sticky", "top": "72px",
        })

    # ── Analytics charts ─────────────────────────────────────────
    @app.callback(
        Output("bar-chart",     "figure"),
        Output("scatter-chart", "figure"),
        Output("ward-table",    "children"),
        Input("tier-filter",       "value"),
        Input("min-venues-slider", "value"),
    )
    def update_analytics(selected_tiers, min_venues):
        df = load_scores()
        filtered = df[
            df["opportunity_tier"].isin(selected_tiers) &
            (df["total_venues"] >= min_venues)
        ].copy()

        if filtered.empty:
            empty = go.Figure()
            empty.update_layout(paper_bgcolor="white",
                annotations=[{"text": "No data", "showarrow": False,
                               "xref": "paper", "yref": "paper",
                               "x": 0.5, "y": 0.5, "font": {"size": 16}}])
            return empty, empty, html.Div("No data.")

        bar = px.bar(
            filtered.sort_values("opportunity_score", ascending=True),
            x="opportunity_score", y="ward_name", orientation="h",
            color="opportunity_tier", color_discrete_map=TIER_COLORS,
            text="opportunity_score",
            labels={"opportunity_score": "Score", "ward_name": "",
                    "opportunity_tier": "Tier"},
        )
        bar.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        bar.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin={"l": 10, "r": 40, "t": 10, "b": 10},
            xaxis={"range": [0, 115], "gridcolor": "#f5f5f5"},
            legend={"orientation": "h", "y": -0.12},
            font={"family": "Inter, sans-serif", "size": 12},
        )

        scatter = px.scatter(
            filtered,
            x="total_venues", y="opportunity_score",
            color="opportunity_tier", color_discrete_map=TIER_COLORS,
            text="ward_name", size="unique_cuisines", size_max=28,
            labels={"total_venues": "Total Venues",
                    "opportunity_score": "Score",
                    "opportunity_tier": "Tier"},
        )
        scatter.update_traces(
            textposition="top center", textfont_size=9,
            marker={"line": {"width": 1, "color": "white"}},
        )
        scatter.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin={"l": 10, "r": 10, "t": 10, "b": 10},
            xaxis={"gridcolor": "#f5f5f5"},
            yaxis={"gridcolor": "#f5f5f5"},
            legend={"orientation": "h", "y": -0.15},
            font={"family": "Inter, sans-serif", "size": 12},
        )

        tdf = filtered[[
            "ward_name", "opportunity_score", "opportunity_tier",
            "total_venues", "unique_cuisines", "delivery_ratio",
        ]].sort_values("opportunity_score", ascending=False).copy()
        tdf.columns = ["Ward", "Score", "Tier", "Venues", "Cuisines", "Delivery %"]
        tdf["Delivery %"] = (tdf["Delivery %"] * 100).round(1).astype(str) + "%"
        tdf["Score"]      = tdf["Score"].round(1)

        table = dash_table.DataTable(
            data=tdf.to_dict("records"),
            columns=[{"name": c, "id": c} for c in tdf.columns],
            style_table={"overflowX": "auto"},
            style_header={
                "backgroundColor": "#1a1a2e", "color": "white",
                "fontWeight": "700", "fontSize": "13px", "padding": "10px 14px",
            },
            style_cell={
                "padding": "9px 14px", "fontSize": "13px",
                "fontFamily": "Inter, sans-serif", "textAlign": "left",
                "border": "none", "borderBottom": "1px solid #f0f0f0",
            },
            style_data_conditional=[
                {"if": {"filter_query": '{Tier} = "High"',   "column_id": "Tier"},
                 "color": "#2ecc71", "fontWeight": "700"},
                {"if": {"filter_query": '{Tier} = "Medium"', "column_id": "Tier"},
                 "color": "#f39c12", "fontWeight": "700"},
                {"if": {"filter_query": '{Tier} = "Low"',    "column_id": "Tier"},
                 "color": "#e74c3c", "fontWeight": "700"},
                {"if": {"row_index": "odd"}, "backgroundColor": "#fafafa"},
            ],
            page_size=12,
        )
        return bar, scatter, table

    # ── Chat: chip click fills input ─────────────────────────────
    @app.callback(
        Output("chat-input", "value"),
        [Input({"type": "chip", "index": i}, "n_clicks")
         for i in range(len(EXAMPLE_QUESTIONS))],
        prevent_initial_call=True,
    )
    def fill_chip(*args):
        triggered = ctx.triggered_id
        if not triggered:
            return ""
        return EXAMPLE_QUESTIONS[triggered["index"]]

    # ── Chat: submit message ──────────────────────────────────────
    @app.callback(
        Output("chat-history", "children"),
        Output("chat-input",   "value", allow_duplicate=True),
        Input("chat-submit", "n_clicks"),
        Input("chat-input",  "n_submit"),
        State("chat-input",  "value"),
        State("chat-history","children"),
        prevent_initial_call=True,
    )
    def handle_chat(n_clicks, n_submit, user_input, history):
        if not user_input or not user_input.strip():
            return history, ""
        text = user_input.strip()
        try:
            df       = load_scores()
            response = _call_groq(text, df)
        except Exception as e:
            response = f"Sorry, something went wrong: {str(e)}"
        return list(history) + [_user_bubble(text), _ai_bubble(response)], ""

    # ── Opportunity Simulator ─────────────────────────────────────
    @app.callback(
        Output("sim-result", "children"),
        Input("sim-submit",  "n_clicks"),
        State("sim-business","value"),
        State("sim-budget",  "value"),
        prevent_initial_call=True,
    )
    def run_simulator(n_clicks, business_type, budget):
        df     = load_scores()
        biz    = BUSINESS_TYPES.get(business_type, BUSINESS_TYPES["cafe"])
        scored = df.copy()

        total = scored["total_venues"].clip(lower=1)
        scored["adjusted_score"] = (
            scored["opportunity_score"] * 0.6
            + (scored["fast_food_count"]  / total) * biz["weight_fast_food"]  * 100
            + (scored["cafe_count"]       / total) * biz["weight_cafe"]        * 100
            + (scored["restaurant_count"] / total) * biz["weight_restaurant"]  * 100
        )
        scored["adjusted_score"] = scored["adjusted_score"].clip(0, 100)
        scored = scored[scored["total_venues"] >= 8]
        best   = scored.sort_values("adjusted_score", ascending=False).iloc[0]
        top3   = scored.sort_values("adjusted_score", ascending=False).head(3)
        color  = TIER_COLORS.get(best["opportunity_tier"], "#888")

        try:
            from dotenv import load_dotenv
            load_dotenv()
            from groq import Groq
            prompt = f"""You are MarketLens AI. A user wants to open a {biz['label']} in Mumbai with budget {budget}.
Best ward: {best['ward_name']} — score {best['opportunity_score']:.0f}/100, {int(best['total_venues'])} venues, {best['delivery_ratio']*100:.0f}% delivery, {int(best['unique_cuisines'])} cuisines.
Other options: {', '.join(top3['ward_name'].tolist()[1:])}
Write 2 sentences on why {best['ward_name']} is best. Be specific. No markdown."""
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            res    = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150, temperature=0.7,
            )
            rec = res.choices[0].message.content.strip()
        except Exception:
            rec = (f"{best['ward_name']} is your best bet — {int(best['total_venues'])} venues "
                   f"and {best['delivery_ratio']*100:.0f}% delivery penetration.")

        def stat(label, value):
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

        return html.Div([
            html.Div([
                html.Div([
                    html.Div("🏆 Best Ward", style={
                        "fontSize": "0.72rem", "fontWeight": "700",
                        "color": "rgba(255,255,255,0.5)",
                        "letterSpacing": "2px", "marginBottom": "8px",
                    }),
                    html.H2(best["ward_name"], style={
                        "color": "white", "fontWeight": "800",
                        "fontSize": "2rem", "margin": "0 0 4px",
                    }),
                    html.Div([
                        html.Span(f"{best['adjusted_score']:.0f}", style={
                            "fontSize": "2.5rem", "fontWeight": "800",
                            "color": color, "lineHeight": "1",
                        }),
                        html.Span("/100", style={
                            "color": "rgba(255,255,255,0.3)", "fontSize": "1rem",
                        }),
                    ], style={"marginBottom": "16px"}),
                    html.Div([
                        stat("Venues",   str(int(best["total_venues"]))),
                        stat("Delivery", f"{best['delivery_ratio']*100:.0f}%"),
                        stat("Cuisines", str(int(best["unique_cuisines"]))),
                        stat("Budget",   budget),
                    ], style={
                        "display": "grid", "gridTemplateColumns": "1fr 1fr",
                        "gap": "10px",
                    }),
                ], style={
                    "backgroundColor": "rgba(255,255,255,0.08)",
                    "border": f"1px solid {color}40",
                    "borderRadius": "14px", "padding": "24px",
                    "flex": "0 0 240px",
                }),

                html.Div([
                    html.Div("🤖  AI Recommendation", style={
                        "fontSize": "0.72rem", "fontWeight": "700",
                        "color": "rgba(255,255,255,0.5)",
                        "letterSpacing": "2px", "marginBottom": "12px",
                    }),
                    html.P(rec, style={
                        "color": "rgba(255,255,255,0.85)", "lineHeight": "1.7",
                        "fontSize": "0.95rem", "margin": "0 0 20px",
                    }),
                    html.Div("Also consider:", style={
                        "fontSize": "0.72rem", "fontWeight": "700",
                        "color": "rgba(255,255,255,0.4)",
                        "letterSpacing": "1px", "marginBottom": "10px",
                    }),
                    html.Div([
                        html.Div([
                            html.Span(f"#{i+2}  {row['ward_name']}", style={
                                "color": "rgba(255,255,255,0.7)",
                                "fontWeight": "600", "fontSize": "0.88rem",
                            }),
                            html.Span(f"{row['adjusted_score']:.0f}", style={
                                "color": TIER_COLORS.get(row["opportunity_tier"], "#888"),
                                "fontWeight": "700", "fontSize": "0.88rem",
                            }),
                        ], style={
                            "display": "flex", "justifyContent": "space-between",
                            "padding": "8px 12px",
                            "backgroundColor": "rgba(255,255,255,0.05)",
                            "borderRadius": "8px", "marginBottom": "6px",
                        })
                        for i, (_, row) in enumerate(list(top3.iterrows())[1:])
                    ]),
                ], style={"flex": "1"}),

            ], style={"display": "flex", "gap": "24px", "flexWrap": "wrap"}),
        ], style={
            "backgroundColor": "rgba(255,255,255,0.05)",
            "border": "1px solid rgba(255,255,255,0.1)",
            "borderRadius": "14px", "padding": "24px",
        })
    
    # ── CSV Download ──────────────────────────────────────────────
    @app.callback(
        Output("download-csv", "data"),
        Input("download-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_csv(n_clicks):
        df = load_scores()
        return dcc.send_data_frame(df.to_csv, "marketlens_ward_scores.csv", index=False)

    # ── Power BI Ready CSV Download ───────────────────────────────
    @app.callback(
        Output("download-bi-csv", "data"),
        Input("download-bi-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_bi_csv(n_clicks):
        df = load_scores()
        bi_df = df.copy()
        bi_df.columns = [
            "Ward Name", "Ward ID", "Total Venues", "Restaurant Count",
            "Fast Food Count", "Cafe Count", "Chain Count", "Independent Count",
            "Delivery Ratio %", "Unique Cuisines", "Dominant Category",
            "Population", "Population Density /km²", "Income Zone",
            "Venues Per 1000 People",
            "Opportunity Score", "Opportunity Tier",
            "Data Confidence", "Confidence %",
        ]
        bi_df["Delivery Ratio %"] = (bi_df["Delivery Ratio %"] * 100).round(1)
        return dcc.send_data_frame(bi_df.to_csv, "marketlens_powerbi_ready.csv", index=False)


def _call_groq(question: str, df: pd.DataFrame) -> str:
    from dotenv import load_dotenv
    load_dotenv()
    from groq import Groq

    summary = df[[
        "ward_name", "opportunity_score", "opportunity_tier",
        "total_venues", "restaurant_count", "fast_food_count",
        "cafe_count", "delivery_ratio", "unique_cuisines",
    ]].to_string(index=False)
    top5 = df.sort_values("opportunity_score", ascending=False).head(5)["ward_name"].tolist()

    prompt = f"""You are MarketLens AI, a market analyst for Mumbai's food sector.

Ward data:
{summary}

Top 5 opportunity wards: {', '.join(top5)}

Question: "{question}"

Answer in 3-4 sentences using real ward names and numbers. No bullet points. No markdown."""

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    res    = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=250, temperature=0.7,
    )
    return res.choices[0].message.content.strip()


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


def _row(label, value):
    return html.Div([
        html.Span(label, style={"color": "#777", "fontSize": "0.83rem"}),
        html.Span(value, style={"fontWeight": "600", "color": "#1a1a2e",
                                 "fontSize": "0.87rem"}),
    ], style={"display": "flex", "justifyContent": "space-between",
              "marginBottom": "7px"})


def _user_bubble(text):
    return html.Div(
        html.P(text, style={"margin": "0", "fontSize": "0.9rem", "color": "white"}),
        style={
            "backgroundColor": "#0f3460",
            "borderRadius": "12px 12px 0 12px",
            "padding": "10px 14px", "marginBottom": "10px",
            "maxWidth": "75%", "marginLeft": "auto",
        },
    )


def _ai_bubble(text):
    return html.Div(
        html.P(text, style={"margin": "0", "fontSize": "0.9rem", "lineHeight": "1.6"}),
        style={
            "backgroundColor": "white",
            "borderRadius": "12px 12px 12px 0",
            "padding": "14px 16px", "marginBottom": "10px",
            "border": "1px solid #e9ecef", "maxWidth": "85%",
        },
    )