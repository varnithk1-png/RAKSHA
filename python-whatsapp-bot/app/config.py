import sys
import os
from dotenv import load_dotenv
import logging


def load_configurations(app):
    load_dotenv()
    app.config["ACCESS_TOKEN"] = os.getenv("ACCESS_TOKEN")
    app.config["YOUR_PHONE_NUMBER"] = os.getenv("YOUR_PHONE_NUMBER")
    app.config["APP_ID"] = os.getenv("APP_ID")
    app.config["APP_SECRET"] = os.getenv("APP_SECRET")
    app.config["RECIPIENT_WAID"] = os.getenv("RECIPIENT_WAID")
    app.config["VERSION"] = os.getenv("VERSION")
    app.config["PHONE_NUMBER_ID"] = os.getenv("PHONE_NUMBER_ID")
    app.config["VERIFY_TOKEN"] = os.getenv("VERIFY_TOKEN")
    # Previously only read via os.getenv() inside whatsapp_utils.py - now
    # registered here too so all config is discoverable in one place.
    app.config["ADMIN_NUMBER"] = os.getenv("ADMIN_NUMBER")
    app.config["DASHBOARD_API_URL"] = os.getenv("DASHBOARD_API_URL")
    app.config["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )