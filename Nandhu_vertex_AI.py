import os
import pandas as pd
from vertexai.generative_models import GenerativeModel
import vertexai 

# Constants
GOOGLE_APPLICATION_CREDENTIALS = "service.json"
EXCEL_DIRECTORY = "xl"  # Path to the directory containing Excel files
PROJECT_ID = "cedar-context-433909-d9"
LOCATION = "us-central1"
GENERATIVE_MODEL_NAME = "gemini-1.5-flash-001"
OUTPUT_SQL_FILE = "bigquery_inserts.sql"  # Output SQL file

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
vertexai.init(project=PROJECT_ID, location=LOCATION)

model = GenerativeModel(GENERATIVE_MODEL_NAME)

def load_excel_files_from_directory(directory):
    """Load all Excel files from a specified directory into DataFrames."""
    dataframes = []
    for file_name in os.listdir(directory):
        if file_name.endswith(".xlsx") or file_name.endswith(".xls"):
            file_path = os.path.join(directory, file_name)
            df = pd.read_excel(file_path)
            dataframes.append((file_name, df))
    return dataframes

def generate_sql_from_description(description):
    """Use Vertex AI to generate SQL from a description."""
    model = GenerativeModel(GENERATIVE_MODEL_NAME)

    prompt = f"You are a BigQuery SQL expert with extensive experience generating SQL statements. Generate a BigQuery SQL expression for the following transformation description: {description}"
    response = model.generate_content(
        prompt,
        generation_config={
            "max_output_tokens": 512,
            "temperature": 0.2,
            "top_p": 0.95,
        }
    )
    return response.text

def generate_bigquery_insert_query(df):
    """Generate a single BigQuery INSERT statement based on transformations for multiple columns."""
    source_table = df['source_table'][0]  # Assuming the same source table for all rows
    target_table = df['target_table'][0]  # Assuming the same target table for all rows
    assignments = []

    for _, row in df.iterrows():
        source_column = row['source_column']
        transformation_logic = row['transformation_logic']
        target_column = row['target_column']

        # Generate SQL using Vertex AI based on transformation logic
        transformed_column_sql = generate_sql_from_description(transformation_logic).strip()

        # Ensure proper SQL assignment
        if not transformed_column_sql.lower().startswith("select"):
            transformed_column_sql = transformed_column_sql.replace("```sql", "").replace("```", "").strip()

        # Prepare assignment for the SQL SELECT statement
        assignments.append(f"{transformed_column_sql} AS {target_column}")

    # Combine assignments into a single SQL query
    assignment_list = ',\n    '.join(assignments)
    query = f"""
    INSERT INTO {target_table} ({', '.join(df['target_column'])})
    SELECT 
    {assignment_list}
    FROM `{source_table}`;
    """
    return query


def write_query_to_file(query, output_file):
    """Write generated query to a SQL file."""
    with open(output_file, 'w') as f:
        f.write(query)

def main():
    # Load all Excel files from the specified directory
    excel_files = load_excel_files_from_directory(EXCEL_DIRECTORY)

    for file_name, df in excel_files:
        print(f"Processing file: {file_name}")

        # Generate a BigQuery INSERT statement for the current DataFrame
        bigquery_query = generate_bigquery_insert_query(df)

        # Write the generated SQL to a file
        output_file = f"{os.path.splitext(file_name)[0]}_{OUTPUT_SQL_FILE}"
        write_query_to_file(bigquery_query, output_file)

        print(f"Generated SQL query has been written to {output_file}")

if __name__ == "__main__":
    main()
