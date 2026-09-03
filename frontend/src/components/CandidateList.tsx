import type { CodeCandidate } from "@/types/claim";

export default function CandidateList({
  candidates,
  approvedCodes,
  onToggle,
}: {
  candidates: CodeCandidate[];
  approvedCodes: string[];
  onToggle: (codes: string[]) => void;
}) {
  function toggle(code: string) {
    onToggle(approvedCodes.includes(code) ? approvedCodes.filter((c) => c !== code) : [...approvedCodes, code]);
  }

  return (
    <div className="border rounded-md p-4 mb-4">
      <h2 className="font-semibold mb-2">Candidate Codes</h2>
      <p className="text-xs text-slate-500 mb-3">
        These are AI-suggested candidates, not confirmed diagnoses. Review and select the ones that apply.
      </p>
      <ul className="flex flex-col gap-2">
        {candidates.map((c) => (
          <li key={c.code} className="flex items-start gap-2 border-b pb-2">
            <input
              type="checkbox"
              checked={approvedCodes.includes(c.code)}
              onChange={() => toggle(c.code)}
              className="mt-1"
            />
            <div>
              <div className="font-mono text-sm">
                {c.code_system} {c.code} — {c.display_name}
              </div>
              <div className="text-xs text-slate-500">
                score: {c.score.toFixed(3)} · matched via: {c.matched_via.join(", ")}
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}