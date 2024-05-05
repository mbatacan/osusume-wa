import streamlit as st
import pandas as pd
import os
import plotly.express as px

# Get the absolute path to the root directory of your project
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Construct the absolute path to the CSV file
csv_file_path = os.path.join(root_dir, 'data', 'one_piece_episode_sentiments.csv')

# Load the data
df = pd.read_csv(csv_file_path)

# Set the title of the app
st.title('One Piece: Episode Success Metrics')

# Create a line chart of the 'success_metric' column with plotly
fig = px.line(
    df,
    y='success_metric',
    labels={'index': 'Episode', 'value': 'Success Metric'},
    title='Success Metric Over Episodes',
)

# Display the line chart
st.plotly_chart(fig)
