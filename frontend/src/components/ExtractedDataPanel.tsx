export default function ExtractedDataPanel({ sessionId }: { sessionId: string }) {
  return (
    <div className="border rounded-md p-4">
      <h2 className="font-semibold mb-2">Claim Session</h2>
      <p className="text-sm text-slate-500 mb-4 font-mono">{sessionId}</p>
      <p className="text-sm text-slate-600">
        Extracted patient/hospital/clinical detail display will be wired up once a
        <code className="mx-1">GET /claims/{"{"}session_id{"}"}</code> endpoint exposes paused graph state
        (planned for Phase 6).
      </p>
    </div>
  );
}