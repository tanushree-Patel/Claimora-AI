"use client";

import { useState } from "react";

export default function ClaimUploadForm({
  onSubmitText,
  onSubmitFile,
  loading,
}: {
  onSubmitText: (rawText: string) => void;
  onSubmitFile: (file: File) => void;
  loading: boolean;
}) {
  const [activeTab, setActiveTab] = useState<"file" | "text">("file");
  const [text, setText] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.type === "application/pdf" || file.name.endsWith(".pdf")) {
        setSelectedFile(file);
      }
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === "application/pdf" || file.name.endsWith(".pdf")) {
        setSelectedFile(file);
      }
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (activeTab === "file" && selectedFile) {
      onSubmitFile(selectedFile);
    } else if (activeTab === "text" && text.trim().length >= 10) {
      onSubmitText(text);
    }
  };

  return (
    <div className="w-full max-w-xl mx-auto bg-white rounded-xl shadow-lg border border-slate-200 overflow-hidden">
      {/* Mode Switcher Tabs */}
      <div className="flex border-b border-slate-200 bg-slate-50 p-1">
        <button
          type="button"
          onClick={() => setActiveTab("file")}
          className={`flex-1 py-2.5 px-4 text-sm font-medium rounded-lg transition-all ${
            activeTab === "file"
              ? "bg-white text-slate-900 shadow-sm font-semibold"
              : "text-slate-600 hover:text-slate-900"
          }`}
        >
          📄 Upload PDF Summary
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("text")}
          className={`flex-1 py-2.5 px-4 text-sm font-medium rounded-lg transition-all ${
            activeTab === "text"
              ? "bg-white text-slate-900 shadow-sm font-semibold"
              : "text-slate-600 hover:text-slate-900"
          }`}
        >
          📝 Paste Clinical Text
        </button>
      </div>

      <form onSubmit={handleSubmit} className="p-6 flex flex-col gap-5">
        {activeTab === "file" ? (
          <div>
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                dragActive
                  ? "border-indigo-500 bg-indigo-50/50"
                  : selectedFile
                  ? "border-emerald-500 bg-emerald-50/30"
                  : "border-slate-300 hover:border-slate-400 bg-slate-50/50"
              }`}
            >
              <input
                type="file"
                accept=".pdf,application/pdf"
                id="pdf-upload"
                className="hidden"
                onChange={handleFileChange}
              />
              <label htmlFor="pdf-upload" className="cursor-pointer block">
                {selectedFile ? (
                  <div className="space-y-2">
                    <div className="w-12 h-12 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto text-xl">
                      ✓
                    </div>
                    <p className="font-semibold text-slate-800">{selectedFile.name}</p>
                    <p className="text-xs text-slate-500">
                      {(selectedFile.size / 1024).toFixed(1)} KB • Click or drag to replace
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div className="w-12 h-12 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto text-xl font-bold">
                      ↑
                    </div>
                    <div>
                      <p className="font-medium text-slate-800">
                        Click to upload or drag & drop PDF
                      </p>
                      <p className="text-xs text-slate-500 mt-1">
                        Upload discharge summary or medical claim PDF
                      </p>
                    </div>
                  </div>
                )}
              </label>
            </div>
          </div>
        ) : (
          <div>
            <textarea
              className="w-full border border-slate-300 rounded-xl p-4 h-48 font-mono text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition"
              placeholder="Paste raw clinical summary / discharge notes here..."
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
          </div>
        )}

        <button
          type="submit"
          disabled={
            loading ||
            (activeTab === "file" && !selectedFile) ||
            (activeTab === "text" && text.trim().length < 10)
          }
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-xl shadow-md disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
              Processing Claim...
            </span>
          ) : (
            "Submit for Coding & AI Processing →"
          )}
        </button>
      </form>
    </div>
  );
}