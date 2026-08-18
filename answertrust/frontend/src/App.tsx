// Main application routes and page components.
import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { BrowserRouter, NavLink, Navigate, Route, Routes, useNavigate, useParams } from 'react-router-dom'
import { createEvaluation, getAnalytics, getBenchmarkRun, getBenchmarkRuns, getEvaluation, getPendingReviews, login, runPublicationBenchmark, setAccessToken, submitReview } from './api'
import type { Analytics, BenchmarkRun, Evaluation, EvaluationInput, ReviewItem, User } from './types'
import './App.css'
import './Review.css'
import './Benchmark.css'
import './Analytics.css'

const overstatementDemo: EvaluationInput = {
  question: 'Did the treatment improve sleep for every participant?',
  paper_text: 'RESULTS\nThe treatment improved sleep quality in some participants.\n\nLIMITATIONS\nThe study was conducted at one clinic and follow-up lasted four weeks.',
  answer: 'The treatment improved sleep for every participant and will work for all patients long term.',
}

function Layout() {
  const [user,setUser]=useState<User|null>(()=>{try{return JSON.parse(localStorage.getItem('answertrust_user')??'null') as User|null}catch{return null}})
  function signedIn(token:string,nextUser:User){localStorage.setItem('answertrust_token',token);localStorage.setItem('answertrust_user',JSON.stringify(nextUser));setAccessToken(token);setUser(nextUser)}
  function signOut(){localStorage.removeItem('answertrust_token');localStorage.removeItem('answertrust_user');setAccessToken('');setUser(null)}
  return <div className="app-shell">
    <header className="site-header">
      <NavLink className="brand" to="/evaluate"><span className="brand-mark">A</span><span>AnswerTrust<small>Research answer safety</small></span></NavLink>
      <nav aria-label="Main navigation">
        <NavLink to="/evaluate">Evaluate</NavLink>{user&&<NavLink to="/review">Review</NavLink>}<NavLink to="/benchmarks">Benchmarks</NavLink>{user?.role==='ADMIN'&&<NavLink to="/analytics">Analytics</NavLink>}
      </nav>
      <div className="account-area">{user?<><span><b>{user.role}</b>{user.email}</span><button onClick={signOut}>Sign out</button></>:<NavLink to="/login">Sign in</NavLink>}</div>
    </header>
    <main><Routes>
      <Route path="/login" element={user?<Navigate to="/review" replace/>:<LoginPage onLogin={signedIn}/>} />
      <Route path="/evaluate" element={<EvaluatePage />} />
      <Route path="/evaluations/:id" element={<EvaluationPage />} />
      <Route path="/review" element={user?<ReviewPage />:<Navigate to="/login" replace />} />
      <Route path="/benchmarks" element={<BenchmarkPage user={user} />} />
      <Route path="/analytics" element={user?.role==='ADMIN'?<AnalyticsPage />:<Navigate to="/login" replace />} />
      <Route path="*" element={<Navigate to="/evaluate" replace />} />
    </Routes></main>
  </div>
}

function LoginPage({onLogin}:{onLogin:(token:string,user:User)=>void}) {
  const [email,setEmail]=useState('');const [password,setPassword]=useState('');const [error,setError]=useState('');const [working,setWorking]=useState(false)
  async function submit(event:FormEvent){event.preventDefault();setError('');setWorking(true);try{const result=await login(email,password);onLogin(result.access_token,result.user)}catch(problem){setError(problem instanceof Error?problem.message:'Sign in failed.')}finally{setWorking(false)}}
  return <section className="login-page"><div className="login-intro"><p className="eyebrow">Protected workspace</p><h1>Sign in to review answers.</h1><p>Review access is limited to approved reviewers and administrators. Evaluation remains available without an account.</p></div><form className="login-card" onSubmit={submit}><h2>Welcome back</h2><p>Use the account created by your administrator.</p><label><span>Email</span><input type="email" required autoComplete="username" value={email} onChange={event=>setEmail(event.target.value)} /></label><label><span>Password</span><input type="password" required autoComplete="current-password" value={password} onChange={event=>setPassword(event.target.value)} /></label>{error&&<div className="error-message" role="alert">{error}</div>}<button className="primary-button" disabled={working}>{working?'Signing in…':'Sign in'}<span>→</span></button></form></section>
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
  function loadDemo(){setForm(overstatementDemo);setError('')}
  return <>
    <section className="hero-panel"><div><p className="eyebrow">Research-grounded answer checking</p><h1>See what the paper really supports.</h1><p>AnswerTrust breaks an AI answer into claims, finds matching evidence, and explains what is safe to publish.</p></div><div className="hero-proof"><span>Evidence first</span><span>Claim by claim</span><span>Human review when needed</span></div></section>
    <div className="evaluate-layout">
      <aside className="guide-card"><p className="eyebrow">How it works</p><ol><li><b>Paste the question</b><span>Copy the question that was given to the AI.</span></li><li><b>Paste the paper text</b><span>Copy the exact excerpt, relevant section, or full paper text.</span></li><li><b>Paste the AI answer</b><span>Copy the answer the AI generated for that question.</span></li></ol><p className="privacy-note">AnswerTrust checks the AI answer only against the paper text you provide. It does not use the web as evidence.</p><div className="responsible-use"><b>Use human judgment</b><p>A result is a screening recommendation, not proof that a scientific claim is true. Expert review is still required for medical, scientific, and publication decisions.</p></div></aside>
      <form className="evaluation-form" onSubmit={submit}>
        <div className="form-heading"><div><span className="step-number">1</span><div><h2>Start a new evaluation</h2><p>All three fields are required.</p></div></div></div>
        <div className="demo-callout"><div><b>Want to see an overstatement?</b><p>Load an example where an AI changes “some participants” into “every participant” and extends a four-week result to the long term.</p></div><button type="button" onClick={loadDemo}>Load demo</button></div>
        <label><span>Research question</span><small>Paste the question that was answered by the AI.</small><input aria-label="Research question" required minLength={3} value={form.question} onChange={e => setForm({...form, question:e.target.value})} placeholder="Example: Did the treatment improve sleep?" /></label>
        <label><span>Text copied from the paper</span><small>Paste the exact excerpt that may support the answer, or paste the full paper text. Section headings are helpful but optional.</small><textarea aria-label="Text copied from the paper" required minLength={3} value={form.paper_text} onChange={e => setForm({...form, paper_text:e.target.value})} placeholder="Paste the paper’s actual words here…" /></label>
        <label><span>AI-generated answer</span><small>Paste the answer the AI generated when it was asked the research question above.</small><textarea aria-label="AI-generated answer" className="answer-field" required minLength={3} value={form.answer} onChange={e => setForm({...form, answer:e.target.value})} placeholder="Paste the AI-generated answer here…" /></label>
        {error && <div className="error-message" role="alert">{error}</div>}
        <button className="primary-button" disabled={submitting} type="submit">{submitting ? 'Checking every claim…' : 'Evaluate claims'}<span aria-hidden="true">→</span></button>
      </form>
    </div>
  </>
}

function EvaluationPage() {
  const { id = '' } = useParams(); const [result, setResult] = useState<Evaluation | null>(null); const [status,setStatus]=useState('QUEUED'); const [attempts,setAttempts]=useState(0); const [error, setError] = useState('')
  useEffect(() => { let cancelled=false;let timer:number|undefined;async function poll(){try{const response=await getEvaluation(id);if(cancelled)return;if('final_decision' in response){setResult(response);return}setStatus(response.state);setAttempts(response.attempt_count);if(response.state==='FAILED'){setError(response.failure_message??'The evaluation could not be completed.');return}timer=window.setTimeout(poll,1500)}catch(problem){if(!cancelled)setError(problem instanceof Error ? problem.message : 'Evaluation not found.')}}poll();return()=>{cancelled=true;if(timer)window.clearTimeout(timer)} }, [id])
  if (error) return <div className="state-card error-message" role="alert">{error}</div>
  if (!result) return <div className="state-card processing-card"><div className="processing-spinner"/><p className="eyebrow">{status.replaceAll('_',' ')}</p><h2>Checking the answer against the paper…</h2><p>{status==='QUEUED'?'Your evaluation is waiting for the worker.':'The worker is checking each claim and finding evidence.'}</p>{attempts>1&&<small>Retry attempt {attempts} of 3</small>}</div>
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

function BenchmarkPage({user}:{user:User|null}) {
  const [runs,setRuns]=useState<BenchmarkRun[]>([]); const [selected,setSelected]=useState<BenchmarkRun|null>(null); const [loading,setLoading]=useState(true); const [running,setRunning]=useState(false); const [error,setError]=useState('')
  useEffect(()=>{getBenchmarkRuns().then(saved=>{setRuns(saved);if(saved[0])return getBenchmarkRun(saved[0].run_id).then(setSelected)}).catch(problem=>setError(problem instanceof Error?problem.message:'Benchmarks are unavailable.')).finally(()=>setLoading(false))},[])
  async function runBenchmark(){setError('');setRunning(true);try{const run=await runPublicationBenchmark();setSelected(run);setRuns(current=>[run,...current.filter(item=>item.run_id!==run.run_id)])}catch(problem){setError(problem instanceof Error?problem.message:'The benchmark could not be completed.')}finally{setRunning(false)}}
  async function selectRun(run:BenchmarkRun){if(run.run_id===selected?.run_id)return;setError('');try{setSelected(await getBenchmarkRun(run.run_id))}catch(problem){setError(problem instanceof Error?problem.message:'The benchmark run could not be loaded.')}}
  const incorrect=selected?.results.filter(result=>!result.is_correct)??[]
  return <section className="benchmark-page">
    <div className="benchmark-hero"><div><p className="eyebrow">Measured, not assumed</p><h1>Test publication safety.</h1><p>This benchmark checks AnswerTrust against 150 labelled examples, including 100 real-paper cases.</p></div>{user?.role==='ADMIN'?<button onClick={runBenchmark} disabled={running}>{running?'Checking 150 examples…':'Run publication benchmark'}<span aria-hidden="true">→</span></button>:<div className="admin-note">Administrators can run new benchmarks.<NavLink to="/login">{user?'Your account is read-only here.':'Sign in as an administrator.'}</NavLink></div>}</div>
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

function AnalyticsPage() {
  const [data,setData]=useState<Analytics|null>(null);const [error,setError]=useState('')
  useEffect(()=>{getAnalytics().then(setData).catch(problem=>setError(problem instanceof Error?problem.message:'Analytics could not be loaded.'))},[])
  if(error)return <div className="state-card error-message" role="alert">{error}</div>
  if(!data)return <div className="state-card">Loading analytics…</div>
  const decisionTotal=Math.max(1,Object.values(data.decision_counts).reduce((sum,value)=>sum+value,0))
  return <section className="analytics-page"><div className="analytics-heading"><div><p className="eyebrow">Administrator analytics</p><h1>How AnswerTrust is performing.</h1><p>These totals come from saved evaluations, reviews, and benchmark runs.</p></div><span>Persistent data</span></div>
    <div className="analytics-summary"><article><span>Total evaluations</span><strong>{data.total_evaluations}</strong><p>Completed decisions saved in the database.</p></article><article><span>Open reviews</span><strong>{data.open_reviews}</strong><p>Answers still waiting for a person.</p></article><article><span>Resolved reviews</span><strong>{data.resolved_reviews}</strong><p>Decisions completed by reviewers.</p></article><article><span>Average evaluation time</span><strong>{data.average_evaluation_latency_ms}<small> ms</small></strong><p>Average processing time per saved evaluation.</p></article></div>
    <div className="analytics-grid"><article className="analytics-card"><div className="card-title"><div><p className="eyebrow">System outcomes</p><h2>Evaluation decisions</h2></div><span>{data.total_evaluations} total</span></div><div className="bar-list">{Object.entries(data.decision_counts).map(([name,value])=><div className="bar-row" key={name}><div><b>{name}</b><span>{value}</span></div><div className="bar-track"><i className={`bar-${name.toLowerCase()}`} style={{width:`${value/decisionTotal*100}%`}} /></div></div>)}</div></article>
      <article className="analytics-card"><div className="card-title"><div><p className="eyebrow">Human outcomes</p><h2>Review decisions</h2></div><span>{data.resolved_reviews} resolved</span></div><div className="review-totals"><div><strong>{data.review_counts.APPROVE}</strong><span>Approved</span></div><div><strong>{data.review_counts.REJECT}</strong><span>Rejected</span></div></div></article></div>
    <article className="analytics-card"><div className="card-title"><div><p className="eyebrow">Regression trend</p><h2>Benchmark history</h2></div><span>Oldest to newest</span></div>{data.benchmark_history.length?<div className="trend-list">{data.benchmark_history.map(run=><div key={run.run_id}><span>{new Date(run.started_at).toLocaleDateString()}</span><b>{run.decision_accuracy_pct}% accuracy</b><small>{run.false_publish_rate_pct}% false publish</small></div>)}</div>:<p className="analytics-empty">No completed benchmark runs yet.</p>}</article>
  </section>
}
export default function App() { return <BrowserRouter><Layout /></BrowserRouter> }
