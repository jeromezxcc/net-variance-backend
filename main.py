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
        mismatches = []

        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if not table or len(table) < 2:
                    continue

                df = pd.DataFrame(table[1:], columns=table[0])
                print("Extracted columns:", df.columns.tolist())

                # Make sure the expected columns are present
                if "Net Rate" in df.columns and "Net Variance" in df.columns:
                    for _, row in df.iterrows():
                        try:
                            rate = float(str(row["Net Rate"]).replace(",", "").strip())
                            variance = float(str(row["Net Variance"]).replace(",", "").replace("−", "-").replace("–", "-").strip())
                            if rate != 0 and variance != -rate:
                                mismatches.append({
                                    "row": row.to_dict(),
                                    "reason": f"Net Variance ({variance}) ≠ -Net Rate ({rate})"
                                })
                        except Exception:
                            continue
                            
        print("Mismatches found:", mismatches)   
        return {
            "status": "ok" if not mismatches else "mismatches",
            "errors": mismatches
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
