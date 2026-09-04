"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import ClaimUploadForm from "@/components/ClaimUploadForm";
import { processClaim, processClaimFile } from "@/lib/api";

export default function HomePage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleTextSubmit(rawText: string) {
    setLoading(true);
    setError(null);
    try {
      const result = await processClaim(rawText);
      if (result.status === "PENDING_REVIEW") {
        router.push(
          `/review/${result.session_id}?candidates=${encodeURIComponent(
            JSON.stringify(result.candidates)
          )}`
        );
      } else {
        setError(
          `Claim could not proceed: ${result.status}. ${result.validation_errors.join(", ")}`
        );
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  async function handleFileSubmit(file: File) {
    setLoading(true);
    setError(null);
    try {
      const result = await processClaimFile(file);
      if (result.status === "PENDING_REVIEW") {
        router.push(
          `/review/${result.session_id}?candidates=${encodeURIComponent(
            JSON.stringify(result.candidates)
          )}`
        );
      } else {
        setError(
          `Claim could not proceed: ${result.status}. ${result.validation_errors.join(", ")}`
        );
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto space-y-8">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight sm:text-4xl">
            Claimora AI Processing
          </h1>
          <p className="text-slate-600 text-base max-w-lg mx-auto">
            Upload medical discharge summaries (PDF) or paste clinical text for AI code extraction & IRDAI form generation.
          </p>
        </div>

        <ClaimUploadForm
          onSubmitText={handleTextSubmit}
          onSubmitFile={handleFileSubmit}
          loading={loading}
        />

        {error && (
          <div className="max-w-xl mx-auto p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm font-medium">
            {error}
          </div>
        )}
      </div>
    </main>
  );
}