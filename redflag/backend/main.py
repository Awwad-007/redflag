import os
import json
import asyncio
import tempfile
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pdfplumber
from groq import Groq
from dotenv import load_dotenv
import aiofiles
import re

load_dotenv()

app = FastAPI(title="RedFlag API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))

KARNATAKA_RENT_ACT_CONTEXT = """
You are an expert Indian legal compliance engine specializing in the Karnataka Rent (Amendment) Act 2025/2026.
You ONLY flag objective statutory deviations — you do NOT provide legal advice or act as a lawyer.
Every response must include a mandatory disclaimer.

KEY STATUTORY RULES — Karnataka Rent (Amendment) Act 2025/2026:
1. SECURITY DEPOSIT (Residential): Maximum 2 months' rent. Any amount above is unenforceable.
2. SECURITY DEPOSIT (Commercial): Maximum 6 months' rent.
3. MANDATORY DIGITAL REGISTRATION: All agreements must be digitally registered via Kaveri 2.0 online portal.
4. NOTICE OF REGISTRATION: Local Rent Authority must be informed within 60 days of execution.
5. RENT INCREMENT/REVISION: Minimum 90 days (3 months) written notice required prior to any revision.
6. OVERSTAYING PENALTY: Landlord may claim double rent for first 2 months, four times rent thereafter.
7. CUTTING OFF BASIC UTILITIES: Strictly prohibited. Landlords face daily civil fines of ₹100/day.
8. LOCK-IN PERIOD: Any lock-in clause must be reciprocal and mutually binding.
9. SUBLETTING: Tenant cannot sublet without written landlord consent.
10. MAINTENANCE: Landlord responsible for structural repairs; tenant for day-to-day upkeep.
11. EVICTION NOTICE: Minimum 30 days written notice for month-to-month tenancy; 90 days for fixed-term.
12. ARBITRARY CLAUSES: Any clause allowing landlord unilateral entry without 24-hour notice is illegal.
"""

SYSTEM_PROMPT = KARNATAKA_RENT_ACT_CONTEXT + """

TASK: Analyze the provided rental agreement text and return a JSON response ONLY — no preamble, no markdown fences.

Return this exact JSON structure:
{
  "overall_risk": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "compliance_score": <integer 0-100>,
  "summary": "<2-3 sentence plain-language summary of the agreement's overall compliance>",
  "flags": [
    {
      "id": "<unique_id e.g. FLAG_001>",
      "severity": "INFO" | "WARNING" | "CRITICAL",
      "category": "<category name>",
      "clause_title": "<short title of the flagged clause>",
      "original_text": "<verbatim excerpt from the agreement, max 200 chars>",
      "violation": "<plain-language explanation of what rule this violates>",
      "statutory_reference": "<specific section of Karnataka Rent Act or relevant law>",
      "recommendation": "<what tenant/landlord should do>"
    }
  ],
  "compliant_clauses": [
    {
      "category": "<category>",
      "description": "<what is compliant and why>"
    }
  ],
  "metadata": {
    "tenant_name": "<extracted or null>",
    "landlord_name": "<extracted or null>",
    "property_address": "<extracted or null>",
    "monthly_rent": "<extracted or null>",
    "security_deposit": "<extracted or null>",
    "lease_duration": "<extracted or null>",
    "commencement_date": "<extracted or null>",
    "agreement_type": "RESIDENTIAL" | "COMMERCIAL" | "UNKNOWN"
  },
  "disclaimer": "RedFlag is an automated compliance search engine. It does not provide legal counsel, represent parties, or establish an attorney-client relationship. All outputs must be verified with an enrolled advocate. RedFlag is not a law firm."
}

CRITICAL: Return ONLY valid JSON. No text before or after. No markdown.
"""


def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to extract text from PDF: {str(e)}")
    
    if not text.strip():
        raise HTTPException(status_code=422, detail="No extractable text found in PDF. Please ensure it is not a scanned image-only document.")
    
    return text.strip()


async def analyze_with_groq(contract_text: str) -> dict:
    # Truncate to avoid token limits (keep first ~6000 chars which covers most contracts)
    truncated_text = contract_text[:8000] if len(contract_text) > 8000 else contract_text
    
    user_message = f"""Analyze this rental agreement for compliance with Karnataka Rent Act 2025/2026:

---AGREEMENT TEXT START---
{truncated_text}
---AGREEMENT TEXT END---

Return ONLY valid JSON as specified."""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.1,
            max_tokens=4096,
        )
        
        raw_response = response.choices[0].message.content.strip()
        
        # Strip markdown fences if present
        raw_response = re.sub(r'^```json\s*', '', raw_response)
        raw_response = re.sub(r'^```\s*', '', raw_response)
        raw_response = re.sub(r'\s*```$', '', raw_response)
        raw_response = raw_response.strip()
        
        result = json.loads(raw_response)
        return result
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"AI returned malformed JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq API error: {str(e)}")


@app.get("/")
async def root():
    return {"status": "RedFlag API is running", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/analyze")
async def analyze_contract(file: UploadFile = File(...)):
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    
    # Check file size (max 10MB)
    file_content = await file.read()
    if len(file_content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit.")
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name
    
    try:
        # Extract text
        contract_text = extract_text_from_pdf(tmp_path)
        
        # Analyze with Groq
        analysis = await analyze_with_groq(contract_text)
        
        # Add word count metadata
        analysis["_meta"] = {
            "filename": file.filename,
            "char_count": len(contract_text),
            "word_count": len(contract_text.split())
        }
        
        return JSONResponse(content=analysis)
        
    finally:
        # Clean up temp file (zero-retention)
        try:
            os.unlink(tmp_path)
        except:
            pass


@app.post("/api/analyze-text")
async def analyze_text_contract(text: str = Form(...)):
    """Analyze contract from pasted text"""
    if len(text.strip()) < 100:
        raise HTTPException(status_code=400, detail="Text too short to be a valid contract.")
    
    analysis = await analyze_with_groq(text)
    analysis["_meta"] = {
        "filename": "pasted_text.txt",
        "char_count": len(text),
        "word_count": len(text.split())
    }
    
    return JSONResponse(content=analysis)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
