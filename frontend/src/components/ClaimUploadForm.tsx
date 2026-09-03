"use client";

import { useState } from "react";

export default function ClaimUploadForm({
  onSubmit,
  loading,
}: {
  onSubmit: (rawText: string) => void;
  loading: boolean;
}) {
  const [text, setText] = useState("");

  return (
    <div className="flex flex-col gap-3">
      <textarea
        className="border rounded-md p-3 h-48 font-mono text-sm"
        placeholder="Paste raw clinical text here..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button
        className="bg-slate-900 text-white rounded-md px-4 py-2 disabled:opacity-50"
        disabled={loading || text.trim().length < 10}
        onClick={() => onSubmit(text)}
      >
        {loading ? "Processing..." : "Submit for Coding"}
      </button>
    </div>
  );
}