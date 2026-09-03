export default function ReviewActions({
  notes,
  onNotesChange,
  onSubmit,
}: {
  notes: string;
  onNotesChange: (value: string) => void;
  onSubmit: () => void;
}) {
  return (
    <div className="border rounded-md p-4">
      <label className="block text-sm font-medium mb-1">Reviewer Notes (optional)</label>
      <textarea
        className="border rounded-md p-2 w-full h-20 text-sm"
        value={notes}
        onChange={(e) => onNotesChange(e.target.value)}
      />
      <button className="mt-3 bg-green-700 text-white rounded-md px-4 py-2" onClick={onSubmit}>
        Submit Review
      </button>
    </div>
  );
}