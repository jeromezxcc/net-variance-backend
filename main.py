from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://net-variance-frontend.vercel.app",  # (your Vercel frontend URL)
        "https://net-variance-backend-production.up.railway.app"  # if you want to allow backend to call itself
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    mismatches = []

    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if not table or len(table) < 2:
                continue

            df = pd.DataFrame(table[1:], columns=table[0])

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

    return {
        "status": "ok" if not mismatches else "mismatches",
        "errors": mismatches
    }
