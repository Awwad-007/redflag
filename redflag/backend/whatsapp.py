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

router = APIRouter()

# Session State: Tracks user conversation states and analysis history
# Keys are wa_id (phone numbers), values are dicts containing:
# - state: "IDLE" | "WAITING_FOR_DOC" | "PROCESSING"
# - last_analysis: dict | None
# - top_issues: list (max 3 critical/warning flags for quick query details)
USER_SESSIONS = {}


def get_user_session(wa_id: str) -> dict:
    """Helper to retrieve or initialize a user session state."""
    if wa_id not in USER_SESSIONS:
        USER_SESSIONS[wa_id] = {
            "state": "IDLE",
            "last_analysis": None,
            "top_issues": []
        }
    return USER_SESSIONS[wa_id]


async def send_whatsapp_message(to: str, text: str) -> None:
    """Sends a text message to a user via the Wappfly API."""
    api_key = os.getenv("WAPPFLY_API_KEY")
    if not api_key:
        print("Warning: WAPPFLY_API_KEY is not configured in .env")
        return
        
    url = "https://app.wappfly.com/api/send-message"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "phone": to,
        "message": text
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=body, headers=headers)
            response_json = response.json()
            if response.status_code != 200:
                print(f"Error sending WhatsApp message via Wappfly: {response_json}")
            else:
                print(f"WhatsApp message sent successfully via Wappfly to {to}")
        except Exception as e:
            print(f"Exception while sending WhatsApp message via Wappfly: {str(e)}")


async def download_whatsapp_media(download_url: str) -> str:
    """
    Downloads media from Wappfly's direct download URL.
    Saves the bytes to a NamedTemporaryFile with a .pdf suffix and returns its path.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(download_url)
        response.raise_for_status()
        file_bytes = response.content
        
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
        
    return tmp_path


def format_analysis_for_whatsapp(result: dict) -> str:
    """
    Converts the compliance report JSON (AnalysisResult) into a clean,
    WhatsApp-friendly text message with proper bolding, emojis, and styling.
    """
    score = result.get("compliance_score", 0)
    risk = result.get("overall_risk", "UNKNOWN")
    summary = result.get("summary", "")
    flags = result.get("flags", [])
    
    n = len(flags)
    critical_count = sum(1 for f in flags if f.get("severity", "").upper() == "CRITICAL")
    warning_count = sum(1 for f in flags if f.get("severity", "").upper() == "WARNING")
    info_count = sum(1 for f in flags if f.get("severity", "").upper() == "INFO")
    
    # Extract top issues (max 3 critical/warning flags)
    top_issues = [f for f in flags if f.get("severity", "").upper() in ["CRITICAL", "WARNING"]]
    top_issues = top_issues[:3]
    
    top_issues_lines = []
    for idx, flag in enumerate(top_issues, 1):
        title = flag.get("clause_title", "Untitled Clause")
        violation = flag.get("violation", "Statutory compliance issue")
        ref = flag.get("statutory_reference", "Karnataka Rent Act")
        top_issues_lines.append(f"{idx}. {title} — {violation} [{ref}]")
        
    top_issues_text = "\n".join(top_issues_lines) if top_issues_lines else "No critical or warning issues found."
    
    msg = (
        "🚩 *RedFlag Analysis Complete*\n\n"
        f"📊 Compliance Score: {score}/100\n"
        f"⚠️ Risk Level: {risk}\n\n"
        f"{summary}\n\n"
        f"*Issues Found ({n} flags):*\n"
        f"🔴 Critical: {critical_count} | 🟡 Warning: {warning_count} | 🔵 Notes: {info_count}\n\n"
        f"*Top Issues:*\n"
        f"{top_issues_text}\n"
    )
    
    if top_issues:
        msg += '\nReply with a number (e.g. "2") to get full details on that issue.\n'
        
    msg += "\n⚠️ _RedFlag is not a law firm. Verify all outputs with an enrolled advocate._"
    
    return msg


@router.post("/whatsapp/webhook")
async def handle_webhook(request: Request):
    """
    Handles incoming webhook payloads from Wappfly (POST).
    Always returns HTTP 200 immediately to prevent Wappfly from retrying on error.
    """
    try:
        payload = await request.json()
        
        # Log payload for debugging
        print(f"Received Wappfly webhook payload: {json.dumps(payload)}")
        
        event = payload.get("event")
        if event != "message":
            return JSONResponse(content={"status": "ignored non-message event"}, status_code=200)
            
        data = payload.get("data", {})
        wa_id = data.get("from")
        
        if not wa_id:
            return JSONResponse(content={"status": "no sender phone number found"}, status_code=200)
            
        # Retrieve or initialize session state
        session = get_user_session(wa_id)
        sender_name = "User"  # Wappfly payload doesn't guarantee profile name, default to User
        
        message_type = data.get("type")
        
        # Handle Text Messages
        if message_type == "text":
            body = data.get("text", {}).get("body", "").strip()
            body_lower = body.lower()
            
            # 1. Greetings checking
            if body_lower in ["hi", "hello", "start", "hey"]:
                session["state"] = "WAITING_FOR_DOC"
                welcome_msg = (
                    f"Hi {sender_name}! 👋\n\n"
                    "Welcome to *RedFlag* — an AI-powered rental agreement compliance checker for Karnataka, India.\n\n"
                    "Please send your rental agreement PDF (residential or commercial), and I will analyze it for statutory deviations under the Karnataka Rent Act.\n\n"
                    "Please upload the PDF document now."
                )
                await send_whatsapp_message(wa_id, welcome_msg)
                
            # 2. Check for follow-up details query
            else:
                is_followup = False
                extracted_num = None
                
                if body.isdigit():
                    is_followup = True
                    extracted_num = int(body)
                else:
                    # Look for expressions like "flag 2", "issue 1", "tell me about 3"
                    match = re.search(r'(?:flag|issue|clause|number|no\.?|show)\s*(\d+)', body_lower)
                    if match:
                        is_followup = True
                        extracted_num = int(match.group(1))
                    else:
                        # Fallback check for standalone digit word
                        standalone_match = re.search(r'\b(\d+)\b', body)
                        if standalone_match and session.get("top_issues"):
                            is_followup = True
                            extracted_num = int(standalone_match.group(1))
                
                # Retrieve the issue details if it's a valid follow-up
                if is_followup and session.get("top_issues") and extracted_num is not None:
                    top_issues = session["top_issues"]
                    if 1 <= extracted_num <= len(top_issues):
                        flag = top_issues[extracted_num - 1]
                        
                        severity_emoji = "🔴"
                        severity_name = flag.get("severity", "WARNING").upper()
                        if severity_name == "WARNING":
                            severity_emoji = "🟡"
                        elif severity_name == "INFO":
                            severity_emoji = "🔵"
                            
                        detail_msg = (
                            f"{severity_emoji} *Issue #{extracted_num}: {flag.get('clause_title')}*\n\n"
                            f"*Severity:* {flag.get('severity')}\n"
                            f"*Category:* {flag.get('category')}\n\n"
                            f"*Excerpt from Agreement:*\n"
                            f"\"{flag.get('original_text')}\"\n\n"
                            f"*Violation:*\n"
                            f"{flag.get('violation')}\n\n"
                            f"*Statutory Reference:*\n"
                            f"{flag.get('statutory_reference')}\n\n"
                            f"*Recommendation:*\n"
                            f"{flag.get('recommendation')}\n\n"
                            f"Reply with another number to view details, or send a new PDF to start a new analysis."
                        )
                        await send_whatsapp_message(wa_id, detail_msg)
                    else:
                        await send_whatsapp_message(
                            wa_id,
                            f"Invalid issue number. Please reply with a number between 1 and {len(top_issues)} to see details."
                        )
                else:
                    # Text was not a greeting or valid follow-up
                    fallback_msg = (
                        "I didn't quite catch that. Please send a rental agreement PDF to analyze it for compliance.\n\n"
                        "If you already analyzed a document, you can reply with a number (e.g. \"1\", \"2\") to get full details on that issue."
                    )
                    await send_whatsapp_message(wa_id, fallback_msg)
                    
        # Handle PDF Document Messages
        elif message_type == "document":
            doc = data.get("document", {})
            mimetype = doc.get("mimetype", "")
            
            if mimetype == "application/pdf":
                session["state"] = "PROCESSING"
                await send_whatsapp_message(wa_id, "📥 PDF received. Analyzing your rental agreement for compliance, please wait...")
                
                tmp_path = None
                try:
                    # 1. Download PDF from Wappfly direct URL
                    download_url = doc.get("url")
                    if not download_url:
                        raise Exception("Wappfly document URL is empty")
                        
                    tmp_path = await download_whatsapp_media(download_url)
                    
                    # 2. Extract Text & Run AI compliance audit
                    # Import locally to prevent circular dependency
                    from main import extract_text_from_pdf, analyze_with_groq
                    
                    contract_text = extract_text_from_pdf(tmp_path)
                    analysis = await analyze_with_groq(contract_text)
                    
                    # 3. Store result in session state
                    flags = analysis.get("flags", [])
                    top_issues = [f for f in flags if f.get("severity", "").upper() in ["CRITICAL", "WARNING"]]
                    top_issues = top_issues[:3]
                    
                    session["last_analysis"] = analysis
                    session["top_issues"] = top_issues
                    session["state"] = "IDLE"
                    
                    # 4. Format & send report
                    report_text = format_analysis_for_whatsapp(analysis)
                    await send_whatsapp_message(wa_id, report_text)
                    
                except HTTPException as he:
                    session["state"] = "IDLE"
                    print(f"HTTPException while processing document: {he.detail}")
                    await send_whatsapp_message(wa_id, f"❌ Analysis failed: {he.detail}")
                except Exception as e:
                    session["state"] = "IDLE"
                    print(f"Error while processing document: {str(e)}")
                    error_msg = (
                        "❌ Sorry, we encountered an error while processing your rental agreement PDF. "
                        "Please ensure the file is not corrupted, is less than 10MB, and contains extractable text."
                    )
                    await send_whatsapp_message(wa_id, error_msg)
                finally:
                    # Clean up the downloaded temporary file
                    if tmp_path and os.path.exists(tmp_path):
                        try:
                            os.unlink(tmp_path)
                        except Exception:
                            pass
            else:
                await send_whatsapp_message(
                    wa_id, 
                    "⚠️ Only PDF documents are supported. Please send your agreement in PDF format."
                )
                
        # Handle Unsupported Message Types (images, voice notes, stickers, etc.)
        else:
            await send_whatsapp_message(
                wa_id, 
                "⚠️ Please send a PDF document of your rental agreement to begin the compliance check."
            )
            
    except Exception as e:
        # Wrap everything in try/except to guarantee we always return 200 to Wappfly
        print(f"Unhandled error in Wappfly webhook: {str(e)}")
        
    return JSONResponse(content={"status": "success"}, status_code=200)
