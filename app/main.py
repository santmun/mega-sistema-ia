"""Backend principal — Modal + FastAPI.

Todos los endpoints son genericos: leen del sofia.config.yaml
y el template de la industria para adaptarse a cualquier negocio.
"""

import modal
from fastapi import FastAPI

modal_app = modal.App("mega-sistema-ia")

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "retell-sdk>=5.0.0",
    "twilio>=9.0.0",
    "anthropic>=0.42.0",
    "notion-client>=2.2.0,<3.0.0",
    "requests>=2.32.0",
    "python-dotenv>=1.0.0",
    "pyyaml>=6.0.0",
    "fastapi>=0.115.0",
)

sofia_secret = modal.Secret.from_name("mega-sistema-credentials")

web_app = FastAPI(title="Mega Sistema IA")


@web_app.get("/health")
def health():
    from app.config import BUSINESS, AGENT
    return {
        "status": "ok",
        "business": BUSINESS.get("name", ""),
        "agent": AGENT.get("name", "Sofia"),
        "industry": BUSINESS.get("industry", ""),
        "version": "1.0.0",
    }


@web_app.post("/retell-webhook")
def retell_webhook(request: dict):
    from app.webhooks.retell_handler import handle_retell_event
    return handle_retell_event(request)


@web_app.post("/twilio-webhook")
def twilio_webhook(request: dict):
    from app.webhooks.twilio_handler import handle_twilio_event
    return handle_twilio_event(request)


@web_app.post("/search-products")
def search_products(request: dict):
    """Busca productos/servicios en el CRM.

    Acepta un dict de filtros generico. Los campos dependen de la industria:
    - inmobiliaria: {"Zona": "Polanco", "Tipo": "Casa"}
    - dental: {"Categoria": "Ortodoncia"}
    - gimnasio: {"Horario": "Completo"}
    """
    from app.services.notion_service import search_products as _search

    query = request.get("args", request).get("query", request.get("args", request))
    # Remover keys que no son filtros
    query.pop("query", None)
    results = _search(query=query if query else None)

    from app.config import CRM_PRODUCT_NAME
    return {"status": "ok", "count": len(results), CRM_PRODUCT_NAME.lower(): results}


@web_app.post("/create-lead")
def create_lead(request: dict):
    from app.services.notion_service import create_lead as _create

    args = request.get("args", request)

    # Separar campos base de campos extra
    base_keys = {"name", "phone", "email", "fuente", "notas"}
    base = {k: args[k] for k in base_keys if k in args}
    extra = {k: args[k] for k in args if k not in base_keys}

    lead = _create(**base, extra_fields=extra if extra else None)
    return {"status": "ok", "lead": lead}


@web_app.post("/book-appointment")
def book_appointment(request: dict):
    """Agenda una cita (generico: visita, consulta, prueba, reservacion)."""
    from app.services.calcom_service import create_booking, get_available_slots
    from app.services.notion_service import find_lead_by_phone, update_lead

    args = request.get("args", request)
    phone = args.get("phone", "")
    name = args.get("name", "")
    email = args.get("email", "cliente@negocio.com")
    event_type_id = int(args.get("event_type_id", 0))
    preferred_date = args.get("preferred_date", "")
    preferred_time = args.get("preferred_time", "")

    if preferred_date and preferred_time:
        start = f"{preferred_date}T{preferred_time}:00"
        booking = create_booking(
            event_type_id=event_type_id,
            start=start,
            name=name,
            email=email,
        )

        if phone:
            lead = find_lead_by_phone(phone)
            if lead:
                from app.config import TEMPLATE
                action_label = TEMPLATE.get("action_label", "Cita agendada")
                update_lead(
                    page_id=lead["id"],
                    estatus="Cita agendada",
                    siguiente_accion=f"{action_label}: {preferred_date} {preferred_time}",
                )

        return {"status": "ok", "booking": booking}

    if preferred_date:
        slots = get_available_slots(
            event_type_id=event_type_id,
            start_date=preferred_date,
            end_date=preferred_date,
        )
        return {"status": "ok", "available_slots": slots}

    return {"status": "error", "message": "Se necesita al menos preferred_date"}


@web_app.post("/update-lead-status")
def update_lead_status(request: dict):
    from app.services.notion_service import find_lead_by_phone, update_lead

    args = request.get("args", request)
    phone = args.get("phone", "")
    page_id = args.get("lead_id", "")

    if not page_id and phone:
        lead = find_lead_by_phone(phone)
        if not lead:
            return {"status": "error", "message": f"No se encontro lead con telefono {phone}"}
        page_id = lead["id"]

    if not page_id:
        return {"status": "error", "message": "Se necesita phone o lead_id"}

    result = update_lead(
        page_id=page_id,
        estatus=args.get("estatus"),
        temperatura=args.get("temperatura"),
        siguiente_accion=args.get("siguiente_accion"),
    )
    return {"status": "ok", "result": result}


@web_app.post("/post-call-summary")
def post_call_summary(request: dict):
    from app.webhooks.retell_handler import process_post_call

    call_id = request.get("call_id", "")
    if not call_id:
        return {"status": "error", "message": "Se necesita call_id"}
    return process_post_call(call_id)


@web_app.post("/trigger-outbound")
def trigger_outbound():
    """Trigger manual del worker outbound."""
    from app.outbound_worker import run_outbound_cycle
    return run_outbound_cycle()


@modal_app.function(image=image, secrets=[sofia_secret])
@modal.asgi_app()
def api():
    return web_app


# ── Worker outbound automatico ──

@modal_app.function(
    image=image,
    secrets=[sofia_secret],
    schedule=modal.Cron("0 * * * *"),
    timeout=600,
)
def outbound_cron():
    """Cron: revisa leads pendientes y les llama cada hora."""
    from app.outbound_worker import run_outbound_cycle
    return run_outbound_cycle()
