import logging
from flask import current_app, jsonify
import json
import requests
import re
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )


def generate_response(user_message: str, is_emergency: bool = False, history: list | None = None) -> str:
    try:
        if is_emergency:
            system_context = (
                "You are RAKSHA, a calm disaster-response WhatsApp assistant "
                "talking to someone who just reported an emergency. Have a "
                "short, natural conversation. Keep every reply to 1-2 short "
                "sentences. Stay calm and reassuring. Do not invent facts "
                "about rescue timing or specific responder actions."
            )
        else:
            system_context = (
                "You are RAKSHA, a disaster-response WhatsApp assistant. Keep "
                "replies short and natural. If the message describes any kind "
                "of emergency or danger, tell them to reply HELP to start an "
                "emergency report."
            )

        convo_text = ""
        if history:
            for turn in history[-6:]:
                convo_text += f"{turn['role']}: {turn['text']}\n"

        prompt = f"{system_context}\n\n{convo_text}User: {user_message}\nRAKSHA:"

        result = model.generate_content(prompt, request_options={"timeout": 6})
        return result.text.strip()
    except Exception as e:
        print(f"Error occurred: {e}")
        if is_emergency:
            return "Please share your location so responders can find you."
        return "This is the RAKSHA emergency line. Reply HELP if you need assistance."


def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }
    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    try:
        response = requests.post(url, data=data, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except requests.RequestException as e:
        logging.error(f"Request failed due to: {e}")
        if e.response is not None:
            logging.error(f"Response body: {e.response.text}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        log_http_response(response)
        return response


def process_text_for_whatsapp(text):
    pattern = r"\【.*?\】"
    text = re.sub(pattern, "", text).strip()
    pattern = r"\*\*(.*?)\*\*"
    replacement = r"*\1*"
    return re.sub(pattern, replacement, text)


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

_seen_message_ids = set()

# active_emergencies[wa_id] = {
#     "name", "status", "latitude", "longitude", "address_text",
#     "injured": None | "yes" | "no",
#     "people_count": None | int,
#     "history": [...],
# }
active_emergencies = {}

PINCODE_RE = re.compile(r"\b\d{6}\b")
NUMBER_RE = re.compile(r"\b(\d{1,2})\b")
LOCATION_HINT_WORDS = {
    "near", "street", "road", "colony", "nagar", "village", "town",
    "building", "block", "sector", "area", "pincode", "pin", "landmark",
}


def _looks_like_location(text: str) -> bool:
    if PINCODE_RE.search(text):
        return True
    lower = text.lower()
    return any(word in lower for word in LOCATION_HINT_WORDS)


def _parse_yes_no(text: str):
    lower = text.lower()
    if any(w in lower for w in ("yes", "yeah", "injured", "hurt", "bleeding")):
        return "yes"
    if any(w in lower for w in ("no", "not injured", "fine", "okay", "ok")):
        return "no"
    return None


def _parse_people_count(text: str):
    match = NUMBER_RE.search(text)
    if match:
        return int(match.group(1))
    if "alone" in text.lower() or "just me" in text.lower():
        return 1
    return None


# ---------------------------------------------------------------------------
# Multi-responder alerting - reads a comma-separated list from .env instead
# of a single hardcoded number.
# ---------------------------------------------------------------------------

def _get_responder_numbers() -> list[str]:
    raw = current_app.config.get("RESPONDER_NUMBERS") or os.getenv("RESPONDER_NUMBERS", "")
    return [n.strip() for n in raw.split(",") if n.strip()]


def _get_admin_number() -> str | None:
    return current_app.config.get("ADMIN_NUMBER") or os.getenv("ADMIN_NUMBER")


def _display_number(number: str) -> str:
    """Cosmetic only - adds a + prefix for display in alert text.
    Does NOT change what's sent to the WhatsApp API (that still uses
    the raw number without +)."""
    number = number.strip()
    return number if number.startswith("+") else f"+{number}"


def _push_to_dashboard(payload: dict) -> None:
    dashboard_url = os.getenv("DASHBOARD_API_URL")
    if not dashboard_url:
        print(f"[DASHBOARD] No DASHBOARD_API_URL set - would have sent: {payload}")
        return
    try:
        requests.post(dashboard_url, json=payload, timeout=5)
    except requests.RequestException as e:
        print(f"[DASHBOARD ERROR] Could not reach dashboard: {e}")


def _notify_dashboard(wa_id: str, record: dict) -> None:
    payload = {
        "name": record["name"],
        "phone": wa_id,
        "latitude": record["latitude"],
        "longitude": record["longitude"],
        "address_text": record["address_text"],
        "injured": record["injured"],
        "people_count": record["people_count"],
        "timestamp": datetime.now().isoformat(),
    }
    _push_to_dashboard(payload)

    if record["latitude"] is not None:
        loc_line = f"https://maps.google.com/?q={record['latitude']},{record['longitude']}"
    else:
        loc_line = record["address_text"] or "not provided"

    # Admin gets the FULL alert with victim details
    admin_number = _get_admin_number()
    if admin_number:
        full_alert = (
            f"NEW EMERGENCY\n"
            f"From: {record['name']} ({_display_number(wa_id)})\n"
            f"Location: {loc_line}\n"
            f"Injured: {record['injured'] or 'unknown'}\n"
            f"People: {record['people_count'] or 'unknown'}"
        )
        send_message(get_text_message_input(admin_number, full_alert))
    else:
        print("[ALERT] No ADMIN_NUMBER set - full alert not sent to anyone")

    # Other responders get a brief heads-up only, no personal victim details
    responder_numbers = [n for n in _get_responder_numbers() if n != admin_number]
    if responder_numbers:
        brief_alert = (
            "New emergency reported. Check the admin/dashboard for full details."
        )
        for number in responder_numbers:
            send_message(get_text_message_input(number, brief_alert))


# ---------------------------------------------------------------------------
# Main handler
# ---------------------------------------------------------------------------

def process_whatsapp_message(body):
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]

    msg_id = message.get("id")
    if msg_id in _seen_message_ids:
        return
    _seen_message_ids.add(msg_id)

    msg_type = message.get("type")
    in_emergency = wa_id in active_emergencies

    if msg_type == "text":
        message_body = message["text"]["body"].strip()

        if message_body.upper().startswith("HELP") and not in_emergency:
            active_emergencies[wa_id] = {
                "name": name,
                "status": "awaiting_location",
                "latitude": None,
                "longitude": None,
                "address_text": None,
                "injured": None,
                "people_count": None,
                "history": [],
            }
            response = "Emergency noted. Please share your location (type an address or use WhatsApp's location share)."

        elif in_emergency:
            record = active_emergencies[wa_id]

            if record["status"] == "awaiting_location" and _looks_like_location(message_body):
                record["address_text"] = message_body
                record["status"] = "awaiting_injury"
                response = "Location noted. Is anyone injured? (yes/no)"

            elif record["status"] == "awaiting_injury":
                parsed = _parse_yes_no(message_body)
                record["injured"] = parsed if parsed else message_body[:50]
                record["status"] = "awaiting_people_count"
                response = "How many people are with you right now?"

            elif record["status"] == "awaiting_people_count":
                count = _parse_people_count(message_body)
                record["people_count"] = count if count else message_body[:20]
                record["status"] = "location_received"
                _notify_dashboard(wa_id, record)
                response = "Thank you. Responders have been alerted with your details. Stay safe."

            else:
                response = generate_response(message_body, is_emergency=True, history=record["history"])

            record["history"].append({"role": "User", "text": message_body})
            record["history"].append({"role": "RAKSHA", "text": response})

        else:
            response = generate_response(message_body, is_emergency=False)

        data = get_text_message_input(wa_id, response)
        send_message(data)

    elif msg_type == "location":
        location = message["location"]
        lat = location.get("latitude")
        lon = location.get("longitude")

        if in_emergency:
            record = active_emergencies[wa_id]
            record["latitude"] = lat
            record["longitude"] = lon
            if record["status"] == "awaiting_location":
                record["status"] = "awaiting_injury"
                response = "Location received. Is anyone injured? (yes/no)"
            else:
                response = "Updated location received."
        else:
            response = "Location received, but no active emergency is linked to this. If this is urgent, reply HELP."

        data = get_text_message_input(wa_id, response)
        send_message(data)

    else:
        response = "This message type isn't supported yet. Please send text or your location."
        data = get_text_message_input(wa_id, response)
        send_message(data)


def is_valid_whatsapp_message(body):
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )