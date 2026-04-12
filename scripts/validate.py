"""Validacion de credenciales — verifica que cada API key funcione."""

import os
import sys
from pathlib import Path

# Agregar el directorio raiz al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def validate_retell() -> tuple[bool, str]:
    """Verifica que la API key de Retell sea valida."""
    api_key = os.environ.get("RETELL_API_KEY", "")
    if not api_key:
        return False, "RETELL_API_KEY no esta configurada en .env"
    try:
        from retell import Retell
        client = Retell(api_key=api_key)
        agents = client.agent.list()
        return True, f"Conectado — {len(agents)} agentes encontrados"
    except Exception as e:
        return False, f"API key invalida — ve a retellai.com/dashboard y copia tu key. Error: {e}"


def validate_twilio() -> tuple[bool, str]:
    """Verifica las credenciales de Twilio."""
    sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
    token = os.environ.get("TWILIO_AUTH_TOKEN", "")
    phone = os.environ.get("TWILIO_PHONE_NUMBER", "")

    if not sid or not token:
        return False, "TWILIO_ACCOUNT_SID o TWILIO_AUTH_TOKEN no estan en .env"
    if not phone:
        return False, "TWILIO_PHONE_NUMBER no esta en .env"
    try:
        from twilio.rest import Client
        client = Client(sid, token)
        account = client.api.accounts(sid).fetch()
        return True, f"Conectado — cuenta: {account.friendly_name}"
    except Exception as e:
        return False, f"Credenciales invalidas — ve a console.twilio.com. Error: {e}"


def validate_notion() -> tuple[bool, str]:
    """Verifica la API key de Notion."""
    api_key = os.environ.get("NOTION_API_KEY", "")
    if not api_key:
        return False, "NOTION_API_KEY no esta en .env"
    try:
        import requests
        resp = requests.get(
            "https://api.notion.com/v1/users/me",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Notion-Version": "2022-06-28",
            },
        )
        if resp.status_code == 200:
            data = resp.json()
            return True, f"Conectado — bot: {data.get('name', 'OK')}"
        return False, f"API key invalida (status {resp.status_code}) — ve a notion.so/my-integrations"
    except Exception as e:
        return False, f"Error de conexion: {e}"


def validate_calcom() -> tuple[bool, str]:
    """Verifica la API key de Cal.com."""
    api_key = os.environ.get("CAL_API_KEY", "")
    if not api_key:
        return False, "CAL_API_KEY no esta en .env"
    try:
        import requests
        resp = requests.get(
            "https://api.cal.com/v2/me",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "cal-api-version": "2024-08-13",
            },
        )
        if resp.status_code == 200:
            return True, "Conectado"
        return False, f"API key invalida (status {resp.status_code}) — ve a app.cal.com/settings/developer/api-keys"
    except Exception as e:
        return False, f"Error de conexion: {e}"


def validate_anthropic() -> tuple[bool, str]:
    """Verifica la API key de Anthropic."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return False, "ANTHROPIC_API_KEY no esta en .env"
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        # Hacer una llamada minima para verificar
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=10,
            messages=[{"role": "user", "content": "ping"}],
        )
        return True, "Conectado"
    except anthropic.AuthenticationError:
        return False, "API key invalida — ve a console.anthropic.com y copia tu key"
    except Exception as e:
        return False, f"Error: {e}"


def validate_all() -> dict:
    """Ejecuta todas las validaciones y retorna resultados."""
    validators = {
        "Retell AI": validate_retell,
        "Twilio": validate_twilio,
        "Notion": validate_notion,
        "Cal.com": validate_calcom,
        "Anthropic": validate_anthropic,
    }

    results = {}
    for name, validator in validators.items():
        ok, message = validator()
        results[name] = {"ok": ok, "message": message}

    return results


if __name__ == "__main__":
    print("\nValidando credenciales...\n")
    results = validate_all()

    passed = 0
    total = len(results)

    for name, result in results.items():
        icon = "✅" if result["ok"] else "❌"
        print(f"  {icon} {name}: {result['message']}")
        if result["ok"]:
            passed += 1

    print(f"\nResultado: {passed}/{total} credenciales validas.\n")

    if passed < total:
        print("Corrige las credenciales que fallaron en tu archivo .env")
        print("y corre este script de nuevo: python scripts/validate.py\n")
        sys.exit(1)
