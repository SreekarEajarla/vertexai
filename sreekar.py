import os
import vertexai
from vertexai.generative_models import GenerativeModel
import time

GOOGLE_APPLICATION_CREDENTIALS = "service.json"
PROJECT_ID = "cedar-context-433909-d9"
LOCATION = "us-central1"
GENERATIVE_MODEL_NAME = "gemini-1.5-flash-001"
RESPONSE_DIR = "responses/" 
RESPONSE_FILE = os.path.join(RESPONSE_DIR, "review_summary.html") 

os.makedirs(RESPONSE_DIR, exist_ok=True)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
vertexai.init(project=PROJECT_ID, location=LOCATION)

model = GenerativeModel(GENERATIVE_MODEL_NAME)

def read_file_content(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return file.read()
    return None

def add_line_numbers(code_content):
    lines = code_content.split('\n')
    numbered_lines = [f"Line {i + 1}: {line}" for i, line in enumerate(lines)]
    return '\n'.join(numbered_lines)

def generate_review(code_content):
    prompt = f"""You are an intelligent code analyst. Please analyze the provided code snippet and provide the following information:
 
1. Syntax Errors:
    - Identification: Identify the exact error-causing line numbers and provide the exact syntax errors.
    - Explanation: Provide a clear and concise explanation of each error.
    - Fix: Suggest a specific fix for each identified error, providing only the necessary code to correct it without rewriting the entire code.
    - Note: If no syntax errors are found, generate a table with "No Syntax Errors Found" in normal font (Times New Roman).
 
2. Code Bugs:
    - Identification: Identify potential logical or runtime errors in the code.
    - Explanation: Provide a detailed explanation of why the identified code segment is problematic.
    - Fix: Suggest the necessary code changes to fix the bugs without rewriting the entire code.
    - Note: If no code bugs are found, give as "No Code Bugs Found" in normal font (Times New Roman).
 
3. Security Vulnerabilities:
    - Identification: Highlight any potential security vulnerabilities in the code (e.g., SQL injection, XSS, insecure deserialization).
    - Explanation: Provide a clear explanation of each identified vulnerability.
    - Fix: Suggest code changes to mitigate the security risks without rewriting the entire code.
    - Note: If no security vulnerabilities are found, give as "No Security Vulnerabilities Found" in normal font (Times New Roman).
 
4. Duplicate Code:
    - Identification: Highlight sections of the code lines that are duplicated.
    - Suggestion: Provide recommendations without rewriting the entire code.
    - Note: If no duplicate code is found, give as "No duplicate code in this file" in normal font (Times New Roman).
 
5. Code Improvement Suggestions:
    - Identification: Highlight sections of the code that can be improved.
        - This could include:
        - Unnecessary complexity
        - Redundant code blocks
        - Potential for using more concise constructs (e.g., list comprehensions, loops)
    - Suggestion: Provide specific points for improvement and the necessary code changes without rewriting the entire code.
    - Note: If no code improvement suggestions are found, give as "No Code Improvement Suggestions Found" in normal font (Times New Roman).
 
6. Do not write any code snippet in the output.
 
7. Generate the output in purely HTML format with consistent table formatting for each section:
    - All tables should have:
        - Table width set to 100%.
        - Inline HTML attributes for consistent formatting:
            - `<table width="100%" border="1" cellpadding="8" style="border-collapse: collapse; font-family: 'Times New Roman';">`
            - Adapt column sizes according to the text in it.
            - Ensure the same border, font, and alignment styles are used consistently.
 
8. Headings like "Syntax Errors", "Code Bugs", "Security Vulnerabilities", "Duplicate Code", and "Code Improvement Suggestions" must be bold and numbered.
    - Ensure the content, such as "No Syntax Errors Found", is in normal font (Times New Roman).
    - Maintain consistent font styles for all headings and content.
 
The Code:
{code_content}
"""
 
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 8192,
                "temperature": 0.5,
                "top_p": 0.95,
            }
        )
        return response.text.strip()  
    except Exception as e:
        return f"Error generating review: {str(e)}"


def review_python_files_in_directory(directory_path):
    """Reviews all Python files in the specified directory and its subdirectories."""
    reviews = []  
    for root, _, files in os.walk(directory_path):  
        for filename in files:
            if filename.endswith('.py') or filename.endswith('.sql'):
                file_path = os.path.join(root, filename)
                start_time = time.time() 

                code_content = read_file_content(file_path)
                numbered_code = add_line_numbers(code_content)
                review = generate_review(numbered_code)

                elapsed_time = time.time() - start_time  
                print(f"Time taken to review {filename}: {elapsed_time:.2f} seconds")  

                reviews.append(f"""
                <div style="margin-bottom: 20px; border: 1px solid #ccc; padding: 15px; border-radius: 8px; background-color: #f9f9f9;">
                    <h2 style="color: #2C3E50;">Review for {filename}</h2>
                    <p style="font-style: italic; color: #000000;">File Path: {file_path}</p>
                    <h3 style="color: #2980B9;">Review:</h3>
                    {review}
                </div>
                """)

    return "\n".join(reviews)  

def main():
    directory_path = r"C:\Users\User\OneDrive - BILVANTIS TECHNOLOGIES PRIVATE LIMITED\Desktop\Devops\VertexAI\test files"

    if not os.path.exists(directory_path):
        print("The specified directory does not exist.")
        return

    overall_start_time = time.time()

    reviews_html = review_python_files_in_directory(directory_path)

    overall_elapsed_time = time.time() - overall_start_time

    with open(RESPONSE_FILE, 'w') as output_file:
        output_file.write(f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Python Code Review Summary</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #ecf0f1; }}
                h1 {{ color: #34495E; text-align: center; }}
                pre {{ }}
            </style>
        </head>
        <body>
            <h1>Python Code Review Summary</h1>
            {reviews_html}
        </body>
        </html>
        """)

    print(f"Total Time Taken for Reviewing all Files: {overall_elapsed_time:.2f} seconds")
    
if __name__ == "__main__":
    main()
