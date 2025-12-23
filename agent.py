import os
from google import genai
from google.genai import types

# 1. Setup with your API Key
client = genai.Client(api_key="AIzaSyCbOc_Y0inBFzu7WprAkBmy63k3_IluSDU")

def find_working_model():
    print("🔎 Checking available models for your API key...")
    try:
        # Get all models that support generating content
        models = [m.name for m in client.models.list() if "generateContent" in m.supported_actions]
        
        # Priority list for 2025
        priority = ["models/gemini-3-flash", "models/gemini-2.5-flash", "models/gemini-2.0-flash"]
        
        for p in priority:
            if p in models:
                print(f"✅ Found priority model: {p}")
                return p
        
        if models:
            print(f"⚠️ Priority models not found. Using available: {models[0]}")
            return models[0]
        
    except Exception as e:
        print(f"❌ Error listing models: {e}")
    
    return "models/gemini-2.0-flash" # Last resort fallback

def run_extraction(image_path, columns):
    model_id = find_working_model()
    
    if not os.path.exists(image_path):
        print(f"❌ Error: {image_path} not found.")
        return

    print(f"🚀 Extracting data using {model_id}...")
    
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    prompt = f"Extract data for these columns: {columns}. Return strictly as a JSON list."

    try:
        response = client.models.generate_content(
            model=model_id,
            contents=[
                prompt,
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
            ]
        )
        print("\n✅ DATA EXTRACTED SUCCESSFULLY:")
        print(response.text)
    except Exception as e:
        print(f"\n❌ Execution Error: {e}")

if __name__ == "__main__":
    run_extraction("my_image.jpeg", "Name, ID, Grade")