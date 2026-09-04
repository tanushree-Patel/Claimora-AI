"use client";

import Link from "next/link";
import { use, useEffect, useState } from "react";

import CandidateList from "@/components/CandidateList";
import ExtractedDataPanel from "@/components/ExtractedDataPanel";
import ReviewActions from "@/components/ReviewActions";
import { resumeClaim } from "@/lib/api";
import type { CodeCandidate } from "@/types/claim";

export default function ReviewPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);

  const [approvedCodes, setApprovedCodes] = useState<string[]>([]);
  const [notes, setNotes] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [candidates, setCandidates] = useState<CodeCandidate[]>([]);

  useEffect(() => {
    fetch(`/api/backend/claims/${sessionId}`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load claim state");
        return res.json();
      })
      .then((data) => {
        setCandidates(data.candidates || []);
        if (data.status) {
          setStatus(data.status);
        }
      })
      .catch((err) => setError(err.message));
  }, [sessionId]);

  async function handleSubmitReview() {
    if (submitting) return;
    setSubmitting(true);
    setError(null);
    try {
      const result = await resumeClaim(sessionId, approvedCodes, notes);
      setStatus(result.status);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setSubmitting(false);
    }
  }

  if (status === "COMPLETED" || status === "APPROVED") {
    return (
      <main className="min-h-screen bg-slate-50 py-12 px-4 flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border border-slate-200 p-8 text-center space-y-6">
          <div className="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto text-3xl font-bold">
            ✓
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Claim Finalized!</h1>
            <p className="text-slate-500 text-sm mt-1">
              IRDAI Part B Claim Form has been successfully generated.
            </p>
          </div>

          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs font-mono text-slate-600 break-all">
            Session ID: {sessionId}
          </div>

          <div className="flex flex-col gap-3">
            <a
              href={`/api/backend/claims/${sessionId}/pdf`}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-3 px-4 rounded-xl shadow-md transition flex items-center justify-center gap-2"
            >
              📥 Download IRDAI Claim PDF
            </a>
            <Link
              href="/"
              className="w-full bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium py-2.5 px-4 rounded-xl transition"
            >
              ← Upload Another Claim
            </Link>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-5xl p-8 grid grid-cols-1 md:grid-cols-2 gap-6">
      <ExtractedDataPanel sessionId={sessionId} />
      <div className="space-y-4">
        <CandidateList
          candidates={candidates}
          approvedCodes={approvedCodes}
          onToggle={setApprovedCodes}
        />
        <ReviewActions
          notes={notes}
          onNotesChange={setNotes}
          onSubmit={handleSubmitReview}
        />
        {submitting && (
          <p className="text-indigo-600 text-sm font-medium animate-pulse">
            Generating IRDAI PDF & finalizing claim...
          </p>
        )}
        {error && <p className="mt-2 text-red-600 text-sm font-medium">{error}</p>}
      </div>
    </main>
  );
}