# Mega Sistema IA — Tu Agente de Voz con IA en 5 Minutos

Sistema completo de agente de voz con inteligencia artificial que atiende llamadas, agenda citas y llena tu CRM automaticamente. Funciona para cualquier tipo de negocio.

**Creado por Santiago Munoz** — [Horizontes IA](https://iahorizontesacademy.com)

---

## Que hace este sistema?

1. **Contesta llamadas** como una recepcionista profesional (24/7)
2. **Busca informacion** del negocio y responde preguntas de clientes
3. **Agenda citas** automaticamente en el calendario
4. **Guarda leads** en tu CRM (Notion) con toda la informacion
5. **Hace llamadas de seguimiento** a prospectos interesados
6. **Analiza cada llamada** y te da un resumen con puntuacion del lead

---

## Industrias soportadas

| Industria | Ejemplo | Accion principal |
|-----------|---------|-----------------|
| Inmobiliaria | Casas, departamentos, terrenos | Agendar visita |
| Clinica dental | Tratamientos, limpiezas, urgencias | Agendar cita |
| Despacho de abogados | Divorcios, laboral, mercantil | Agendar consulta |
| Gimnasio | Membresias, clases, entrenador | Agendar prueba gratis |
| Restaurante | Reservaciones, eventos, menu | Hacer reservacion |

Cada industria viene con prompts profesionales listos para usar.

---

## Requisitos previos

Necesitas cuentas en estos servicios (todos tienen plan gratis para empezar):

| Servicio | Para que | Donde registrarte |
|----------|----------|-------------------|
| [Retell AI](https://www.retellai.com) | Agente de voz | retellai.com |
| [Twilio](https://www.twilio.com) | Numero de telefono | twilio.com |
| [Notion](https://www.notion.so) | CRM / base de datos | notion.so |
| [Cal.com](https://cal.com) | Agendar citas | cal.com |
| [Anthropic](https://console.anthropic.com) | Analisis con IA | console.anthropic.com |
| [Modal](https://modal.com) | Hosting del backend | modal.com |

---

## Instalacion paso a paso

### Paso 1: Clona el repositorio

```bash
git clone https://github.com/santmun/mega-sistema-ia.git
cd mega-sistema-ia
```

### Paso 2: Abre el proyecto en tu editor con Claude Code

```bash
claude
```

### Paso 3: Corre el setup

```
/setup
```

Claude te va a guiar paso a paso:
- Te pregunta los datos del negocio
- Te ayuda a conseguir las credenciales de cada servicio
- Configura todo automaticamente

### Paso 4: Verifica que todo funciona

```
/test
```

Si los 5 checks pasan, tu agente esta listo.

### Paso 5: Prueba tu agente

Llama al numero de telefono que configuraste. Tu agente virtual va a contestar.

---

## Estructura del proyecto

```
mega-sistema-ia/
├── sofia.config.yaml        ← Edita este archivo con los datos del negocio
├── .env                     ← Tus credenciales (NUNCA subir a git)
├── .env.example             ← Template de referencia para las credenciales
├── prompts/                 ← Prompts por industria (no necesitas tocarlos)
│   ├── inmobiliaria.yaml
│   ├── dental.yaml
│   ├── abogados.yaml
│   ├── gimnasio.yaml
│   └── restaurante.yaml
├── app/                     ← Backend (Python + Modal)
├── scripts/                 ← Scripts de setup y testing
└── dashboard/               ← Panel de control (Next.js)
```

---

## Comandos disponibles (Claude Code)

| Comando | Que hace |
|---------|----------|
| `/setup` | Configuracion completa — te guia paso a paso |
| `/test` | Verifica que todos los servicios funcionan |
| `/customize` | Modifica algo despues del setup (prompt, CRM, horarios) |
| `/status` | Muestra el estado de todos los servicios |

---

## Personalizacion

### Cambiar el prompt del agente
```
/customize → [1] Prompt del agente
```

### Agregar campos al CRM
```
/customize → [2] Campos del CRM
```

### Cambiar horario de llamadas salientes
```
/customize → [3] Horario de llamadas salientes
```

---

## Preguntas frecuentes

**Cuanto cuesta operar el sistema?**
Con volumenes bajos (< 100 llamadas/mes), todos los servicios pueden funcionar en plan gratuito o con costos minimos (< $20 USD/mes total).

**Puedo usarlo para una industria que no esta en la lista?**
Si. Usa cualquier template como base y modifica los prompts y campos del CRM con `/customize`.

**Que pasa si algo deja de funcionar?**
Corre `/status` para ver que servicio esta fallando, y `/test` para diagnosticar el problema.

**Puedo tener multiples agentes para diferentes clientes?**
Si. Clona el repo para cada cliente con su propio `sofia.config.yaml` y `.env`.

---

## Soporte

- **Comunidad Skool**: [Horizontes IA](https://iahorizontesacademy.com)
- **YouTube**: Tutoriales paso a paso en el canal de Horizontes IA
- **Creado por**: Santiago Munoz (@santmun)
