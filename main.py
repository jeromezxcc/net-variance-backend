from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import re
import io

# ✅ FIRST: define the app
app = FastAPI()

# ✅ THEN: apply CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["https://net-variance-frontend.vercel.app/upload/"]
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
                text = page.extract_text()
                if text:
                    full_text += text + "\n"

        # Debug
        print("=== PDF Contents Start ===")
        print(full_text)
        print("=== PDF Contents End ===")

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
            return {"result": "❌ Missing: Net Rate or Net Variance not found in PDF"}

    except Exception as e:
        return {"result": f"❌ Error: {str(e)}"}


