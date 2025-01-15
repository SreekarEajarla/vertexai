import os
import subprocess
import vertexai
import time
from vertexai.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials_file.json"

vertexai.init(project="bilvantisaimlproject", location="us-west1")

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 0.5,
    "top_p": 0.95,
}

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
}

generative_model = GenerativeModel("gemini-1.5-flash-001")

OUTPUT_FILE = "review_summary.html"


def read_file_content(file_path):
    """Reads the content of the file."""
    with open(file_path, 'r') as file:
        return file.read()


def add_line_numbers(code_content):
    """Adds line numbers to code content for better error referencing."""
    lines = code_content.split('\n')
    numbered_lines = [f"Line {i + 1}: {line}" for i, line in enumerate(lines)]
    return '\n'.join(numbered_lines)


def format_time(seconds):
    """Converts seconds into a human-readable format."""
    return f"{seconds:.2f} seconds"


def append_to_output_file(content, file_name, file_path, time_taken):
    """Append content to the output file as HTML with proper formatting."""
    if not os.path.exists(OUTPUT_FILE):
        # If the file doesn't exist, create it with the initial HTML structure
        with open(OUTPUT_FILE, "w", encoding="utf-8") as output_file:
            output_file.write(f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Python Code Review Summary</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #34495E; text-align: center; }}
                pre {{ }}
            </style>
        </head>
        <body>
            <h1>Python Code Review Summary</h1>
        </body>
        </html>
        """)
    # Append the formatted review to the file
    with open(OUTPUT_FILE, "a", encoding="utf-8") as output_file:
        output_file.write(f"""
             <div style="margin-bottom: 20px; border: 1px solid #ccc; padding: 15px; border-radius: 8px; background-color: #f9f9f9;">
                    <h2 style="color: #2C3E50;">Review for {file_name}</h2>
                    <p style="font-style: italic; color: #000000;">File Path: {file_path}</p>
                    <h3 style="color: #2980B9;">Review:</h3>
                    {content}
                </div>
        """)


def generate_content_for_review(code_content):
    """Generates a detailed review of the provided code snippet."""
    response_text = ""
    try:
        responses = generative_model.generate_content(
            [prompt(code_content)],
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=True,
        )
        for response in responses:
            response_text += response.text

    except ValueError as e:
        if "SAFETY" in str(e):
            print(f"WARNING: Generated content blocked by safety filters: {e}")
        else:
            raise e

    return response_text


def prompt(code_content):
    """Creates a prompt to analyze code for various issues."""
    return f"""  you are an intelligent code expert.   
Please analyze the provided code snippet and provide the following information:
1. Syntax Errors:
    - Identification: Identify the exact error-causing line numbers and provide the exact syntax errors.
    - Explanation: Provide a clear and concise explanation of each error.
    - Fix: Suggest a specific fix for each identified error, providing only the necessary code to correct it without rewriting the entire code.
    - Criticality: Assign a criticality level to the error:
        - Low: Minor issues like unused imports or misplaced punctuation that don’t significantly affect execution.
        - Medium: Errors that cause the program to malfunction or produce incorrect results, such as incorrect function calls or wrong operators.
        - High: Critical errors that cause the code to fail immediately, such as undefined variables, missing parentheses, or incorrect indentation.
    - Note: If no syntax errors are found, generate a table with "No Syntax Errors Found" in normal font (Times New Roman).

 
2. Code Bugs:
    -  Identification: Identify potential logical or runtime errors in the code.
    -  Explanation: Provide a detailed explanation of why the identified code segment is problematic.
    -  Fix: Suggest the necessary code changes to fix the bugs without rewriting the entire code.
    - Criticality: Assign a criticality level to the bug:
        - Low: Bugs that have minimal impact and do not prevent the code from executing.
        - Medium: Bugs that cause incorrect behavior in certain cases but do not crash the program.
        - High: Bugs that prevent the program from running or produce severe functional issues.
    -  Note: If no code bugs are found, generate a table with "No Code Bugs Found" in normal font (Times New Roman).


3. Security Vulnerabilities:
    -  Identification: Highlight any potential security vulnerabilities in the code (e.g., SQL injection, XSS, insecure deserialization).
    -  Explanation: Provide a clear explanation of each identified vulnerability.
    -  Fix: Suggest code changes to mitigate the security risks without rewriting the entire code.
    - Criticality: Assign a criticality level to the vulnerability:
        - Low: Potential vulnerabilities that are unlikely to be exploited under typical use cases.
        - Medium: Security issues that could be exploited with some effort, like SQL injection or weak validation.
        - High: Critical security flaws that allow immediate exploitation (e.g., arbitrary code execution, severe data leaks).
    - Note: If no security vulnerabilities are found, generate a table with "No Security Vulnerabilities Found" in normal font (Times New Roman).
    -  Note: If no security vulnerabilities are found, generate a table with "No Security Vulnerabilities Found" in normal font (Times New Roman).
 
4. Duplicate Code:
    -  Identification: Highlight sections of the code lines that are duplicated.
    -  Suggestion: Provide recommendations without rewriting the entire code.
    - Criticality: Assign a criticality level to the duplicate code:
        - Low: A small section of duplicated code that has minimal impact.
        - Medium: Duplicated code that affects readability and increases maintenance effort.
        - High: Extensive duplication that significantly complicates debugging and future changes.
    -  Note: If no duplicate code is found, generate a table with "No duplicate code in this file" in normal font (Times New Roman).
 
5.  Code Improvement Suggestions :
    -  Identification : Highlight sections of the code that can be improved.
        - This could include:
        - Unnecessary complexity
        - Redundant code blocks
        - Potential for using more concise constructs (e.g., list comprehensions, loops)
    -  Suggestion: Provide specific points for improvement and the necessary code changes without rewriting the entire code.
    - Criticality: Assign a criticality level to the suggestion:
        - Low: Suggestions that are more about style or minor optimizations.
        - Medium: Improvements that can enhance readability or performance.
        - High: Major improvements that significantly affect efficiency, maintainability, or scalability.
    -  Note: If no code improvement suggestions are found, generate a table with "No Code Improvement Suggestions Found" in normal font (Times New Roman).

6.  Don't write any kind of code or code snippet in the output: 

7. Generate the output in purely HTML format with consistent table formatting for each section:
    - set response table width to 100%
    - strictly use only the 100% of the page not more than that
    - strictly do not give any headings for review response of file
    - ensure there is no "File:Untitled" or "code analysis report" headings in the final output
    - All tables should have:
        - Table width set to 100%.
        - Inline HTML attributes for consistent formatting:
            - <table width="100%" border="1" cellpadding="8" style="border-collapse: collapse; font-family: 'Times New Roman';">
            - Adapt column sizes according to the text in it.
            - Ensure the same border, font, and alignment styles are used consistently.
        - ensure all headings, section headings, content, file names, and paths should be left-aligned and text color is black.
        - make sure that line number is present in present in identification column itself(no more column containing line numbers)
        - ensure that Identification, Explanation, Fix, and criticality are the only column names for Syntax Errors, Code Bugs, Security Vulnerabilities sections and
          Identification, Suggestions, and Criticality are the only column names for duplicate code and code improvement suggestions
           - strictly no other columns are allowed.
 
8. Headings like "Syntax Errors", "Code Bugs", "Security Vulnerabilities", "Duplicate Code", and "Code Improvement Suggestions" must be bold and numbered.
    - Ensure the content, such as "No Syntax Errors Found", is in normal font (Times New Roman).
    - Maintain consistent font styles for all headings and content.
 
9. Page Layout:
   - The page width must be constrained to 100%, ensuring it does not exceed this width.
   - Use "Overflow-wrap: break-word;" to handle long text gracefully without exceeding the table width.
   - Ensure all tables fit within this page width, with no overflow beyond the page boundaries.

The code:
{code_content}
"""


# def process_changed_files(directory_path):
#     """Processes each changed file in the directory and generates a review."""
#     # Get the list of changed files using git diff
#     result = subprocess.run(['git', 'diff', '--name-only', 'HEAD^..HEAD'], capture_output=True, text=True)
#     changed_files = result.stdout.splitlines()

#     # Filter changed files that are in the specified directory
#     code_files = [file for file in changed_files if file.startswith(directory_path)]

#     for file_path in code_files:
#         if os.path.isfile(file_path):
#             # Read and review the changed file
#             code_content = read_file_content(file_path)
#             code_content_with_line_numbers = add_line_numbers(code_content)
#             print(f"\n\nReviewing file: {file_path}")

#             start_time = time.time()

#             response_text = generate_content_for_review(code_content_with_line_numbers)
#             time_taken = time.time() - start_time

#             # Append the review response to the output file
#             if response_text.strip():
#                 append_to_output_file(response_text, os.path.basename(file_path), file_path, time_taken)
#             else:
#                 append_to_output_file("No response received from the AI model.", os.path.basename(file_path), file_path, time_taken)
#         else:
#             print(f"{file_path} does not exist or was renamed. Skipping...")


def process_changed_files(directory_path):
    """Processes each changed file in the directory and generates a review."""
    # Get the list of changed files using git diff
    result = subprocess.run(['git', 'diff', '--name-only', 'HEAD^..HEAD'], capture_output=True, text=True)
    changed_files = set(result.stdout.splitlines())

    # Traverse the directory using os.walk
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)

            # Process only files that are listed in the git diff output
            if file_path in changed_files and os.path.isfile(file_path):
                # Read and review the changed file
                code_content = read_file_content(file_path)
                code_content_with_line_numbers = add_line_numbers(code_content)
                print(f"\n\nReviewing file: {file_path}")

                start_time = time.time()

                response_text = generate_content_for_review(code_content_with_line_numbers)
                time_taken = time.time() - start_time

                # Append the review response to the output file
                if response_text.strip():
                    append_to_output_file(response_text, os.path.basename(file_path), file_path, time_taken)
                else:
                    append_to_output_file("No response received from the AI model.", os.path.basename(file_path), file_path, time_taken)
            elif file_path not in changed_files:
                print(f"{file_path} is not listed in changed files. Skipping...")


def main():
    # Define the directory path to process files
    python_dir = "folder"

    # Process changed files and generate reviews
    process_changed_files(python_dir)


if __name__ == "__main__":
    main()

