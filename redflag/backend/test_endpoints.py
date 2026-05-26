import sys
import os
import unittest
from unittest.mock import AsyncMock, patch

# Add backend to path
sys.path.insert(0, r"c:\Users\Afzan Khan\Documents\redflag\redflag\backend")

# Set dummy env vars for test run
os.environ["WHATSAPP_VERIFY_TOKEN"] = "test_token_123"
os.environ["WHATSAPP_ACCESS_TOKEN"] = "fake_access_token"
os.environ["WHATSAPP_PHONE_NUMBER_ID"] = "fake_phone_id"

from fastapi.testclient import TestClient
from main import app

class TestWhatsAppEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_verify_webhook_success(self):
        response = self.client.get(
            "/whatsapp/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "test_token_123",
                "hub.challenge": "challenge_accepted"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "challenge_accepted")

    def test_verify_webhook_failure(self):
        response = self.client.get(
            "/whatsapp/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "wrong_token",
                "hub.challenge": "challenge_accepted"
            }
        )
        self.assertEqual(response.status_code, 403)

    @patch("whatsapp.send_whatsapp_message", new_callable=AsyncMock)
    def test_post_webhook_greeting(self, mock_send_msg):
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "12345",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {"display_phone_number": "1", "phone_number_id": "1"},
                                "contacts": [{"profile": {"name": "Alice"}, "wa_id": "919999999999"}],
                                "messages": [
                                    {
                                        "from": "919999999999",
                                        "id": "wamid.123",
                                        "timestamp": "123456789",
                                        "text": {"body": "hello"},
                                        "type": "text"
                                    }
                                ]
                            },
                            "field": "messages"
                        }
                    ]
                }
            ]
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
    def test_post_webhook_status_update(self, mock_send_msg):
        # A status payload (e.g. read/delivered receipt) contains no messages
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "12345",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "statuses": [{"id": "wamid.123", "status": "read"}]
                            },
                            "field": "messages"
                        }
                    ]
                }
            ]
        }
        
        response = self.client.post("/whatsapp/webhook", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "status update received"})
        mock_send_msg.assert_not_called()

    @patch("whatsapp.send_whatsapp_message", new_callable=AsyncMock)
    def test_post_webhook_fallback(self, mock_send_msg):
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "12345",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "contacts": [{"profile": {"name": "Alice"}, "wa_id": "919999999999"}],
                                "messages": [
                                    {
                                        "from": "919999999999",
                                        "id": "wamid.123",
                                        "timestamp": "123456789",
                                        "text": {"body": "some random text"},
                                        "type": "text"
                                    }
                                ]
                            },
                            "field": "messages"
                        }
                    ]
                }
            ]
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
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "12345",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "contacts": [{"profile": {"name": "Alice"}, "wa_id": "919999999999"}],
                                "messages": [
                                    {
                                        "from": "919999999999",
                                        "id": "wamid.doc123",
                                        "timestamp": "123456789",
                                        "document": {
                                            "filename": "lease.pdf",
                                            "mime_type": "application/pdf",
                                            "id": "media_id_123"
                                        },
                                        "type": "document"
                                    }
                                ]
                            },
                            "field": "messages"
                        }
                    ]
                }
            ]
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
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "12345",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "contacts": [{"profile": {"name": "Alice"}, "wa_id": "919999999999"}],
                                "messages": [
                                    {
                                        "from": "919999999999",
                                        "id": "wamid.query1",
                                        "timestamp": "123456789",
                                        "text": {"body": "tell me about issue 1"},
                                        "type": "text"
                                    }
                                ]
                            },
                            "field": "messages"
                        }
                    ]
                }
            ]
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
