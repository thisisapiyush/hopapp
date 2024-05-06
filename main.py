import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Function to create a database connection
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

# Function to create a table in the database
def create_table(conn):
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS Users (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        stamps INTEGER
                     )''')
    except sqlite3.Error as e:
        print(e)

# Function to create a table for orders in the database
def create_orders_table(conn):
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS Orders (
                        id INTEGER PRIMARY KEY,
                        customer_id INTEGER,
                        coffee_type TEXT,
                        quantity INTEGER,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(customer_id) REFERENCES Users(id)
                     )''')
    except sqlite3.Error as e:
        print(e)

# Function to insert data into the Users table
def insert_data(conn, name, stamps):
    sql = ''' INSERT INTO Users(name, stamps)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, (name, stamps))
    conn.commit()
    return cur.lastrowid

# Function to insert data into the Orders table
def insert_order(conn, customer_id, coffee_type, quantity):
    sql = ''' INSERT INTO Orders(customer_id, coffee_type, quantity)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, (customer_id, coffee_type, quantity))
    conn.commit()
    return cur.lastrowid

# Function to update stamps count for a customer
def update_stamps(conn, customer_id, quantity):
    # Update stamps count for the customer
    sql = '''UPDATE Users SET stamps = stamps + ? WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, (quantity, customer_id))
    conn.commit()

# Function to retrieve orders from the database
def select_orders(conn):
    cur = conn.cursor()
    cur.execute("SELECT o.id, u.name, o.coffee_type, o.quantity, datetime(o.timestamp, 'localtime') FROM Orders o INNER JOIN Users u ON o.customer_id = u.id")
    rows = cur.fetchall()
    return rows

# Function to define the Orders Received page
def orders_received_page(conn):
    st.title('Orders Received')

    # Display existing orders in tables
    rows = select_orders(conn)
    if rows:
        st.write("Existing Orders:")
        df = pd.DataFrame(rows, columns=["Order ID", "Customer's Name", "Coffee Type", "Quantity", "Timestamp"])
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['Timestamp'] = df['Timestamp'].dt.strftime("%d %B, %Y, %A, %Y, %I:%M %p")
        st.write(df)
    else:
        st.write("No orders received")

# Function to define the Coffee Order page
def order_page(conn):
    st.title('Place Coffee Order')

    # Retrieve existing customer data for dropdown menu
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM Users")
    customer_data = cur.fetchall()

    # Create a dropdown menu for selecting customer
    selected_customer_id = st.selectbox("Select customer:", [f"{name} (ID: {id})" for id, name in customer_data])

    # Extract customer ID from selected option if a customer is selected
    if selected_customer_id:
        selected_customer_id = int(selected_customer_id.split("(ID: ")[1].split(")")[0])
    else:
        st.warning("Please select a customer.")

    # Coffee types
    coffee_types = ["Espresso", "Latte", "Cappuccino", "Americano", "Mocha", "Macchiato"]

    # Add a dropdown menu for selecting coffee type
    coffee_type = st.selectbox("Select coffee type:", coffee_types)

    # Add a number input widget for quantity
    quantity = st.number_input("Enter quantity", min_value=1, step=1)

    # Add a button widget to submit order
    if st.button("Place Order"):
        # Insert order into the database
        insert_order(conn, selected_customer_id, coffee_type, quantity)

        # Update stamps count for the customer
        update_stamps(conn, selected_customer_id, quantity)

        st.success("Order placed successfully!")

# Function to define the input page
def input_page(conn):
    st.title('Loyalty Points')

    # Add a text input widget
    customer_name = st.text_input("Enter customer's name", "John Doe")

    # Add a slider widget
    number_of_stamps = st.slider("Select the number of stamps collected", 0, 100, 25)

    # Add a button widget to submit data
    if st.button("Add to database"):
        # Insert data into the database
        insert_data(conn, customer_name, number_of_stamps)

# Function to retrieve data from the database
def select_data(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, name, stamps FROM Users")
    rows = cur.fetchall()
    return rows

# Function to define the Customer Data page
def results_page(conn):
    st.title('Customer Data')

    # Display existing data in tables
    rows = select_data(conn)
    if rows:
        st.write("Existing Data:")
        df = pd.DataFrame(rows, columns=["User ID", "Customer's Name", "Stamps"])
        st.write(df)
    else:
        st.write("No data available")

# Main function to control the app flow
def main():
    # Create a database connection
    conn = create_connection("customer_database.db")
    if conn is not None:
        # Create tables if they don't exist
        create_table(conn)
        create_orders_table(conn)

        # Render the input page by default
        page = st.sidebar.radio("Navigation", ["Loyalty Points Entry Point", "Customer Data", "Place Coffee Order", "Orders Received"])

        # Control the navigation based on the selected page
        if page == "Loyalty Points Entry Point":
            input_page(conn)
        elif page == "Customer Data":
            results_page(conn)
        elif page == "Place Coffee Order":
            order_page(conn)
        elif page == "Orders Received":
            orders_received_page(conn)

        # Close the database connection
        conn.close()
    else:
        st.error("Error: Could not establish a database connection.")

if __name__ == "__main__":
    main()
