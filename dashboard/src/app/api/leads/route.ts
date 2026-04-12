import { NextResponse } from "next/server";
import { getLeads } from "@/lib/notion";

export async function GET() {
  const leads = await getLeads();
  return NextResponse.json(leads);
}
