import os
import time
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting, HarmCategory, HarmBlockThreshold


# Input Variables
GOOGLE_APPLICATION_CREDENTIALS = "C:\\vertexai_task\\credentials_file.json"
PROJECT_ID = "cedar-context-433909-d9"
LOCATION ='us-west4'
GENERATIVE_MODEL_NAME = "gemini-1.5-flash-001"
OUTPUT_FILE = "C:\\vertexai_task\\final_python_response.html"

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
    """Generate the review using the AI model based on file type."""
    code_content = read_file_content(file_path)
    numbered_code_content = add_line_numbers(code_content)
    
    if file_type == "py":
        prompt = create_prompt(numbered_code_content, "Python")
    elif file_type == "sql":
        prompt = create_prompt(numbered_code_content, "SQL")
    
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


def create_prompt(code_content, language):
    """Creates a dynamic prompt for code review based on the language."""
    return f"""
You are an {language} expert.  
Please analyze the provided code snippet and provide the following information:

1. **Syntax Errors:**
    - **Identification**: Identify the exact error-causing line numbers and provide the exact syntax errors.
    - **Explanation**: Provide a clear and concise explanation of each error.
    - **Fix**: Suggest a specific fix for each identified error, providing only the necessary code to correct it without rewriting the entire code.
    - **Note**: If no syntax errors are found, generate a table with "No Syntax Errors Found" in normal font (Times New Roman).

2. **Code Bugs:**
    - **Identification**: Identify potential logical or runtime errors in the code.
    - **Explanation**: Provide a detailed explanation of why the identified code segment is problematic.
    - **Fix**: Suggest the necessary code changes to fix the bugs without rewriting the entire code.
    - **Note**: If no code bugs are found, generate a table with "No Code Bugs Found" in normal font (Times New Roman).

3. **Security Vulnerabilities:**
    - **Identification**: Highlight any potential security vulnerabilities in the code (e.g., SQL injection, XSS, insecure deserialization).
    - **Explanation**: Provide a clear explanation of each identified vulnerability.
    - **Fix**: Suggest code changes to mitigate the security risks without rewriting the entire code.
    - **Note**: If no security vulnerabilities are found, generate a table with "No Security Vulnerabilities Found" in normal font (Times New Roman).

4. **Duplicate Code:**
    - **Identification**: Highlight sections of the code lines that are duplicated.
    - **Suggestion**: Provide recommendations without rewriting the entire code.
    - **Note**: If no duplicate code is found, generate a table with "No duplicate code in this file" in normal font (Times New Roman).

5. **Code Improvement Suggestions:**
    - **Identification**: Highlight sections of the code that can be improved.
        - This could include:
        - Unnecessary complexity
        - Redundant code blocks
        - Potential for using more concise constructs (e.g., list comprehensions, loops)
    - **Suggestion**: Provide specific points for improvement and the necessary code changes without rewriting the entire code.
    - **Note**: If no code improvement suggestions are found, generate a table with "No Code Improvement Suggestions Found" in normal font (Times New Roman).

6. **Don't write any kind of code or code snippet in the output.**

7. Generate the output in a purely HTML format so that the file can be opened and displayed as a proper web page.
   - Format the entire output in **HTML** with consistent table formatting for each section.
   - Strictly do not give any headings for review response of file.
   - Ensure there is no "File: Untitled" or "code analysis report" headings in the final output.
   - Use the following table structure:
        - `<table width="100%" border="1" cellpadding="8" style="border-collapse: collapse; font-family: 'Times New Roman';">`
        - Ensure consistent table widths, borders, and spacing across all sections.
        - Adapt the column widths to fit the text appropriately.
        - Ensure uniform font style (Times New Roman) and table alignment throughout.
   - Make sure that line number is present in identification column itself(no more column containing line numbers)
   - ensure that Identification, Explanation and Fix are the column names for Syntax Errors, Code Bugs, Security Vulnerabilities sections
     and Identification, suggestion are the only column names for Duplicate Code, and Code Improvement Suggestions.
        - note: strictly no other columns are allowed.

8. Headings like Syntax Errors, Code Bugs, Security Vulnerabilities, Duplicate Code, and Code Improvement Suggestions must be bold and numbered.
    - Ensure the content, such as "No Syntax Errors Found," is in normal font (Times New Roman).
    - Keep headings and content in distinct fonts.

**The Code:**
{code_content}
"""


def format_time(time_taken):
    """Format the time into minutes and seconds."""
    if time_taken < 60:
        return f"{time_taken:.2f} seconds"
    else:
        minutes = int(time_taken // 60)
        seconds = time_taken % 60
        return f"{minutes} minutes {seconds:.2f} seconds"


def append_to_output_file(content, file_name, file_path, time_taken):
    """Append content to the output file as HTML with proper formatting."""
    with open(OUTPUT_FILE, "a", encoding="utf-8") as output_file:
        output_file.write(f"""
        <div style='border: 2px solid #3498db; padding: 20px; margin: 20px 0; border-radius: 5px; background-color: #ecf0f1;'>
            <p style='font-family:verdana; font-size: 25px; color: blue;'>
                <strong>Code Review Report for <strong>{file_name}</strong>
            </p>
            <p style='font-family:verdana; font-size: 18px; color: #34495e;'>
                File Name: <strong>{file_name}</strong><br>
                File Path: <strong>{file_path}</strong><br>
                Time Taken for Review: <strong>{format_time(time_taken)}</strong>
            </p>
            {content}
        </div>
        """)

def main():
    """Main function to run code reviews automatically for Python and SQL files."""
    path = "C:\\vertexai_task\\pyfiles"
    os.chdir(path)
    total_time = 0  # To keep track of the total time for all files

    def read_and_review_file(file_path, file_name, file_type):
        start_time = time.time()  # Start timing before the review starts
        review = generate_review(file_path, file_type)
        end_time = time.time()  # End timing after the review finishes

        time_taken = end_time - start_time  # Time taken for this specific file
        append_to_output_file(review, file_name, file_path, time_taken)  # Include time taken in the output
        print(f"Review for {file_name} appended to {OUTPUT_FILE}. Time taken: {format_time(time_taken)}.")
        return time_taken

    for dirpath, _, filenames in os.walk(path):
        for file in filenames:
            if file.endswith(".py"):
                file_path = os.path.join(dirpath, file)
                total_time += read_and_review_file(file_path, file, "py")
            elif file.endswith(".sql"):
                file_path = os.path.join(dirpath, file)
                total_time += read_and_review_file(file_path, file, "sql")

    print(f"Total time taken for all reviews: {format_time(total_time)}.")

if __name__ == "__main__":
    main()
