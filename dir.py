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
    """Reads the content of a file."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return file.read()
    return None

def add_line_numbers(code_content):
    """Adds line numbers to each line of the code content."""
    lines = code_content.split('\n')
    numbered_lines = [f"Line {i + 1}: {line}" for i, line in enumerate(lines)]
    return '\n'.join(numbered_lines)

def generate_review(code_content):
    """Generates a review using the Vertex AI model."""
    prompt = f"""You are a code analysis assistant. Analyze the provided code snippet and provide the following information:
 
1. Syntax Errors:
   - Identify the exact error-causing line numbers and provide the exact syntax errors.
   - Provide a clear and concise explanation of each error.
   - Suggest a specific fix for each identified error, describing the necessary changes without writing any code.
 
2. Code Bugs:
   - Identify potential logical or runtime errors in the code.
   - Provide a detailed explanation of why the identified code segment is problematic.
   - Suggest the necessary changes to fix the bugs without writing any code.
 
3. Security Vulnerabilities:
   - Highlight any potential security vulnerabilities in the code (e.g., SQL injection, XSS, insecure deserialization).
   - Provide a clear explanation of each identified vulnerability.
   - Suggest changes to mitigate the security risks without writing any code.
 
4. Duplicate Code:
   - Highlight sections of the code lines that are duplicated.
   - Provide recommendations for reducing duplication without writing any code.
 
5. Code Improvement Suggestions:
   - Highlight sections of the code that can be improved.
     This could include:
     - Unnecessary complexity
     - Redundant code blocks
     - Potential for using more concise constructs (e.g., list comprehensions, loops)
   - Provide specific points for improvement and describe the necessary changes without writing any code.
   - If no code improvement suggestions are found, state "No Code Improvement Suggestions Found."
6.Generate the output in a purely HTML format so that the file can be opened and displayed as a proper web page.
     - Maintain a consistent format for all review responses.
     - Use CSS for styling (not too light or too bright colors)
     - Clearly separate review responses for each file:
     - Each file's review should be in a distinct section, easily identifiable with proper headings and spacing.
     - Table Format: Structure the content in tables with the following specifications:
     - Use appropriate column names such as "Identification," "Explanation," and "Fix" (or relevant headers based on the context).
     - Populate the rows with detailed content corresponding to each header.
Important: Do not write any kind of code or code snippet in your output. Describe the necessary changes or improvements without providing actual code.
 
Present your analysis in a structured HTML format with basic styling. Use appropriate headings, lists, and paragraphs to organize the information. Here's an example of how you might structure your response:
 
<answer>
<html>
<head>
<style>
body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
h1 {{  }}
h2 {{}}
.error, .bug, .vulnerability {{  }}
.duplicate, .improvement {{ }}
</style>
</head>
<body>
<h1>Code Analysis Report</h1>
 
<h2>1. Syntax Errors</h2>
<ul>
<li class="error">
<strong>Line X:</strong> [Description of the syntax error]
<p><em>Explanation:</em> [Clear and concise explanation of the error]</p>
<p><em>Fix:</em> [Suggestion for fixing the error without writing code]</p>
</li>
</ul>
 
<h2>2. Code Bugs</h2>
<ul>
<li class="bug">
<strong>Issue:</strong> [Description of the logical or runtime error]
<p><em>Explanation:</em> [Detailed explanation of why this is problematic]</p>
<p><em>Fix:</em> [Suggestion for fixing the bug without writing code]</p>
</li>
</ul>
 
<h2>3. Security Vulnerabilities</h2>
<ul>
<li class="vulnerability">
<strong>Vulnerability:</strong> [Description of the security vulnerability]
<p><em>Explanation:</em> [Clear explanation of the vulnerability]</p>
<p><em>Mitigation:</em> [Suggestion for mitigating the risk without writing code]</p>
</li>
</ul>
 
<h2>4. Duplicate Code</h2>
<ul>
<li class="duplicate">
<strong>Duplication:</strong> [Description of the duplicated code sections]
<p><em>Recommendation:</em> [Suggestion for reducing duplication without writing code]</p>
</li>
</ul>
 
<h2>5. Code Improvement Suggestions</h2>
<ul>
<li class="improvement">
<strong>Improvement:</strong> [Description of the code section that can be improved]
<p><em>Suggestion:</em> [Specific points for improvement without writing code]</p>
</li>
</ul>
 
</body>
</html>
</answer>
 
Remember to adapt this structure based on your findings, and ensure that you do not include any actual code in your response.
    
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
            if filename.endswith('.py'):
                file_path = os.path.join(root, filename)
                code_content = read_file_content(file_path)
                numbered_code = add_line_numbers(code_content)
                review = generate_review(numbered_code)

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
    directory_path = input("Enter the directory path containing Python files: ")

    if not os.path.exists(directory_path):
        print("The specified directory does not exist.")
        return

    start_time = time.time()

    reviews_html = review_python_files_in_directory(directory_path)

    elapsed_time = time.time() - start_time

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

    print(f"Total Time Taken for Review: {elapsed_time:.2f} seconds")
    
if __name__ == "__main__":
    main()
