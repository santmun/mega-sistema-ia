"""Servicio Anthropic — analisis post-llamada con Claude."""

import json
import os

import anthropic


def get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def analyze_call(transcript: str) -> dict:
    """Analiza la transcripcion usando el prompt del template de la industria.

    Returns dict con al menos:
        resumen, nombre_cliente, temperatura, sentimiento,
        interes_principal, siguiente_accion, cita_agendada
    """
    from app.config import BUSINESS, AGENT, get_post_call_prompt

    post_call_prompt = get_post_call_prompt()

    # Si el template tiene prompt de analisis, usarlo
    if post_call_prompt:
        system_prompt = post_call_prompt
    else:
        # Fallback generico
        system_prompt = f"Analiza esta llamada de {BUSINESS.get('name', 'el negocio')}."

    client = get_client()
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": f"""{system_prompt}

Responde UNICAMENTE con un JSON valido (sin markdown, sin backticks) con esta estructura:

{{
  "resumen": "Resumen de 2-3 oraciones de la llamada",
  "nombre_cliente": "Nombre del cliente si se menciono, o vacio",
  "temperatura": "Hot si quiere agendar/comprar ya, Warm si muestra interes activo, Cold si solo pregunta",
  "sentimiento": "Positivo, Neutral o Negativo",
  "interes_principal": "Que producto/servicio le interesa",
  "siguiente_accion": "Que hacer despues con este lead",
  "cita_agendada": true o false
}}

Transcripcion:
{transcript}""",
            }
        ],
    )

    raw = message.content[0].text.strip()
    # Limpiar markdown code fences si hay
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "resumen": raw[:500],
            "nombre_cliente": "",
            "temperatura": "Warm",
            "sentimiento": "Neutral",
            "interes_principal": "",
            "siguiente_accion": "Revisar transcripcion manualmente",
            "cita_agendada": False,
        }
