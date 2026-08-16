export type Decision = 'PUBLISH' | 'REVIEW' | 'REJECT'
export interface EvaluationInput { question: string; paper_text: string; answer: string }
export interface Evidence { section: string; passage: string; similarity: number }
export interface ClaimResult { claim: string; label: string; evidence: Evidence[]; explanation: string; failure_types: string[]; nli_label: string | null; nli_confidence: number | null }
export interface Evaluation { evaluation_id: string; timestamp: string; overall_score: number; final_decision: Decision; claim_results: ClaimResult[]; main_concern: string; explanation: string; recommended_action: string; total_latency_ms: number }
export interface ReviewItem { question: string; answer: string; evaluation: Evaluation; reviewed: boolean }
export interface BenchmarkMetrics { total_examples: number; decision_accuracy_pct: number; unsupported_detection_rate_pct: number; contradiction_detection_rate_pct: number; false_publish_rate_pct: number; review_rate_pct: number }
export interface BenchmarkResult { example_id: string; expected_label: string; actual_label: string; is_correct: boolean; details: { category?: string; expected_claim_label?: string; actual_claim_label?: string; [key: string]: unknown } }
export interface BenchmarkRun { run_id: string; benchmark_name: string; status: 'RUNNING' | 'COMPLETED' | 'FAILED'; started_at: string; completed_at: string | null; metrics: BenchmarkMetrics | null; error_message: string | null; results: BenchmarkResult[] }
