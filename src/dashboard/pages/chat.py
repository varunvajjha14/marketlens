from dash import html, dcc
import dash_bootstrap_components as dbc

EXAMPLE_QUESTIONS = [
    "Where should I open a cafe in Mumbai?",
    "Which ward has the least competition?",
    "Best area for a pizza place under ₹15 lakh?",
    "Which wards have zero delivery penetration?",
    "Where is the biggest fast food gap?",
]


def layout():
    return html.Div([

        html.Div([
            html.Div([
                html.H1("AI Market Consultant", style={
                    "fontWeight": "800", "color": "white",
                    "fontSize": "2rem", "margin": "0 0 6px",
                }),
                html.P("Ask MarketLens anything about Mumbai food market opportunities",
                       style={"color": "rgba(255,255,255,0.65)", "margin": "0"}),
            ], style={"maxWidth": "800px", "margin": "0 auto", "padding": "0 24px"}),
        ], style={
            "background": "linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%)",
            "padding": "36px 0 28px",
        }),

        html.Div([

            html.P("Try asking:", style={
                "fontWeight": "600", "color": "#555",
                "fontSize": "0.88rem", "marginBottom": "10px",
            }),
            html.Div([
                html.Button(
                    q,
                    id={"type": "chip", "index": i},
                    n_clicks=0,
                    className="chip-btn",
                )
                for i, q in enumerate(EXAMPLE_QUESTIONS)
            ], style={"display": "flex", "flexWrap": "wrap",
                      "gap": "8px", "marginBottom": "20px"}),

            html.Div(
                id="chat-history",
                children=[_welcome_message()],
                style={
                    "minHeight": "360px", "maxHeight": "460px",
                    "overflowY": "auto", "padding": "16px",
                    "backgroundColor": "#f8f9fa", "borderRadius": "12px",
                    "marginBottom": "12px", "border": "1px solid #e9ecef",
                },
            ),

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
                        "border": "2px solid #0f3460",
                        "borderRight": "none",
                        "fontSize": "0.95rem",
                        "fontFamily": "Inter, sans-serif",
                        "outline": "none",
                    },
                ),
                html.Button(
                    "Ask →", id="chat-submit", n_clicks=0,
                    style={
                        "padding": "12px 24px",
                        "borderRadius": "0 8px 8px 0",
                        "backgroundColor": "#0f3460", "color": "white",
                        "border": "2px solid #0f3460",
                        "fontWeight": "700", "fontSize": "0.95rem",
                        "cursor": "pointer",
                        "fontFamily": "Inter, sans-serif",
                    },
                ),
            ], style={"display": "flex"}),

        ], style={"maxWidth": "800px", "margin": "0 auto", "padding": "36px 24px"}),

        html.Footer([
            html.P("MarketLens · OpenStreetMap · scikit-learn · Plotly Dash · Groq LLaMA",
                   style={"textAlign": "center", "color": "#aaa",
                          "fontSize": "0.82rem", "margin": "0"}),
        ], style={"backgroundColor": "#1a1a2e", "padding": "20px"}),
    ])


def _welcome_message():
    return html.Div([
        html.Span("🤖 ", style={"fontSize": "1.2rem"}),
        html.Span(
            "Hi! I have real data on all 24 Mumbai wards. Ask me where to open "
            "your next restaurant, which ward has the least competition, or "
            "anything about Mumbai's food market.",
            style={"fontSize": "0.9rem", "color": "#444"},
        ),
    ], style={
        "backgroundColor": "white", "borderRadius": "12px",
        "padding": "14px 16px", "marginBottom": "10px",
        "border": "1px solid #e9ecef", "maxWidth": "85%",
    })