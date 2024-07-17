# STREAMLITAPP LAUNCHING

import streamlit as st
import mysql.connector
import pandas as pd


# MySQL connection configuration
mysql_config = {
    'host': 'localhost',
    'database': 'redbus',
    'user': 'root',
    'password': 'Syamala@9666'
}

# Function to fetch data from MySQL
def fetch_data():
    connection = None
    try:
        connection = mysql.connector.connect(**mysql_config)
        if connection.is_connected():
            cursor = connection.cursor()
            query = "SELECT * FROM bus_routes"
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=columns)
            return df
    except mysql.connector.Error as e:
        st.error(f"Error connecting to MySQL: {e}")
    finally:
        if connection is not None and connection.is_connected():
            connection.close()

# Load data from MySQL
df = fetch_data()

print(df)

# Sidebar filters
st.sidebar.title('Filters')

# Filter by bustype
selected_bustype = st.sidebar.selectbox('Select Bus Type', df['bustype'].unique())

# Filter by route_name
selected_route = st.sidebar.selectbox('Select Route', df['route_name'].unique())

# Filter by price range
price_min = st.sidebar.number_input('Minimum Price', min_value=int(df['price'].min()), max_value=int(df['price'].max()))
price_max = st.sidebar.number_input('Maximum Price', min_value=int(df['price'].min()), max_value=int(df['price'].max()))

# Filter by star_rating
selected_star_rating = st.sidebar.slider('Select Star Rating', min_value=float(df['star_rating'].min()), max_value=float(df['star_rating'].max()))

# Filter by seats_available
selected_seats_available = st.sidebar.slider('Select Seats Available', min_value=int(df['seats_available'].min()), max_value=int(df['seats_available'].max()))

# Apply filters
filtered_df = df[
    (df['bustype'] == selected_bustype) &
    (df['route_name'] == selected_route) &
    (df['price'] >= price_min) &
    (df['price'] <= price_max) &
    (df['star_rating'] >= selected_star_rating) &
    (df['seats_available'] >= selected_seats_available)
]

# Display filtered data using Streamlit
st.title('Redbus Data Analysis')
st.write("Data fetched from MySQL database with filters applied:")

st.write(filtered_df)  # Display the DataFrame
