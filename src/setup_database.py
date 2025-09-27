# import libraries
import psycopg2
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()

# Create connection with dbt postgres database
DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'port':os.getenv("DB_PORT"),
    'dbname':os.getenv("DB_NAME"),
    'user':os.getenv("DB_USER"),
    'password':os.getenv("DB_PASSWORD")
}

def setup_database():
    """
    Connect to the PostgreSQL and guarantee that the 'bronze' schema and all
    the necessary columns exist
    """
    conn = None

    try:
        logging.info("Connectingo to the PostgreSQL database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        logging.info("Successfully connected to the database.")

        # Create staging schema in the database
        cursor.execute("CREATE SCHEMA IF NOT EXISTS bronze;")
        logging.info("Schema 'staging' guaranteed.")

        # Crete tables in the staging schema
        crate_table_queries = {
            "users" : """
                CREATE TABLE IF NOT EXISTS bronze.users (
                    id INT PRIMARY KEY,
                    email VARCHAR(255),
                    username VARCHAR(255),
                    password VARCHAR(255),
                    name JSONB,
                    address JSONB,
                    phone VARCHAR(255),
                    _loaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """,
            "products":  """
                CREATE TABLE IF NOT EXISTS bronze.products (
                    id INT PRIMARY KEY,
                    title VARCHAR(255),
                    price NUMERIC(10,2),
                    category VARCHAR(255),
                    description TEXT,
                    image VARCHAR(255),
                    _loaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """,
            "carts": """
                CREATE TABLE IF NOT EXISTS bronze.carts(
                    id INT PRIMARY KEY,
                    user_id INT,
                    date TIMESTAMP,
                    products JSONB,
                    _loaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """
        }

        # Loop to create all the tables
        for table_name, query in crate_table_queries.items():
            logging.info(f"Creating table 'bronze.{table_name}'...")
            cursor.execute(query)

        # Commit the changes made in this script
        conn.commit()
        logging.info("\n Database setup successfully completed!")
    
    except psycopg2.Error as e:
        logging.exception(f"Error in the database setup: {e}")
        if conn:
            conn.rollback()
        raise

    finally:
        if conn:
            conn.close()
            logging.info("Closed the connection with the database")

if __name__ == "__main__":
    setup_database()