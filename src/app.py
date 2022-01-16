from datetime import date
import dash
import dash_core_components as dcc
import dash_html_components as html
import inflection
import logging
import numpy as np
import pandera as pa
from typing import Dict

import banana


# NOTE logging used in banana.
# logging.basicConfig(level=logging.INFO)


# Load, validate, sort data pipeline.
df = (
    banana.get_banana_df(
        "https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1045165/",
        banana.get_file_name(banana.get_last_weekday_date(date.today())),
        "data/bananas-1nov21.csv",
    )
    .pipe(
        pa.DataFrameSchema(
            {
                "Origin": pa.Column(str, pa.Check.str_length(max_value=50)),
                "Date": pa.Column(pa.DateTime),
                "Price": pa.Column(float, pa.Check.ge(0)),
                "Units": pa.Column(str, pa.Check.eq("£/kg")),
            },
            index=pa.Index(int),
            strict=True,
            coerce=True,
        ).validate
    )
    .sort_values("Date")
)

# Define Dash app.
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "UK Banana Analytics"
app.layout = html.Div(
    children=[
        # Header.
        html.Div(
            children=[
                html.P(children="🍌", className="header-emoji"),
                html.H1(children="UK Banana Analytics", className="header-title"),
                html.P(
                    children="Average wholesale prices of bananas by country of origin. The prices are national averages of the most usual prices charged for bananas at wholesale markets in Birmingham and London.",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        # Menu.
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Origin", className="menu-title"),
                        dcc.Dropdown(
                            id="origin-filter",
                            options=[
                                {"label": inflection.titleize(origin), "value": origin}
                                for origin in np.sort(df["Origin"].unique())
                            ],
                            value="all_bananas",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Date Range", className="menu-title"),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=df["Date"].min().date(),
                            max_date_allowed=df["Date"].max().date(),
                            start_date=df["Date"].min().date(),
                            end_date=df["Date"].max().date(),
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        # Price Chart.
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="price-chart",
                        config={"displayModeBar": False},
                        figure={
                            "data": [
                                {
                                    "x": df["Date"],
                                    "y": df["Price"],
                                    "type": "lines",
                                    "hovertemplate": "£/kg %{y:.2f}" "<extra></extra>",
                                },
                            ],
                            "layout": {
                                "title": {
                                    "text": "Average Price of Bananas",
                                    "x": 0.05,
                                    "xanchor": "left",
                                },
                                "xaxis": {"fixedrange": True},
                                "yaxis": {
                                    "tickprefix": "£/kg ",
                                    "fixedrange": True,
                                },
                                "colorway": ["#F9A602"],
                            },
                        },
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)

# Define output.
@app.callback(
    dash.dependencies.Output("price-chart", "figure"),
    [
        dash.dependencies.Input("origin-filter", "value"),
        dash.dependencies.Input("date-range", "start_date"),
        dash.dependencies.Input("date-range", "end_date"),
    ],
)
def update_price_charts(origin: str, start_date: str, end_date: str) -> Dict:
    """Filter df based on new values. Return updated price chart figure dictionary.

    Args:
        origin (str): Origin filter value.
        start_date (str): Start date filter value.
        end_date (str): End date filter value.

    Returns:
        Dict: Updated price chart figure dictionary.
    """

    # Filter df.
    filtered_df = df[
        (df["Origin"] == origin) & (df["Date"] >= start_date) & (df["Date"] <= end_date)
    ]

    # Updated price chart figure.
    return {
        "data": [
            {
                "x": filtered_df["Date"],
                "y": filtered_df["Price"],
                "type": "lines",
                "hovertemplate": "£/kg %{y:.2f}<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "Average Price of Bananas",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"name": "hi", "tickprefix": "£/kg ", "fixedrange": True},
            "colorway": ["#F9A602"],
        },
    }


if __name__ == "__main__":
    app.run_server(debug=True)
