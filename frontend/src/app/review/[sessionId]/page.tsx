"use client";

import { use, useState } from "react";

import CandidateList from "@/components/CandidateList";
import ExtractedDataPanel from "@/components/ExtractedDataPanel";
import ReviewActions from "@/components/ReviewActions";
import { resumeClaim } from "@/lib/api";
import type { CodeCandidate } from "@/types/claim";

export default function ReviewPage({
  params,
  searchParams,
}: {
  params: Promise<{ sessionId: string }>;
  searchParams: Promise<{ candidates?: string }>;
}) {
  const { sessionId } = use(params);
  const resolvedSearchParams = use(searchParams);

  const candidates: CodeCandidate[] = resolvedSearchParams.candidates
    ? JSON.parse(decodeURIComponent(resolvedSearchParams.candidates))
    : [];

  const [approvedCodes, setApprovedCodes] = useState<string[]>([]);
  const [notes, setNotes] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmitReview() {
    setError(null);
    try {
      const result = await resumeClaim(sessionId, approvedCodes, notes);
      setStatus(result.status);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    }
  }

  if (status === "APPROVED") {
    return <div className="p-8 text-lg font-medium text-green-700">Claim approved — session {sessionId}</div>;
  }

  return (
    <main className="mx-auto max-w-5xl p-8 grid grid-cols-2 gap-6">
      <ExtractedDataPanel sessionId={sessionId} />
      <div>
        <CandidateList candidates={candidates} approvedCodes={approvedCodes} onToggle={setApprovedCodes} />
        <ReviewActions notes={notes} onNotesChange={setNotes} onSubmit={handleSubmitReview} />
        {error && <p className="mt-2 text-red-600">{error}</p>}
      </div>
    </main>
  );
}