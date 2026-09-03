export interface CodeCandidate {
  code_system: string;
  code: string;
  display_name: string;
  score: number;
  matched_via: string[];
}

export interface ExtractedData {
  patient: { full_name: string; date_of_birth?: string; gender?: string; abha_id?: string; policy_number?: string };
  hospital: { hospital_name: string; hospital_id?: string; admission_date?: string; discharge_date?: string };
  clinical: { diagnosis_text: string; procedure_text?: string; symptoms: string[] };
  extraction_confidence?: number;
}

export interface ProcessClaimResponse {
  session_id: string;
  status: string;
  candidates: CodeCandidate[];
  validation_errors: string[];
}

export interface ResumeClaimResponse {
  session_id: string;
  status: string;
}