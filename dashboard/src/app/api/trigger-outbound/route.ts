import { NextResponse } from "next/server";

export async function POST() {
  const baseUrl = process.env.MODAL_BASE_URL;
  if (!baseUrl) {
    return NextResponse.json(
      { status: "error", message: "MODAL_BASE_URL not configured" },
      { status: 500 }
    );
  }

  const res = await fetch(`${baseUrl}/trigger-outbound`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  const data = await res.json();
  return NextResponse.json(data);
}
