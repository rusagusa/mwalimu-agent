import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
import json
from PIL import Image
import os

# 1. Page Config
st.set_page_config(page_title="Mwalimu-Agent Pro", page_icon="📝", layout="wide")

# 2. Setup Gemini Client (Using your verified MLH key)
API_KEY = "AIzaSyCbOc_Y0inBFzu7WprAkBmy63k3_IluSDU"
client = genai.Client(api_key=API_KEY)

# 3. Sidebar Branding
with st.sidebar:
    st.title("🏫 Mwalimu-Agent")
    st.markdown("---")
    st.subheader("Config")
    # Using the model that worked in your terminal
    model_id = "models/gemini-2.5-flash"
    cols_input = st.text_input("Columns to Extract:", "Name, ID, Grade")

# 4. Main App Interface
st.title("🤖 Universal Handwritten Data Entry")
st.info(f"Agent Active: {model_id}")

uploaded_file = st.file_uploader("Upload Handwritten Record", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Show the uploaded image
    img = Image.open(uploaded_file)
    st.image(img, caption="Target Document", use_container_width=True)
    
    if st.button("🚀 Run Extraction"):
        with st.spinner("Agent is transcribing..."):
            try:
                # Convert image for the SDK
                img_bytes = uploaded_file.getvalue()
                
                prompt = f"Extract data for these columns: {cols_input}. Return strictly as a JSON list."
                
                response = client.models.generate_content(
                    model=model_id,
                    contents=[
                        prompt,
                        types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
                    ],
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                
                # Parse and display
                data = json.loads(response.text)
                df = pd.DataFrame(data)
                
                st.success("✅ Digitalization Complete!")
                # st.data_editor is the professional way to show AI data in 2025
                st.data_editor(df, use_container_width=True, num_rows="dynamic")
                
                st.download_button("💾 Download CSV", df.to_csv(index=False), "mwalimu_data.csv")
                st.balloons()
                
            except Exception as e:
                st.error(f"UI Error: {e}")