import subprocess
from pathlib import Path
from prefect import task, flow

# Task for DBT
@task(
    name="Execute DBT command",
    log_prints=True,
    retries=2,
    retry_delay_seconds=10
)
def dbt_command_task(command: str):

    project_dir = Path(__file__).parent / "dbt_project"
    full_command = f"dbt {command}"
    print(f"Executing command: '{full_command}' in '{project_dir}'")

    # Execute dbt command as a subprocess
    subprocess.run(full_command, shell=True, check=True, cwd=project_dir)

# Tasks for python scripts
from src.setup_database import setup_database
from src.extract_load import main as run_extract_load

@task(name="Setup database schema")
def setup_database_task():
    "Task responsible to execute the database setup (DDL)"
    setup_database()

@task(name="Extract and load raw data")
def extract_load_task():
    "Task responsible to execute the extract and load pipeline"
    run_extract_load()

# --- Main flow ---
@flow(name="E-Commerce ELT pipeline")
def elt_pipeline_flow():
    "Orchestrate the ELT pipeline. Defines the order and dependencies between tasks"
    
    # Guarantee that the schema and tables exist
    setup_result = setup_database_task()

    # Extract and load
    el_result = extract_load_task()

    # Execute dbt build
    dbt_build_result = dbt_command_task("build", wait_for=[el_result])