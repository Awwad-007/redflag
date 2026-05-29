"""
WAPPFLY SANDBOX SETUP
1. Sign up at https://app.wappfly.com
2. Click "Connect Device" and scan the QR code with your personal WhatsApp
3. Go to API Keys → generate a key → add it to .env as WAPPFLY_API_KEY
4. Go to Webhooks → set URL to: https://<your-ngrok-url>/whatsapp/webhook
5. Run ngrok locally: ngrok http 8000
6. Test by messaging the WhatsApp number you scanned from
"""

import os
import re
import json
import tempfile
import httpx
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from groq import Groq

router = APIRouter()

# Session State
# Keys are wa_id (phone numbers), values are dicts:
# - state: "IDLE" | "WAITING_FOR_DOC" | "PROCESSING"
# - last_analysis: dict | None
# - top_issues: list (max 3 critical/warning flags)
# - chat_history: list of {role, content} for multi-turn Q&A
USER_SESSIONS = {}

LEGAL_QA_SYSTEM_PROMPT = """You are RedFlag, an expert AI assistant specialising in Karnataka residential and commercial tenancy law, specifically the Karnataka Rent (Amendment) Act 2025/2026, the Karnataka Rent Control Act 2001, and related Indian tenancy regulations.

YOUR ROLE:
- Answer questions from tenants and landlords about their rights, obligations, and legal requirements under Karnataka tenancy law
- Explain clauses, legal terms, and procedures in plain, simple language
- Flag anything that sounds illegal or non-compliant
- Be concise — this is WhatsApp, keep replies under 400 words
- Use bullet points and bold (*bold*) for clarity on WhatsApp
- Always add a short disclaimer at the end

KEY RULES YOU KNOW:
- Security deposit: max 2 months rent (residential), max 6 months (commercial)
- All agreements must be digitally registered via Kaveri 2.0
- Rent hike requires 90 days written notice
- Eviction: 30 days notice (month-to-month), 90 days (fixed-term)
- Cutting utilities is illegal — ₹100/day fine for landlord
- Lock-in must be reciprocal
- Landlord needs 24-hour notice before entry
- Subletting needs written landlord consent

WHAT YOU DO NOT DO:
- Do not draft legal documents
- Do not represent anyone in legal proceedings
- Do not give advice specific to ongoing court cases
- Always recommend consulting an advocate for complex situations

FORMAT FOR WHATSAPP:
- Use *bold* for key terms
- Keep paragraphs short
- End with: _⚠️ This is general legal information, not legal advice. Consult an enrolled advocate for your specific situation._"""


def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        raise Exception("GROQ_API_KEY not configured")
    return Groq(api_key=api_key)


def get_user_session(wa_id: str) -> dict:
    if wa_id not in USER_SESSIONS:
        USER_SESSIONS[wa_id] = {
            "state": "IDLE",
            "last_analysis": None,
            "top_issues": [],
            "chat_history": []
        }
    return USER_SESSIONS[wa_id]


async def send_whatsapp_message(to: str, text: str) -> None:
    api_key = os.getenv("WAPPFLY_API_KEY")
    if not api_key:
        print("Warning: WAPPFLY_API_KEY is not configured")
        return

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://app.wappfly.com/api/send-message",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"phone": to, "message": text}
            )
            if response.status_code != 200:
                print(f"Wappfly error: {response.json()}")
        except Exception as e:
            print(f"Wappfly send error: {e}")


async def answer_legal_question(question: str, chat_history: list) -> str:
    """Use Groq to answer a legal question with conversation history."""
    try:
        client = get_groq_client()

        # Build messages with history (last 6 turns to stay within token limits)
        messages = [{"role": "system", "content": LEGAL_QA_SYSTEM_PROMPT}]
        messages += chat_history[-6:]
        messages.append({"role": "user", "content": question})

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            max_tokens=600,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Sorry, I couldn't process your question right now. Please try again. ({str(e)})"


async def download_whatsapp_media(download_url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(download_url)
        response.raise_for_status()

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(response.content)
        return tmp.name


def format_analysis_for_whatsapp(result: dict) -> str:
    score = result.get("compliance_score", 0)
    risk = result.get("overall_risk", "UNKNOWN")
    summary = result.get("summary", "")
    flags = result.get("flags", [])

    critical_count = sum(1 for f in flags if f.get("severity", "").upper() == "CRITICAL")
    warning_count  = sum(1 for f in flags if f.get("severity", "").upper() == "WARNING")
    info_count     = sum(1 for f in flags if f.get("severity", "").upper() == "INFO")

    top_issues = [f for f in flags if f.get("severity", "").upper() in ["CRITICAL", "WARNING"]][:3]

    top_lines = []
    for i, flag in enumerate(top_issues, 1):
        top_lines.append(
            f"{i}. *{flag.get('clause_title')}* — {flag.get('violation')} [{flag.get('statutory_reference')}]"
        )

    msg = (
        "🚩 *RedFlag Analysis Complete*\n\n"
        f"📊 *Compliance Score:* {score}/100\n"
        f"⚠️ *Risk Level:* {risk}\n\n"
        f"{summary}\n\n"
        f"*Issues Found ({len(flags)} flags):*\n"
        f"🔴 Critical: {critical_count}  🟡 Warning: {warning_count}  🔵 Notes: {info_count}\n"
    )

    if top_lines:
        msg += "\n*Top Issues:*\n" + "\n".join(top_lines)
        msg += '\n\nReply with a number (e.g. "2") to get full details on that issue.'

    msg += "\n\nYou can also ask me any question about Karnataka tenancy law — just type it!"
    msg += "\n\n_⚠️ RedFlag is not a law firm. Verify all outputs with an enrolled advocate._"
    return msg


def is_legal_question(text: str) -> bool:
    """Detect if a message is a legal question vs a command/greeting."""
    greetings = {"hi", "hello", "hey", "start", "help", "menu"}
    if text.lower().strip() in greetings:
        return False
    if text.strip().isdigit():
        return False

    # If it looks like a question or contains legal keywords, treat as Q&A
    legal_keywords = [
        "rent", "deposit", "evict", "notice", "lease", "tenant", "landlord",
        "agreement", "clause", "legal", "law", "right", "can", "allowed",
        "register", "kaveri", "lock-in", "utility", "sublet", "repair",
        "maintenance", "penalty", "fine", "increase", "hike", "month",
        "karnataka", "court", "illegal", "valid", "contract", "terminate"
    ]
    lower = text.lower()
    has_keyword = any(k in lower for k in legal_keywords)
    is_question = "?" in text or lower.startswith(("what", "how", "can", "is", "are", "do", "does", "when", "why", "who", "which"))

    return has_keyword or is_question or len(text) > 30


@router.post("/whatsapp/webhook")
async def handle_webhook(request: Request):
    try:
        payload = await request.json()
        print(f"Wappfly webhook: {json.dumps(payload)}")

        if payload.get("event") != "message":
            return JSONResponse(content={"status": "ignored"}, status_code=200)

        data = payload.get("data", {})
        wa_id = data.get("from")
        if not wa_id:
            return JSONResponse(content={"status": "no sender"}, status_code=200)

        session = get_user_session(wa_id)
        message_type = data.get("type")

        # ── TEXT MESSAGES ──────────────────────────────────────────────
        if message_type == "text":
            body = data.get("text", {}).get("body", "").strip()
            body_lower = body.lower()

            # 1. Greeting / menu
            if body_lower in ["hi", "hello", "hey", "start"]:
                session["state"] = "IDLE"
                session["chat_history"] = []
                await send_whatsapp_message(wa_id,
                    "👋 Hi! Welcome to *RedFlag* — Karnataka Rental Agreement Compliance.\n\n"
                    "Here's what I can do:\n"
                    "📄 *Send a PDF* — I'll analyse your rental agreement for legal issues\n"
                    "💬 *Ask anything* — type any question about Karnataka tenancy law\n\n"
                    "What would you like to do?"
                )

            # 2. Help / menu
            elif body_lower in ["help", "menu"]:
                await send_whatsapp_message(wa_id,
                    "🚩 *RedFlag Help Menu*\n\n"
                    "📄 Send a PDF → full compliance analysis\n"
                    "💬 Type a question → instant legal Q&A\n"
                    "🔢 Reply with a number → details on a flagged issue\n\n"
                    "_Example questions:_\n"
                    "• Can my landlord increase rent without notice?\n"
                    "• What is the max security deposit in Karnataka?\n"
                    "• Is my landlord allowed to cut electricity?\n"
                    "• How much notice do I need to vacate?"
                )

            # 3. Numbered follow-up on analysis flags
            elif session.get("top_issues") and (body.isdigit() or re.search(r'\b(\d+)\b', body)):
                match = re.search(r'\b(\d+)\b', body)
                num = int(match.group(1)) if match else None
                top_issues = session["top_issues"]

                if num and 1 <= num <= len(top_issues):
                    flag = top_issues[num - 1]
                    sev_emoji = {"CRITICAL": "🔴", "WARNING": "🟡", "INFO": "🔵"}.get(flag.get("severity", "").upper(), "⚠️")
                    await send_whatsapp_message(wa_id,
                        f"{sev_emoji} *Issue #{num}: {flag.get('clause_title')}*\n\n"
                        f"*Severity:* {flag.get('severity')}\n"
                        f"*Category:* {flag.get('category')}\n\n"
                        f"*Excerpt:*\n\"{flag.get('original_text')}\"\n\n"
                        f"*Violation:*\n{flag.get('violation')}\n\n"
                        f"*Legal Reference:*\n{flag.get('statutory_reference')}\n\n"
                        f"*Recommendation:*\n{flag.get('recommendation')}\n\n"
                        "_Reply with another number or ask me a legal question._"
                    )
                else:
                    await send_whatsapp_message(wa_id,
                        f"Please reply with a number between 1 and {len(top_issues)}."
                    )

            # 4. Legal Q&A — the new feature
            elif is_legal_question(body):
                await send_whatsapp_message(wa_id, "🔍 Looking that up for you...")

                answer = await answer_legal_question(body, session["chat_history"])

                # Store in history for multi-turn context
                session["chat_history"].append({"role": "user", "content": body})
                session["chat_history"].append({"role": "assistant", "content": answer})

                await send_whatsapp_message(wa_id, answer)

            # 5. Fallback
            else:
                await send_whatsapp_message(wa_id,
                    "I'm not sure what you mean. You can:\n"
                    "📄 Send a PDF rental agreement to analyse\n"
                    "💬 Ask me a legal question\n"
                    "Type *help* to see all options."
                )

        # ── PDF DOCUMENT ───────────────────────────────────────────────
        elif message_type == "document":
            doc = data.get("document", {})
            if doc.get("mimetype") == "application/pdf":
                session["state"] = "PROCESSING"
                await send_whatsapp_message(wa_id,
                    "📥 PDF received! Analysing your rental agreement for Karnataka Rent Act compliance, please wait..."
                )

                tmp_path = None
                try:
                    download_url = doc.get("url")
                    if not download_url:
                        raise Exception("No download URL in payload")

                    tmp_path = await download_whatsapp_media(download_url)

                    from main import extract_text_from_pdf, analyze_with_groq
                    contract_text = extract_text_from_pdf(tmp_path)
                    analysis = await analyze_with_groq(contract_text)

                    top_issues = [
                        f for f in analysis.get("flags", [])
                        if f.get("severity", "").upper() in ["CRITICAL", "WARNING"]
                    ][:3]

                    session["last_analysis"] = analysis
                    session["top_issues"] = top_issues
                    session["state"] = "IDLE"

                    await send_whatsapp_message(wa_id, format_analysis_for_whatsapp(analysis))

                except Exception as e:
                    session["state"] = "IDLE"
                    print(f"PDF processing error: {e}")
                    await send_whatsapp_message(wa_id,
                        "❌ Couldn't process your PDF. Make sure it:\n"
                        "• Is under 10MB\n"
                        "• Contains selectable text (not a scanned image)\n"
                        "• Is a valid rental agreement\n\n"
                        "Try again or type a legal question instead."
                    )
                finally:
                    if tmp_path and os.path.exists(tmp_path):
                        try:
                            os.unlink(tmp_path)
                        except:
                            pass
            else:
                await send_whatsapp_message(wa_id,
                    "⚠️ Only PDF files are supported. Please send your agreement as a PDF."
                )

        # ── OTHER MESSAGE TYPES ────────────────────────────────────────
        else:
            await send_whatsapp_message(wa_id,
                "⚠️ I can only process PDF documents and text messages.\n"
                "Send your rental agreement as a PDF, or type a legal question."
            )

    except Exception as e:
        print(f"Unhandled webhook error: {e}")

    return JSONResponse(content={"status": "success"}, status_code=200)