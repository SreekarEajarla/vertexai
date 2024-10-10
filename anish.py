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
    Please provide the output in HTML format without any extra spacing or line breaks between the elements
  - Table Format so that the file can be opened and displayed as a proper web page.
  - Maintain a consistent format for all review responses.
  - Table Format: Structure the content in tables with the following specifications:
      - Use appropriate column names such as "Identification," "Explanation," ,"Fix" (or relevant headers based on the context) and type of error(syntax error like that).
      - Populate the rows with detailed content corresponding to each header.
      use css colors for every python code with different.
    - Dont show the code , show only errors.
    - Dont give spaces as it should in one page
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

# import os
# import vertexai
# from vertexai.generative_models import GenerativeModel
# # Configuration
# GOOGLE_APPLICATION_CREDENTIALS = "service.json"
# PROJECT_ID = "cedar-context-433909-d9"
# LOCATION = "us-central1"
# GENERATIVE_MODEL_NAME = "gemini-1.5-flash-001"
# INPUT_DIRECTORY = "py"  # Directory containing Python files
# # Set up Google Cloud credentials and initialize Vertex AI
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
# vertexai.init(project=PROJECT_ID, location=LOCATION)
# # Initialize the Generative Model
# model = GenerativeModel(GENERATIVE_MODEL_NAME)
# def read_file_content(file_path):
#     """Reads the content of the Python file."""
#     with open(file_path, 'r') as file:
#         return file.read()
    
# def generate_review(code_content):
#     """Generates a review of the provided code using the AI model."""
#     prompt = f"""
#     Generate the output in a purely HTML format so that the file can be opened and displayed as a proper web page.
#   - Maintain a consistent format for all review responses.
#   - Clearly separate review responses for each file:
#       - Each file's review should be in a distinct section, easily identifiable with proper headings and spacing.
#   - Table Format: Structure the content in tables with the following specifications:
#       - Use appropriate column names such as "Identification," "Explanation," and "Fix" (or relevant headers based on the context).
#       - Populate the rows with detailed content corresponding to each header.
#       use various css properties, colors, borders
    
#     **Code**:
#     {code_content}
#     """
    
#     try:
#         response = model.generate_content(
#             prompt,
#             generation_config={
#                 "max_output_tokens": 8192,
#                 "temperature": 0.2,
#                 "top_p": 0.95,
#             }
#         )
#         return response.text.strip()
#     except Exception as e:
#         return f"Error generating review: {str(e)}"
# def generate_html_report(file_name, review_text):
#     """Generates an HTML report from the analysis results."""
#     return f"""
#     <html>
#         <head><title>Code Review Report for {file_name}</title></head>
#         <body>
#             <h1>Code Review Report for {file_name}</h1>
#             <h2>Review Summary</h2>
#             <pre>{review_text}</pre>
#         </body>
#     </html>
#     """
# def main():
#     # Process each Python file in the specified directory
#     for filename in os.listdir(INPUT_DIRECTORY):
#         if filename.endswith('.py'):
#             file_path = os.path.join(INPUT_DIRECTORY, filename)
#             code_content = read_file_content(file_path)
#             review_text = generate_review(code_content)
            
#             # Generate HTML report
#             html_report = generate_html_report(filename, review_text)
            
#             # Write the report to an HTML file
#             output_file = os.path.join(INPUT_DIRECTORY, f"{filename[:-3]}_review.html")
#             with open(output_file, 'w') as report_file:
#                 report_file.write(html_report)
#             print(f"Generated report for {filename}: {output_file}")
# if __name__ == "__main__":
#     main()
has context menu
