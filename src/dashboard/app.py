import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap",
    ],
    title="MarketLens — Mumbai Market Intelligence",
    suppress_callback_exceptions=True,
    assets_folder="assets",
    use_pages=False,
)

from src.dashboard.callbacks import register_callbacks
register_callbacks(app)


def navbar():
    return html.Nav([
        html.Div([
            html.A("MarketLens", href="/", style={
                "fontWeight": "800", "fontSize": "1.15rem",
                "color": "white", "textDecoration": "none",
                "letterSpacing": "-0.3px",
            }),
            html.Div([
                html.A("Home",      href="/",          className="nav-link-ml"),
                html.A("Dashboard", href="/dashboard", className="nav-link-ml"),
                html.A("AI Analyst", href="/chat",     className="nav-link-ml"),
            ], style={"display": "flex", "gap": "4px"}),
        ], style={
            "maxWidth": "1200px", "margin": "0 auto", "width": "100%",
            "display": "flex", "justifyContent": "space-between",
            "alignItems": "center", "padding": "0 32px",
        }),
    ], className="ml-navbar", style={
        "height": "60px", "display": "flex", "alignItems": "center",
        "position": "sticky", "top": "0", "zIndex": "1000",
    })


app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    navbar(),
    html.Div(id="page-content"),
], style={"fontFamily": "Inter, sans-serif"})


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def route(pathname):
    if pathname == "/dashboard":
        from src.dashboard.pages.dashboard import layout
        return layout()
    elif pathname == "/chat":
        from src.dashboard.pages.chat import layout
        return layout()
    else:
        from src.dashboard.pages.home import layout
        return layout()


if __name__ == "__main__":
    app.run(debug=True, port=8050)