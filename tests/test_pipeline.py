import pytest
import psycopg2
from psycopg2.extras import execute_values
import os
import requests
from dotenv import load_dotenv

# Import the functions to be tested
from src.setup_database import setup_database
from src.extract_load import fetch_api_data, upsert_data

# Load environment variables to use in the tests
load_dotenv()

# Configuration for the test database
DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'port': os.getenv("DB_PORT"),
    'dbname': os.getenv("DB_NAME"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD")
}

def test_setup_database_creates_tables():
    """
    Integration test: executes the setup function and verifies that the tables were
    actually created in the database.
    """

    # Ensure the database is in a clean state before the test
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("DROP SCHEMA IF EXISTS bronze CASCADE;")
    conn.commit()
    conn.close()

    setup_database()

    # Connect again and verify that the tables now exist
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    tables_to_check = ['users', 'products', 'carts']
    for table in tables_to_check:
        cursor.execute(f"SELECT to_regclass('bronze.{table}');")
        assert cursor.fetchone()[0] is not None, f"Table bronze.{table} was not created."
    
    conn.close()

def test_fetch_api_data_success(mocker):
    """
    Unit test: tests the success path for the featch_api_data function.
    Verifies that it processes a valid JSON response correctly
    """

    # Prepare a fake JSON  result and configure the mock
    fake_json_response = [{"id": 1, "title": "Test product"}]

    mock_get = mocker.patch('requests.get')

    # Configure the mock to return a successful response object
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = fake_json_response

    result = fetch_api_data("http://fake-api.com/products")

    # Verify that the result is what we expect
    assert result == fake_json_response
    mock_get.assert_called_once_with("http://fake-api.com/products", timeout=10)

def test_fetch_api_data_failure(mocker):
    """
    Unit test: tests the failure path for the fetch_api_data function.
    Verifies that it returns None when the API raises an error.
    """

    # Configure the mock to simulate a network error
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Network Error"))

    # Execute the function
    result = fetch_api_data("http://fake-api.com/products")

    # Verify that the result is None, as expected
    assert result is None

def test_upsert_data_prepares_correct_arguments(mocker):
    """
    Unit test: Verifies that the upsert_data function calls execute_values
    with the correct SQL query and prepared data.
    """
    # Mock the function
    mock_execute_values = mocker.patch('src.extract_load.execute_values')

    mock_conn = mocker.MagicMock()

    # Input data for the test case
    sample_data = [{'id': 1, 'name': 'Product A', 'price': 10.50}]
    table_name = "products_test"
    primary_key = "id"
    columns = ["id", "name", "price"]

    # Execute the function under test.
    upsert_data(mock_conn, table_name, sample_data, primary_key, columns)

    #Verify that the mock was called correctly and with the right arguments.
    mock_execute_values.assert_called_once()
    
    # Capture the arguments passed to the mocked execute_values function
    # call_args.args is a tuple of the positional arguments
    captured_cursor, captured_query, captured_data = mock_execute_values.call_args.args

    # Assert that the generated SQL query is correct
    expected_query = """
            INSERT INTO bronze.products_test (id, name, price)
            VALUES %s
            ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name, price = EXCLUDED.price,
            _loaded_at = NOW()
            WHERE bronze.products_test.name IS DISTINCT FROM EXCLUDED.name OR bronze.products_test.price IS DISTINCT FROM EXCLUDED.price;
        """
    # Compare the queries after normalizing whitespace
    assert " ".join(captured_query.split()) == " ".join(expected_query.split())

    # Assert that the data was prepared correctly as a list of tuples
    expected_data = [(1, 'Product A', 10.50)]
    assert captured_data == expected_data
    
    # Verify that the commit method was called on the mock connection
    mock_conn.commit.assert_called_once()
