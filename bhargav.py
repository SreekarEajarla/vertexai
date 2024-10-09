import os
import vertexai
from vertexai.generative_models import GenerativeModel

# Configuration
GOOGLE_APPLICATION_CREDENTIALS = "service.json"
PROJECT_ID = "cedar-context-433909-d9"
LOCATION = "us-central1"
GENERATIVE_MODEL_NAME = "gemini-1.5-flash-001"
INPUT_DIRECTORY = "pythonreview"  # Directory containing Python files
OUTPUT_FILE = "detailed_python_review_report.html"  # Output HTML file

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
    """Generates a detailed review of the provided code using the AI model."""
    prompt = f"""
    Hi vertexai, you are an expert in Python code analysis. Please review the following Python code for various issues:
    
    1. **Syntax Errors**:
        - **Identification**: Identify the exact error-causing line numbers and provide the exact syntax errors.
        - **Explanation**: Provide a clear and concise explanation of each error.
        - **Fix**: Suggest a specific fix for each identified error, providing only the necessary code to correct it without rewriting the entire code.
        
    2. **Code Bugs**:
        - **Identification**: Identify potential logical or runtime errors in the code.
        - **Explanation**: Provide a detailed explanation of why the identified code segment is problematic.
        - **Fix**: Suggest the necessary code changes to fix the bugs without rewriting the entire code.
    
    3. **Security Vulnerabilities**:
        - **Identification**: Highlight any potential security vulnerabilities in the code.
        - **Explanation**: Provide a clear explanation of each identified vulnerability.
        - **Fix**: Suggest code changes to mitigate the security risks without rewriting the entire code.
    
    4. **Duplicate Code**:
        - **Identification**: Highlight sections of the code lines that are duplicated.
        - **Suggestion**: Provide recommendations to remove redundancy without rewriting the entire code.
    
    5. **Code Improvement Suggestions**:
        - **Identification**: Highlight sections of the code that can be improved (e.g., unnecessary complexity, redundant code).
        - **Suggestion**: Provide specific points for improvement and the necessary code changes without rewriting the entire code.
    
    Provide the response in HTML table format for each section with the following columns:
        - Line Number
        - Issue Type
        - Explanation
        - Fix
        
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
        
        # Log the raw response for debugging
        print(f"Raw response for {filename}:\n{table_response}\n")

        # Clean the response by removing unnecessary code block markers
        table_response = table_response.replace("```html", "").replace("```", "").strip()

        # Check if the response has the expected structure and contains the table header
        if "| Line Number" in table_response:
            table_response = table_response.replace("|", "").replace("---", "").replace("# Python Code Analysis", "").strip()
            
            # Wrap the table in proper HTML tags
            table_html = """
            <table border="1" cellpadding="10" cellspacing="0" style="border-collapse: collapse;">
                <thead>
                    <tr>
                        <th>Line Number</th>
                        <th>Issue Type</th>
                        <th>Explanation</th>
                        <th>Fix</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for line in table_response.splitlines():
                parts = line.split("  ")
                if len(parts) == 4:  # Check if there are 4 parts (Line Number, Issue Type, Explanation, Fix)
                    table_html += f"""
                    <tr>
                        <td>{parts[0].strip()}</td>
                        <td>{parts[1].strip()}</td>
                        <td>{parts[2].strip()}</td>
                        <td>{parts[3].strip()}</td>
                    </tr>
                    """
            
            table_html += "</tbody></table>"
            return table_html
        else:
            # If no issues were found, return a table with NA values
            return """
            <table border="1" cellpadding="10" cellspacing="0" style="border-collapse: collapse;">
                <thead>
                    <tr>
                        <th>Line Number</th>
                        <th>Issue Type</th>
                        <th>Explanation</th>
                        <th>Fix</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>NA</td>
                        <td>NA</td>
                        <td>NA</td>
                        <td>NA</td>
                    </tr>
                </tbody>
            </table>
            """
        
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
                review_html = generate_review(filename, code_content)
                
                # Add file name and review to the report
                html_report += f"<h2>Review for {filename}</h2>{review_html}"
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
