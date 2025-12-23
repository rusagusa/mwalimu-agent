import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
import json
from PIL import Image
import io

# 1. Page Configuration
st.set_page_config(page_title="data entry agency", page_icon="📚", layout="wide")

# 2. API Setup
API_KEY = "AIzaSyCbOc_Y0inBFzu7WprAkBmy63k3_IluSDU"
client = genai.Client(api_key=API_KEY)
MODEL_ID = "models/gemini-2.5-flash"

# 3. Branding & Header
st.title("📚 data entry: Bulk Digitalizer")
st.markdown("Upload multiple classroom records to generate a single consolidated report.")

# 4. Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Extraction Settings")
    target_cols = st.text_input("Data Columns (comma-separated):", "Student Name, ID, Marks")
    st.info(f"Using Engine: {MODEL_ID}")

# 5. File Uploader (Accepts Multiple Files)
uploaded_files = st.file_uploader(
    "Upload handwritten record photos", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if uploaded_files:
    # Display image previews in a grid
    st.subheader("🖼️ Uploaded Documents")
    cols = st.columns(4)
    for idx, file in enumerate(uploaded_files):
        cols[idx % 4].image(file, use_container_width=True, caption=file.name)

    if st.button("🚀 Process All Records"):
        all_results = []
        progress_bar = st.progress(0)
        
        # 6. Processing Loop
        for i, file in enumerate(uploaded_files):
            with st.spinner(f"Transcribing {file.name}..."):
                try:
                    img_bytes = file.getvalue()
                    prompt = f"Extract data for {target_cols}. Return strictly as a JSON list."
                    
                    response = client.models.generate_content(
                        model=MODEL_ID,
                        contents=[
                            prompt,
                            types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
                        ],
                        config=types.GenerateContentConfig(response_mime_type="application/json")
                    )
                    
                    # Add current image results to our master list
                    current_data = json.loads(response.text)
                    all_results.extend(current_data)
                    
                except Exception as e:
                    st.error(f"Error in {file.name}: {e}")
            
            # Update progress
            progress_bar.progress((i + 1) / len(uploaded_files))

        # 7. Final Results & Download
        if all_results:
            st.success(f"✅ Successfully processed {len(uploaded_files)} files!")
            final_df = pd.DataFrame(all_results)
            
            # Display the consolidated table
            st.subheader("📊 Consolidated Data")
            st.data_editor(final_df, use_container_width=True)
            
            # One-click CSV Download
            csv_data = final_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="💾 Download Consolidated CSV",
                data=csv_data,
                file_name="mwalimu_bulk_report.csv",
                mime="text/csv",
                key="download-csv"
            )
            st.balloons()
