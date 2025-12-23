import streamlit as st
import pandas as pd
import os
import json
import io
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

# 1. Load Security Credentials from .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# 2. Page Configuration
st.set_page_config(page_title="data entry agent", page_icon="📚", layout="wide")

# 3. Branding
st.title("📚 data entry agent: National Digitization Portal")
st.markdown("---")

if not API_KEY:
    st.error("🔑 API Key not found! Please ensure GEMINI_API_KEY is set in your .env file.")
    st.stop()

# 4. Initialize Client
client = genai.Client(api_key=API_KEY)
MODEL_ID = "models/gemini-2.5-flash"

# 5. Sidebar Settings
with st.sidebar:
    st.header("⚙️ Configuration")
    target_cols = st.text_input("Extraction Columns:", "Student Name, ID, Grade")
    st.info(f"Engine: {MODEL_ID}")
    st.write("---")
    st.write("📍 **Location:** Kigali, Rwanda")

# 6. Bulk File Uploader
uploaded_files = st.file_uploader(
    "Drag and drop handwritten records (JPG/PNG)", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if uploaded_files:
    # Preview Grid
    st.subheader("🖼️ Previewing Uploads")
    cols = st.columns(4)
    for idx, file in enumerate(uploaded_files):
        cols[idx % 4].image(file, use_container_width=True, caption=file.name)

    if st.button("🚀 Process All Documents"):
        all_results = []
        progress_bar = st.progress(0)
        
        for i, file in enumerate(uploaded_files):
            try:
                # Read image bytes
                img_bytes = file.getvalue()
                
                # AI Prompt
                prompt = (
                    f"Extract data for these columns: {target_cols}. "
                    "Return strictly as a JSON list. If handwriting is illegible, use 'N/A'."
                )
                
                # AI Execution
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=[
                        prompt,
                        types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
                    ],
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                
                # Parse and Collect
                batch_data = json.loads(response.text)
                # Add a column to track which file the data came from
                for entry in batch_data:
                    entry["Source_File"] = file.name
                all_results.extend(batch_data)
                
            except Exception as e:
                st.error(f"❌ Error processing {file.name}: {str(e)}")
            
            # Update Progress
            progress_bar.progress((i + 1) / len(uploaded_files))

        # 7. Final Output
        if all_results:
            st.success(f"✅ Successfully Digitized {len(uploaded_files)} Records!")
            df = pd.DataFrame(all_results)
            
            # Interactive Table
            st.subheader("📊 Consolidated Data Table")
            st.data_editor(df, use_container_width=True, num_rows="dynamic")
            
            # CSV Export
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="💾 Download Consolidated CSV",
                data=csv_buffer.getvalue(),
                file_name="mwalimu_bulk_export.csv",
                mime="text/csv"
            )
            st.balloons()
