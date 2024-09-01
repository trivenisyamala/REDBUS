import mysql.connector
import streamlit as st
import pandas as pd

# Establish a connection to the MySQL database
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Syamala@9666",
        database="redbus"
    )

@st.cache_data(ttl=600)
def get_unique_values(column_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"SELECT DISTINCT {column_name} FROM bus_routes"
    cursor.execute(query)
    result = [row[0] for row in cursor.fetchall()]
    conn.close()
    return result

def fetch_data_with_limit(offset=0, limit=10, query=None, sort_column=None, sort_order='ASC'):
    conn = get_db_connection()
    cursor = conn.cursor()

    if query:
        if sort_column:
            query += f" ORDER BY {sort_column} {sort_order} LIMIT {limit} OFFSET {offset}"
        else:
            query += f" LIMIT {limit} OFFSET {offset}"
    else:
        query = f"SELECT * FROM bus_routes LIMIT {limit} OFFSET {offset}"

    cursor.execute(query)
    data = cursor.fetchall()
    column_names = [i[0] for i in cursor.description]
    conn.close()
    return pd.DataFrame(data, columns=column_names)

# Streamlit app
def main():
    st.sidebar.title("Filters")

    # Fetch unique values for the dropdowns
    states = get_unique_values("state")
    bus_types = get_unique_values("bustype")
    routes = get_unique_values("route_name")
    departure_times = get_unique_values("departing_time")

    # Create filter options in the sidebar
    selected_state = st.sidebar.selectbox("Select State", ["All"] + states)
    selected_bus_type = st.sidebar.selectbox("Select Bus Type", ["All"] + bus_types)
    selected_route = st.sidebar.selectbox("Select Route", ["All"] + routes)
    selected_departure_time = st.sidebar.selectbox("Select Departure Time", ["All"] + departure_times)

    # Add a Search button in the sidebar
    search_button = st.sidebar.button("Search")

    st.title("Redbus Data Analysis")
    st.write("Data fetched from MySQL database with filters applied:")

    # Pagination variables
    limit = 10
    if 'offset' not in st.session_state:
        st.session_state.offset = 0

    if search_button or st.session_state.offset == 0:
        # Build the SQL query based on selected filters
        query = "SELECT * FROM bus_routes WHERE 1=1"
        
        if selected_state != "All":
            query += f" AND state = '{selected_state}'"
        if selected_bus_type != "All":
            query += f" AND bustype = '{selected_bus_type}'"
        if selected_route != "All":
            query += f" AND route_name = '{selected_route}'"
        if selected_departure_time != "All":
            query += f" AND departing_time = '{selected_departure_time}'"

        # Store the query in the session state
        st.session_state.query = query
        st.session_state.offset = 0

    # Fetch columns for the sorting selectbox
    df_sample = fetch_data_with_limit(limit=1, query=st.session_state.query)  # Fetch one row to get columns
    sort_column = st.selectbox("Sort by", options=["None"] + list(df_sample.columns))
    sort_order = st.radio("Order", options=["Ascending", "Descending"])

    if sort_column == "None":
        sort_column = None
    else:
        sort_order = 'ASC' if sort_order == "Ascending" else 'DESC'

    # Fetch and display the data
    df = fetch_data_with_limit(offset=st.session_state.offset, limit=limit, query=st.session_state.query, sort_column=sort_column, sort_order=sort_order)
    st.table(df)

    # Next button for pagination
    if len(df) == limit:
        if st.button("Next"):
            st.session_state.offset += limit
            st.experimental_rerun()

    # Previous button for pagination
    if st.session_state.offset > 0:
        if st.button("Previous"):
            st.session_state.offset -= limit
            st.experimental_rerun()

if __name__ == "__main__":
    main()
