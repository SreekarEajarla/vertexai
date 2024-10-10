import os
import time
import vertexai
from vertexai.generative_models import GenerativeModel

GOOGLE_APPLICATION_CREDENTIALS = "service.json"
PROJECT_ID = "cedar-context-433909-d9"
LOCATION = "us-central1"
GENERATIVE_MODEL_NAME = "gemini-1.5-flash-001"
OUTPUT_FILE = "review.html"

# Set Google Cloud credentials and initialize Vertex AI
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
vertexai.init(project=PROJECT_ID, location=LOCATION)
 
# Initialize the Generative Model
model = GenerativeModel(GENERATIVE_MODEL_NAME)
 
def error_refer(code_py):
    lines = code_py.split('\n')
    numbered_lines = [f"Line {i + 1}: {line}" for i, line in enumerate(lines)]
    return '\n'.join(numbered_lines)
 
def generate_review(code_py,filename):
    start_time = time.time()
    prompt = f"""

        you are an python expert.   
Please analyze the provided code snippet and provide the following information:
1. ** Syntax Errors :**
    - ** Identification **: Identify the exact error-causing line numbers and provide the exact syntax errors.
    - ** Explanation **: Provide a clear and concise explanation of each error.
    - ** Fix **: Suggest a specific fix for each identified error, providing only the necessary code to correct it without rewriting the entire code.
    - ** Note **: If no syntax errors are found, simply state "No Syntax Errors Found."
    - ** highlight  the word SYNTAX ERROR
 
2. ** Code Bugs :**
    - ** Identification **: Identify potential logical or runtime errors in the code.
    - ** Explanation **: Provide a detailed explanation of why the identified code segment is problematic.
    - ** Fix **: Suggest the necessary code changes to fix the bugs without rewriting the entire code.
    - ** Note **: If no code bugs found, simply state "No Code Bugs Found."
    - ** highlight the word CODE BUGS
 
3. ** Security Vulnerabilities :**
    - ** Identification **: Highlight any potential security vulnerabilities in the code (e.g., SQL injection, XSS, insecure deserialization).
    - ** Explanation **: Provide a clear explanation of each identified vulnerability.
    - ** Fix **: Suggest code changes to mitigate the security risks without rewriting the entire code.
    - ** Note **: If no security vulnerabilities are found, simply state "No Security Vulnerabilities Found."
    - ** highlight the word SECURITY VULNERABITIES
 
4. ** Duplicate Code :**
    - ** Identification **: Highlight sections of the code lines that are duplicated.
    - ** Suggestion **: Provide recommendations without rewriting the entire code.
    - ** Note **: If no code duplicate code is found, simply state "No duplicate code in this file."
    - ** highlight the word DUPLICATE CODE
 
5. ** Code Improvement Suggestions :**
    - ** Identification **: Highlight sections of the code that can be improved.
        - This could include:
        - Unnecessary complexity
        - Redundant code blocks
        - Potential for using more concise constructs (e.g., list comprehensions, loops)
    - ** Suggestion **: Provide specific points for improvement and the necessary code changes without rewriting the entire code.
    - ** Note **: If no code improvement suggestions are found, simply state "No Code Improvement Suggestions Found."
    - ** highlight the word CODE IMPROVEMENTS

6. ** Don't write any kind of code or code snippet in the output: **

7.Generate the output in a purely HTML format so that the file can be opened and displayed as a proper web page.
  - Maintain a consistent format for all review responses.
  - Clearly separate review responses for each file:
      - Each file's review should be in a distinct section, easily identifiable with proper headings and spacing.
  - Table Format: Structure the content in tables with the following specifications:
      - Use appropriate column names such as "Identification," "Explanation," and "Fix" (or relevant headers based on the context).
      - Populate the rows with detailed content corresponding to each header.
**The Code:**
{code_py}



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
        end_time = time.time()
        print(f"total time taken for {filename}:  {end_time-start_time}")
        return response.text
    except Exception as e:
        end_time = time.time()
        print(f"total time taken for {filename}:  {end_time-start_time}")
        return f"Error generating review: {str(e)}"
     
def main(content,filename,file_path):
    numbered_code = error_refer(content)    
    review = generate_review(numbered_code,filename)
    filename=f"{filename}.html"
    # Write the review to the output file
    with open(OUTPUT_FILE, 'a') as output_file:
    # Write a heading
        output_file.write(f"""
        <div style='border: 2px solid #3498db; padding: 20px; margin: 20px 0; border-radius: 5px; background-color: #ecf0f1;'>
            <p style='font-family:verdana; font-size: 25px; color: blue;'>
                <strong>Code Review Report for <strong>{filename}</strong>
            </p>
            <p style='font-family:verdana; font-size: 18px; color: #34495e;'>
                File Name: <strong>{filename}</strong><br>
                Flie Path: <strong>{file_path}</strong><br>
            </p>
            {review}
        </div>
        """)

def read_file_content(file_path):
    """Reads the content of the file."""
    with open(file_path, 'r') as file:
        return file.read()

def read_files_in_directory(directory_path):
    """Reads all Python files in the given directory."""
    # List to store content of each file
    
    
    # Loop through each file in the directory
    for filename in os.listdir(directory_path):
        # Check if the file is a Python file
        if filename.endswith('.py'):
            file_path = os.path.join(directory_path, filename)
            content = read_file_content(file_path)
            
            main(content,filename,file_path)
           
directory_path = r"C:\taskgcp\python_file5"# Change this to your directory


all_files_content = read_files_in_directory(directory_path)
