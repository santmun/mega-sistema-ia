"""Servicio Twilio — telefonia y SMS."""

import os

from twilio.rest import Client


def get_client() -> Client:
    return Client(
        os.environ["TWILIO_ACCOUNT_SID"],
        os.environ["TWILIO_AUTH_TOKEN"],
    )


def send_sms(to: str, body: str) -> str:
    """Envia un SMS y retorna el SID del mensaje."""
    client = get_client()
    message = client.messages.create(
        body=body,
        from_=os.environ["TWILIO_PHONE_NUMBER"],
        to=to,
    )
    return message.sid
