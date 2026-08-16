export type Decision = 'PUBLISH' | 'REVIEW' | 'REJECT'
export interface EvaluationInput { question: string; paper_text: string; answer: string }
export interface Evidence { section: string; passage: string; similarity: number }
export interface ClaimResult { claim: string; label: string; evidence: Evidence[]; explanation: string; failure_types: string[]; nli_label: string | null; nli_confidence: number | null }
export interface Evaluation { evaluation_id: string; timestamp: string; overall_score: number; final_decision: Decision; claim_results: ClaimResult[]; main_concern: string; explanation: string; recommended_action: string; total_latency_ms: number }
export interface ReviewItem { question: string; answer: string; evaluation: Evaluation; reviewed: boolean }
