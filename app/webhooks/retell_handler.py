"""Handler de webhooks de Retell AI."""

from app.services import anthropic_service, notion_service, retell_service


def _extract_call_id(data: dict) -> str:
    call_obj = data.get("call", {})
    if isinstance(call_obj, dict) and call_obj.get("call_id"):
        return call_obj["call_id"]
    return data.get("call_id", "")


def handle_retell_event(request: dict) -> dict:
    """Procesa eventos de Retell: call_started, call_ended, call_analyzed."""
    event_type = request.get("event", "unknown")
    print(f"[Agent] Webhook: event={event_type}")

    if event_type == "call_started":
        call_id = _extract_call_id(request)
        return {"status": "ok", "call_id": call_id}
    elif event_type == "call_ended":
        return _on_call_ended(request)
    elif event_type == "call_analyzed":
        call_id = _extract_call_id(request)
        return {"status": "ok", "call_id": call_id}
    else:
        return {"status": "ignored", "event": event_type}


def _on_call_ended(data: dict) -> dict:
    """Al colgar: transcripcion → analisis con Claude → guardar en Notion."""
    call_id = _extract_call_id(data)
    if not call_id:
        return {"status": "error", "error": "call_id vacio en webhook"}

    try:
        return process_post_call(call_id)
    except Exception as e:
        print(f"[Agent] Error en post-call: {e}")
        return {"status": "error", "call_id": call_id, "error": str(e)}


def process_post_call(call_id: str) -> dict:
    """Flujo completo post-llamada:
    1. Obtener transcripcion de Retell
    2. Analizar con Claude
    3. Registrar llamada en Notion
    4. Crear o actualizar lead
    """
    from app.config import AGENT

    agent_name = AGENT.get("name", "Sofia")

    # 1. Obtener datos de la llamada
    call_data = retell_service.get_call(call_id)
    transcript = call_data.get("transcript", "")
    phone = call_data.get("from_number", "") or call_data.get("to_number", "")
    direction = call_data.get("direction", "inbound")
    duration_sec = int(call_data.get("duration_ms", 0) / 1000)

    if not transcript:
        return {"status": "no_transcript", "call_id": call_id}

    # 2. Analizar con Claude
    analysis = anthropic_service.analyze_call(transcript)

    tipo_llamada = "Inbound" if "inbound" in direction.lower() else "Outbound"
    nombre = analysis.get("nombre_cliente", "") or "Cliente"

    # 3. Registrar llamada en historial
    call_record = notion_service.create_call_record(
        titulo=f"{tipo_llamada} — {nombre}",
        tipo=tipo_llamada,
        resultado="Contestada",
        telefono=phone,
        nombre_lead=nombre,
        duracion_seg=duration_sec,
        resumen=analysis.get("resumen", ""),
        sentimiento=analysis.get("sentimiento", "Neutral"),
        cita_agendada=analysis.get("cita_agendada", False),
        retell_call_id=call_id,
    )

    # 4. Crear o actualizar lead
    lead_id = None
    if phone:
        existing = notion_service.find_lead_by_phone(phone)
        if existing:
            lead_id = existing["id"]
            notion_service.update_lead(
                page_id=lead_id,
                temperatura=analysis.get("temperatura", "Warm"),
                resumen_ia=analysis.get("resumen", ""),
                siguiente_accion=analysis.get("siguiente_accion", ""),
                estatus="Cita agendada" if analysis.get("cita_agendada") else None,
            )
        else:
            lead = notion_service.create_lead(
                name=nombre,
                phone=phone,
                fuente="Llamada entrante" if tipo_llamada == "Inbound" else "Llamada saliente",
                notas=analysis.get("resumen", ""),
            )
            lead_id = lead["id"]

    print(f"[{agent_name}] Post-call completo: call={call_id}, lead={lead_id}")
    return {
        "status": "ok",
        "call_id": call_id,
        "call_record_id": call_record["id"],
        "lead_id": lead_id,
        "analysis": analysis,
    }
