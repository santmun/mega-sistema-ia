"""Customize — aplica cambios puntuales post-setup.

Modifica un aspecto especifico del sistema sin correr todo el setup de nuevo.
Actualiza tanto el servicio (Retell, Notion) como sofia.config.yaml.
"""

import os
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "sofia.config.yaml"

sys.path.insert(0, str(PROJECT_ROOT))
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def save_config(config: dict):
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def update_retell_prompt(new_prompt: str):
    """Actualiza el prompt del agente inbound en Retell."""
    import requests

    api_key = os.environ.get("RETELL_API_KEY", "")
    llm_id = os.environ.get("RETELL_LLM_ID", "")

    if not api_key or not llm_id:
        print("❌ RETELL_API_KEY o RETELL_LLM_ID no estan en .env")
        return False

    resp = requests.patch(
        f"https://api.retellai.com/update-retell-llm/{llm_id}",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={"general_prompt": new_prompt},
    )

    if resp.status_code == 200:
        print("  ✅ Prompt actualizado en Retell")
        return True
    else:
        print(f"  ❌ Error actualizando prompt: {resp.text}")
        return False


def update_agent_voice(voice_id: str):
    """Cambia la voz del agente en Retell."""
    import requests

    api_key = os.environ.get("RETELL_API_KEY", "")
    agent_id = os.environ.get("RETELL_INBOUND_AGENT_ID", "")

    if not api_key or not agent_id:
        print("❌ RETELL_API_KEY o RETELL_INBOUND_AGENT_ID no estan en .env")
        return False

    resp = requests.patch(
        f"https://api.retellai.com/update-agent/{agent_id}",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={"voice_id": voice_id},
    )

    if resp.status_code == 200:
        print(f"  ✅ Voz del agente cambiada a {voice_id}")
        return True
    else:
        print(f"  ❌ Error cambiando voz: {resp.text}")
        return False


def update_outbound_schedule(config: dict, schedule: str, days: list[str]):
    """Actualiza el horario de llamadas salientes en el config."""
    config["outbound"]["schedule"] = schedule
    config["outbound"]["days"] = days
    save_config(config)
    print(f"  ✅ Horario de outbound actualizado: {schedule} ({', '.join(days)})")
    print("  ℹ️  Redespliega el backend para aplicar: modal deploy app/main.py")


def update_business_info(config: dict, field: str, value: str):
    """Actualiza un dato del negocio en el config."""
    if field in config.get("business", {}):
        config["business"][field] = value
        save_config(config)
        print(f"  ✅ {field} actualizado a: {value}")
    else:
        print(f"  ❌ Campo '{field}' no existe en business")


def show_menu():
    """Muestra el menu interactivo de customize."""
    config = load_config()
    business_name = config.get("business", {}).get("name", "tu negocio")
    agent_name = config.get("agent", {}).get("name", "Sofia")

    print(f"\n🔧 Personalizar — {business_name}")
    print("=" * 40)
    print(f"  [1] Prompt del agente ({agent_name})")
    print(f"  [2] Campos del CRM")
    print(f"  [3] Horario de llamadas salientes")
    print(f"  [4] Datos del negocio")
    print(f"  [5] Voz del agente")
    print(f"  [0] Salir")
    print()

    return config


if __name__ == "__main__":
    config = show_menu()
    print("Usa /customize desde Claude Code para la experiencia interactiva.")
    print("O importa las funciones de este script para usarlas programaticamente.")
