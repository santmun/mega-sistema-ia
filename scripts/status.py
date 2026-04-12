"""Status — muestra el estado actual de todos los servicios."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def load_config() -> dict:
    config_path = Path(__file__).resolve().parent.parent / "sofia.config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def check_retell() -> tuple[str, str]:
    """Verifica Retell y retorna estado + detalle."""
    api_key = os.environ.get("RETELL_API_KEY", "")
    if not api_key:
        return "❌ Offline", "API key no configurada"
    try:
        from retell import Retell
        client = Retell(api_key=api_key)
        agents = client.agent.list()
        config = load_config()
        agent_name = config.get("agent", {}).get("name", "Sofia")
        return "✅ Online", f"Agente: {agent_name} ({len(agents)} agentes)"
    except Exception as e:
        return "❌ Offline", str(e)


def check_twilio() -> tuple[str, str]:
    """Verifica Twilio."""
    phone = os.environ.get("TWILIO_PHONE_NUMBER", "")
    sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
    token = os.environ.get("TWILIO_AUTH_TOKEN", "")
    if not all([sid, token, phone]):
        return "❌ Offline", "Credenciales incompletas"
    try:
        from twilio.rest import Client
        client = Client(sid, token)
        numbers = client.incoming_phone_numbers.list(phone_number=phone)
        if numbers:
            return "✅ Online", f"Numero: {phone}"
        return "⚠️ Warning", f"Numero {phone} no encontrado en la cuenta"
    except Exception as e:
        return "❌ Offline", str(e)


def check_notion() -> tuple[str, str]:
    """Verifica Notion y cuenta leads/llamadas."""
    import requests

    api_key = os.environ.get("NOTION_API_KEY", "")
    leads_id = os.environ.get("NOTION_LEADS_DB_ID", "")
    calls_id = os.environ.get("NOTION_CALLS_DB_ID", "")

    if not api_key:
        return "❌ Offline", "API key no configurada"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    leads_count = 0
    calls_count = 0

    try:
        if leads_id:
            resp = requests.post(
                f"https://api.notion.com/v1/databases/{leads_id}/query",
                headers=headers,
                json={"page_size": 1},
            )
            if resp.status_code == 200:
                # Notion no da count directo, hacemos query sin limit
                resp2 = requests.post(
                    f"https://api.notion.com/v1/databases/{leads_id}/query",
                    headers=headers,
                    json={"page_size": 100},
                )
                if resp2.status_code == 200:
                    leads_count = len(resp2.json().get("results", []))

        if calls_id:
            resp = requests.post(
                f"https://api.notion.com/v1/databases/{calls_id}/query",
                headers=headers,
                json={"page_size": 100},
            )
            if resp.status_code == 200:
                calls_count = len(resp.json().get("results", []))

        return "✅ Online", f"Leads: {leads_count} | Llamadas: {calls_count}"
    except Exception as e:
        return "❌ Offline", str(e)


def check_calcom() -> tuple[str, str]:
    """Verifica Cal.com."""
    import requests

    api_key = os.environ.get("CAL_API_KEY", "")
    if not api_key:
        return "❌ Offline", "API key no configurada"

    try:
        resp = requests.get(
            "https://api.cal.com/v2/event-types",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "cal-api-version": "2024-08-13",
            },
        )
        if resp.status_code == 200:
            events = resp.json().get("data", [])
            return "✅ Online", f"{len(events)} tipos de evento"
        return "❌ Offline", f"Status {resp.status_code}"
    except Exception as e:
        return "❌ Offline", str(e)


def check_modal() -> tuple[str, str]:
    """Verifica Modal."""
    try:
        result = os.popen("modal app list 2>&1").read()
        if "mega-sistema-ia" in result:
            return "✅ Online", "Backend desplegado"
        return "⚠️ No deploy", "Corre: modal deploy app/main.py"
    except Exception:
        return "❌ Offline", "Modal CLI no instalado"


def run_status():
    """Muestra el estado de todos los servicios."""
    config = load_config()
    business_name = config.get("business", {}).get("name", "tu negocio")

    print(f"\nEstado del sistema — {business_name}")
    print("━" * 50)

    checks = [
        ("Retell AI", check_retell),
        ("Twilio", check_twilio),
        ("Notion CRM", check_notion),
        ("Cal.com", check_calcom),
        ("Modal Backend", check_modal),
    ]

    for name, check_fn in checks:
        status, detail = check_fn()
        print(f"  {name:<16} {status}    {detail}")

    print()


if __name__ == "__main__":
    run_status()
