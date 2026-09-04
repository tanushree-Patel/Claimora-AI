"use client";

import { useEffect, useState } from "react";

export default function ExtractedDataPanel({ sessionId }: { sessionId: string }) {
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`/api/backend/claims/${sessionId}`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load claim state");
        return res.json();
      })
      .then(setData)
      .catch((err) => setError(err.message));
  }, [sessionId]);

  if (error) return <p className="text-red-600">{error}</p>;
  if (!data) return <p className="text-slate-400">Loading claim data...</p>;

  return (
    <div className="border rounded-md p-4">
      <h2 className="font-semibold mb-2">Claim Session</h2>
      <p className="text-sm text-slate-500 mb-4 font-mono">{sessionId}</p>
      <p className="text-sm">Status: <span className="font-medium">{String(data.status)}</span></p>
    </div>
  );
}