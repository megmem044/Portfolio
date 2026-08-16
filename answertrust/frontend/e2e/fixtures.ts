export const evaluation = {
  evaluation_id: 'evaluation-123',
  timestamp: '2026-08-16T12:00:00Z',
  overall_score: 92,
  final_decision: 'PUBLISH',
  claim_results: [{
    claim: 'Daily walking lowered blood pressure.',
    label: 'SUPPORTED',
    evidence: [{ section: 'RESULTS', passage: 'Daily walking lowered blood pressure.', similarity: 0.96 }],
    explanation: 'The result directly supports this claim.',
    failure_types: [],
    nli_label: null,
    nli_confidence: null,
  }],
  dimension_scores: [],
  main_concern: 'None',
  explanation: 'The answer is supported.',
  recommended_action: 'The answer can be published.',
  total_latency_ms: 25,
  deterministic_latency_ms: 25,
}

export const reviewEvaluation = {
  ...evaluation,
  evaluation_id: 'review-123',
  overall_score: 64,
  final_decision: 'REVIEW',
  recommended_action: 'A person should review this answer.',
}

export const benchmark = {
  run_id: 'benchmark-123',
  benchmark_name: 'publication-safety',
  status: 'COMPLETED',
  started_at: '2026-08-16T12:00:00Z',
  completed_at: '2026-08-16T12:00:02Z',
  metrics: {
    total_examples: 50,
    decision_accuracy_pct: 98,
    unsupported_detection_rate_pct: 100,
    contradiction_detection_rate_pct: 100,
    false_publish_rate_pct: 0,
    review_rate_pct: 20,
  },
  error_message: null,
  results: [{
    example_id: 'part-01',
    expected_label: 'REVIEW',
    actual_label: 'PUBLISH',
    is_correct: false,
    details: { category: 'overstated' },
  }],
}
