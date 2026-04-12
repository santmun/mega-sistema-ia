"""Worker outbound generico — llama leads pendientes con datos dinamicos."""

import time

from app.services import notion_service, retell_service


def run_outbound_cycle() -> dict:
    """Ciclo completo del worker outbound.

    1. Consulta leads con estatus "Pendiente de llamar"
    2. Cambia estatus a "En proceso"
    3. Dispara llamada outbound con datos del lead como variables dinamicas
    4. Espera entre llamadas
    """
    from app.config import AGENT, OUTBOUND, CRM_LEAD_EXTRA_FIELDS

    max_calls = OUTBOUND.get("max_daily_calls", 20)
    agent_name = AGENT.get("name", "Sofia")

    leads = notion_service.get_pending_leads()

    if not leads:
        print(f"[{agent_name} Outbound] No hay leads pendientes.")
        return {"status": "ok", "leads_found": 0, "calls_made": 0}

    print(f"[{agent_name} Outbound] {len(leads)} leads pendientes.")

    calls_made = 0
    errors = []

    for i, lead in enumerate(leads):
        if calls_made >= max_calls:
            print(f"[{agent_name} Outbound] Limite diario alcanzado ({max_calls}).")
            break

        nombre = lead["nombre"]
        telefono = lead["telefono"]
        lead_id = lead["id"]

        if not telefono:
            continue

        # Cambiar estatus antes de llamar
        try:
            notion_service.update_lead(
                page_id=lead_id,
                estatus="En proceso",
                intentos=int(lead["intentos"]) + 1,
            )
        except Exception as e:
            errors.append({"lead": nombre, "error": str(e)})
            continue

        # Construir variables dinamicas del lead para el prompt de outbound
        dynamic_vars = {
            "lead_name": nombre,
            "lead_notes": lead.get("notas", ""),
        }
        # Agregar campos extra de la industria
        for field in CRM_LEAD_EXTRA_FIELDS:
            fname = field["name"]
            value = lead.get(fname, "")
            # Convertir listas a string para Retell
            if isinstance(value, list):
                value = ", ".join(value) if value else "no especificado"
            dynamic_vars[fname.lower().replace(" ", "_")] = str(value) if value else "no especificado"

        # Disparar llamada
        try:
            result = retell_service.create_outbound_call(
                to_number=telefono,
                dynamic_variables=dynamic_vars,
            )
            calls_made += 1
            print(f"[{agent_name} Outbound] Llamada {calls_made}: {nombre} ({telefono})")
        except Exception as e:
            errors.append({"lead": nombre, "error": str(e)})
            try:
                notion_service.update_lead(page_id=lead_id, estatus="Pendiente de llamar")
            except Exception:
                pass
            continue

        # Esperar entre llamadas
        if i < len(leads) - 1:
            time.sleep(30)

    print(f"[{agent_name} Outbound] Ciclo completo: {calls_made}/{len(leads)} llamadas.")
    return {
        "status": "ok",
        "leads_found": len(leads),
        "calls_made": calls_made,
        "errors": errors,
    }
