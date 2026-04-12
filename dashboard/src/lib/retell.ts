const RETELL_API = "https://api.retellai.com";

function headers() {
  return {
    Authorization: `Bearer ${process.env.RETELL_API_KEY}`,
    "Content-Type": "application/json",
  };
}

export async function getAgent() {
  const agentId = process.env.RETELL_INBOUND_AGENT_ID;
  if (!agentId) return null;

  const res = await fetch(`${RETELL_API}/get-agent/${agentId}`, {
    headers: headers(),
    next: { revalidate: 60 },
  });
  if (!res.ok) return null;
  return res.json();
}

export async function getLlm(llmId?: string) {
  const id = llmId || process.env.RETELL_LLM_ID;
  if (!id) return null;

  const res = await fetch(`${RETELL_API}/get-retell-llm/${id}`, {
    headers: headers(),
    next: { revalidate: 60 },
  });
  if (!res.ok) return null;
  return res.json();
}

export async function updateLlm(updates: {
  begin_message?: string;
  general_prompt?: string;
  model_temperature?: number;
}) {
  const llmId = process.env.RETELL_LLM_ID;
  if (!llmId) throw new Error("RETELL_LLM_ID not set");

  const res = await fetch(`${RETELL_API}/update-retell-llm/${llmId}`, {
    method: "PATCH",
    headers: headers(),
    body: JSON.stringify(updates),
  });
  if (!res.ok) throw new Error(`Retell ${res.status}: ${await res.text()}`);
  return res.json();
}
