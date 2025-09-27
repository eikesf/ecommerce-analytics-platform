# Import libraries
import os
import json
import requests
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s -%(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()

# Database connection configuration
DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'port':os.getenv("DB_PORT"),
    'dbname':os.getenv("DB_NAME"),
    'user':os.getenv("DB_USER"),
    'password':os.getenv("DB_PASSWORD")
}

# Define endpoints of the fake store API
API_ENDPOINTS = {
    "users": "https://fakestoreapi.com/users",
    "products": "https://fakestoreapi.com/products",
    "carts": "https://fakestoreapi.com/carts"
}

def fetch_api_data(api_url: str) -> list | None:
    """Fetches data from a given API endpoint and returns a list of dictionaries."""
    logging.info(f"Fetching data from: {api_url}")
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.exception(f"Error calling API {api_url}: {e}")
        return None
    
def upsert_data(conn, table_name: str, data: list, primary_key: str, columns: list):
    """Performs and upsert (insert/update) of data into a PostgreSQL table."""
    if not data:
        logging.info(f"No data received from API for table {table_name}. Skipping.")
        return
    
    with conn.cursor() as cursor:

        # Prepare the column string and the 'update' string
        cols_str = ", ".join(columns)
        update_str = ", ".join([f"{col} = EXCLUDED.{col}" for col in columns if col != primary_key])

        # Compare each column with the new data
        columns_to_check = [col for col in columns if col != primary_key]
        where_clause = " OR ".join([f"bronze.{table_name}.{col} IS DISTINCT FROM EXCLUDED.{col}" for col in columns_to_check])

        # Guarantee that all the dictionaries contain the expected keys
        values_to_insert = []
        for row in data:
            row_values = []
            for col in columns:
                api_key = "userId" if col == "user_id" else col
                value = row.get(api_key)
                # Convert dicts/lists to a JSON string for the JSONB columns
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                row_values.append(value)
            values_to_insert.append(tuple(row_values))

        query = f"""
            INSERT INTO bronze.{table_name} ({cols_str})
            VALUES %s
            ON CONFLICT ({primary_key}) DO UPDATE SET
            {update_str},
            _loaded_at = NOW()
            WHERE {where_clause};
        """

        try:
            execute_values(cursor, query, values_to_insert)
            conn.commit()
            logging.info(f"Process finished for table bronze.{table_name}.\n Records affected: {cursor.rowcount}.")
        except psycopg2.Error as e:
            logging.exception(f"Error on loading data into table {table_name}: {e}")
            conn.rollback()

def main():
    logging.info("--- Starting Extract & Load pipeline ---")
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logging.info("Database connection successfull.")

        # Process users
        logging.info("--- Processing users ---")
        users_data = fetch_api_data(API_ENDPOINTS["users"])
        if users_data:
            upsert_data(conn, "users", users_data, "id", 
                        ["id", "email", "username", "password", "name", "address", "phone"])
            
        # Process products
        logging.info("--- Processing products ---")
        products_data = fetch_api_data(API_ENDPOINTS["products"])
        if products_data:
            upsert_data(conn, "products", products_data, "id",
                        ["id", "title", "price", "description", "category", "image"])
            
        # Process carts
        logging.info("--- Processing carts ---")
        carts_data = fetch_api_data(API_ENDPOINTS["carts"])
        if carts_data:
            upsert_data(conn, "carts", carts_data, "id",
                        ["id", "user_id", "date", "products"])
    
    except psycopg2.Error as e:
        logging.exception(f"Error connecting to the database: {e}")
    finally:
        if conn:
            conn.close()
            logging.info("---Pipeline finished. Connection closed. ---")

if __name__ == "__main__":
    main()