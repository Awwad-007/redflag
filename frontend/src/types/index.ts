export type Severity = 'INFO' | 'WARNING' | 'CRITICAL';
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type AgreementType = 'RESIDENTIAL' | 'COMMERCIAL' | 'UNKNOWN';

export interface Flag {
  id: string;
  severity: Severity;
  category: string;
  clause_title: string;
  original_text: string;
  violation: string;
  statutory_reference: string;
  recommendation: string;
}

export interface CompliantClause {
  category: string;
  description: string;
}

export interface ContractMetadata {
  tenant_name: string | null;
  landlord_name: string | null;
  property_address: string | null;
  monthly_rent: string | null;
  security_deposit: string | null;
  lease_duration: string | null;
  commencement_date: string | null;
  agreement_type: AgreementType;
}

export interface AnalysisMeta {
  filename: string;
  char_count: number;
  word_count: number;
}

export interface AnalysisResult {
  overall_risk: RiskLevel;
  compliance_score: number;
  summary: string;
  flags: Flag[];
  compliant_clauses: CompliantClause[];
  metadata: ContractMetadata;
  disclaimer: string;
  _meta: AnalysisMeta;
}

export type AnalysisState =
  | { status: 'idle' }
  | { status: 'uploading' }
  | { status: 'analyzing' }
  | { status: 'done'; result: AnalysisResult }
  | { status: 'error'; message: string };
