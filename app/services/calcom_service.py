"""Servicio Cal.com — agenda de citas."""

import os

import requests

CAL_BASE_URL = "https://api.cal.com/v2"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {os.environ['CAL_API_KEY']}",
        "Content-Type": "application/json",
        "cal-api-version": "2024-08-13",
    }


def get_available_slots(event_type_id: int, start_date: str, end_date: str) -> list:
    """Obtiene slots disponibles para un tipo de evento."""
    resp = requests.get(
        f"{CAL_BASE_URL}/slots/available",
        headers=_headers(),
        params={
            "startTime": start_date,
            "endTime": end_date,
            "eventTypeId": event_type_id,
        },
    )
    resp.raise_for_status()
    return resp.json().get("data", {}).get("slots", [])


def create_booking(event_type_id: int, start: str, name: str, email: str) -> dict:
    """Crea una reserva en Cal.com usando la timezone del config."""
    from app.config import BUSINESS

    timezone = BUSINESS.get("timezone", "America/Mexico_City")

    resp = requests.post(
        f"{CAL_BASE_URL}/bookings",
        headers=_headers(),
        json={
            "eventTypeId": event_type_id,
            "start": start,
            "attendee": {"name": name, "email": email, "timeZone": timezone},
        },
    )
    resp.raise_for_status()
    return resp.json().get("data", {})
