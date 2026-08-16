import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { BrowserRouter, NavLink, Navigate, Route, Routes, useNavigate, useParams } from 'react-router-dom'
import { createEvaluation, getBenchmarkRun, getBenchmarkRuns, getEvaluation, getPendingReviews, runPublicationBenchmark, submitReview } from './api'
import type { BenchmarkRun, Evaluation, EvaluationInput, ReviewItem } from './types'
import './App.css'
import './Review.css'
import './Benchmark.css'

function Layout() {
  return <div className="app-shell">
    <header className="site-header">
      <NavLink className="brand" to="/evaluate"><span className="brand-mark">A</span><span>AnswerTrust<small>Research answer safety</small></span></NavLink>
      <nav aria-label="Main navigation">
        <NavLink to="/evaluate">Evaluate</NavLink><NavLink to="/review">Review</NavLink><NavLink to="/benchmarks">Benchmarks</NavLink>
      </nav>
    </header>
    <main><Routes>
      <Route path="/evaluate" element={<EvaluatePage />} />
      <Route path="/evaluations/:id" element={<EvaluationPage />} />
      <Route path="/review" element={<ReviewPage />} />
      <Route path="/benchmarks" element={<BenchmarkPage />} />
      <Route path="*" element={<Navigate to="/evaluate" replace />} />
    </Routes></main>
  </div>
}

function EvaluatePage() {
  const navigate = useNavigate()
  const [form, setForm] = useState<EvaluationInput>({ question: '', paper_text: '', answer: '' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  async function submit(event: FormEvent) {
    event.preventDefault(); setError(''); setSubmitting(true)
    try { const result = await createEvaluation(form); navigate(`/evaluations/${result.evaluation_id}`) }
    catch (problem) { setError(problem instanceof Error ? problem.message : 'The evaluation could not be completed.') }
    finally { setSubmitting(false) }
  }
  return <>
    <section className="hero-panel"><div><p className="eyebrow">Research-grounded answer checking</p><h1>See what the paper really supports.</h1><p>AnswerTrust breaks an AI answer into claims, finds matching evidence, and explains what is safe to publish.</p></div><div className="hero-proof"><span>Evidence first</span><span>Claim by claim</span><span>Human review when needed</span></div></section>
    <div className="evaluate-layout">
      <aside className="guide-card"><p className="eyebrow">How it works</p><ol><li><b>Add the question</b><span>Tell us what the answer is trying to explain.</span></li><li><b>Paste trusted research</b><span>Use the paper or the most relevant sections.</span></li><li><b>Add the AI answer</b><span>We check each statement against the research.</span></li></ol><p className="privacy-note">Your text is sent only to your configured AnswerTrust API.</p></aside>
      <form className="evaluation-form" onSubmit={submit}>
        <div className="form-heading"><div><span className="step-number">1</span><div><h2>Start a new evaluation</h2><p>All three fields are required.</p></div></div></div>
        <label><span>Research question</span><small>The question the AI answer was asked.</small><input required minLength={3} value={form.question} onChange={e => setForm({...form, question:e.target.value})} placeholder="Example: Did the treatment improve sleep?" /></label>
        <label><span>Paper or selected text</span><small>Include section headings such as METHODS and RESULTS when possible.</small><textarea required minLength={3} value={form.paper_text} onChange={e => setForm({...form, paper_text:e.target.value})} placeholder={'METHODS\nDescribe how the study was run…\n\nRESULTS\nPaste the measured findings…'} /></label>
        <label><span>AI-generated answer</span><small>The exact answer you want to check.</small><textarea className="answer-field" required minLength={3} value={form.answer} onChange={e => setForm({...form, answer:e.target.value})} placeholder="Paste the AI-generated answer here…" /></label>
        {error && <div className="error-message" role="alert">{error}</div>}
        <button className="primary-button" disabled={submitting} type="submit">{submitting ? 'Checking every claim…' : 'Evaluate claims'}<span aria-hidden="true">→</span></button>
      </form>
    </div>
  </>
}

function EvaluationPage() {
  const { id = '' } = useParams(); const [result, setResult] = useState<Evaluation | null>(null); const [error, setError] = useState('')
  useEffect(() => { getEvaluation(id).then(setResult).catch(problem => setError(problem instanceof Error ? problem.message : 'Evaluation not found.')) }, [id])
  if (error) return <div className="state-card error-message" role="alert">{error}</div>
  if (!result) return <div className="state-card">Loading evaluation…</div>
  return <section className="result-page">
    <NavLink className="back-link" to="/evaluate">← New evaluation</NavLink>
    <div className={`verdict verdict-${result.final_decision.toLowerCase()}`}><div><p className="eyebrow">Recommended decision</p><h1>{result.final_decision}</h1><p>{decisionExplanation(result.final_decision)}</p></div><div className="score"><strong>{result.overall_score}</strong><small>out of 100</small></div></div>
    <div className="result-summary"><div><span>What to do next</span><p>{result.recommended_action}</p></div><div><span>Main concern</span><p>{result.main_concern}</p></div></div>
    <div className="section-heading"><div><p className="eyebrow">Evidence check</p><h2>Claim-by-claim audit</h2></div><p>Each claim is compared with the closest evidence found in the paper.</p></div>
    <div className="claim-list">{result.claim_results.map((claim,index) => <article className="claim-card" key={`${claim.claim}-${index}`}>
      <div className="claim-heading"><span>Claim {index+1}</span><b className={`label-${claim.label.toLowerCase()}`}>{claim.label.replaceAll('_',' ')}</b></div><h3>{claim.claim}</h3><p className="claim-explanation">{claim.explanation}</p>
      {claim.failure_types.length>0 && <div className="flags">{claim.failure_types.map(flag=><span key={flag}>{flag.replaceAll('_',' ')}</span>)}</div>}
      <h4>Evidence from the paper</h4>{claim.evidence.map((evidence,i)=><blockquote key={`${evidence.passage}-${i}`}><div><b>{evidence.section}</b><small>{Math.round(evidence.similarity*100)}% match</small></div><p>{evidence.passage}</p></blockquote>)}
    </article>)}</div>
  </section>
}

function decisionExplanation(decision: Evaluation['final_decision']) {
  if (decision === 'PUBLISH') return 'The checked claims are supported by the supplied research.'
  if (decision === 'REVIEW') return 'Some wording needs a person to make the final call.'
  return 'One or more important claims are unsupported or contradicted.'
}

function ReviewPage() {
  const [items,setItems]=useState<ReviewItem[]>([]); const [notes,setNotes]=useState<Record<string,string>>({}); const [loading,setLoading]=useState(true); const [workingId,setWorkingId]=useState(''); const [error,setError]=useState('')
  useEffect(()=>{getPendingReviews().then(setItems).catch(problem=>setError(problem instanceof Error?problem.message:'Review queue unavailable.')).finally(()=>setLoading(false))},[])
  async function decide(id:string,decision:'APPROVE'|'REJECT') { setError('');setWorkingId(id);try{await submitReview(id,decision,notes[id]?.trim()??'');setItems(current=>current.filter(item=>item.evaluation.evaluation_id!==id))}catch(problem){setError(problem instanceof Error?problem.message:'The review could not be saved.')}finally{setWorkingId('')} }
  if(loading)return <div className="state-card">Loading review queue…</div>
  return <section className="review-page">
    <div className="page-heading"><div><p className="eyebrow">Human decision needed</p><h1>Review uncertain answers.</h1><p>Check the original wording and evidence, then record a clear reason for your decision.</p></div><strong>{items.length}<small> awaiting review</small></strong></div>
    {error&&<div className="error-message" role="alert">{error}</div>}
    {items.length===0&&!error&&<div className="state-card"><h2>Review queue clear</h2><p>No evaluations currently require human judgment.</p></div>}
    <div className="review-list">{items.map(item=>{const id=item.evaluation.evaluation_id;const valid=(notes[id]?.trim().length??0)>=3;return <article className="review-card" key={id}>
      <div className="review-card-header"><span>Evaluation {id.slice(0,8)}</span><b>Needs your decision</b></div><div className="review-context"><div><span>Research question</span><p>{item.question}</p></div><div><span>AI-generated answer</span><p>{item.answer}</p></div></div>
      {item.evaluation.claim_results.map((claim,index)=><div className="review-claim" key={`${id}-${index}`}><div className="claim-heading"><span>Claim {index+1}</span><b>{claim.label.replaceAll('_',' ')}</b></div><h3>{claim.claim}</h3>{claim.evidence.map((evidence,i)=><blockquote key={i}><b>{evidence.section}</b><p>{evidence.passage}</p></blockquote>)}</div>)}
      <label><span>Reviewer notes</span><small>Explain why the answer is safe or unsafe. At least 3 characters are required.</small><textarea className="review-notes" value={notes[id]??''} onChange={event=>setNotes({...notes,[id]:event.target.value})} placeholder="Write the reason for your decision…" /></label>
      <div className="review-actions"><button className="approve" disabled={!valid||workingId===id} onClick={()=>decide(id,'APPROVE')}>Approve answer</button><button className="reject" disabled={!valid||workingId===id} onClick={()=>decide(id,'REJECT')}>Reject answer</button></div>
    </article>})}</div>
  </section>
}

const metricLabels: Array<[keyof NonNullable<BenchmarkRun['metrics']>, string, string]> = [
  ['decision_accuracy_pct', 'Decision accuracy', 'Correct publish, review, or reject decisions.'],
  ['unsupported_detection_rate_pct', 'Unsupported detection', 'Claims caught when the paper has no support.'],
  ['contradiction_detection_rate_pct', 'Contradiction detection', 'Claims caught when the paper says the opposite.'],
  ['false_publish_rate_pct', 'False publish rate', 'Unsafe answers incorrectly marked ready to publish.'],
  ['review_rate_pct', 'Human-review rate', 'Answers sent to a person for a final decision.'],
]

function BenchmarkPage() {
  const [runs,setRuns]=useState<BenchmarkRun[]>([]); const [selected,setSelected]=useState<BenchmarkRun|null>(null); const [loading,setLoading]=useState(true); const [running,setRunning]=useState(false); const [error,setError]=useState('')
  useEffect(()=>{getBenchmarkRuns().then(saved=>{setRuns(saved);if(saved[0])return getBenchmarkRun(saved[0].run_id).then(setSelected)}).catch(problem=>setError(problem instanceof Error?problem.message:'Benchmarks are unavailable.')).finally(()=>setLoading(false))},[])
  async function runBenchmark(){setError('');setRunning(true);try{const run=await runPublicationBenchmark();setSelected(run);setRuns(current=>[run,...current.filter(item=>item.run_id!==run.run_id)])}catch(problem){setError(problem instanceof Error?problem.message:'The benchmark could not be completed.')}finally{setRunning(false)}}
  async function selectRun(run:BenchmarkRun){if(run.run_id===selected?.run_id)return;setError('');try{setSelected(await getBenchmarkRun(run.run_id))}catch(problem){setError(problem instanceof Error?problem.message:'The benchmark run could not be loaded.')}}
  const incorrect=selected?.results.filter(result=>!result.is_correct)??[]
  return <section className="benchmark-page">
    <div className="benchmark-hero"><div><p className="eyebrow">Measured, not assumed</p><h1>Test publication safety.</h1><p>This benchmark checks AnswerTrust against 50 examples where the correct decision is already known.</p></div><button onClick={runBenchmark} disabled={running}>{running?'Checking 50 examples…':'Run publication benchmark'}<span aria-hidden="true">→</span></button></div>
    {error&&<div className="error-message" role="alert">{error}</div>}
    {loading?<div className="state-card">Loading benchmark history…</div>:<>
      {selected?.metrics?<>
        <div className="metric-grid">{metricLabels.map(([key,label,help])=><article className={key==='false_publish_rate_pct'?'risk-metric':''} key={key}><div><span>{label}</span><p>{help}</p></div><strong>{selected.metrics?.[key]}%</strong></article>)}</div>
        <div className="benchmark-detail"><div className="detail-heading"><div><p className="eyebrow">Error analysis</p><h2>{incorrect.length ? `${incorrect.length} mismatched ${incorrect.length===1?'example':'examples'}` : 'All examples matched'}</h2></div><span>{selected.results.length} labelled examples</span></div>
          {incorrect.length?<div className="result-table" role="table" aria-label="Mismatched benchmark examples">{incorrect.map(result=><div className="result-row" role="row" key={result.example_id}><b>{result.example_id}</b><span>{result.details.category??'Uncategorised'}</span><span>Expected <strong>{result.expected_label}</strong></span><span>Actual <strong>{result.actual_label}</strong></span></div>)}</div>:<p className="all-correct">No decision mismatches were found in this run.</p>}
        </div>
      </>:<div className="state-card"><h2>No measured runs yet</h2><p>Run the publication benchmark to create the first persisted baseline.</p></div>}
      {runs.length>0&&<div className="run-history"><div className="detail-heading"><div><p className="eyebrow">Saved runs</p><h2>Benchmark history</h2></div></div><div className="history-list">{runs.map(run=><button className={run.run_id===selected?.run_id?'selected':''} onClick={()=>selectRun(run)} key={run.run_id}><span><b>{run.benchmark_name.replaceAll('-',' ')}</b><small>{new Date(run.started_at).toLocaleString()}</small></span><span className={`run-status status-${run.status.toLowerCase()}`}>{run.status}</span><strong>{run.metrics?.decision_accuracy_pct??'—'}%</strong></button>)}</div></div>}
    </>}
    <p className="benchmark-note"><b>Important:</b> This is a small project regression set. It does not measure performance across all academic research.</p>
  </section>
}
export default function App() { return <BrowserRouter><Layout /></BrowserRouter> }
