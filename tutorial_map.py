"""Choropleth map tutorial: https://towardsdatascience.com/how-to-create-outstanding-custom-choropleth-maps-with-plotly-and-dash-49ac918a5f05"""

import os
import sys
import json
import pandas as pd
import plotly.express as px
import numpy as np


BASE_PATH = os.getcwd()



def get_data():
    file_path = f"{BASE_PATH}/tutorial_data/data.csv"
    file_exists = os.path.exists(file_path)
    if not file_exists:
        # Load online dataset
        online_dataset_path = 'https://public.opendatasoft.com/explore/dataset/covid-19-pandemic-worldwide-data/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B'
        df = pd.read_csv(online_dataset_path, sep=';')
        df.to_csv(file_path)

    df = pd.read_csv (r'{}'.format(file_path))

    # Columns renaming
    df.columns = [col.lower() for col in df.columns]
    # Filtering
    df = df[df['date']=='2020-11-19'].drop('date', axis=1)
    df = df[df['category']=='Confirmed'].drop('category', axis=1)
    # Droping unnecessary colunms
    df = df[['zone', 'count']]
    # Aggregating by Zone
    df = df.groupby('zone').sum()
    df = df.reset_index(drop=False)

    return df


def get_geo_data():
    # Loading geojson from (DATA_PATH depending on your local settings)
    world_path = f"{BASE_PATH}/continent.geo.json"
    with open(world_path) as f:
        geo_world = json.load(f)

    # Instanciating necessary lists
    found = []
    missing = []
    countries_geo = []

    # For simpler acces, setting "zone" as index in a temporary dataFrame
    tmp = df.set_index('zone')

    # Looping over the custom GeoJSON file
    for country in geo_world['features']:
        # Country name detection
        country_name = country['properties']['name']
        # Checking if that country is in the dataset
        if country_name in tmp.index:
            # Adding country to our "Matched/found" countries
            found.append(country_name)
            # Getting information from both GeoJSON file and dataFrame
            geometry = country['geometry']
            # Adding 'id' information for further match between map and data
            countries_geo.append({
                'type': 'Feature',
                'geometry': geometry,
                'id':country_name
            })
        # Else, adding the country to the missing countries
        else:
            missing.append(country_name)

    # Displaying metrics
    print(f'Countries found    : {len(found)}')
    print(f'Countries not found: {len(missing)}')
    geo_world_ok = {'type': 'FeatureCollection', 'features': countries_geo}

    return geo_world_ok


def generate_plot(df, geo_world_data):
    # Create the log count column
    df['count_color'] = df['count'].apply(np.log10)

    # Get the maximum value to cap displayed values
    max_log = df['count_color'].max()
    max_val = int(max_log) + 1

    # Prepare the range of the colorbar
    values = [i for i in range(max_val)]
    ticks = [10**i for i in values]

    # Create figure
    fig = px.choropleth_mapbox(
        df,
        geojson=geo_world_data,
        locations='zone',
        color=df['count_color'],
        color_continuous_scale='YlOrRd',
        range_color=(0, df['count_color'].max()),
        hover_name='zone',
        hover_data={'count_color': False, 'zone': False, 'count': True},
        mapbox_style='open-street-map',
        zoom=1,
        center={'lat': 19, 'lon': 11},
        opacity=0.6
    )
    # Define layout specificities
    fig.update_layout(
        margin={'r':0,'t':0,'l':0,'b':0},
        coloraxis_colorbar={
            'title':'Confirmed people',
            'tickvals':values,
            'ticktext':ticks
        }
    )
    # Display figure
    fig.show()

    return


if __name__ == "__main__":
    df = get_data()
    geo_world_data = get_geo_data()
    generate_plot(df, geo_world_data)
