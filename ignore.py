import os
import time
import vertexai
from vertexai.generative_models import GenerativeModel

GOOGLE_APPLICATION_CREDENTIALS = "service.json"
PROJECT_ID = "cedar-context-433909-d9"
LOCATION = "us-central1"
GENERATIVE_MODEL_NAME = "gemini-1.5-flash-001"
IGNORE_FILE_NAME = "ignore.txt"
OUTPUT_REPORT_NAME = "code_review_report.html"  # Output HTML file

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
vertexai.init(project=PROJECT_ID, location=LOCATION)

model = GenerativeModel(GENERATIVE_MODEL_NAME)

def read_file_content(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def add_line_numbers(code_content):
    lines = code_content.split('\n')
    numbered_lines = [f"Line {i + 1}: {line}" for i, line in enumerate(lines)]
    return '\n'.join(numbered_lines)

def read_ignore_list(file_path):
    """Reads the ignore list from a file, handling file not found."""
    try:
        file_path = os.path.abspath(file_path)
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Warning: {file_path} not found. No issues will be ignored.")
        return []
    except Exception as e:
        print(f"An error occurred while reading the ignore file: {e}")
        return []

def generate_review(code_content, ignore_list):
    prompt = f"""Please analyze the provided code snippet and provide the following information in a consistent HTML format:
1. **Syntax Errors**:
    - **Identification**: Identify the exact error-causing line numbers and provide the exact syntax errors.
    - **Explanation**: Provide a clear and concise explanation of each error.
    - **Fix**: Suggest a specific fix for each identified error, providing only the necessary code to correct it without rewriting the entire code.

2. **Code Bugs**:
    - **Identification**: Identify potential logical or runtime errors in the code.
    - **Explanation**: Provide a detailed explanation of why the identified code segment is problematic.
    - **Fix**: Suggest the necessary code changes to fix the bugs without rewriting the entire code.

3. **Security Vulnerabilities**:
    - **Identification**: Highlight any potential security vulnerabilities in the code (e.g., SQL injection, XSS, insecure deserialization).
    - **Explanation**: Provide a clear explanation of each identified vulnerability.
    - **Fix**: Suggest code changes to mitigate the security risks without rewriting the entire code.

4. **Duplicate Code**:
    - **Identification**: Highlight sections of the code lines that are duplicated.
    - **Suggestion**: Provide recommendations without rewriting the entire code.

5. **Code Improvement Suggestions**:
    - **Identification**: Highlight sections of the code that can be improved, including unnecessary complexity or redundant blocks.
    - **Suggestion**: Provide specific points for improvement without rewriting the entire code. If no suggestions are found, state "No Code Improvement Suggestions Found."
    
6. **Output Requirements**:
    - Do not include any code snippets in your output.
    - Ensure all responses are formatted consistently in HTML.

The Code:
{code_content}
    
Ignore the issues mentioned in the ignore list: {', '.join(ignore_list)}
"""

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 8192,
                "temperature": 0.2,
                "top_p": 0.95,
            }
        )
        return response.text.strip()  
    except Exception as e:
        return f"Error generating review: {str(e)}"

def review_python_files_in_directory(directory_path, ignore_list):
    all_reviews_html = ""
    for root, dirs, files in os.walk(directory_path):
        for filename in files:
            if filename.endswith('.py'):
                file_path = os.path.join(root, filename)
                code_content = read_file_content(file_path)
                numbered_code = add_line_numbers(code_content)
                review = generate_review(numbered_code, ignore_list)
                
                all_reviews_html += f"""
                    <h3>Review for {filename}</h3>
                    <h4>File Path:</h4>
                    <p>{file_path}</p>
                    <h4>Review:</h4>
                    <pre>{review}</pre>
                """
    
    return all_reviews_html

def generate_final_report(reviews_html):
   
    html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Code Review Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #ecf0f1; }}
                h1 {{ color: #34495E; }}
                h3 {{ color: #34495E; }}
                h4 {{ color: #34495E; }}
                pre {{ white-space: pre-wrap; word-wrap: break-word; }}
                .error {{ color: red; font-weight: bold; }}
                .success {{ color: green; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>Code Review Report</h1>
            {reviews_html}
        </body>
        </html>
        """
    return html_content
    


def main():
    directory_path = input("Enter the directory path containing Python files: ")

    if not os.path.exists(directory_path):
        print("The specified directory does not exist.")
        return
    
    ignore_list = read_ignore_list(IGNORE_FILE_NAME)
    
    start_time = time.time()
    
    reviews_html = review_python_files_in_directory(directory_path, ignore_list)

    end_time = time.time()
    elapsed_time = end_time - start_time
    
    final_html_content = generate_final_report(reviews_html)

    with open(OUTPUT_REPORT_NAME, 'w') as output_file:
        output_file.write(final_html_content)
    
    print(f"Total Time Taken for Review: {elapsed_time:.2f} seconds")
    print(f"Code review report is saved to {OUTPUT_REPORT_NAME}")

if __name__ == "__main__":
    main()
