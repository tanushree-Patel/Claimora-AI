"use client";

import { useState } from "react";

import CandidateList from "@/components/CandidateList";
import ExtractedDataPanel from "@/components/ExtractedDataPanel";
import ReviewActions from "@/components/ReviewActions";
import { resumeClaim } from "@/lib/api";
import type { CodeCandidate } from "@/types/claim";

export default function ReviewPage({
  params,
  searchParams,
}: {
  params: { sessionId: string };
  searchParams: { candidates?: string };
}) {
  // NOTE: passed via query string from page.tsx's redirect (see Integration Note below)
  const candidates: CodeCandidate[] = searchParams.candidates
    ? JSON.parse(decodeURIComponent(searchParams.candidates))
    : [];

  const [approvedCodes, setApprovedCodes] = useState<string[]>([]);
  const [notes, setNotes] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmitReview() {
    setError(null);
    try {
      const result = await resumeClaim(params.sessionId, approvedCodes, notes);
      setStatus(result.status);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    }
  }

  if (status === "APPROVED") {
    return <div className="p-8 text-lg font-medium text-green-700">Claim approved — session {params.sessionId}</div>;
  }

  return (
    <main className="mx-auto max-w-5xl p-8 grid grid-cols-2 gap-6">
      <ExtractedDataPanel sessionId={params.sessionId} />
      <div>
        <CandidateList candidates={candidates} approvedCodes={approvedCodes} onToggle={setApprovedCodes} />
        <ReviewActions notes={notes} onNotesChange={setNotes} onSubmit={handleSubmitReview} />
        {error && <p className="mt-2 text-red-600">{error}</p>}
      </div>
    </main>
  );
}