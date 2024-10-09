import os
import vertexai
from vertexai.generative_models import GenerativeModel

# Configuration
GOOGLE_APPLICATION_CREDENTIALS = "service.json"
PROJECT_ID = "cedar-context-433909-d9"
LOCATION = "us-central1"
GENERATIVE_MODEL_NAME = "gemini-1.5-flash-001"
INPUT_DIRECTORY = "pythonreview"  # Directory containing Python files
OUTPUT_FILE = "combined_python_review_report.html"  # Output HTML file

# Set up Google Cloud credentials and initialize Vertex AI
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Initialize the Generative Model
model = GenerativeModel(GENERATIVE_MODEL_NAME)

def read_file_content(file_path):
    """Reads the content of the Python file."""
    with open(file_path, 'r') as file:
        return file.read()

def generate_review(filename, code_content):
    """Generates a review of the provided code using the AI model."""
    prompt = f"""
    Hi vertexai, you are an expert in Python. Please review the following Python code:
    - For each syntax error, provide the error type, line number, and how to fix the error.
    - Provide the response in HTML table format with the following columns: 
        - Line Number
        - Syntax Error
        - Fix
    - If no errors are found, write 'NA' in each column.
    The Python code to review is from the file: {filename}.
    
    **Code**:
    {code_content}
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 7000,
                "temperature": 0.3,
                "top_p": 0.95,
            }
        )
        
        table_response = response.text.strip()

        # Clean the response if headers or extra content are redundant
        table_response = table_response.replace("```html", "").replace("```", "").strip()

        # If the response contains valid error data, append it into a single table
        if "Line Number" in table_response:
            # Clean the repeated headers if present and extract error rows
            table_rows = table_response.split("<thead>")[1].split("</thead>")[1].strip()

            # Format the response as an HTML table with the desired order
            table_response = f"""
            <table border="1" style="margin-bottom: 5px; width: 100%; border-collapse: collapse;">
                <thead>
                    <tr><th>Line Number</th><th>Syntax Error</th><th>Fix</th></tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
            """
        else:
            # If no errors, return a default "NA" table
            table_response = """
            <table border="1" style="margin-bottom: 5px;">
                <tr><th>Line Number</th><th>Syntax Error</th><th>Fix</th></tr>
                <tr><td colspan="3">NA</td></tr>
            </table>
            """
        
        return table_response
    except Exception as e:
        return f"Error generating review: {str(e)}"

def main():
    # Initialize the HTML report
    html_report = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 8px; text-align: left; border: 1px solid #ddd; }
            th { background-color: #f2f2f2; }
            table + table { margin-top: 10px; }
        </style>
    </head>
    <body>
    """

    # Process each Python file in the specified directory
    for filename in os.listdir(INPUT_DIRECTORY):
        if filename.endswith('.py'):
            file_path = os.path.join(INPUT_DIRECTORY, filename)
            try:
                # Read content of the file and generate the review
                code_content = read_file_content(file_path)
                review_text = generate_review(filename, code_content)
                
                # Add file name and review to the report
                html_report += f"<h2>Review for {filename}</h2>{review_text}"
            except Exception as e:
                html_report += f"<h2>Review for {filename} failed</h2><p>{str(e)}</p>"
    
    # Close the HTML tags
    html_report += "</body></html>"

    try:
        # Write the combined report to an HTML file
        with open(OUTPUT_FILE, 'w') as output_file:
            output_file.write(html_report)
        print(f"Generated combined report: {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error writing the HTML report: {str(e)}")

if __name__ == "__main__":
    main()
