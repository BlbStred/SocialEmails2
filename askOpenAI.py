import os
import sys
from openai import OpenAI
from dotenv import load_dotenv # run 'pip install python-dotenv'


load_dotenv()


# Reconfigure stdout to handle errors gracefully
sys.stdout.reconfigure(errors='replace')

# 1. Setup Client (Make sure your API key is in your environment variables)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def analyze_comment(input_text):
    print(f"--- Analyzing: {input_text[:50]}... ---")
    
    try:
        # 2. The Request
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a classifier. Answer 'YES' if the text is a comment on something, and 'NO' if it is not. Provide a brief reason."},
                {"role": "user", "content": input_text}
            ]
        )
        
        result = response.choices[0].message.content
        
        # 3. Defensive Printing 
        # Using .encode().decode() handles any stray characters like \u034f
        clean_result = result.encode('ascii', 'replace').decode('ascii')
        print(f"Result: {clean_result}")

    except Exception as e:
        # This catches API errors, connection issues, or encoding bugs
        print(f"An error occurred, but we're skipping it: {e}")

# --- Execution ---
test_strings = [
    "I really think the lighting in this photo is too harsh.",
    "The quick brown fox jumps over the lazy dog.",
    "This movie was a total waste of time, honestly. \u034f" # Including your troublemaker character
]

for s in test_strings:
    analyze_comment(s)

print("\nProgram finished successfully.")
