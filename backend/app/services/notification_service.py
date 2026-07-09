import boto3
from app.core.config import settings

class NotificationService:
    def __init__(self):
        self.sns_client = None
        if not settings.MOCK_AWS and settings.KMS_KEY_ID != "mockKmsKeyId":
            self.sns_client = boto3.client("sns", region_name=settings.AWS_DEFAULT_REGION)

    def send_sms(self, phone_number: str, message: str) -> bool:
        """Dispatches an SMS notification via AWS SNS. Falls back to console printing."""
        print(f"📡 DISPATCHING SMS to {phone_number}: {message}")
        if self.sns_client:
            try:
                self.sns_client.publish(
                    PhoneNumber=phone_number,
                    Message=message
                )
                return True
            except Exception as e:
                print(f"AWS SNS Publish failed: {e}")
                return False
        
        # Twilio SMS/WhatsApp integration fallback
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                from twilio.rest import Client
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                # If WhatsApp SID/Template is provided
                if settings.TWILIO_TEMPLATE_SID:
                    # WhatsApp template dispatch
                    client.messages.create(
                        content_sid=settings.TWILIO_TEMPLATE_SID,
                        from_=settings.TWILIO_WHATSAPP_FROM,
                        to=settings.TWILIO_WHATSAPP_TO
                    )
                else:
                    client.messages.create(
                        body=message,
                        from_=settings.TWILIO_WHATSAPP_FROM,
                        to=phone_number
                    )
                return True
            except Exception as e:
                print(f"Twilio message dispatch failed: {e}")
                return False

        print("📡 Notification dispatched in mock mode (credentials missing).")
        return True

    def trigger_escalation(self, wearer_id: str, alert_id: str, message: str, contacts: list[dict[str, str]]) -> bool:
        """Auto-escalate alerts to secondary contacts list if primary does not respond in N minutes"""
        print(f"🚨 ESCALATING Alert {alert_id} for Wearer {wearer_id}")
        for idx, contact in enumerate(contacts):
            name = contact.get("name", "Secondary Contact")
            phone = contact.get("phone")
            if phone:
                escalation_msg = f"Escalated emergency alert for {wearer_id}: {message}"
                self.send_sms(phone, escalation_msg)
        return True

notification_service = NotificationService()
