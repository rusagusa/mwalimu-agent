import os
import csv
import json
from google import genai
from google.genai import types

# 1. Setup
client = genai.Client(api_key="AIzaSyCbOc_Y0inBFzu7WprAkBmy63k3_IluSDU")
MODEL_ID = "models/gemini-2.5-flash"

def save_to_csv(json_data, filename="extracted_data.csv"):
    """Converts JSON list to a CSV file."""
    if not json_data:
        return
    
    try:
        # Get headers from the first dictionary keys
        headers = json_data[0].keys()
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(json_data)
        
        print(f"\n💾 SUCCESS: Data saved to {os.path.abspath(filename)}")
    except Exception as e:
        print(f"❌ CSV Error: {e}")

def run_extraction(image_path, columns):
    print(f"🔍 Scanning {image_path}...")
    
    if not os.path.exists(image_path):
        print(f"❌ Error: File '{image_path}' not found!")
        return

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    prompt = f"Extract data for these columns: {columns}. Return strictly as a JSON list."

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[
                prompt,
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
            ],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        # Parse text into JSON
        extracted_json = json.loads(response.text)
        print("\n✅ DATA EXTRACTED SUCCESSFULLY")
        
        # Save to CSV
        save_to_csv(extracted_json)
        
    except Exception as e:
        print(f"\n❌ AI Error: {e}")

if __name__ == "__main__":
    # Ensure this matches your uploaded image name
    run_extraction("my_image.jpeg", "Name, ID, Grade")