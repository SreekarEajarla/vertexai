import os
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting, HarmCategory, HarmBlockThreshold


# Input Variables
GOOGLE_APPLICATION_CREDENTIALS = "C:\\vertexai_task\\credentials_file.json"
PROJECT_ID = "cedar-context-433909-d9"
LOCATION = "us-central1"
GENERATIVE_MODEL_NAME = "gemini-1.5-flash-001"
OUTPUT_FILE ="C:\\vertexai_task\\final_python_response.html"

 
# Set your Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
 
# Initialize Vertex AI with your project details
vertexai.init(project=PROJECT_ID, location=LOCATION)

generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.4,
        "top_p": 0.25,
    }

safety_settings = [
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH
    ),
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH
    ),
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH
    ),
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH
    ),
]

generative_model = GenerativeModel(GENERATIVE_MODEL_NAME)
 
def read_file_content(file_path):
    """Reads the content of the file."""
    with open(file_path, 'r') as file:
        return file.read()

def add_line_numbers(code_content):
    """Adds line numbers to code content for better error referencing."""
    lines = code_content.split('\n')
    numbered_lines = [f"Line {i + 1}: {line}" for i, line in enumerate(lines)]
    return '\n'.join(numbered_lines)

def generate_review(file_path, file_type):
    code_content = read_file_content(file_path)
    numbered_code_content = add_line_numbers(code_content)
    prompt = create_prompt(numbered_code_content, file_type)
    response_text = ""
    try:
        responses = generative_model.generate_content(
            [prompt],
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=True,
        )
        for response in responses:
            response_text += response.text
    except Exception as e:
        response_text = f"Error generating review: {str(e)}"
    return response_text

def create_prompt(code_content,language):
    return f"""
you are an {language} expert.   
Please analyze the provided code snippet and provide the following information:
1. ** Syntax Errors :**
    - ** Identification **: Identify the exact error-causing line numbers and provide the exact syntax errors.
    - ** Explanation **: Provide a clear and concise explanation of each error.
    - ** Fix **: Suggest a specific fix for each identified error, providing only the necessary code to correct it without rewriting the entire code.
    - ** Note **: If no syntax errors are found, simply state "No Syntax Errors Found."

 
2. ** Code Bugs :**
    - ** Identification **: Identify potential logical or runtime errors in the code.
    - ** Explanation **: Provide a detailed explanation of why the identified code segment is problematic.
    - ** Fix **: Suggest the necessary code changes to fix the bugs without rewriting the entire code.
    - ** Note **: If no code bugs found, simply state "No Code Bugs Found."

 
3. ** Security Vulnerabilities :**
    - ** Identification **: Highlight any potential security vulnerabilities in the code (e.g., SQL injection, XSS, insecure deserialization).
    - ** Explanation **: Provide a clear explanation of each identified vulnerability.
    - ** Fix **: Suggest code changes to mitigate the security risks without rewriting the entire code.
    - ** Note **: If no security vulnerabilities are found, simply state "No Security Vulnerabilities Found."

 
4. ** Duplicate Code :**
    - ** Identification **: Highlight sections of the code lines that are duplicated.
    - ** Suggestion **: Provide recommendations without rewriting the entire code.
    - ** Note **: If no code duplicate code is found, simply state "No duplicate code in this file."

 
5. ** Code Improvement Suggestions :**
    - ** Identification **: Highlight sections of the code that can be improved.
        - This could include:
        - Unnecessary complexity
        - Redundant code blocks
        - Potential for using more concise constructs (e.g., list comprehensions, loops)
    - ** Suggestion **: Provide specific points for improvement and the necessary code changes without rewriting the entire code.
    - ** Note **: If no code improvement suggestions are found, simply state "No Code Improvement Suggestions Found."

6. ** Don't write any kind of code or code snippet in the output: **

7.Generate the output in a purely HTML format so that the file can be opened and displayed as a proper web page.
  - Maintain a consistent format for all review responses.
  - Clearly separate review responses for each file:
      - Each file's review should be in a distinct section, easily identifiable with proper headings and spacing.
  - Table Format: Structure the content in tables with the following specifications:
      - Use appropriate column names such as "Identification," "Explanation," and "Fix" (or relevant headers based on the context).
      - Populate the rows with detailed content corresponding to each header.
**The Code:**
{code_content}
"""


def append_to_output_file(content, file_name, file_path):
    """Append content to the output file as HTML with proper formatting."""
    with open(OUTPUT_FILE, "a", encoding="utf-8") as output_file:
        output_file.write(f"""
        <div style='border: 2px solid #3498db; padding: 20px; margin: 20px 0; border-radius: 5px; background-color: #ecf0f1;'>
            <p style='font-family:verdana; font-size: 25px; color: blue;'>
                <strong>Code Review Report for <strong>{file_name}</strong>
            </p>
            <p style='font-family:verdana; font-size: 18px; color: #34495e;'>
                File Name: <strong>{file_name}</strong><br>
                File Path: <strong>{file_path}</strong>
            </p>
            {content}
        </div>
        """)

def main():
    file_type = input("Which file do you want to review? Enter 'py' for Python or 'sql' for SQL: ")
    path = "C:\\vertexai_task\\pyfiles"
    os.chdir(path)
    def read_and_review_file(file_path, file_name):   
        review = generate_review(file_path, file_type)  
        append_to_output_file(review, file_name, file_path) 
        print(f"Review for {file_name} appended to {OUTPUT_FILE}.")
    
    for dirpath, _, filenames in os.walk(path):
        for file in filenames:
            if file.endswith(f".{file_type}"):  
                file_path = os.path.join(dirpath, file) 
                read_and_review_file(file_path, file)  

if __name__ == "__main__":
    main()
