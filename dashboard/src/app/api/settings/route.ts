import { NextResponse } from "next/server";
import { getLlm, updateLlm } from "@/lib/retell";

export async function GET() {
  const llm = await getLlm();
  return NextResponse.json({
    beginMessage: llm?.begin_message ?? "",
    generalPrompt: llm?.general_prompt ?? "",
    modelTemperature: llm?.model_temperature ?? 0.4,
    model: llm?.model ?? "",
  });
}

export async function PATCH(request: Request) {
  const body = await request.json();
  const updates: Record<string, unknown> = {};

  if (body.beginMessage !== undefined) updates.begin_message = body.beginMessage;
  if (body.generalPrompt !== undefined) updates.general_prompt = body.generalPrompt;
  if (body.modelTemperature !== undefined) updates.model_temperature = body.modelTemperature;

  const result = await updateLlm(updates);
  return NextResponse.json({ status: "ok", llm_id: result.llm_id });
}
