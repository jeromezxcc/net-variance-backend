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
            for page_number, page in enumerate(pdf.pages):
                table = page.extract_table()
print(f"\nPage {page_number + 1}: Table found? {bool(table)}")

if not table:
    print(f"Page {page_number + 1}: No table extracted")
    continue

print(f"Page {page_number + 1}: Table length: {len(table)}")

if len(table) < 2:
    print(f"Page {page_number + 1}: Table too short for header + rows")
    continue

print("Raw table content:", table)
df = pd.DataFrame(table[1:], columns=table[0])
print("Extracted columns:", df.columns.tolist())


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
                        except Exception as e:
                            print("Error processing row:", e)
                            continue

        print("Mismatches found:", mismatches)

        return {
            "status": "ok" if not mismatches else "mismatches",
            "errors": mismatches
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
