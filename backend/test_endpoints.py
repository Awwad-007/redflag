import sys
import os
import unittest
from unittest.mock import AsyncMock, patch

# Add backend to path
sys.path.insert(0, r"c:\Users\Afzan Khan\Documents\redflag\redflag\backend")

# Set dummy env vars for test run
os.environ["WAPPFLY_API_KEY"] = "fake_wappfly_key"

from fastapi.testclient import TestClient
from main import app

class TestWhatsAppEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("whatsapp.send_whatsapp_message", new_callable=AsyncMock)
    def test_post_webhook_greeting(self, mock_send_msg):
        payload = {
            "event": "message",
            "data": {
                "from": "919999999999",
                "type": "text",
                "text": {"body": "hello"}
            }
        }
        
        response = self.client.post("/whatsapp/webhook", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success"})
        
        # Verify a greeting message was sent
        mock_send_msg.assert_called_once()
        args, kwargs = mock_send_msg.call_args
        self.assertEqual(args[0], "919999999999")
        self.assertIn("Welcome to *RedFlag*", args[1])

    @patch("whatsapp.send_whatsapp_message", new_callable=AsyncMock)
    def test_post_webhook_ignored_event(self, mock_send_msg):
        # Wappfly sends status or device connected events. We should ignore them.
        payload = {
            "event": "device_status",
            "data": {
                "status": "connected"
            }
        }
        
        response = self.client.post("/whatsapp/webhook", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ignored non-message event"})
        mock_send_msg.assert_not_called()

    @patch("whatsapp.send_whatsapp_message", new_callable=AsyncMock)
    def test_post_webhook_fallback(self, mock_send_msg):
        payload = {
            "event": "message",
            "data": {
                "from": "919999999999",
                "type": "text",
                "text": {"body": "some random text"}
            }
        }
        
        response = self.client.post("/whatsapp/webhook", json=payload)
        self.assertEqual(response.status_code, 200)
        
        # Verify fallback message was sent
        mock_send_msg.assert_called_once()
        args, kwargs = mock_send_msg.call_args
        self.assertEqual(args[0], "919999999999")
        self.assertIn("Please send a rental agreement PDF", args[1])

    @patch("whatsapp.download_whatsapp_media", new_callable=AsyncMock)
    @patch("whatsapp.send_whatsapp_message", new_callable=AsyncMock)
    @patch("main.extract_text_from_pdf")
    @patch("main.analyze_with_groq", new_callable=AsyncMock)
    def test_post_webhook_pdf_document(self, mock_analyze, mock_extract, mock_send_msg, mock_download):
        mock_download.return_value = "dummy_path.pdf"
        mock_extract.return_value = "dummy text content of rental agreement"
        mock_analyze.return_value = {
            "compliance_score": 85,
            "overall_risk": "MEDIUM",
            "summary": "The lease is generally compliant with some warnings.",
            "flags": [
                {
                    "id": "FLAG_001",
                    "severity": "CRITICAL",
                    "category": "SECURITY DEPOSIT",
                    "clause_title": "Excess Security Deposit",
                    "original_text": "Security Deposit is 10 months rent.",
                    "violation": "Violates maximum 2 months rent rule for residential.",
                    "statutory_reference": "Section 35 of Karnataka Rent Act",
                    "recommendation": "Reduce to 2 months."
                },
                {
                    "id": "FLAG_002",
                    "severity": "WARNING",
                    "category": "UTILITIES",
                    "clause_title": "Utilities cut-off",
                    "original_text": "Landlord can cut off water.",
                    "violation": "Strictly prohibited.",
                    "statutory_reference": "Section 41 of Karnataka Rent Act",
                    "recommendation": "Remove lock out option."
                }
            ],
            "compliant_clauses": [],
            "metadata": {},
            "disclaimer": "Disclaimer here"
        }
        
        payload = {
            "event": "message",
            "data": {
                "from": "919999999999",
                "type": "document",
                "document": {
                    "url": "https://example.com/agreement.pdf",
                    "filename": "lease.pdf",
                    "mimetype": "application/pdf"
                }
            }
        }
        
        response = self.client.post("/whatsapp/webhook", json=payload)
        self.assertEqual(response.status_code, 200)
        
        # Verify user was notified about processing, and then sent final report
        self.assertEqual(mock_send_msg.call_count, 2)
        
        # First call is status update:
        first_call_args = mock_send_msg.call_args_list[0][0]
        self.assertIn("PDF received. Analyzing", first_call_args[1])
        
        # Second call is the actual analysis report:
        second_call_args = mock_send_msg.call_args_list[1][0]
        self.assertIn("RedFlag Analysis Complete", second_call_args[1])
        self.assertIn("Compliance Score: 85/100", second_call_args[1])
        self.assertIn("Risk Level: MEDIUM", second_call_args[1])
        self.assertIn("🔴 Critical: 1 | 🟡 Warning: 1 | 🔵 Notes: 0", second_call_args[1])

    @patch("whatsapp.send_whatsapp_message", new_callable=AsyncMock)
    def test_post_webhook_followup(self, mock_send_msg):
        # First set the user session state
        from whatsapp import USER_SESSIONS
        USER_SESSIONS["919999999999"] = {
            "state": "IDLE",
            "last_analysis": {},
            "top_issues": [
                {
                    "id": "FLAG_001",
                    "severity": "CRITICAL",
                    "category": "SECURITY DEPOSIT",
                    "clause_title": "Excess Security Deposit",
                    "original_text": "Security Deposit is 10 months rent.",
                    "violation": "Violates maximum 2 months rent rule for residential.",
                    "statutory_reference": "Section 35 of Karnataka Rent Act",
                    "recommendation": "Reduce to 2 months."
                },
                {
                    "id": "FLAG_002",
                    "severity": "WARNING",
                    "category": "UTILITIES",
                    "clause_title": "Utilities cut-off",
                    "original_text": "Landlord can cut off water.",
                    "violation": "Strictly prohibited.",
                    "statutory_reference": "Section 41 of Karnataka Rent Act",
                    "recommendation": "Remove lock out option."
                }
            ]
        }
        
        # Now query details of issue 1
        payload = {
            "event": "message",
            "data": {
                "from": "919999999999",
                "type": "text",
                "text": {"body": "tell me about issue 1"}
            }
        }
        
        response = self.client.post("/whatsapp/webhook", json=payload)
        self.assertEqual(response.status_code, 200)
        
        mock_send_msg.assert_called_once()
        args = mock_send_msg.call_args[0]
        self.assertEqual(args[0], "919999999999")
        self.assertIn("Issue #1: Excess Security Deposit", args[1])
        self.assertIn("Violates maximum 2 months rent", args[1])

if __name__ == "__main__":
    unittest.main()
