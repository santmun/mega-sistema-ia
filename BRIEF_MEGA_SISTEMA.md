# Brief: Mega Sistema IA — Version Comunidad

## Contexto

Sistema de agentes de voz con IA que ya funciona en produccion para una inmobiliaria (repo: `santmun/sofia-voice-agent`). Este repo (`mega-sistema-ia`) es la **plantilla reutilizable** para alumnos de Horizontes IA — llenan un archivo de configuracion, corren `/setup`, y en 5 minutos tienen un agente de voz funcionando para cualquier tipo de negocio.

**Publico objetivo**: 80% no-dev. Profesionales que quieren vender este servicio a negocios locales. Necesitan ser guiados paso a paso — nada de asumir conocimiento tecnico.

**Estrategia**: El repo de YouTube (`sofia-voice-agent`) ensena a construir desde cero (gratis). Este repo da el atajo + setup automatizado (producto de paga en comunidad Skool). No hay gatekeeping de tech, solo de negocio (ventas, contratos, pricing, prospeccion).

## Lo que ya existe (repo base: `santmun/sofia-voice-agent`)

- **Backend en Python + Modal** — 8 endpoints (search, create lead, book visit, update lead, post-call summary, webhooks, health, trigger outbound)
- **Retell AI** — agente de voz (inbound + outbound con dynamic variables)
- **Twilio** — telefonia via SIP trunk
- **Notion** — CRM (3 bases de datos: propiedades, leads, historial de llamadas)
- **Cal.com** — agendar citas
- **Claude Sonnet 4.5** — analisis post-llamada (resumen + lead scoring)
- **Next.js + shadcn/ui** — dashboard con analiticas
- **Worker outbound** — cron cada hora en Modal

Todo desplegado y funcional. Numero: +16624938662 conectado via SIP trunk.

---

## Arquitectura del producto

### Principio central: "Edita UN archivo, corre UN comando"

El alumno no toca codigo. Todo se configura desde `sofia.config.yaml` (datos del negocio) y `.env` (credenciales). El sistema se adapta solo.

### Separacion config vs credenciales

```
sofia.config.yaml  → Datos del negocio (safe para git)
.env               → API keys y secrets (gitignored, NUNCA en el repo)
.env.example       → Template con las variables necesarias y comentarios de ayuda
```

**Por que separar**: Si un alumno hace `git push` por error, no expone las API keys de su cliente.

---

## 1. Archivo de configuracion: `sofia.config.yaml`

Un solo archivo con TODO lo especifico del negocio. Sin credenciales. Comentado para que un no-dev entienda cada campo.

```yaml
# ============================================
# SOFIA.CONFIG.YAML
# Configuracion de tu agente de voz con IA
# Edita este archivo con los datos de tu cliente
# ============================================

version: "1.0"  # No tocar — para actualizaciones futuras

# --- DATOS DEL NEGOCIO ---
business:
  name: "Clinica Dental Sonrie"        # Nombre del negocio de tu cliente
  industry: "dental"                     # Opciones: inmobiliaria, dental, abogados, gimnasio, restaurante
  timezone: "America/Mexico_City"        # Zona horaria (busca la tuya en: timezones.io)
  phone: "+525512345678"                 # Numero de telefono del negocio
  address: "Av. Reforma 123, CDMX"      # Direccion fisica (el agente la menciona si preguntan)
  website: "https://sonrie.com"          # Sitio web (opcional)
  hours: "Lunes a Viernes 9:00-18:00"   # Horario de atencion

# --- AGENTE DE VOZ ---
agent:
  name: "Ana"                            # Nombre de la asistente virtual
  voice_id: "11lab-shimmer"              # ID de voz (Retell te da opciones)
  language: "es-MX"                      # Idioma: es-MX, es-CO, es-AR, en-US, etc.
  personality: "amable, profesional"      # Como quieres que suene (maximo 3 palabras)

# --- LLAMADAS SALIENTES (OUTBOUND) ---
outbound:
  enabled: true                          # true = el agente hace llamadas de seguimiento
  schedule: "09:00-17:00"               # Horario permitido para llamar
  max_daily_calls: 20                    # Maximo de llamadas por dia
  days: ["lun", "mar", "mie", "jue", "vie"]  # Dias activos

# --- CRM (Base de datos en Notion) ---
crm:
  product_name: "Tratamientos"           # Como se llama lo que vende tu cliente
  product_fields:                        # Campos de la tabla de productos
    - name: "Tratamiento"
      type: "title"
    - name: "Precio"
      type: "number"
      format: "dollar"
    - name: "Duracion"
      type: "rich_text"
    - name: "Categoria"
      type: "select"
      options: ["Limpieza", "Ortodoncia", "Implantes", "Blanqueamiento"]

  lead_extra_fields:                     # Campos adicionales para cada lead
    - name: "Tratamiento de interes"
      type: "select"
      options: ["Limpieza", "Ortodoncia", "Implantes"]
    - name: "Urgencia"
      type: "select"
      options: ["Urgente", "Esta semana", "Este mes", "Solo explorando"]

# --- APARIENCIA DEL DASHBOARD ---
branding:
  primary_color: "#06b6d4"               # Color principal (hex)
  logo_text: "Sonrie"                    # Texto que aparece como logo
  dashboard_title: "Panel de Control"    # Titulo del dashboard
```

---

## 2. Credenciales: `.env` y `.env.example`

### `.env.example` (commitable — template de referencia)

```bash
# ============================================
# CREDENCIALES — COPIA ESTE ARCHIVO COMO .env
# Comando: cp .env.example .env
# Luego llena cada valor con tus datos reales
# ============================================

# RETELL AI — Consigue tu key en: https://www.retellai.com/dashboard
# Tutorial: [link al video de Santi explicando]
RETELL_API_KEY=

# TWILIO — Consigue tus datos en: https://console.twilio.com
# Tutorial: [link al video]
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# NOTION — Crea una integracion en: https://www.notion.so/my-integrations
# Tutorial: [link al video]
NOTION_API_KEY=
NOTION_PARENT_PAGE_ID=

# CAL.COM — Consigue tu key en: https://app.cal.com/settings/developer/api-keys
# Tutorial: [link al video]
CAL_API_KEY=
CAL_EVENT_TYPE_ID=

# ANTHROPIC (CLAUDE) — Consigue tu key en: https://console.anthropic.com
# Tutorial: [link al video]
ANTHROPIC_API_KEY=

# MODAL — Se configura automaticamente con: modal token new
# Tutorial: [link al video]
```

Cada variable tiene:
- Link directo a donde conseguirla
- Referencia al video tutorial de Santi explicando el paso

---

## 3. Skills de Claude Code

### `/setup` — Setup completo (entrevista interactiva)

**Default: modo entrevista** (para no-devs). Claude pregunta todo paso a paso.

**Flujo de la entrevista:**

```
/setup

Claude: "Vamos a configurar tu agente de voz. Te voy a hacer unas preguntas.
         Si ya llenaste sofia.config.yaml, puedes correr /setup --skip-interview"

1. "Como se llama el negocio de tu cliente?"
   → business.name

2. "Que tipo de negocio es?"
   [1] Inmobiliaria  [2] Clinica dental  [3] Despacho de abogados
   [4] Gimnasio      [5] Restaurante
   → business.industry (pre-carga el template de esa industria)

3. "En que zona horaria esta? (ejemplo: America/Mexico_City)"
   → business.timezone

4. "Como quieres que se llame la asistente virtual? (ejemplo: Sofia, Ana, Maria)"
   → agent.name

5. "Como describirias la personalidad del agente en 3 palabras?"
   → agent.personality

6. "Quieres que el agente haga llamadas de seguimiento automaticas? (si/no)"
   → outbound.enabled + config de horarios

7. "Vamos con las credenciales. Tienes tu API key de Retell? (si/no)"
   → Si no: "Entra a retellai.com, crea cuenta, y copia tu API key. Te espero."
   → Si si: validar que funcione en tiempo real

8. [Repite para cada credencial: Twilio, Notion, Cal.com, Anthropic]

9. "Perfecto. Voy a configurar todo. Esto toma ~2 minutos..."
   → Ejecuta el setup automatizado
```

**Setup automatizado (lo que corre internamente):**

1. Lee/genera `sofia.config.yaml` con las respuestas
2. Valida TODAS las credenciales (llama a cada API para verificar)
3. Carga el template de prompts de la industria seleccionada
4. Crea las 3 bases de datos en Notion (productos, leads, llamadas) con los campos del config
5. Crea el LLM y los Agentes en Retell (inbound + outbound)
6. Configura el SIP trunk en Twilio y conecta el numero
7. Importa el numero en Retell y lo asigna a los agentes
8. Despliega el backend en Modal
9. Genera `.env.local` para el dashboard
10. Muestra resumen final con todo lo configurado

**Modo avanzado**: `/setup --skip-interview` — lee directo del YAML y `.env`.

### `/test` — Verificacion post-setup

Despues del setup, el alumno necesita SABER que todo funciona antes de conectar un cliente real.

```
/test

Claude: "Voy a verificar que todo este funcionando..."

[1/5] Retell AI       ✅ Agente "Ana" activo, voz configurada
[2/5] Twilio          ✅ Numero +525512345678 conectado via SIP
[3/5] Notion CRM      ✅ 3 bases de datos creadas (Tratamientos, Leads, Llamadas)
[4/5] Cal.com         ✅ Calendario conectado, evento tipo "Consulta" disponible
[5/5] Modal Backend   ✅ 8 endpoints respondiendo

Resultado: 5/5 checks pasaron. Tu agente esta listo.

Siguiente paso: Llama al numero para probarlo tu mismo.
```

Si algo falla:
```
[3/5] Notion CRM      ❌ Error: API key invalida
      → Solucion: Entra a notion.so/my-integrations, copia tu Internal Integration Secret,
        y actualizalo en tu .env (variable NOTION_API_KEY)
      → Luego corre /test otra vez
```

Mensajes de error claros con la solucion exacta. Nada de "Error 401 unauthorized" — sino "Tu API key de Notion no funciona, ve a este link y copiala de nuevo".

### `/customize` — Cambios post-setup

Para modificaciones despues del setup inicial sin correr todo de nuevo.

```
/customize

Claude: "Que quieres modificar?"

[1] Prompt del agente (cambiar tono, agregar instrucciones)
[2] Campos del CRM (agregar/quitar campos en Notion)
[3] Horario de llamadas salientes
[4] Datos del negocio (nombre, direccion, horario)
[5] Voz del agente

→ Seleccion: 1

Claude: "Actualmente el agente Ana tiene este estilo: 'amable, profesional'
         Que quieres cambiar?"

Usuario: "Quiero que sea mas casual y use el nombre del cliente"

Claude: "Listo. Actualice el prompt en Retell y en sofia.config.yaml.
         Corre /test para verificar que todo siga funcionando."
```

### `/status` — Estado de todos los servicios

Para debugging cuando algo deja de funcionar.

```
/status

Estado del sistema — Clinica Dental Sonrie
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Retell AI        ✅ Online    Agente: Ana (inbound + outbound)
Twilio           ✅ Online    Numero: +525512345678
Notion CRM       ✅ Online    Leads: 47 | Llamadas: 123
Cal.com          ✅ Online    Citas esta semana: 8
Modal Backend    ✅ Online    Ultimo deploy: hace 2 dias
Dashboard        ⚠️ No deploy  Corre: cd dashboard && npm run dev

Ultima llamada: Hace 3 horas (Maria Lopez — agenda cita para manana)
```

---

## 4. Libreria de prompts por industria

Directorio `prompts/` con templates completos. Cada archivo define todo lo que el agente necesita saber para esa industria.

### Lanzamiento: 5 industrias

| Industria | Archivo | Producto | Accion principal |
|-----------|---------|----------|-----------------|
| Inmobiliaria | `inmobiliaria.yaml` | Propiedades | Agendar visita |
| Dental | `dental.yaml` | Tratamientos | Agendar cita |
| Abogados | `abogados.yaml` | Servicios legales | Agendar consulta |
| Gimnasio | `gimnasio.yaml` | Membresias | Agendar prueba gratis |
| Restaurante | `restaurante.yaml` | Menu/Eventos | Hacer reservacion |

### Estructura de cada template

```yaml
# prompts/dental.yaml
industry: "dental"
display_name: "Clinica Dental"

# Prompt del agente para llamadas entrantes (inbound)
inbound_prompt: |
  Eres {agent.name}, asistente virtual de {business.name}.
  Tu trabajo es atender llamadas de pacientes y prospectos.

  PERSONALIDAD: {agent.personality}

  LO QUE PUEDES HACER:
  1. Responder preguntas sobre tratamientos y precios
  2. Agendar citas con el dentista
  3. Tomar datos del paciente para seguimiento

  INFORMACION DEL NEGOCIO:
  - Direccion: {business.address}
  - Horario: {business.hours}
  - Sitio web: {business.website}

  REGLAS:
  - Siempre se amable y empatico
  - Si preguntan por urgencias dentales, agenda la cita mas pronto posible
  - Si no sabes algo, di "Dejame verificar con el doctor y te llamo de vuelta"
  - Siempre confirma nombre, telefono y correo antes de colgar

# Prompt para llamadas salientes (outbound/seguimiento)
outbound_prompt: |
  Eres {agent.name} de {business.name}. Estas llamando a {lead.name}
  para darle seguimiento.

  CONTEXTO DE LA LLAMADA:
  - Motivo original: {lead.interest}
  - Ultima interaccion: {lead.last_contact}
  - Notas previas: {lead.notes}

  OBJETIVO: Confirmar si sigue interesado y agendar una cita.
  Si no contesta o no puede hablar, se amable y pregunta cuando puedes volver a llamar.

# Campos especificos del CRM para esta industria
crm_fields:
  product_fields:
    - name: "Tratamiento"
      type: "title"
    - name: "Precio"
      type: "number"
      format: "dollar"
    - name: "Duracion"
      type: "rich_text"
    - name: "Categoria"
      type: "select"
      options: ["Limpieza", "Ortodoncia", "Implantes", "Blanqueamiento", "Endodoncia"]

  lead_extra_fields:
    - name: "Tratamiento de interes"
      type: "select"
      options: ["Limpieza", "Ortodoncia", "Implantes", "Blanqueamiento"]
    - name: "Urgencia"
      type: "select"
      options: ["Urgente", "Esta semana", "Este mes", "Solo explorando"]
    - name: "Seguro dental"
      type: "select"
      options: ["Si", "No", "No se"]

# Datos de ejemplo para cargar al CRM (el alumno los reemplaza)
sample_products:
  - name: "Limpieza dental"
    price: 800
    duration: "45 minutos"
    category: "Limpieza"
  - name: "Blanqueamiento"
    price: 3500
    duration: "1 hora"
    category: "Blanqueamiento"
  - name: "Consulta de ortodoncia"
    price: 500
    duration: "30 minutos"
    category: "Ortodoncia"

# Prompt para el analisis post-llamada (Claude Sonnet)
post_call_analysis: |
  Analiza esta llamada de {business.name} (clinica dental).
  Evalua:
  1. Interes del paciente (1-10)
  2. Tratamiento de interes
  3. Urgencia
  4. Probabilidad de agendar cita
  5. Resumen en 2-3 oraciones
  6. Siguiente accion recomendada
```

### Futuras industrias (updates mensuales para Skool)

Mes 1 post-lanzamiento:
- `salon-belleza.yaml` — Servicios, estilistas, disponibilidad
- `veterinaria.yaml` — Citas, vacunas, emergencias

Mes 2:
- `clinica.yaml` — Citas medicas, especialidades, seguros
- `escuela.yaml` — Inscripciones, horarios, informes

Cada nueva industria = contenido de retencion para la comunidad.

---

## 5. Estructura del repo

```
mega-sistema-ia/
├── sofia.config.yaml           # Datos del negocio (safe para git)
├── .env.example                # Template de credenciales con links de ayuda
├── .env                        # Credenciales reales (GITIGNORED)
├── .gitignore                  # Ignora .env, node_modules, .modal/
├── CLAUDE.md                   # Skills: /setup, /test, /customize, /status
├── prompts/
│   ├── inmobiliaria.yaml       # Template inmobiliaria
│   ├── dental.yaml             # Template dental
│   ├── abogados.yaml           # Template abogados
│   ├── gimnasio.yaml           # Template gimnasio
│   └── restaurante.yaml        # Template restaurante
├── app/                        # Backend Python + Modal (parametrizado)
│   ├── main.py                 # Endpoints (lee de sofia.config.yaml)
│   ├── notion_client.py        # Cliente Notion (campos dinamicos)
│   ├── retell_client.py        # Cliente Retell (prompts dinamicos)
│   ├── cal_client.py           # Cliente Cal.com
│   ├── analysis.py             # Analisis post-llamada con Claude
│   └── outbound_worker.py      # Worker de llamadas salientes
├── scripts/
│   ├── setup.py                # Setup automatizado (lo que /setup ejecuta)
│   ├── test.py                 # Verificacion (lo que /test ejecuta)
│   └── validate.py             # Validacion de credenciales
├── dashboard/                  # Next.js + shadcn/ui (FASE 2)
│   ├── next.config.js
│   ├── tailwind.config.js      # Lee primary_color del config
│   └── src/
│       ├── config/             # Lee sofia.config.yaml para labels y branding
│       └── ...
└── README.md                   # Guia paso a paso para alumnos
```

---

## 6. Prioridades de desarrollo

### Fase 1 — Core (lo que importa)
1. `sofia.config.yaml` con estructura completa y comentarios claros
2. `.env.example` con links y tutoriales para cada credencial
3. Templates de prompts para las 5 industrias
4. Skill `/setup` con entrevista interactiva
5. Skill `/test` con verificacion de todos los servicios
6. Backend parametrizado que lee del config
7. `README.md` con guia paso a paso

### Fase 2 — Polish
8. Skill `/customize` para cambios post-setup
9. Skill `/status` para monitoreo
10. Dashboard parametrizado (colores, labels, branding)

### Fase 3 — Crecimiento
11. Nuevas industrias (salon-belleza, veterinaria, clinica, escuela)
12. Skill `/upgrade` para actualizar cuando sale nueva version del template

---

## Notas tecnicas

- Repo base: `santmun/sofia-voice-agent` — clonar como punto de partida
- Stack: Python + Modal (backend), Next.js + shadcn/ui (dashboard)
- Todos los servicios tienen plan gratis para empezar
- Dashboard: dark mode, tipografia premium (Playfair Display italic + Inter)
- El config debe tener `version` para manejar migraciones futuras
- Mensajes de error SIEMPRE con la solucion, nunca codigos tecnicos crudos
- La entrevista del /setup es el default — el YAML manual es para power users
