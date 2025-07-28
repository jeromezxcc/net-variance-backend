from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import re
import io

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Optional: restrict to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() + "\n"

        # Debug: Print PDF contents
        print("=== PDF Contents Start ===")
        print(full_text)
        print("=== PDF Contents End ===")

        # Find Net Variance and Net Rate
        variance_match = re.search(r"Net Variance\s*=?\s*(-?\d+)", full_text)
        rate_match = re.search(r"Net Rate\s*=?\s*(-?\d+)", full_text)

        if variance_match and rate_match:
            variance = int(variance_match.group(1))
            rate = int(rate_match.group(1))

            if variance == -rate:
                return {"result": f"✅ Passed: Net Variance = {variance}, Net Rate = {rate}"}
            else:
                return {"result": f"⚠️ Failed: Net Variance = {variance}, Net Rate = {rate}"}
        else:
            return {"result": "❌ Missing values: Could not detect Net Variance or Net Rate in the PDF"}

    except Exception as e:
        return {"result": f"❌ Error processing file: {str(e)}"}
