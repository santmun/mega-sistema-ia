"""Handler de webhooks de Twilio."""


def handle_twilio_event(request: dict) -> dict:
    """Procesa eventos de Twilio: SMS entrantes, status de llamadas."""
    message_body = request.get("Body", "")
    from_number = request.get("From", "")
    event_type = request.get("EventType", request.get("MessageStatus", "sms_incoming"))

    if message_body:
        print(f"[Agent] SMS de {from_number}: {message_body}")
        return {"status": "ok", "type": "sms_received"}
    else:
        print(f"[Agent] Twilio status update: {event_type}")
        return {"status": "ok", "type": event_type}
