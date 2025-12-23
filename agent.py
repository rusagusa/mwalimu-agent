import os
import json
import csv
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Load security credentials
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ ERROR: GEMINI_API_KEY not found in .env file!")

# 2. Initialize the AI Client
client = genai.Client(api_key=API_KEY)
MODEL_ID = "models/gemini-2.5-flash"

def save_to_csv(data, filename="mwalimu_output.csv"):
    """Saves a list of dictionaries to a CSV file."""
    if not data:
        return
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    print(f"✅ Data saved to {filename}")

def run_extraction(image_path, target_columns):
    """Processes an image and extracts structured data."""
    print(f"🚀 Processing: {image_path}...")
    
    if not os.path.exists(image_path):
        print(f"❌ File not found: {image_path}")
        return

    # Load image as bytes
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    # The Prompt: Telling the AI exactly what we need
    prompt = (
        f"Act as a Rwandan data entry expert. Extract the following columns: {target_columns}. "
        "Return the result strictly as a JSON list. If a value is unclear, use 'null'."
    )

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[
                prompt,
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        # Parse and save
        extracted_data = json.loads(response.text)
        print(f"📝 Extracted: {json.dumps(extracted_data, indent=2)}")
        
        save_to_csv(extracted_data)
        return extracted_data

    except Exception as e:
        print(f"❌ AI Extraction failed: {e}")
        return None

if __name__ == "__main__":
    # Change 'my_image.jpeg' to your actual file name
    run_extraction("my_image.jpeg", "Name, ID Number, Grade")