"""Servicio Retell AI — llamadas de voz inbound y outbound."""

import os

from retell import Retell


def get_client() -> Retell:
    return Retell(api_key=os.environ["RETELL_API_KEY"])


def get_call(call_id: str) -> dict:
    """Obtiene detalles de una llamada incluyendo transcripcion."""
    client = get_client()
    call = client.call.retrieve(call_id)
    return {
        "call_id": call.call_id,
        "status": call.call_status,
        "from_number": getattr(call, "from_number", ""),
        "to_number": getattr(call, "to_number", ""),
        "direction": getattr(call, "direction", ""),
        "duration_ms": getattr(call, "end_timestamp", 0) - getattr(call, "start_timestamp", 0),
        "transcript": getattr(call, "transcript", ""),
    }


def create_phone_call(to_number: str, agent_id: str) -> dict:
    """Inicia una llamada saliente via Retell AI."""
    client = get_client()
    call = client.call.create_phone_call(
        from_number=os.environ["TWILIO_PHONE_NUMBER"],
        to_number=to_number,
        override_agent_id=agent_id,
    )
    return {"call_id": call.call_id, "status": call.call_status}


def create_outbound_call(to_number: str, dynamic_variables: dict) -> dict:
    """Inicia llamada outbound con variables dinamicas del lead.

    dynamic_variables es un dict generico con los datos del lead
    que el prompt del agente puede referenciar.
    """
    client = get_client()
    agent_id = os.environ["RETELL_OUTBOUND_AGENT_ID"]

    call = client.call.create_phone_call(
        from_number=os.environ["TWILIO_PHONE_NUMBER"],
        to_number=to_number,
        override_agent_id=agent_id,
        retell_llm_dynamic_variables=dynamic_variables,
    )
    return {"call_id": call.call_id, "status": call.call_status}
