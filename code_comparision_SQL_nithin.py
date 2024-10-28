import os
import time
import vertexai
from vertexai.generative_models import GenerativeModel

GOOGLE_APPLICATION_CREDENTIALS = "service.json"
PROJECT_ID = "cedar-context-433909-d9"
LOCATION = "us-central1"
GENERATIVE_MODEL_NAME = "gemini-1.5-flash-001"

OUTPUT_FILE = "review01.html"
string=""
 
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
    hi vertexai you are an expert in sql. Please review the following  code and identify  syntax  errors:
    -I do not want my enrite code to display again ,i  want only the  syntax errors
    - Syntax Errors (highlight with **1. Syntax Error:**)
    - please give me only the syntax errors i do'nt want any extra information more than syntax error in a single line 
    - i thing you got me
    -The code to review:
        {code_py}
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
        end_time = time.time()
        print(f"Total time taken for {filename}: {round(end_time - start_time, 3)} seconds")
        return response.text
    except Exception as e:
        end_time = time.time()
        

        print(f"Total time taken for {filename}: {round(end_time - start_time, 3)} seconds")

        return f"Error generating review: {str(e)}"

def generate_review_comparision(code_py1,code_py2):
    prompt = f"""
Compare the sql error files {code_py1} and {code_py2}.

- Only show the  errors that are **new** in {code_py1} and not present in {code_py2}.
- Ignore any identical errors or content that appears same  in both files.
- Do not include any extra information other than  the new errors in {code_py1}.
- just show only new errors and remove all the extra information

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
        return response.text
    except Exception as e:
        return f"Error generating review: {str(e)}"

def generate_review_html(code_py,filename):
    start_time = time.time()
    prompt = f"""

       
you are an SQL expert.   
Please analyze the provided code snippet and provide the following information:
1. ** Syntax Errors :**
    - ** Identification **: Identify the exact error-causing line numbers and provide the exact syntax errors.
    - ** Explanation **: Provide a clear and concise explanation of each error.
    - ** Fix **: Suggest a specific fix for each identified error, providing only the necessary code to correct it without rewriting the entire code.
    - ** Note **: If no syntax errors are found, simply state "No Syntax Errors Found."
    - ** highlight  the word Syntax Error
 
2. ** Code Bugs :**
    - ** Identification **: Identify potential logical or runtime errors in the code.
    - ** Explanation **: Provide a detailed explanation of why the identified code segment is problematic.
    - ** Fix **: Suggest the necessary code changes to fix the bugs without rewriting the entire code.
    - ** Note **: If no code bugs found, simply state "No Code Bugs Found."
    - ** highlight the word Code Bugs
 
3. ** Security Vulnerabilities :**
    - ** Identification **: Highlight any potential security vulnerabilities in the code (e.g., SQL injection, XSS, insecure deserialization).
    - ** Explanation **: Provide a clear explanation of each identified vulnerability.
    - ** Fix **: Suggest code changes to mitigate the security risks without rewriting the entire code.
    - ** Note **: If no security vulnerabilities are found, simply state "No Security Vulnerabilities Found."
    - ** highlight the word Security Vulnerabilities
 
4. ** Duplicate Code :**
    - ** Identification **: Highlight sections of the code lines that are duplicated.
    - ** Suggestion **: Provide recommendations without rewriting the entire code.
    - ** Note **: If no code duplicate code is found, simply state "No duplicate code in this file."
    - ** highlight the word Duplicate Code
 
5. ** Code Improvement Suggestions :**
    - ** Identification **: Highlight sections of the code that can be improved.
        - This could include:
        - Unnecessary complexity
        - Redundant code blocks
        - Potential for using more concise constructs (e.g., list comprehensions, loops)
    - ** Suggestion **: Provide specific points for improvement and the necessary code changes without rewriting the entire code.
    - ** Note **: If no code improvement suggestions are found, simply state "No Code Improvement Suggestions Found."
    - ** highlight the word Code Improvement Suggestions

6. ** Don't write any kind of code or code snippet in the output: **

7.Generate the output in a purely HTML format so that the file can be opened and displayed as a proper web page.
  - Maintain a consistent format for all review responses.
  - Clearly separate review responses for each file:
      - Each file's review should be in a distinct section, easily identifiable with proper headings and spacing.
  - Table Format: Structure the content in tables with the following specifications:
      - Use appropriate column names such as "Identification," "Explanation," and "Fix" (or relevant headers based on the context).
      - Populate the rows with detailed content corresponding to each header.
8. Make sure the tables have no background color. Avoid using any colored backgrounds, including green.
9. Ensure that there is no "File : " section/heading in the response.
10. Headings like syntax errors, code bugs, security vulnerabilities, duplicate code and code improvement suggestions must be bold, numbered and in the same format for all the response files.
 
11. add one more column to the every table column name is criticality in that column give the complexcity of the code like low or medium or high based on your reviewing the code.
 
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


def main(code_py,filename):
    
    numbered_code = error_refer(code_py) 
   
    if a=="1":
         review = generate_review_html(numbered_code,filename)

    else:
        review = generate_review(numbered_code,filename)

   
    return review

def createfolder(folder_path):
     
    try:
        os.makedirs(folder_path, exist_ok=True)  # exist_ok=True prevents error if folder exists
        
    except Exception as e:
        print(f"Error creating folder: {e}")


def read_file_content(file_path):
    """Reads the content of the file."""
    with open(file_path, 'r') as file:
        return file.read()


def read_files_in_directory(directory_path):
    """Reads all sql files in the given directory."""
    # List to store content of each file
    global string
    file_contents = {}
    if a=="2":
        createfolder("ignore")

    # Loop through each file in the directory
    for filename in os.listdir(directory_path):
        # Check if the file is a sql file
        if filename.endswith('.sql'):
            file_path = os.path.join(directory_path, filename)
            
            content = read_file_content(file_path)
            file_contents[filename] = content
           
            file=main(content,filename)
            if a=="1":
                writefile(file,filename,file_path)
            elif a=="2":
                
                writefilebyfile(file,filename)
            elif a=="3":
                file_path=f"ignore/{filename}_ignore.txt"
                code_py1=read_file_content(file_path)

                newreview=generate_review_comparision(file,code_py1)
                
                writefile(newreview,filename,file_path)
                 

            
    
    
def writefile(review,filename,file_path):
    global OUTPUT_FILE
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


def writefilebyfile(review,filename):

    ignorefile = f"ignore\{filename}_ignore.txt"
    with open(ignorefile, 'w') as output_file:
    # Write a heading
                
                output_file.write(review)
                

a=input("hello ,i am vertex AI. if this is your 1st run press 1 else 2 else 3  :  ")
if a=="1":
    directory_path = r"C:\taskgcp\SQL_files5"

    read_files_in_directory(directory_path)

    
elif a=="2":

    directory_path = r"C:\taskgcp\SQL_files5"
    read_files_in_directory(directory_path)

elif a=="3":   
     
    directory_path = r"C:\taskgcp\SQL_files5"
    read_files_in_directory(directory_path)
     