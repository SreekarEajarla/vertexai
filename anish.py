import os
import vertexai
from vertexai.generative_models import GenerativeModel

# Configuration
GOOGLE_APPLICATION_CREDENTIALS = "service.json"
PROJECT_ID = "cedar-context-433909-d9"
LOCATION = "us-central1"
GENERATIVE_MODEL_NAME = "gemini-1.5-flash-001"
INPUT_DIRECTORY = "py" 
OUTPUT_FILE = "review7.html"
# Set Google Cloud credentials and initialize Vertex AI
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Initialize the Generative Model
model = GenerativeModel(GENERATIVE_MODEL_NAME)

def read_file_content(file_path):
    """Reads the content of a file."""
    with open(file_path, 'r') as file:
        return file.read()

def add_line_numbers(code_content):
    """Adds line numbers to code content for better error referencing."""
    lines = code_content.split('\n')
    numbered_lines = [f"Line {i + 1}: {line}" for i, line in enumerate(lines)]
    return '\n'.join(numbered_lines)

def generate_review(code_content):
    """Generates a review of the provided code using the AI model."""
    prompt = f"""You are an intelligent AI bot. Review the following code and check if there are any type of errors in the files. If there are any errors, list them clearly in HTML format.
    Please provide the output in HTML format without any spacing or line breaks between the elements
  - Table Format so that the file can be opened and displayed as a proper web page.
  - Maintain a consistent format for all review responses.
  - Table Format: Structure the content in tables with the following specifications:
  - Use appropriate column names such as "Identification," "Explanation," ,"Fix" (or relevant headers based on the context) , "type of error(syntax error like that)", "code improvements" .
  - Populate the rows with detailed content corresponding to each header.
    use css colors for every python code with different.
  - Dont show the code , show only errors.
  - Dont give spaces as it should in one page
  Please analyze the provided code snippet and provide the following information:
1. ** Syntax Errors :**
    - ** Identification **: Identify the exact error-causing line numbers and provide the exact syntax errors.
    - ** Explanation **: Provide a clear and concise explanation of each error.
    - ** Fix **: Suggest a specific fix for each identified error, providing only the necessary code to correct it without rewriting the entire code.
 
2. ** Code Bugs :**
    - ** Identification **: Identify potential logical or runtime errors in the code.
    - ** Explanation **: Provide a detailed explanation of why the identified code segment is problematic.
    - ** Fix **: Suggest the necessary code changes to fix the bugs without rewriting the entire code.
 
3. ** Security Vulnerabilities :**
    - ** Identification **: Highlight any potential security vulnerabilities in the code (e.g., SQL injection, XSS, insecure deserialization).
    - ** Explanation **: Provide a clear explanation of each identified vulnerability.
    - ** Fix **: Suggest code changes to mitigate the security risks without rewriting the entire code.
 
4. ** Duplicate Code :**
    - ** Identification **: Highlight sections of the code lines that are duplicated.
    - ** Suggestion **: Provide recommendations without rewriting the entire code.
 
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
  - Use CSS for styling (not too light or too bright colors)
  - Clearly separate review responses for each file:
      - Each file's review should be in a distinct section, easily identifiable with proper headings and spacing.
  - Table Format: Structure the content in tables with the following specifications:
      - Use appropriate column names such as "Identification," "Explanation," and "Fix" (or relevant headers based on the context).
      - Populate the rows with detailed content corresponding to each header.
The code to review:
{code_content}"""
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 8192,
                "temperature": 0.2,
                "top_p": 0.95,
            }
        )
        return response.text
    except Exception as e:
        return f"Error generating review: {str(e)}"

def review_python_files(directory):
    """Reviews all Python files in the specified directory."""
    review_results = ""
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            file_path = os.path.join(directory, filename)
            code_content = read_file_content(file_path)
            numbered_code = add_line_numbers(code_content)
            review = generate_review(numbered_code)
            review_results += f"<h2>Review for {filename}</h2><pre>{review}</pre>\n"
    return review_results

def main():
    # Review all Python files in the input directory
    review_results = review_python_files(INPUT_DIRECTORY)

    # Write the reviews to the output file
    with open(OUTPUT_FILE, 'w') as output_file:
        output_file.write(f"<html><head><title>Python Code Reviews</title></head><body>{review_results}</body></html>")

    print(f"Review report saved as '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()
