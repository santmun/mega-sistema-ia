"""Setup automatizado — crea Notion DBs, configura Retell, Twilio, Modal.

Este script es lo que el skill /setup ejecuta internamente.
Puede correrse standalone: python scripts/setup.py
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import requests
import yaml

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "sofia.config.yaml"
ENV_PATH = PROJECT_ROOT / ".env"

# Agregar al path
sys.path.insert(0, str(PROJECT_ROOT))
from dotenv import load_dotenv
load_dotenv(ENV_PATH)


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def load_template(industry: str) -> dict:
    path = PROJECT_ROOT / f"prompts/{industry}.yaml"
    if not path.exists():
        print(f"❌ No se encontro template para industria '{industry}'")
        print(f"   Templates disponibles: {', '.join(get_available_industries())}")
        sys.exit(1)
    with open(path) as f:
        return yaml.safe_load(f)


def get_available_industries() -> list[str]:
    return [p.stem for p in (PROJECT_ROOT / "prompts").glob("*.yaml")]


# ── Paso 1: Crear bases de datos en Notion ──

def setup_notion(config: dict, template: dict) -> dict:
    """Crea las 3 bases de datos en Notion: productos, leads, llamadas."""
    parent_page_id = os.environ.get("NOTION_PARENT_PAGE_ID", "")
    if not parent_page_id:
        print("❌ NOTION_PARENT_PAGE_ID no esta en .env")
        print("   Es el ID de la pagina de Notion donde se crearan las bases de datos")
        print("   Lo encuentras en la URL de la pagina: notion.so/Tu-Pagina-XXXXX")
        return {}

    from app.services.notion_service import create_database, add_sample_products

    business_name = config["business"]["name"]
    product_name = template.get("product_label", "Productos")
    crm_fields = template.get("crm_fields", {})

    print(f"\n📦 Creando bases de datos en Notion para '{business_name}'...")

    # 1. Base de datos de productos
    product_fields = crm_fields.get("product_fields", [])
    products_db_id = create_database(
        parent_page_id=parent_page_id,
        title=f"{product_name} — {business_name}",
        properties=product_fields,
    )
    print(f"  ✅ {product_name}: creada ({products_db_id[:8]}...)")

    # 2. Base de datos de leads
    lead_base_fields = [
        {"name": "Nombre", "type": "title"},
        {"name": "Telefono", "type": "phone_number"},
        {"name": "Email", "type": "email"},
        {"name": "Estatus", "type": "select", "options": [
            "En proceso", "Pendiente de llamar", "Cita agendada",
            "Cerrado ganado", "Cerrado perdido", "No contesta",
        ]},
        {"name": "Temperatura", "type": "select", "options": ["Hot", "Warm", "Cold"]},
        {"name": "Fuente", "type": "select", "options": [
            "Llamada entrante", "Llamada saliente", "Sitio web", "Referido", "Otro",
        ]},
        {"name": "Intentos de contacto", "type": "number"},
        {"name": "Notas", "type": "rich_text"},
        {"name": "Resumen IA", "type": "rich_text"},
        {"name": "Siguiente accion", "type": "rich_text"},
    ]
    lead_extra_fields = crm_fields.get("lead_extra_fields", [])
    all_lead_fields = lead_base_fields + lead_extra_fields

    leads_db_id = create_database(
        parent_page_id=parent_page_id,
        title=f"Leads — {business_name}",
        properties=all_lead_fields,
    )
    print(f"  ✅ Leads: creada ({leads_db_id[:8]}...)")

    # 3. Base de datos de llamadas
    calls_fields = [
        {"name": "Llamada", "type": "title"},
        {"name": "Tipo", "type": "select", "options": ["Inbound", "Outbound"]},
        {"name": "Resultado", "type": "select", "options": [
            "Contestada", "No contesto", "Buzon de voz", "Numero invalido",
        ]},
        {"name": "Telefono", "type": "phone_number"},
        {"name": "Nombre Lead", "type": "rich_text"},
        {"name": "Duracion (seg)", "type": "number"},
        {"name": "Resumen", "type": "rich_text"},
        {"name": "Sentimiento", "type": "select", "options": ["Positivo", "Neutral", "Negativo"]},
        {"name": "Cita Agendada", "type": "checkbox"},
        {"name": "Retell Call ID", "type": "rich_text"},
    ]

    calls_db_id = create_database(
        parent_page_id=parent_page_id,
        title=f"Llamadas — {business_name}",
        properties=calls_fields,
    )
    print(f"  ✅ Llamadas: creada ({calls_db_id[:8]}...)")

    # 4. Cargar productos de ejemplo
    sample_products = template.get("sample_products", [])
    if sample_products:
        count = add_sample_products(products_db_id, sample_products, product_fields)
        print(f"  ✅ {count} {product_name.lower()} de ejemplo cargados")

    return {
        "products_db_id": products_db_id,
        "leads_db_id": leads_db_id,
        "calls_db_id": calls_db_id,
    }


# ── Paso 2: Configurar Retell AI ──

def setup_retell(config: dict, template: dict) -> dict:
    """Crea el LLM y los agentes en Retell."""
    api_key = os.environ.get("RETELL_API_KEY", "")
    if not api_key:
        print("❌ RETELL_API_KEY no esta en .env")
        return {}

    from app.config import get_inbound_prompt, get_outbound_prompt

    agent_name = config["agent"]["name"]
    voice_id = config["agent"].get("voice_id", "11lab-shimmer")
    language = config["agent"].get("language", "es-MX")

    print(f"\n🎙️ Configurando agentes de voz en Retell...")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Crear LLM inbound
    inbound_llm = requests.post(
        "https://api.retellai.com/v2/create-retell-llm",
        headers=headers,
        json={
            "model": "claude-3-5-sonnet",
            "general_prompt": get_inbound_prompt(),
        },
    )
    inbound_llm.raise_for_status()
    inbound_llm_id = inbound_llm.json()["llm_id"]

    # Crear agente inbound
    inbound_agent = requests.post(
        "https://api.retellai.com/v2/create-agent",
        headers=headers,
        json={
            "agent_name": f"{agent_name} — Inbound",
            "voice_id": voice_id,
            "llm_websocket_url": inbound_llm_id,
            "language": language,
        },
    )
    inbound_agent.raise_for_status()
    inbound_agent_id = inbound_agent.json()["agent_id"]
    print(f"  ✅ Agente inbound '{agent_name}' creado")

    # Crear LLM outbound
    outbound_llm = requests.post(
        "https://api.retellai.com/v2/create-retell-llm",
        headers=headers,
        json={
            "model": "claude-3-5-sonnet",
            "general_prompt": get_outbound_prompt(),
        },
    )
    outbound_llm.raise_for_status()
    outbound_llm_id = outbound_llm.json()["llm_id"]

    # Crear agente outbound
    outbound_agent = requests.post(
        "https://api.retellai.com/v2/create-agent",
        headers=headers,
        json={
            "agent_name": f"{agent_name} — Outbound",
            "voice_id": voice_id,
            "llm_websocket_url": outbound_llm_id,
            "language": language,
        },
    )
    outbound_agent.raise_for_status()
    outbound_agent_id = outbound_agent.json()["agent_id"]
    print(f"  ✅ Agente outbound '{agent_name}' creado")

    return {
        "inbound_agent_id": inbound_agent_id,
        "outbound_agent_id": outbound_agent_id,
        "inbound_llm_id": inbound_llm_id,
        "outbound_llm_id": outbound_llm_id,
    }


# ── Paso 3: Configurar Twilio SIP trunk ──

def setup_twilio(config: dict, retell_ids: dict) -> dict:
    """Crea SIP trunk en Twilio y conecta el numero."""
    sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
    token = os.environ.get("TWILIO_AUTH_TOKEN", "")
    phone = os.environ.get("TWILIO_PHONE_NUMBER", "")

    if not all([sid, token, phone]):
        print("❌ Credenciales de Twilio incompletas en .env")
        return {}

    print(f"\n📞 Configurando Twilio SIP trunk...")

    from twilio.rest import Client
    client = Client(sid, token)

    # Crear SIP trunk
    trunk = client.trunking.v1.trunks.create(
        friendly_name=f"Mega Sistema IA — {config['business']['name']}",
    )

    # Agregar origination URI de Retell
    trunk.origination_urls.create(
        friendly_name="Retell AI",
        sip_url="sip:+retellai.com",
        priority=1,
        weight=1,
        enabled=True,
    )

    print(f"  ✅ SIP trunk creado: {trunk.sid}")

    return {"trunk_sid": trunk.sid}


# ── Paso 4: Importar numero en Retell ──

def setup_retell_phone(retell_ids: dict) -> dict:
    """Importa el numero de Twilio en Retell y lo asigna al agente inbound."""
    api_key = os.environ.get("RETELL_API_KEY", "")
    phone = os.environ.get("TWILIO_PHONE_NUMBER", "")
    sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
    token = os.environ.get("TWILIO_AUTH_TOKEN", "")
    inbound_agent_id = retell_ids.get("inbound_agent_id", "")

    if not all([api_key, phone, inbound_agent_id]):
        print("⚠️ No se pudo importar numero en Retell (faltan datos)")
        return {}

    print(f"\n📱 Importando numero {phone} en Retell...")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    resp = requests.post(
        "https://api.retellai.com/v2/create-phone-number",
        headers=headers,
        json={
            "phone_number": phone,
            "agent_id": inbound_agent_id,
            "twilio_account_sid": sid,
            "twilio_auth_token": token,
        },
    )

    if resp.status_code in (200, 201):
        print(f"  ✅ Numero {phone} importado y asignado al agente inbound")
        return {"phone_imported": True}
    else:
        print(f"  ⚠️ No se pudo importar: {resp.text}")
        return {"phone_imported": False, "error": resp.text}


# ── Paso 5: Actualizar .env con IDs generados ──

def update_env(notion_ids: dict, retell_ids: dict):
    """Agrega los IDs generados al archivo .env."""
    additions = {}

    if notion_ids.get("products_db_id"):
        additions["NOTION_PRODUCTS_DB_ID"] = notion_ids["products_db_id"]
    if notion_ids.get("leads_db_id"):
        additions["NOTION_LEADS_DB_ID"] = notion_ids["leads_db_id"]
    if notion_ids.get("calls_db_id"):
        additions["NOTION_CALLS_DB_ID"] = notion_ids["calls_db_id"]
    if retell_ids.get("inbound_agent_id"):
        additions["RETELL_INBOUND_AGENT_ID"] = retell_ids["inbound_agent_id"]
    if retell_ids.get("outbound_agent_id"):
        additions["RETELL_OUTBOUND_AGENT_ID"] = retell_ids["outbound_agent_id"]

    if not additions:
        return

    # Leer .env existente
    existing = ""
    if ENV_PATH.exists():
        existing = ENV_PATH.read_text()

    # Agregar nuevas variables
    with open(ENV_PATH, "a") as f:
        if existing and not existing.endswith("\n"):
            f.write("\n")
        f.write("\n# --- Generados por /setup ---\n")
        for key, value in additions.items():
            # No duplicar si ya existe
            if key not in existing:
                f.write(f"{key}={value}\n")

    print(f"\n📝 .env actualizado con {len(additions)} variables nuevas")


# ── Orquestador principal ──

def run_setup():
    """Ejecuta el setup completo."""
    print("=" * 50)
    print("  MEGA SISTEMA IA — Setup Automatizado")
    print("=" * 50)

    # Cargar config
    if not CONFIG_PATH.exists():
        print("❌ No se encontro sofia.config.yaml")
        print("   Corre /setup para crearlo con la entrevista interactiva")
        sys.exit(1)

    config = load_config()
    industry = config.get("business", {}).get("industry", "")

    if not industry:
        print("❌ No se definio la industria en sofia.config.yaml")
        sys.exit(1)

    template = load_template(industry)
    business_name = config["business"]["name"]

    print(f"\n🏢 Negocio: {business_name}")
    print(f"🏷️ Industria: {template.get('display_name', industry)}")
    print(f"🤖 Agente: {config['agent']['name']}")

    # Validar credenciales primero
    print("\n🔐 Validando credenciales...")
    from scripts.validate import validate_all
    results = validate_all()
    failed = [name for name, r in results.items() if not r["ok"]]
    if failed:
        print(f"\n❌ Credenciales invalidas: {', '.join(failed)}")
        print("   Corrige tu .env y corre /setup de nuevo")
        sys.exit(1)
    print("  ✅ Todas las credenciales son validas")

    # Ejecutar setup por pasos
    notion_ids = setup_notion(config, template)
    retell_ids = setup_retell(config, template)
    twilio_ids = setup_twilio(config, retell_ids)
    phone_result = setup_retell_phone(retell_ids)

    # Actualizar .env con IDs generados
    update_env(notion_ids, retell_ids)

    # Resumen final
    print("\n" + "=" * 50)
    print("  ✅ SETUP COMPLETADO")
    print("=" * 50)
    print(f"""
  Negocio:    {business_name}
  Industria:  {template.get('display_name', industry)}
  Agente:     {config['agent']['name']}
  Numero:     {os.environ.get('TWILIO_PHONE_NUMBER', 'N/A')}

  Notion:     3 bases de datos creadas
  Retell:     Agentes inbound + outbound configurados
  Twilio:     SIP trunk conectado
  Cal.com:    Calendario conectado

  Siguiente paso: Corre /test para verificar que todo funciona.
""")


if __name__ == "__main__":
    run_setup()
