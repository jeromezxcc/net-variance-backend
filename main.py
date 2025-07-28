from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()  # ✅ THIS MUST COME BEFORE anything using "app"

# ✅ Add CORS to allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to ["https://net-variance-frontend.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    # Replace with your logic
    return {"result": "Processed successfully"}

        # Debug: Print PDF contents
        print("=== PDF Contents Start ===")
        print(full_text)
        print("=== PDF Contents End ===")

        # Try to find Net Variance and Net Rate values
        variance_match = re.search(r"Net Variance\s*=\s*(-?\d+)", full_text)
        rate_match = re.search(r"Net Rate\s*=\s*(-?\d+)", full_text)

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
