#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
Created on Thu Oct  2 21:09:30 2025

@author: nielspeterjorgensen
"""
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd


# -------------------------------
# Load your dataframe
# -------------------------------
df = pd.read_csv("/Users/nielspeterjorgensen/Library/CloudStorage/OneDrive-SyddanskUniversitet/Projekter/Landings_dash/cod_landings_with_coords.csv", encoding="utf-8")

# -------------------------------
# Load your dataframe
# -------------------------------

df.rename(columns={
    "√Ör": "År",
    "Art": "Art",
    "Landingsplads": "Landingsplads",
    "Levende v√¶gt (kg)": "Levende vægt (kg)",
    "Landet v√¶gt (kg)": "Landet vægt (kg)",
    "V√¶rdi (kr)": "Værdi (kr)"
}, inplace=True)

# Ensure numeric
df["År"] = pd.to_numeric(df["År"], errors="coerce")
df["Landet vægt (kg)"] = (
    df["Landet vægt (kg)"]
    .astype(str)
    .str.replace(",", "", regex=False)
)
df["Landet vægt (kg)"] = pd.to_numeric(df["Landet vægt (kg)"], errors="coerce")
df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
df["lon"] = pd.to_numeric(df["lon"], errors="coerce")

# -------------------------------
# Build Dash app
# -------------------------------
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Cod Landings in Denmark", style={"textAlign": "center"}),

    # Dropdown for species
    html.Label("Choose species:"),
    dcc.Dropdown(
        id="species-dropdown",
        options=[{"label": art, "value": art} for art in sorted(df["Art"].unique())],
        value="Torsk",  # default
        clearable=False
    ),

    # Dropdown for year
    html.Label("Choose year:"),
    dcc.Dropdown(
        id="year-dropdown",
        options=[{"label": year, "value": year} for year in sorted(df["År"].unique())],
        value=df["År"].min(),  # default to first year
        clearable=False
    ),
    
    html.Label("Select ports:"),
dcc.Dropdown(
    id="ports-dropdown",
    options=[{"label": port, "value": port} for port in sorted(df["Landingsplads"].unique())],
    value=[df["Landingsplads"].unique()[0]],  # default selection
    multi=True  # allow multiple selections
    ),

    # Map
    dcc.Graph(id="map-plot", style={"height": "70vh"}),

    html.H2("Time series for selected port"),
    dcc.Graph(id="timeseries-plot", style={"height": "40vh"})
])

# -------------------------------
# Callbacks
# -------------------------------
@app.callback(
    Output("map-plot", "figure"),
    Input("species-dropdown", "value"),
    Input("year-dropdown", "value")
)
def update_map(selected_species, selected_year):
    dff = df[(df["Art"] == selected_species) & (df["År"] == selected_year)]

    fig = px.scatter_mapbox(
        dff,
        lat="lat",
        lon="lon",
        size="Landet vægt (kg)",
        color="Landet vægt (kg)",
        hover_name="Landingsplads",
        hover_data={
            "Landet vægt (kg)": True,
            "Værdi (kr)": True,
            "lon": False,
            "lat": False
        },
        zoom=5,
        height=1000,
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_center={"lat": 56.0, "lon": 10.0},
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    return fig


@app.callback(
    Output("timeseries-plot", "figure"),
    Input("ports-dropdown", "value"),
    Input("species-dropdown", "value")
)
def update_timeseries(selected_ports, selected_species):
    if not selected_ports:
        return px.line(title="Select one or more ports to see time series")

    dff = df[(df["Landingsplads"].isin(selected_ports)) & (df["Art"] == selected_species)]

    fig = px.line(
        dff,
        x="År",
        y="Landet vægt (kg)",
        color="Landingsplads",
        markers=True,
        title="Landings over time"
    )
    fig.update_layout(yaxis_title="Landet vægt (kg)")
    return fig

# -------------------------------
# Run app
# -------------------------------
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=False)