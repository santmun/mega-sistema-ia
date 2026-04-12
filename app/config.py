"""Configuracion central del sistema.

Carga sofia.config.yaml (datos del negocio) + el template de la industria
+ credenciales desde .env / variables de entorno.
"""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env for local dev
load_dotenv(PROJECT_ROOT / ".env")


def _load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


# --- Sofia config (datos del negocio) ---
_config = _load_yaml(PROJECT_ROOT / "sofia.config.yaml")

BUSINESS = _config.get("business", {})
AGENT = _config.get("agent", {})
OUTBOUND = _config.get("outbound", {})
BRANDING = _config.get("branding", {})

# --- Template de la industria ---
_industry = BUSINESS.get("industry", "")
TEMPLATE: dict = {}

if _industry:
    template_path = PROJECT_ROOT / f"prompts/{_industry}.yaml"
    if template_path.exists():
        TEMPLATE = _load_yaml(template_path)

# CRM fields: usa los del config si estan definidos, si no los del template
_config_crm = _config.get("crm", {})
CRM_PRODUCT_NAME = _config_crm.get("product_name") or TEMPLATE.get("product_label", "Productos")
CRM_PRODUCT_FIELDS = _config_crm.get("product_fields") or TEMPLATE.get("crm_fields", {}).get("product_fields", [])
CRM_LEAD_EXTRA_FIELDS = _config_crm.get("lead_extra_fields") or TEMPLATE.get("crm_fields", {}).get("lead_extra_fields", [])

# --- Prompts (del template, con variables para reemplazar) ---
def get_inbound_prompt() -> str:
    raw = TEMPLATE.get("inbound_prompt", "")
    return _replace_variables(raw)

def get_outbound_prompt() -> str:
    raw = TEMPLATE.get("outbound_prompt", "")
    return _replace_variables(raw)

def get_post_call_prompt() -> str:
    raw = TEMPLATE.get("post_call_analysis", "")
    return _replace_variables(raw)

def _replace_variables(text: str) -> str:
    """Reemplaza {agent.name}, {business.name}, etc. con valores del config."""
    replacements = {
        "{agent.name}": AGENT.get("name", "Sofia"),
        "{agent.personality}": AGENT.get("personality", "amable, profesional"),
        "{business.name}": BUSINESS.get("name", ""),
        "{business.address}": BUSINESS.get("address", ""),
        "{business.hours}": BUSINESS.get("hours", ""),
        "{business.website}": BUSINESS.get("website", ""),
        "{business.phone}": BUSINESS.get("phone", ""),
    }
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text


# --- Credenciales (siempre de env, nunca del YAML) ---
RETELL_API_KEY = os.environ.get("RETELL_API_KEY", "")
RETELL_INBOUND_AGENT_ID = os.environ.get("RETELL_INBOUND_AGENT_ID", "")
RETELL_OUTBOUND_AGENT_ID = os.environ.get("RETELL_OUTBOUND_AGENT_ID", "")

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "")

NOTION_API_KEY = os.environ.get("NOTION_API_KEY", "")
NOTION_PARENT_PAGE_ID = os.environ.get("NOTION_PARENT_PAGE_ID", "")
NOTION_PRODUCTS_DB_ID = os.environ.get("NOTION_PRODUCTS_DB_ID", "")
NOTION_LEADS_DB_ID = os.environ.get("NOTION_LEADS_DB_ID", "")
NOTION_CALLS_DB_ID = os.environ.get("NOTION_CALLS_DB_ID", "")

CAL_API_KEY = os.environ.get("CAL_API_KEY", "")
CAL_EVENT_TYPE_ID = os.environ.get("CAL_EVENT_TYPE_ID", "")

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
