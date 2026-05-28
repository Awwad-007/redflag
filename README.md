# 🚩 RedFlag — Legal Clarity Engine

> AI-powered rental agreement compliance checker for Karnataka, India.
> Instantly flags illegal clauses against the **Karnataka Rent (Amendment) Act 2025/26**.

---

## What It Does

RedFlag is a **WhatsApp-first + Web Dashboard** legal compliance engine designed for everyday Indians — gig workers, low-income tenants, families of undertrial prisoners. Upload any rental agreement PDF and get:

- **Compliance Score** (0–100) with risk level (Low / Medium / High / Critical)
- **Clause-by-clause flags** mapped to specific statutory rules
- **Compliant clauses** clearly identified
- **Contract metadata** extraction (tenant, landlord, rent, deposit, dates)
- **Plain-language explanations** of every violation
- All in under 10 seconds

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript + Vite |
| Styling | CSS Modules (Fraunces + DM Sans) |
| Backend | Python 3.11 + FastAPI |
| PDF Processing | pdfplumber |
| Legal AI | Llama 3.3 70B via Groq API |
| HTTP Client | Axios |
| File Upload | react-dropzone |

---

## Project Structure

```
redflag/
├── frontend/                  # React TypeScript app
│   ├── src/
│   │   ├── components/        # UI components
│   │   │   ├── Header.tsx
│   │   │   ├── HeroSection.tsx
│   │   │   ├── UploadZone.tsx
│   │   │   ├── ScoreRing.tsx
│   │   │   ├── FlagCard.tsx
│   │   │   ├── MetadataPanel.tsx
│   │   │   └── ResultsDashboard.tsx
│   │   ├── api/client.ts      # Axios API client
│   │   ├── types/index.ts     # TypeScript types
│   │   ├── App.tsx
│   │   └── index.css          # Global design tokens
│   └── package.json
│
└── backend/                   # FastAPI server
    ├── main.py                # All routes + Groq integration
    ├── requirements.txt
    └── .env.example
```

---

## Setup & Running

### 1. Get a Groq API Key
Sign up free at [console.groq.com](https://console.groq.com) — Llama 3.3 70B is free tier eligible.

### 2. Backend Setup

```bash
cd backend

# Copy env file
cp .env.example .env

# Add your key to .env:
# GROQ_API_KEY=gsk_xxxxxxxxxxxx

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn main:app --reload --port 8000
```

Backend runs at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend

# Copy env file
cp .env.example .env
# VITE_API_URL=http://localhost:8000

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs at: `http://localhost:5173`

---

## API Endpoints

### `POST /api/analyze`
Upload a PDF for analysis.

**Request:** `multipart/form-data` with `file` field (PDF only, max 10MB)

**Response:**
```json
{
  "overall_risk": "HIGH",
  "compliance_score": 42,
  "summary": "This agreement contains 3 critical violations...",
  "flags": [
    {
      "id": "FLAG_001",
      "severity": "CRITICAL",
      "category": "Security Deposit",
      "clause_title": "Excessive Security Deposit",
      "original_text": "...10 months' rent as security deposit...",
      "violation": "Exceeds the 2-month cap under Section 4...",
      "statutory_reference": "Karnataka Rent Act 2025/26, Section 4",
      "recommendation": "Negotiate deposit down to maximum 2 months..."
    }
  ],
  "compliant_clauses": [...],
  "metadata": {
    "tenant_name": "John Doe",
    "monthly_rent": "₹25,000",
    ...
  },
  "disclaimer": "..."
}
```

### `POST /api/analyze-text`
Analyze pasted contract text.

**Request:** `multipart/form-data` with `text` field

---

## Legal Compliance

RedFlag strictly follows the **pith and substance test** from *BCI v. A.K. Balaji (2018)*:

- ✅ Acts as an **automated compliance search engine** only
- ✅ Flags **objective statutory deviations** (deposit > 2 months, missing notice periods, etc.)
- ✅ Does **not** provide custom legal counsel or draft agreements
- ✅ Mandatory disclaimer on every response
- ✅ **Zero-retention**: documents processed in RAM and deleted immediately
- ✅ **DPDPA 2023 compliant**: no document storage, no PII retention

---

## Hackathon Build Notes

### What's included (MVP + Level 2):
- [x] Full PDF upload and text extraction
- [x] Groq/Llama 3.3 70B legal analysis
- [x] Karnataka Rent Act 2025/26 rule set
- [x] Severity-coded flag cards (Critical / Warning / Info)
- [x] Animated compliance score ring
- [x] Contract metadata extraction
- [x] Compliant clauses panel
- [x] Legal disclaimer on all outputs
- [x] Zero-retention architecture
- [x] Mobile-responsive design

### Future (Level 3 — post-hackathon):
- [ ] WhatsApp bot via Wappfly + n8n
- [ ] Bhashini API for Kannada/Hindi translation
- [ ] eCourts CourtWatch scraper
- [ ] Multi-state rent act support
