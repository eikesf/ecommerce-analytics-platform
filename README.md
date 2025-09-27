# E-Commerce Analytics Platform
An end-to-end, orchestrated ELT (Extract, Load, Transform) which ingests e-commerce data from the fakeStore public API, loads it into a PostgreSQL database, and transforms it into analytics-ready models using dbt, with the entire workflow orchestrated by Prefect.

## Badges
![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)
![Prefect](https://img.shields.io/badge/Prefect-3.4-blueviolet?style=for-the-badge&logo=prefect)
![dbt](https://img.shields.io/badge/dbt-1.10-orange?style=for-the-badge&logo=dbt)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-28.4-022A42?style=for-the-badge&logo=docker)
![Pytest](https://img.shields.io/badge/Pytest-8.4-619685?style=for-the-badge&logo=pytest)

## Architecture Diagram

A high-level overview of the data flow and technologies involved in the pipeline.

![Architecture diagram](./assets/ecommerce_diagram.svg)

## Key features
- **End-to-End Orchestration**: Uses **Prefect** to manage, schedule, and monitor the entire ELT workflow, ensuring reliability and visibility.

- **Modern data transformation**: Leverages dbt to apply a layered Medallion Architecture (Bronze, Silver, Gold), transforming raw data into clean, aggregated, and business-ready models.

- **Data quality assurance**: Integrates data tests with dbt and the dbt-expectations package to guarantee data integrity and quality at every stage.

- **Containerized environment**: The entire infrastructure, including the PostgreSQL databasse, is managed with Docker and Docker Compose for a seamless, one-command setup.

- **Scalable & Modular architecture**: The project is structured with clear separation of concerns, making it easy to extend, maintain, and add new data sources or transformations.

## Technology stack

| Component | Technology |
|---|---:|
Orchestration | Prefect
Data transformation | dbt (data built tool)
Database | PostgreSQL
Extraction & Load | Python(Requests, psycopg2)
Containerization | Docker & Docker Compose
Data quality | dbt-expectations
Unit testing | Pytest

## Installation

Follow these steps to set up and run the project locally

### Prerequisites

- [Docker](https://docs.docker.com/engine/install/) and Docker Compose
- [Python](https://www.python.org/downloads/) 3.13+
- A python virtual environment tool (like `venv` or `conda`)

### Step-by-Step Guide

1. **Clone the repository**
```bash
git clone https://github.com/your-username/ecommerce-analytics-platform.git
cd ecommerce-analytics-platform
```

2. **Set up environment variables**

Copy the example environment file and fill in your database credentials.

```bash
cp .env.example .env
````
&emsp; **Note:** The default credentials in `docker-compose.yml` and `.env.example` should work out-of-the-box for local development.

3. **Create and activate a virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate
````

4. **Install Python & dbt dependencies**

&ensp; Install all required Python packages and the dbt packages for data quality tests.

```bash
pip install -r requirements.txt
dbt deps
```

5. **Launch the database**

&ensp; Start the PostgreSQL service using Docker Compose. This will run it in the background
```bash
docker compose up -d
```

### Usage

Once the installation is complete, you can run the ELT pipeline.

1. **Start the Prefect Server**

This will start the local Prefect UI, tipically available at `http://127.0.0.1:4200`.
```bash
prefect server start
```

2. **Start a Prefect Worker**

Open a **new terminal window**, activate the virtual environment (`source .venv/bin/activate`).

First create the work pool that the worker will connect to:
```bash
# Replace 'e-commerce-pool' if you plan to use a different name
prefect work-pool create 'e-commerce-pool' --type process
```

Now, start a worker to pick up flow runs from your work pool:
```bash
# Replace 'e-commerce-pool' if you named it differently
prefect worker start --pool 'e-commerce-pool'
```

3. **Deploy and Run the Flow**

- Deploy the main flow to Prefect so it becomes available for runs
```bash
prefect deploy --from-source orchestrate.py:elt_pipeline_flow
```
- Navigate to the Prefect UI in your browser (`http://127.0.0.1:4200`).

- Go to the "Deployments" page, find the `elt_pipeline_flow` deployment, and click **Run** to trigger the pipeline manually.

### Data Models & Architecture
The project follows the Medallion Architecture to progressively refine data:

- **Bronze Layer** (`schema: bronze`): Raw, immutable data loaded directly from the source API. Materialized as tables.

- **Silver Layer** (`schema: silver`): Cleaned, standardized, and enriched data. Models are materialized as views for flexibility during development.

- **Gold Layer** (`schema: gold`): Business-level aggregations and fact tables, ready for analytics and BI tools. Materialized as tables for high performance.

## Testing
This project employs a two-layered testing strategy to ensure both data integrity and code reliability.

### Data Quality Tests (dbt)

Data quality tests are defined in the `.yml` files within the `dbt_project/models/` directory and are executed as part of the `dbt build` command. These tests validate the final data models against specific rules (e.g., uniqueness, non-null values, relationships).

To run the data tests standalone, use the following command from the `dbt_project` directory:
```bash
dbt test
```

### Unit Tests (pytest)

Unit tests are used to validate the business logic within the Python scripts (e.g., data extraction, loading functions). These tests are written using the pytest framework.

To run the unit tests, execute the following command from the project's root directory:
```bash
pytest
```

### Contributing
Contributions are welcome! We believe that a collaborative community is the best way to grow and improve. If you'd like to contribute, please follow these steps:

1. **Fork the repository.**

2. Create a new branch for your feature or bug fix: `git checkout -b feature/my-new-feature` or `git checkout -b fix/issue-description`.

3. Make your changes and commit them with a clear, descriptive message.

4. Push your changes to your fork: `git push origin feature/my-new-feature`.

5. Open a Pull Request against the `main` branch of this repository.

Please open an issue first to discuss any major changes you would like to make.

## Author & Credits

- **Eike Scudellari Franco** - Initial Work & Development

    - [LinkedIn](https://www.linkedin.com/in/eike-scudellari-franco-1a251014a/?locale=en_US)

    - [GitHub](https://github.com/eikesf)