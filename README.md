# 🚩 RedFlag — Legal Clarity Engine

> AI-powered rental agreement compliance checker for Karnataka, India.  
> Instantly flags illegal clauses against the **Karnataka Rent (Amendment) Act 2025/26** — via a web dashboard and WhatsApp chatbot.

---

## What It Does

RedFlag is a **WhatsApp-first + Web Dashboard** legal compliance engine designed for everyday Indians — tenants, gig workers, and families navigating rental agreements without legal support. Upload any rental agreement PDF or just ask a question and get:

- **Compliance Score** (0–100) with risk level (Low / Medium / High / Critical)
- **Clause-by-clause flags** mapped to specific statutory rules
- **Compliant clauses** clearly identified
- **Contract metadata** extraction (tenant, landlord, rent, deposit, dates)
- **Plain-language explanations** of every violation
- **WhatsApp chatbot** — ask any Karnataka tenancy law question, no PDF needed
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
| WhatsApp | Wappfly API + ngrok |
| HTTP Client | Axios + httpx |
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
│   ├── postcss.config.cjs     # PostCSS config
│   ├── vite.config.ts         # Vite + dev proxy
│   └── package.json
│
├── backend/                   # FastAPI server
│   ├── main.py                # All routes + Groq integration
│   ├── whatsapp.py            # WhatsApp chatbot + legal Q&A
│   ├── requirements.txt
│   └── .env.example
│
├── setup.sh                   # First-time install script
└── start.sh                   # Start both servers
```

---

## Setup & Running

### Prerequisites
- Python 3.10+
- Node.js 18+
- A free [Groq API key](https://console.groq.com)

---

### Option A — Quickstart scripts

```bash
# First time only
./setup.sh

# Every time after
./start.sh
```

- Web app: `http://localhost:5173`
- API docs: `http://localhost:8000/docs`

---

### Option B — Two terminals (manual)

**Terminal 1 — Backend:**
```bash
cd backend
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## WhatsApp Bot Setup

The WhatsApp bot lets users analyse PDFs and ask legal questions directly from WhatsApp — no web browser needed.

### 1. Set up Wappfly
1. Sign up at [app.wappfly.com](https://app.wappfly.com)
2. Click **Connect Device** → scan the QR code with your WhatsApp
3. Go to **API Keys** → generate a key → add it to `backend/.env`:
   ```
   WAPPFLY_API_KEY=your_key_here
   ```

### 2. Expose your backend with ngrok
```bash
# Install ngrok from https://ngrok.com, then:
ngrok http 8000
# Copy the https URL it gives you e.g. https://abc123.ngrok-free.app
```

### 3. Set the webhook
In Wappfly → **Webhooks** → set URL to:
```
https://abc123.ngrok-free.app/whatsapp/webhook
```

### 4. Start the backend and test
Restart your backend, then WhatsApp the number you scanned from and type **"hi"**.

---

### WhatsApp Bot Features

| You send | Bot does |
|---|---|
| `hi` / `hello` | Welcome message + menu |
| `help` | Shows all available commands |
| Any legal question | Instant AI answer with Karnataka Rent Act context |
| A PDF file | Full compliance analysis with score + flags |
| `1`, `2`, `3` after analysis | Detailed breakdown of that specific flag |
| Follow-up questions | Remembers conversation context |

**Example questions the bot answers:**
- *"Can my landlord increase rent without notice?"*
- *"What is the maximum security deposit in Karnataka?"*
- *"Is my landlord allowed to cut my electricity?"*
- *"My landlord wants 6 months deposit — is that legal?"*
- *"How much notice do I need to give before vacating?"*

---

## API Endpoints

### `POST /api/analyze`
Upload a PDF for compliance analysis.

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
      "original_text": "...10 months rent as security deposit...",
      "violation": "Exceeds the 2-month cap under Section 4...",
      "statutory_reference": "Karnataka Rent Act 2025/26, Section 4",
      "recommendation": "Negotiate deposit down to maximum 2 months..."
    }
  ],
  "compliant_clauses": [...],
  "metadata": {
    "tenant_name": "John Doe",
    "monthly_rent": "₹25,000"
  },
  "disclaimer": "..."
}
```

### `POST /api/analyze-text`
Analyze pasted contract text instead of a PDF.

**Request:** `multipart/form-data` with `text` field

### `GET /health`
Health check endpoint used by `start.sh`.

### `POST /whatsapp/webhook`
Wappfly webhook — handles incoming WhatsApp messages.

---

## Legal Compliance

RedFlag strictly follows the **pith and substance test** from *BCI v. A.K. Balaji (2018)*:

- ✅ Acts as an **automated compliance search engine** only
- ✅ Flags **objective statutory deviations** (deposit > 2 months, missing notice periods, etc.)
- ✅ Does **not** provide custom legal counsel or draft agreements
- ✅ Mandatory disclaimer on every response
- ✅ **Zero-retention**: documents processed in memory and deleted immediately
- ✅ **DPDPA 2023 compliant**: no document storage, no PII retention

---

## Build Checklist

### MVP (done):
- [x] PDF upload and text extraction
- [x] Groq / Llama 3.3 70B legal analysis
- [x] Karnataka Rent Act 2025/26 rule set
- [x] Severity-coded flag cards (Critical / Warning / Info)
- [x] Animated compliance score ring
- [x] Contract metadata extraction
- [x] Compliant clauses panel
- [x] Legal disclaimer on all outputs
- [x] Zero-retention architecture
- [x] Mobile-responsive design

### Level 2 (done):
- [x] WhatsApp chatbot via Wappfly
- [x] Free-text legal Q&A (no PDF required)
- [x] Multi-turn conversation memory
- [x] Flag detail drill-down on WhatsApp

### Level 3 (post-hackathon):
- [ ] Bhashini API for Kannada / Hindi translation
- [ ] eCourts CourtWatch scraper
- [ ] Multi-state rent act support
- [ ] Voice note support on WhatsApp

---

## Environment Variables

### `backend/.env`
```
GROQ_API_KEY=       # Required — get from console.groq.com
WAPPFLY_API_KEY=    # Optional — only needed for WhatsApp bot
```

### `frontend/.env`
```
VITE_API_URL=http://localhost:8000
```

---

> ⚠️ **Disclaimer:** RedFlag is an automated compliance search engine. It does not provide legal counsel, represent parties, or establish an attorney-client relationship. All outputs must be verified with an enrolled advocate. RedFlag is not a law firm.