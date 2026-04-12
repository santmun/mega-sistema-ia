"""Servicio Notion generico — lee campos del config/template de la industria."""

import os

import requests


NOTION_BASE_URL = "https://api.notion.com/v1"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {os.environ['NOTION_API_KEY']}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }


def _post(path: str, body: dict) -> dict:
    resp = requests.post(f"{NOTION_BASE_URL}{path}", headers=_headers(), json=body)
    resp.raise_for_status()
    return resp.json()


def _patch(path: str, body: dict) -> dict:
    resp = requests.patch(f"{NOTION_BASE_URL}{path}", headers=_headers(), json=body)
    resp.raise_for_status()
    return resp.json()


# ── Productos (generico: propiedades, tratamientos, membresias, etc.) ──

def search_products(query: dict | None = None) -> list[dict]:
    """Busca productos en Notion con filtros dinamicos.

    query es un dict de {campo: valor} que se convierte en filtros de Notion.
    Los nombres de campo deben coincidir con los definidos en el template.
    """
    from app.config import CRM_PRODUCT_FIELDS

    db_id = os.environ["NOTION_PRODUCTS_DB_ID"]

    filters: list[dict] = []
    if query:
        for field_name, value in query.items():
            field_def = _find_field(field_name, CRM_PRODUCT_FIELDS)
            if not field_def:
                continue
            notion_filter = _build_filter(field_name, value, field_def["type"])
            if notion_filter:
                filters.append(notion_filter)

    body: dict = {"page_size": 10}
    if filters:
        body["filter"] = {"and": filters} if len(filters) > 1 else filters[0]

    result = _post(f"/databases/{db_id}/query", body)

    products = []
    for page in result.get("results", []):
        props = page["properties"]
        product = {"id": page["id"]}
        for field in CRM_PRODUCT_FIELDS:
            fname = field["name"]
            ftype = field["type"]
            product[fname] = _extract_value(props.get(fname, {}), ftype)
        products.append(product)

    return products


# ── Leads ──

def create_lead(
    name: str,
    phone: str,
    email: str = "",
    fuente: str = "Llamada entrante",
    notas: str = "",
    extra_fields: dict | None = None,
) -> dict:
    """Crea un lead con campos base + campos extra de la industria."""
    db_id = os.environ["NOTION_LEADS_DB_ID"]

    props: dict = {
        "Nombre": {"title": [{"text": {"content": name}}]},
        "Telefono": {"phone_number": phone},
        "Estatus": {"select": {"name": "En proceso"}},
        "Temperatura": {"select": {"name": "Warm"}},
        "Fuente": {"select": {"name": fuente}},
        "Intentos de contacto": {"number": 1},
    }

    if email:
        props["Email"] = {"email": email}
    if notas:
        props["Notas"] = {"rich_text": [{"text": {"content": notas}}]}

    # Campos extra de la industria
    if extra_fields:
        from app.config import CRM_LEAD_EXTRA_FIELDS
        for field_name, value in extra_fields.items():
            field_def = _find_field(field_name, CRM_LEAD_EXTRA_FIELDS)
            if field_def and value:
                props[field_name] = _build_property_value(value, field_def["type"])

    page = _post("/pages", {"parent": {"database_id": db_id}, "properties": props})
    return {"id": page["id"], "nombre": name}


def get_pending_leads() -> list[dict]:
    """Obtiene leads con estatus 'Pendiente de llamar'."""
    db_id = os.environ["NOTION_LEADS_DB_ID"]

    result = _post(f"/databases/{db_id}/query", {
        "filter": {"property": "Estatus", "select": {"equals": "Pendiente de llamar"}},
        "page_size": 20,
    })

    leads = []
    for page in result.get("results", []):
        props = page["properties"]
        lead = {
            "id": page["id"],
            "nombre": _get_title(props.get("Nombre", {})),
            "telefono": props.get("Telefono", {}).get("phone_number", ""),
            "email": props.get("Email", {}).get("email", ""),
            "notas": _get_rich_text(props.get("Notas", {})),
            "intentos": _get_number(props.get("Intentos de contacto", {})) or 0,
        }
        # Leer campos extra de la industria
        from app.config import CRM_LEAD_EXTRA_FIELDS
        for field in CRM_LEAD_EXTRA_FIELDS:
            fname = field["name"]
            ftype = field["type"]
            lead[fname] = _extract_value(props.get(fname, {}), ftype)
        leads.append(lead)

    return leads


def find_lead_by_phone(phone: str) -> dict | None:
    """Busca un lead por telefono."""
    db_id = os.environ["NOTION_LEADS_DB_ID"]

    result = _post(f"/databases/{db_id}/query", {
        "filter": {"property": "Telefono", "phone_number": {"equals": phone}},
        "page_size": 1,
    })

    pages = result.get("results", [])
    if not pages:
        return None

    page = pages[0]
    props = page["properties"]
    return {
        "id": page["id"],
        "nombre": _get_title(props.get("Nombre", {})),
        "telefono": phone,
        "estatus": _get_select(props.get("Estatus", {})),
        "temperatura": _get_select(props.get("Temperatura", {})),
    }


def update_lead(
    page_id: str,
    estatus: str | None = None,
    temperatura: str | None = None,
    siguiente_accion: str | None = None,
    resumen_ia: str | None = None,
    intentos: int | None = None,
) -> dict:
    """Actualiza campos de un lead."""
    props: dict = {}
    if estatus:
        props["Estatus"] = {"select": {"name": estatus}}
    if temperatura:
        props["Temperatura"] = {"select": {"name": temperatura}}
    if siguiente_accion:
        props["Siguiente accion"] = {"rich_text": [{"text": {"content": siguiente_accion}}]}
    if resumen_ia:
        props["Resumen IA"] = {"rich_text": [{"text": {"content": resumen_ia[:2000]}}]}
    if intentos is not None:
        props["Intentos de contacto"] = {"number": intentos}

    _patch(f"/pages/{page_id}", {"properties": props})
    return {"id": page_id, "updated_fields": list(props.keys())}


# ── Historial de Llamadas ──

def create_call_record(
    titulo: str,
    tipo: str,
    resultado: str,
    telefono: str,
    nombre_lead: str = "",
    duracion_seg: int = 0,
    resumen: str = "",
    sentimiento: str = "Neutral",
    cita_agendada: bool = False,
    retell_call_id: str = "",
) -> dict:
    """Registra una llamada en el historial."""
    db_id = os.environ["NOTION_CALLS_DB_ID"]

    props: dict = {
        "Llamada": {"title": [{"text": {"content": titulo}}]},
        "Tipo": {"select": {"name": tipo}},
        "Resultado": {"select": {"name": resultado}},
        "Telefono": {"phone_number": telefono},
        "Sentimiento": {"select": {"name": sentimiento}},
        "Cita Agendada": {"checkbox": cita_agendada},
    }

    if nombre_lead:
        props["Nombre Lead"] = {"rich_text": [{"text": {"content": nombre_lead}}]}
    if duracion_seg:
        props["Duracion (seg)"] = {"number": duracion_seg}
    if resumen:
        props["Resumen"] = {"rich_text": [{"text": {"content": resumen[:2000]}}]}
    if retell_call_id:
        props["Retell Call ID"] = {"rich_text": [{"text": {"content": retell_call_id}}]}

    page = _post("/pages", {"parent": {"database_id": db_id}, "properties": props})
    return {"id": page["id"], "titulo": titulo}


# ── Creacion de bases de datos (para /setup) ──

def create_database(parent_page_id: str, title: str, properties: list[dict]) -> str:
    """Crea una base de datos en Notion y retorna su ID."""
    notion_props = {}
    for field in properties:
        notion_props[field["name"]] = _field_to_notion_property(field)

    body = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"type": "text", "text": {"content": title}}],
        "properties": notion_props,
    }

    result = _post("/databases", body)
    return result["id"]


def add_sample_products(db_id: str, products: list[dict], fields: list[dict]) -> int:
    """Agrega productos de ejemplo a la base de datos."""
    count = 0
    for product in products:
        props: dict = {}
        for field in fields:
            fname = field["name"]
            ftype = field["type"]
            # Buscar el valor en el producto (por nombre de campo o por key en minusculas)
            value = product.get(fname) or product.get(fname.lower().replace(" ", "_"))
            if value is not None:
                props[fname] = _build_property_value(value, ftype)

        if props:
            _post("/pages", {"parent": {"database_id": db_id}, "properties": props})
            count += 1

    return count


# ── Helpers internos ──

def _find_field(name: str, fields: list[dict]) -> dict | None:
    for f in fields:
        if f["name"] == name:
            return f
    return None


def _build_filter(field_name: str, value, field_type: str) -> dict | None:
    if field_type == "title":
        return {"property": field_name, "title": {"contains": str(value)}}
    elif field_type == "rich_text":
        return {"property": field_name, "rich_text": {"contains": str(value)}}
    elif field_type == "number":
        if isinstance(value, dict):
            return {"property": field_name, "number": value}
        return {"property": field_name, "number": {"equals": value}}
    elif field_type == "select":
        return {"property": field_name, "select": {"equals": str(value)}}
    elif field_type == "multi_select":
        return {"property": field_name, "multi_select": {"contains": str(value)}}
    elif field_type == "checkbox":
        return {"property": field_name, "checkbox": {"equals": bool(value)}}
    return None


def _build_property_value(value, field_type: str) -> dict:
    if field_type == "title":
        return {"title": [{"text": {"content": str(value)}}]}
    elif field_type == "rich_text":
        return {"rich_text": [{"text": {"content": str(value)}}]}
    elif field_type == "number":
        return {"number": float(value) if value else 0}
    elif field_type == "select":
        return {"select": {"name": str(value)}}
    elif field_type == "multi_select":
        if isinstance(value, list):
            return {"multi_select": [{"name": str(v)} for v in value]}
        return {"multi_select": [{"name": str(value)}]}
    elif field_type == "checkbox":
        return {"checkbox": bool(value)}
    elif field_type == "date":
        return {"date": {"start": str(value)}}
    return {"rich_text": [{"text": {"content": str(value)}}]}


def _field_to_notion_property(field: dict) -> dict:
    ftype = field["type"]
    if ftype == "title":
        return {"title": {}}
    elif ftype == "rich_text":
        return {"rich_text": {}}
    elif ftype == "number":
        fmt = field.get("format", "number")
        return {"number": {"format": fmt}}
    elif ftype == "select":
        options = [{"name": opt} for opt in field.get("options", [])]
        return {"select": {"options": options}}
    elif ftype == "multi_select":
        options = [{"name": opt} for opt in field.get("options", [])]
        return {"multi_select": {"options": options}}
    elif ftype == "checkbox":
        return {"checkbox": {}}
    elif ftype == "date":
        return {"date": {}}
    elif ftype == "phone_number":
        return {"phone_number": {}}
    elif ftype == "email":
        return {"email": {}}
    return {"rich_text": {}}


def _extract_value(prop: dict, field_type: str):
    if field_type == "title":
        return _get_title(prop)
    elif field_type == "rich_text":
        return _get_rich_text(prop)
    elif field_type == "number":
        return _get_number(prop)
    elif field_type == "select":
        return _get_select(prop)
    elif field_type == "multi_select":
        return _get_multi_select(prop)
    elif field_type == "checkbox":
        return prop.get("checkbox", False)
    elif field_type == "date":
        date = prop.get("date")
        return date.get("start", "") if date else ""
    return ""


def _get_title(prop: dict) -> str:
    items = prop.get("title", [])
    return items[0]["text"]["content"] if items else ""

def _get_rich_text(prop: dict) -> str:
    items = prop.get("rich_text", [])
    return items[0]["text"]["content"] if items else ""

def _get_select(prop: dict) -> str:
    sel = prop.get("select")
    return sel["name"] if sel else ""

def _get_multi_select(prop: dict) -> list[str]:
    return [opt["name"] for opt in prop.get("multi_select", [])]

def _get_number(prop: dict) -> float | None:
    return prop.get("number")
