# 🚩 RedFlag — Legal Clarity Engine

> **AI‑powered rental agreement compliance checker for Karnataka, India.** Instantly flags illegal clauses against the **Karnataka Rent (Amendment) Act 2025/26**.

---

## ✨ What It Does

RedFlag is a **WhatsApp‑first + Web Dashboard** legal compliance engine tailored for everyday Indians – gig workers, low‑income tenants, and local businesses. Upload any rental agreement PDF to the web portal **or** chat with the WhatsApp assistant to receive:

- **Compliance Score** (0‑100) with risk tier (Low / Medium / High / Critical)
- **Clause‑by‑clause flags** mapped to specific statutory rules
- **Compliant clauses** clearly identified
- **Contract metadata** (tenant, landlord, rent, deposit, dates, etc.)
- **Plain‑language explanations** for every violation
- **Interactive Q&A** via WhatsApp for follow‑up queries
- **Lightning‑fast responses** – under 10 seconds per document

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18 + TypeScript + Vite |
| **Styling** | CSS Modules (Fraunces + DM Sans) – modern dark‑mode, glassmorphism, micro‑animations |
| **Backend** | Python 3.11 + FastAPI |
| **PDF Processing** | pdfplumber |
| **Legal AI** | Llama 3.3 70B via Groq API |
| **WhatsApp Integration** | **Wappfly Sandbox** – QR‑code WhatsApp Web wrapper (no Meta approval needed) |
| **HTTP Client** | Axios (frontend) • httpx (backend, async) |
| **File Upload** | react-dropzone |
| **Testing** | unittest + FastAPI TestClient |
| **CI / CD** | GitHub Actions (run tests, lint, format) |

---

## 📂 Project Structure

```
redflag/
├── frontend/                  # React TypeScript app
│   ├── src/
│   │   ├── components/        # UI components (Header, Hero, UploadZone, …)
│   │   ├── api/client.ts      # Axios API client
│   │   ├── types/index.ts     # TypeScript types
│   │   ├── App.tsx
│   │   └── index.css          # Global design tokens
│   └── package.json
│
└── backend/                   # FastAPI server
    ├── main.py                # Core FastAPI app & REST endpoints
    ├── whatsapp.py            # Wappfly webhook router & message handling
    ├── test_endpoints.py      # Automated webhook test suite
    ├── requirements.txt       # Dependency configuration
    └── .env.example           # Environment template
```

---

## ⚙️ Setup & Running

### 1️⃣ Backend

```bash
cd backend
# Copy env template and add your keys
cp .env.example .env
# Edit .env → set GROQ_API_KEY and WAPPFLY_API_KEY
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend URL: `http://localhost:8000`   (Docs: `http://localhost:8000/docs`)

### 2️⃣ Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

---

## 📱 WhatsApp Integration (Wappfly Sandbox)

1. **Sign Up** – Create an account on [Wappfly](https://app.wappfly.com).
2. **Connect Device** – In the console click **Connect Device** and scan the QR code with WhatsApp > Linked Devices.
3. **API Key** – Copy the generated API key and add it to `backend/.env`:
   ```env
   WAPPFLY_API_KEY=your_key_here
   ```
4. **Expose Local Server** – Use `ngrok` (or similar) so Wappfly can reach your webhook:
   ```bash
   ngrok http 8000
   ```
5. **Configure Webhook URL** – In the Wappfly console set:
   `https://<your‑ngrok‑subdomain>.ngrok-free.app/whatsapp/webhook`
6. **Start Chatting** – Send a message or PDF to the connected WhatsApp number and watch RedFlag work!

---

## 📡 API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/analyze` | Upload a PDF (multipart) → returns compliance JSON.
| `POST` | `/api/analyze-text` | Upload plain text → returns compliance JSON.
| `POST` | `/whatsapp/webhook` | Receives Wappfly events (text or document) and replies via WhatsApp.

---

## 🧪 Testing

```bash
cd backend
python -m unittest discover -v
```

The suite covers:
- Webhook payload parsing
- Session state machine
- Message formatting & error handling

---

## 📜 Legal Compliance & Ethics

RedFlag adheres to the **pith‑and‑substance test** (BCI v. A.K. Balaji 2018) and follows strict data‑privacy guidelines:
- **Zero‑retention** – Files are processed in RAM and deleted instantly.
- **DPDPA 2023** – No PII is stored long‑term.
- **No legal advice** – Only flags statutory non‑compliance; a disclaimer appears on every response.

---

## 🏆 Hackathon Build Highlights (MVP + Level 2/3)

- ✅ Full PDF upload & text extraction
- ✅ Groq/Llama 3.3 70B legal analysis
- ✅ Karnataka Rent Act 2025/26 rule set
- ✅ Severity‑coded flag cards (Critical / Warning / Info)
- ✅ Animated compliance score ring
- ✅ Contract metadata extraction
- ✅ Compliant clauses panel
- ✅ Legal disclaimer on all outputs
- ✅ Zero‑retention architecture
- ✅ Mobile‑responsive design
- ✅ **WhatsApp chatbot via Wappfly**
- ✅ In‑memory conversational session states & follow‑up Q&A
- ✅ Automated webhook unit‑test suite

### Future Roadmap (Level 3)
- 🔲 Bhashini API for Kannada/Hindi translation
- 🔲 eCourts CourtWatch scraper
- 🔲 Multi‑state rent‑act support

---

*Made with ❤️ by the RedFlag team – powering transparent rentals across Karnataka.*
