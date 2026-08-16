import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { BrowserRouter, NavLink, Navigate, Route, Routes, useNavigate, useParams } from 'react-router-dom'
import { createEvaluation, getEvaluation, getPendingReviews, submitReview } from './api'
import type { Evaluation, EvaluationInput, ReviewItem } from './types'
import './App.css'
import './Review.css'

function Layout() {
  return <div className="app-shell">
    <header className="site-header">
      <NavLink className="brand" to="/evaluate">AnswerTrust</NavLink>
      <nav aria-label="Main navigation">
        <NavLink to="/evaluate">Evaluate</NavLink><NavLink to="/review">Review</NavLink><NavLink to="/benchmarks">Benchmarks</NavLink>
      </nav>
    </header>
    <main><Routes>
      <Route path="/evaluate" element={<EvaluatePage />} />
      <Route path="/evaluations/:id" element={<EvaluationPage />} />
      <Route path="/review" element={<ReviewPage />} />
      <Route path="/benchmarks" element={<ComingSoon title="Benchmarks" />} />
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
    <section className="hero-panel"><p className="eyebrow">Research-grounded AI evaluation</p><h1>Know what the paper actually supports.</h1><p>Check every claim in an AI-generated answer against evidence from one trusted paper.</p></section>
    <form className="evaluation-form" onSubmit={submit}>
      <label><span>Research question</span><input required minLength={3} value={form.question} onChange={e => setForm({...form, question:e.target.value})} placeholder="Did the treatment improve sleep?" /></label>
      <div className="field-grid">
        <label><span>Paper or selected text</span><textarea required minLength={3} value={form.paper_text} onChange={e => setForm({...form, paper_text:e.target.value})} placeholder={'METHODS\n...\n\nRESULTS\n...'} /></label>
        <label><span>AI-generated answer</span><textarea required minLength={3} value={form.answer} onChange={e => setForm({...form, answer:e.target.value})} placeholder="Paste the answer to check." /></label>
      </div>
      {error && <div className="error-message" role="alert">{error}</div>}
      <button disabled={submitting} type="submit">{submitting ? 'Checking claims…' : 'Evaluate claims'}</button>
    </form>
  </>
}

function EvaluationPage() {
  const { id = '' } = useParams(); const [result, setResult] = useState<Evaluation | null>(null); const [error, setError] = useState('')
  useEffect(() => { getEvaluation(id).then(setResult).catch(problem => setError(problem instanceof Error ? problem.message : 'Evaluation not found.')) }, [id])
  if (error) return <div className="state-card error-message" role="alert">{error}</div>
  if (!result) return <div className="state-card">Loading evaluation…</div>
  return <section className="result-page">
    <NavLink className="back-link" to="/evaluate">← New evaluation</NavLink>
    <div className={`verdict verdict-${result.final_decision.toLowerCase()}`}><div><p className="eyebrow">Final decision</p><h1>{result.final_decision}</h1></div><strong>{result.overall_score}<small>/100</small></strong></div>
    <p className="result-summary">{result.recommended_action}</p><h2>Claim audit</h2>
    <div className="claim-list">{result.claim_results.map((claim,index) => <article className="claim-card" key={`${claim.claim}-${index}`}>
      <div className="claim-heading"><span>Claim {index+1}</span><b>{claim.label.replaceAll('_',' ')}</b></div><h3>{claim.claim}</h3><p>{claim.explanation}</p>
      {claim.failure_types.length>0 && <div className="flags">{claim.failure_types.map(flag=><span key={flag}>{flag.replaceAll('_',' ')}</span>)}</div>}
      <h4>Evidence used</h4>{claim.evidence.map((evidence,i)=><blockquote key={`${evidence.passage}-${i}`}><b>{evidence.section}</b><p>{evidence.passage}</p><small>{Math.round(evidence.similarity*100)}% match</small></blockquote>)}
    </article>)}</div>
  </section>
}

function ReviewPage() {
  const [items,setItems]=useState<ReviewItem[]>([]); const [notes,setNotes]=useState<Record<string,string>>({}); const [loading,setLoading]=useState(true); const [workingId,setWorkingId]=useState(''); const [error,setError]=useState('')
  useEffect(()=>{getPendingReviews().then(setItems).catch(problem=>setError(problem instanceof Error?problem.message:'Review queue unavailable.')).finally(()=>setLoading(false))},[])
  async function decide(id:string,decision:'APPROVE'|'REJECT') { setError('');setWorkingId(id);try{await submitReview(id,decision,notes[id]?.trim()??'');setItems(current=>current.filter(item=>item.evaluation.evaluation_id!==id))}catch(problem){setError(problem instanceof Error?problem.message:'The review could not be saved.')}finally{setWorkingId('')} }
  if(loading)return <div className="state-card">Loading review queue…</div>
  return <section className="review-page">
    <div className="page-heading"><div><p className="eyebrow">Human-in-the-loop safety</p><h1>Review the edge cases.</h1></div><strong>{items.length}<small> awaiting review</small></strong></div>
    {error&&<div className="error-message" role="alert">{error}</div>}
    {items.length===0&&!error&&<div className="state-card"><h2>Review queue clear</h2><p>No evaluations currently require human judgment.</p></div>}
    <div className="review-list">{items.map(item=>{const id=item.evaluation.evaluation_id;const valid=(notes[id]?.trim().length??0)>=3;return <article className="review-card" key={id}>
      <div className="review-context"><div><span>Research question</span><p>{item.question}</p></div><div><span>AI-generated answer</span><p>{item.answer}</p></div></div>
      {item.evaluation.claim_results.map((claim,index)=><div className="review-claim" key={`${id}-${index}`}><div className="claim-heading"><span>Claim {index+1}</span><b>{claim.label.replaceAll('_',' ')}</b></div><h3>{claim.claim}</h3>{claim.evidence.map((evidence,i)=><blockquote key={i}><b>{evidence.section}</b><p>{evidence.passage}</p></blockquote>)}</div>)}
      <label><span>Reviewer notes</span><textarea className="review-notes" value={notes[id]??''} onChange={event=>setNotes({...notes,[id]:event.target.value})} placeholder="Explain the decision…" /></label>
      <div className="review-actions"><button className="approve" disabled={!valid||workingId===id} onClick={()=>decide(id,'APPROVE')}>Approve</button><button className="reject" disabled={!valid||workingId===id} onClick={()=>decide(id,'REJECT')}>Reject</button></div>
    </article>})}</div>
  </section>
}

function ComingSoon({title}:{title:string}) { return <section className="state-card"><p className="eyebrow">React migration</p><h1>{title}</h1><p>This screen will be connected in the next frontend chunk.</p></section> }
export default function App() { return <BrowserRouter><Layout /></BrowserRouter> }
