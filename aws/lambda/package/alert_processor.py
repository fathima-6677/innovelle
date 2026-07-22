import os
import json
import logging
import urllib.request
import urllib.parse
from typing import Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Load environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
CAREGIVER_PHONE_NUMBER = os.getenv("CAREGIVER_PHONE_NUMBER")

def send_sms(body: str) -> None:
    """Sends an SMS using Twilio HTTP API."""
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, CAREGIVER_PHONE_NUMBER]):
        logger.error("Missing required Twilio configuration in environment variables.")
        return

    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    
    data = urllib.parse.urlencode({
        "To": CAREGIVER_PHONE_NUMBER,
        "From": TWILIO_FROM_NUMBER,
        "Body": body
    }).encode("utf-8")
    
    import base64
    auth = f"{TWILIO_ACCOUNT_SID}:{TWILIO_AUTH_TOKEN}"
    b64_auth = base64.b64encode(auth.encode("utf-8")).decode("utf-8")
    
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            res_data = response.read().decode("utf-8")
            logger.info(f"Twilio SMS sent successfully. Response: {res_data}")
    except urllib.error.URLError as e:
        logger.error(f"Failed to send Twilio SMS: {e}")

def parse_dynamodb_type(value_dict: Dict[str, Any]) -> Any:
    """Helper to parse a single DynamoDB typed dictionary to Python type."""
    if "S" in value_dict:
        return str(value_dict["S"])
    elif "N" in value_dict:
        # Convert to float or int
        val = value_dict["N"]
        return float(val) if "." in val else int(val)
    elif "BOOL" in value_dict:
        return bool(value_dict["BOOL"])
    return None

def parse_dynamodb_image(image: Dict[str, Any]) -> Dict[str, Any]:
    """Parses a DynamoDB image dictionary into a regular Python dictionary."""
    parsed = {}
    for key, val_dict in image.items():
        parsed[key] = parse_dynamodb_type(val_dict)
    return parsed

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    logger.info(f"Received DynamoDB Stream event: {json.dumps(event)}")
    
    try:
        for record in event.get("Records", []):
            if record.get("eventName") == "INSERT":
                new_image = record.get("dynamodb", {}).get("NewImage", {})
                if not new_image:
                    continue
                
                data = parse_dynamodb_image(new_image)
                logger.info(f"Parsed new record: {data}")
                
                # Extract fields with defaults
                device_id = data.get("device_id", "Unknown")
                heart_rate = data.get("heart_rate", 0)
                stress_score = data.get("stress_score", 0)
                fall_detected = data.get("fall_detected", False)
                sound_alert = data.get("sound_alert", False)
                latitude = data.get("latitude", 0.0)
                longitude = data.get("longitude", 0.0)
                
                # Check alert conditions
                trigger_alert = any([
                    heart_rate > 120,
                    stress_score > 80,
                    fall_detected,
                    sound_alert
                ])
                
                if trigger_alert:
                    message_body = (
                        f"ALERT!\n"
                        f"Device: {device_id}\n\n"
                        f"Heart Rate: {heart_rate}\n"
                        f"Stress Score: {stress_score}\n"
                        f"Fall Detected: {fall_detected}\n"
                        f"Sound Alert: {sound_alert}\n\n"
                        f"Location:\n"
                        f"{latitude}, {longitude}"
                    )
                    
                    logger.info(f"Conditions met. Triggering SMS alert for device {device_id}.")
                    send_sms(message_body)
                else:
                    logger.info(f"No alert conditions met for device {device_id}.")
                    
        return {
            "statusCode": 200,
            "body": json.dumps("Processed stream successfully.")
        }
    except Exception as e:
        logger.error(f"Error processing stream record: {str(e)}", exc_info=True)
        # Raise the exception to ensure Lambda retries the batch if appropriate
        raise e
