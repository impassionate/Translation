import openai
import time
import sys
import json
from docx import Document

# ... [your extraction function remains unchanged]
# Function to extract Java problems from the DOCX file
def extract_java_problems_from_docx(file_path):
    doc = Document(file_path)
    problems = {}
    current_problem_name = None
    current_problem_code = []

    for line in [paragraph.text.strip() for paragraph in doc.paragraphs if paragraph.text.strip()]:
        if "public" in line:
            if current_problem_name:
                current_problem_code.append(line)
                problems[current_problem_name] = "\n".join(current_problem_code)
        else:
            current_problem_name = line
            current_problem_code = []

    if current_problem_name and current_problem_code:
        problems[current_problem_name] = "\n".join(current_problem_code)
    
    return problems
# Updated function to translate Java code to Python using OpenAI API
def translate_java_to_python(java_code, api_key):
    openai.api_key = api_key
    start_time = time.time()
    prompt = f"Translate the following Java code to Python(return python code only) :\n\n{java_code}\n"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        end_time = time.time()
        translation_time = end_time - start_time
        translated_code = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error while translating the code: {e}")
        translated_code = ""
        translation_time = float('inf')
    
    return translated_code, translation_time

# New function to generate and test cases using OpenAI API
def generate_and_test_cases(python_code, api_key):
    openai.api_key = api_key
    prompt = f"return a score based on the your analysis of the code, max point 100 points (just return the score value, no need to show me the analysis) :\n\n{python_code}\n"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        test_score = float(response['choices'][0]['message']['content'].strip())
    except Exception as e:
        print(f"Error while generating and testing cases: {e}")
        test_score = 0.0
    
    return test_score

def save_results_to_json(results):
    overall_score = sum([problem_scores["total_score"] for problem_scores in results.values()]) / len(results)
    # Scaling the overall score from 0 to 100
    overall_score *= 100

    output_data = {
        "output": overall_score,
        "details": results
    }

    with open("output.json", "w") as outfile:
        json.dump(output_data, outfile, indent=4)
# Main function remains largely the same with added step for test case generation and evaluation
def extract_translate_and_evaluate(java_file_path, api_key):
    # Extract Java problems
    java_problems = extract_java_problems_from_docx(java_file_path)
    
    results = {}
    for problem_name, problem_code in java_problems.items():
        # Translate Java code to Python
        translated_code, time_taken = translate_java_to_python(problem_code, api_key)
        
        # Generate and test cases for translated code
        test_score = generate_and_test_cases(translated_code, api_key)
        time_score = 1 / time_taken
        memory_score = 10000 / sys.getsizeof(translated_code)
        total_score = (time_score + memory_score + test_score) / 3
        
        # Store results
        results[problem_name] = {
            "total_score": total_score,
            "time_score": time_score,
            "memory_score": memory_score,
            "test_score": test_score
        }
    # Save the results to output.json
    save_results_to_json(results)    
    return results

# usage:
api_key = "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"  # Remember to use your own key
results = extract_translate_and_evaluate("test.docx", api_key)
print(results)
