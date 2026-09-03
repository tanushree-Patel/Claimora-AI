"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import ClaimUploadForm from "@/components/ClaimUploadForm"
import { processClaim } from "@/lib/api";

export default function HomePage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(rawText: string) {
    setLoading(true);
    setError(null);
    try {
      const result = await processClaim(rawText);
      if (result.status === "PENDING_REVIEW") {
        router.push(`/review/${result.session_id}?candidates=${encodeURIComponent(JSON.stringify(result.candidates))}`);
      } else {
        setError(`Claim could not proceed: ${result.status}. ${result.validation_errors.join(", ")}`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-2xl p-8">
      <h1 className="text-2xl font-semibold mb-4">Submit Clinical Text for Coding</h1>
      <ClaimUploadForm onSubmit={handleSubmit} loading={loading} />
      {error && <p className="mt-4 text-red-600">{error}</p>}
    </main>
  );
}