import type { ProcessClaimResponse, ResumeClaimResponse } from "@/types/claim";

const BASE = "/api/backend";

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed with status ${res.status}`);
  }
  return res.json();
}

export async function processClaim(rawText: string): Promise<ProcessClaimResponse> {
  const res = await fetch(`${BASE}/claims/process`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ raw_text: rawText }),
  });
  return handleResponse<ProcessClaimResponse>(res);
}

export async function processClaimFile(file: File): Promise<ProcessClaimResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${BASE}/claims/process-file`, {
    method: "POST",
    body: formData,
  });
  return handleResponse<ProcessClaimResponse>(res);
}

export async function resumeClaim(
  sessionId: string,
  approvedCodes: string[],
  reviewerNotes: string
): Promise<ResumeClaimResponse> {
  const res = await fetch(`${BASE}/claims/${sessionId}/resume`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ approved_codes: approvedCodes, reviewer_notes: reviewerNotes || null }),
  });
  return handleResponse<ResumeClaimResponse>(res);
}