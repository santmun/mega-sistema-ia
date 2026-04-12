import { NextResponse } from "next/server";
import { getCalls } from "@/lib/notion";

export async function GET() {
  const calls = await getCalls();
  return NextResponse.json(calls);
}
