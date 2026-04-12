"""Test de servicios — verifica que todo este funcionando post-setup."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import yaml


def load_config() -> dict:
    config_path = Path(__file__).resolve().parent.parent / "sofia.config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def test_retell() -> tuple[bool, str]:
    """Verifica que los agentes existen y estan activos."""
    api_key = os.environ.get("RETELL_API_KEY", "")
    inbound_id = os.environ.get("RETELL_INBOUND_AGENT_ID", "")
    outbound_id = os.environ.get("RETELL_OUTBOUND_AGENT_ID", "")

    if not api_key:
        return False, "RETELL_API_KEY no configurada"

    try:
        from retell import Retell
        client = Retell(api_key=api_key)

        agents = client.agent.list()
        agent_ids = [a.agent_id for a in agents]

        issues = []
        if inbound_id and inbound_id not in agent_ids:
            issues.append("Agente inbound no encontrado")
        if outbound_id and outbound_id not in agent_ids:
            issues.append("Agente outbound no encontrado")

        if issues:
            return False, "; ".join(issues)

        # Buscar nombre del agente
        config = load_config()
        agent_name = config.get("agent", {}).get("name", "Sofia")
        return True, f"Agente '{agent_name}' activo (inbound + outbound)"

    except Exception as e:
        return False, f"Error: {e}"


def test_twilio() -> tuple[bool, str]:
    """Verifica que el numero esta conectado."""
    sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
    token = os.environ.get("TWILIO_AUTH_TOKEN", "")
    phone = os.environ.get("TWILIO_PHONE_NUMBER", "")

    if not all([sid, token, phone]):
        return False, "Credenciales de Twilio incompletas"

    try:
        from twilio.rest import Client
        client = Client(sid, token)

        # Verificar que el numero existe en la cuenta
        numbers = client.incoming_phone_numbers.list(phone_number=phone)
        if numbers:
            return True, f"Numero {phone} conectado"
        return False, f"Numero {phone} no encontrado en tu cuenta de Twilio"

    except Exception as e:
        return False, f"Error: {e}"


def test_notion() -> tuple[bool, str]:
    """Verifica que las 3 bases de datos existen y son accesibles."""
    import requests

    api_key = os.environ.get("NOTION_API_KEY", "")
    products_id = os.environ.get("NOTION_PRODUCTS_DB_ID", "")
    leads_id = os.environ.get("NOTION_LEADS_DB_ID", "")
    calls_id = os.environ.get("NOTION_CALLS_DB_ID", "")

    if not api_key:
        return False, "NOTION_API_KEY no configurada"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28",
    }

    dbs = {
        "Productos": products_id,
        "Leads": leads_id,
        "Llamadas": calls_id,
    }

    found = 0
    missing = []

    for name, db_id in dbs.items():
        if not db_id:
            missing.append(name)
            continue
        try:
            resp = requests.get(
                f"https://api.notion.com/v1/databases/{db_id}",
                headers=headers,
            )
            if resp.status_code == 200:
                found += 1
            else:
                missing.append(name)
        except Exception:
            missing.append(name)

    if found == 3:
        return True, f"3 bases de datos accesibles (Productos, Leads, Llamadas)"
    elif missing:
        return False, f"Bases faltantes: {', '.join(missing)} — corre /setup para crearlas"
    return False, "No se pudieron verificar las bases de datos"


def test_calcom() -> tuple[bool, str]:
    """Verifica que el calendario esta conectado."""
    import requests

    api_key = os.environ.get("CAL_API_KEY", "")
    event_type_id = os.environ.get("CAL_EVENT_TYPE_ID", "")

    if not api_key:
        return False, "CAL_API_KEY no configurada"

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "cal-api-version": "2024-08-13",
        }

        resp = requests.get("https://api.cal.com/v2/event-types", headers=headers)
        if resp.status_code != 200:
            return False, "API key invalida — ve a app.cal.com/settings/developer/api-keys"

        event_types = resp.json().get("data", [])
        if event_type_id:
            found = any(str(et.get("id")) == str(event_type_id) for et in event_types)
            if found:
                return True, f"Calendario conectado, evento tipo #{event_type_id} disponible"
            return False, f"Evento tipo #{event_type_id} no encontrado — verifica CAL_EVENT_TYPE_ID"

        if event_types:
            return True, f"Calendario conectado ({len(event_types)} tipos de evento)"
        return False, "Calendario conectado pero sin tipos de evento — crea uno en Cal.com"

    except Exception as e:
        return False, f"Error: {e}"


def test_modal() -> tuple[bool, str]:
    """Verifica que Modal esta configurado y el backend responde."""
    try:
        result = os.popen("modal app list 2>&1").read()
        if "mega-sistema-ia" in result:
            return True, "Backend desplegado en Modal"
        elif "modal" in result.lower() or "error" not in result.lower():
            return False, "Backend no desplegado — corre: modal deploy app/main.py"
        else:
            return False, "Modal CLI no configurado — corre: modal token new"
    except Exception as e:
        return False, f"Modal CLI no instalado — corre: pip install modal && modal token new"


def run_tests():
    """Ejecuta todos los tests."""
    config = load_config()
    business_name = config.get("business", {}).get("name", "tu negocio")

    print(f"\nVerificando sistema — {business_name}\n")

    tests = [
        ("Retell AI", test_retell),
        ("Twilio", test_twilio),
        ("Notion CRM", test_notion),
        ("Cal.com", test_calcom),
        ("Modal Backend", test_modal),
    ]

    passed = 0
    for i, (name, test_fn) in enumerate(tests, 1):
        ok, message = test_fn()
        icon = "✅" if ok else "❌"
        print(f"  [{i}/{len(tests)}] {name:<16} {icon} {message}")
        if ok:
            passed += 1

    print(f"\nResultado: {passed}/{len(tests)} checks pasaron.")

    if passed == len(tests):
        phone = os.environ.get("TWILIO_PHONE_NUMBER", "tu numero")
        print(f"\n🎉 Tu agente esta listo. Llama a {phone} para probarlo.\n")
    else:
        print("\n⚠️ Arregla los errores de arriba y corre /test otra vez.\n")
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
