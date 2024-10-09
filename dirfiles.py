import os
import time
import vertexai
from vertexai.generative_models import GenerativeModel

GOOGLE_APPLICATION_CREDENTIALS = "service.json"
PROJECT_ID = "cedar-context-433909-d9"
LOCATION = "us-central1"
GENERATIVE_MODEL_NAME = "gemini-1.5-flash-001"

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

def generate_review(code_content):
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

def review_python_files_in_directory(directory_path):
    for root, dirs, files in os.walk(directory_path): 
        for filename in files:
            if filename.endswith('.py'):
                file_path = os.path.join(root, filename)
                code_content = read_file_content(file_path)
                numbered_code = add_line_numbers(code_content)
                review = generate_review(numbered_code)

                output_file_path = os.path.splitext(file_path)[0] + "_review.html"
                with open(output_file_path, 'w') as output_file:
                    output_file.write(f"""
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Review for {filename}</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #ecf0f1; }}
                            h1 {{ color: #34495E; }}
                            pre {{ white-space: pre-wrap; word-wrap: break-word; }}
                            .error {{ color: red; font-weight: bold; }}
                            .success {{ color: green; font-weight: bold; }}
                        </style>
                    </head>
                    <body>
                        <h1>Review for {filename}</h1>
                        <h3>File Path:</h3>
                        <p>{file_path}</p>
                        <h3>Review:</h3>
                        <pre>{review}</pre>
                    </body>
                    </html>
                    """)

def main():
    directory_path = input("Enter the directory path containing Python files: ")

    if not os.path.exists(directory_path):
        print("The specified directory does not exist.")
        return

    start_time = time.time()

    review_python_files_in_directory(directory_path)

    end_time = time.time() 
    elapsed_time = end_time - start_time

    print(f"Total Time Taken for Review: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()
