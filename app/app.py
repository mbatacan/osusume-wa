# app/app.py
import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go

# Get the absolute path to the root directory of your project
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load the data for all animes
data_files = os.listdir(os.path.join(root_dir, 'data'))
animes = {
    ' '.join(file.split('_')[:-2]): pd.read_csv(os.path.join(root_dir, 'data', file))
    for file in data_files
}

# Set the title of the app
st.title('Anime: Episode Success Metrics')

# Add an option to the dropdown menu to plot all animes
options = list(animes.keys()) + ['All']
selected_option = st.selectbox('Select an anime', options)

if selected_option == 'All':
    # Create a line chart with a line for each anime
    fig = go.Figure()

    for anime, df in animes.items():
        fig.add_trace(
            go.Scatter(
                x=df.episode_num, y=df['success_metric'], mode='lines', name=anime
            )
        )

    fig.update_layout(
        title='Success Metric Over Episodes for All Animes',
        xaxis_title='Episode Num',
        yaxis_title='Success Metric',
    )
else:
    # Create a line chart of the 'success_metric' column with plotly
    fig = px.line(
        animes[selected_option],  # type: ignore
        x='episode_num',
        y='success_metric',
        labels={'index': 'episode_date', 'value': 'Success Metric'},
        title=f'Success Metric Over Episodes for {selected_option}',
    )

# Display the line chart
st.plotly_chart(fig)
