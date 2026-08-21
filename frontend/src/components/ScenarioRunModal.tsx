import { FormEvent, ReactNode, useEffect, useMemo, useState } from 'react';
import { BrainCircuit, CheckCircle2, FileSearch, FileText, LoaderCircle, Scale, UploadCloud, X } from 'lucide-react';
import { apiFetch, jsonBody } from '../lib/api';

type Matter = { id: string; case_name: string };
type ScenarioField = { name: string; label: string; type: string; options?: string[]; required?: boolean };
type ScenarioType = { event_type: string; label: string; description: string; fields: ScenarioField[] };
export type FactEvidenceRow = { fact: string; source: string; status: string };
export type IssueAnalysis = { issue: string; facts: string; applicable_law: string; application: string; conclusion: string };
export type OpponentRebuttal = { opponent_argument: string; our_rebuttal: string; supporting_facts: string };
export type FilingChecklistItem = { item: string; status: string; note?: string };
export type ScenarioResult = {
  summary?: string;
  factual_findings?: string[];
  key_issues?: string[];
  fact_evidence_matrix?: FactEvidenceRow[];
  issue_analysis?: IssueAnalysis[];
  evidence_assessment?: string[];
  missing_evidence?: string[];
  timeline_builder?: { event: string; date: string }[];
  strength_analysis?: { potential_strengths?: string[]; risks_or_uncertainties?: string[]; readiness?: string };
  opponent_arguments?: string[];
  opponent_rebuttal?: OpponentRebuttal[];
  recommended_reliefs?: string[];
  next_steps?: string[];
  filing_checklist?: FilingChecklistItem[];
};
type UploadState = { id?: string; name: string; status: 'selected' | 'uploading' | 'extracting' | 'ready' | 'failed'; error?: string };
type RunPhase = 'idle' | 'preparing' | 'extracting' | 'analysing' | 'finalising';

export function ScenarioRunModal({ clientId, cases, initialCaseId, onClose, onCreated }: {
  clientId: string; cases: Matter[]; initialCaseId?: string; onClose: () => void; onCreated: () => void;
}) {
  const [types, setTypes] = useState<ScenarioType[]>([]);
  const [caseId, setCaseId] = useState(initialCaseId || cases[0]?.id || '');
  const [eventType, setEventType] = useState('');
  const [values, setValues] = useState<Record<string, string>>({});
  const [files, setFiles] = useState<File[]>([]);
  const [uploads, setUploads] = useState<UploadState[]>([]);
  const [result, setResult] = useState<ScenarioResult | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [runPhase, setRunPhase] = useState<RunPhase>('idle');
  const [completedDocuments, setCompletedDocuments] = useState(0);
  const selected = useMemo(() => types.find((item) => item.event_type === eventType), [types, eventType]);

  useEffect(() => {
    void apiFetch<{ types: ScenarioType[] }>('/api/scenarios/types')
      .then(({ types: loaded }) => { setTypes(loaded); setEventType(loaded[0]?.event_type || ''); })
      .catch(() => setError('Unable to load scenario types.'));
  }, []);

  const updateUpload = (index: number, next: Partial<UploadState>) => setUploads((current) => current.map((item, position) => position === index ? { ...item, ...next } : item));
  const chooseFiles = (selectedFiles: FileList | null) => {
    const picked = Array.from(selectedFiles || []);
    setFiles(picked);
    setUploads(picked.map((file) => ({ name: file.name, status: 'selected' })));
  };

  async function waitForAbbyy(documentId: string, index: number): Promise<void> {
    for (let attempt = 0; attempt < 120; attempt += 1) {
      await new Promise((resolve) => window.setTimeout(resolve, 1500));
      const document = await apiFetch<{ processing_status: string; ocr_status: string; error_message?: string }>(`/api/documents/${documentId}/processing-status`);
      if (document.processing_status === 'processed' && document.ocr_status === 'processed') { updateUpload(index, { status: 'ready' }); return; }
      if (document.processing_status === 'failed' || document.ocr_status === 'failed') throw new Error(document.error_message || 'ABBYY could not extract this document.');
    }
    throw new Error('ABBYY extraction is taking too long. Please try again shortly.');
  }

  async function uploadSingleEvidence(file: File, index: number): Promise<string> {
    try {
      updateUpload(index, { status: 'uploading', error: undefined });
      const ticket = await apiFetch<{ document_id: string; upload_url: string }>('/api/documents/upload-url', jsonBody({
        client_id: clientId, case_id: caseId, file_name: file.name, mime_type: file.type || 'application/octet-stream', document_type: 'scenario_evidence',
      }));
      const body = new FormData(); body.append('', file, file.name); body.append('cacheControl', '3600');
      const upload = await fetch(ticket.upload_url, { method: 'PUT', headers: { 'x-upsert': 'false' }, body });
      if (!upload.ok) throw new Error(`Could not upload ${file.name}.`);
      updateUpload(index, { id: ticket.document_id, status: 'extracting' });
      await apiFetch(`/api/documents/${ticket.document_id}/process?use_abbyy=true&direct_context_only=true`, { method: 'POST' });
      await waitForAbbyy(ticket.document_id, index);
      setCompletedDocuments((count) => count + 1);
      return ticket.document_id;
    } catch (reason) {
      const message = reason instanceof Error ? reason.message : `Could not process ${file.name}.`;
      updateUpload(index, { status: 'failed', error: message });
      throw new Error(message);
    }
  }

  async function uploadEvidence(): Promise<string[]> {
    // Every document gets its own ABBYY transaction, so uploads and OCR can run together.
    return Promise.all(files.map((file, index) => uploadSingleEvidence(file, index)));
  }

  const submit = async (event: FormEvent) => {
    event.preventDefault(); if (!selected || !caseId) return;
    setLoading(true); setError(''); setCompletedDocuments(0); setRunPhase('preparing');
    try {
      // Let the focused progress view render before the parallel evidence jobs begin.
      await new Promise<void>((resolve) => window.setTimeout(resolve, 250));
      setRunPhase('extracting');
      const documentIds = await uploadEvidence();
      setRunPhase('analysing');
      const created = await apiFetch<{ result: ScenarioResult }>('/api/scenarios', jsonBody({
        client_id: clientId, case_id: caseId, name: `${selected.label} analysis`, event_type: selected.event_type, input_parameters: values, document_ids: documentIds,
      }));
      setRunPhase('finalising');
      setResult(created.result);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to run scenario analysis.');
    } finally { setLoading(false); setRunPhase('idle'); }
  };

  if (result) return <ScenarioResultModal result={result} onClose={onCreated} />;
  if (loading) return <ScenarioProgressModal phase={runPhase} completedDocuments={completedDocuments} totalDocuments={files.length} />;
  return <div className="modal-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget && !loading) onClose(); }}>
    <form className="modal scenario-modal" onSubmit={submit}>
      <div className="modal-heading"><div><p className="eyebrow">ABBYY DOCUMENT ANALYSIS</p><h2>Run a case review</h2><p className="muted">ABBYY extracts the uploaded evidence; AbbyAdv uses it with your case facts for this analysis.</p></div><button type="button" className="icon-button" onClick={onClose} disabled={loading}><X size={18}/></button></div>
      {!initialCaseId && <label className="scenario-field">Case<select required value={caseId} onChange={(event) => setCaseId(event.target.value)}><option value="">Select a case</option>{cases.map((matter) => <option key={matter.id} value={matter.id}>{matter.case_name}</option>)}</select></label>}
      <label className="scenario-field">Practice area<select required value={eventType} onChange={(event) => { setEventType(event.target.value); setValues({}); }}><option value="">Select practice area</option>{types.map((type) => <option key={type.event_type} value={type.event_type}>{type.label}</option>)}</select></label>
      {selected && <><p className="scenario-description">{selected.description}</p><div className="scenario-form-grid">{selected.fields.map((field) => <label className="scenario-field" key={field.name}>{field.label}{field.type === 'textarea' ? <textarea required={field.required} value={values[field.name] || ''} onChange={(event) => setValues((current) => ({ ...current, [field.name]: event.target.value }))}/> : field.type === 'select' ? <select required={field.required} value={values[field.name] || ''} onChange={(event) => setValues((current) => ({ ...current, [field.name]: event.target.value }))}><option value="">Select</option>{field.options?.map((option) => <option key={option}>{option}</option>)}</select> : <input type={field.type === 'date' ? 'date' : 'text'} required={field.required} value={values[field.name] || ''} onChange={(event) => setValues((current) => ({ ...current, [field.name]: event.target.value }))}/>}</label>)}</div></>}
      <label className="scenario-upload"><input type="file" multiple accept=".pdf,.png,.jpg,.jpeg,.tif,.tiff" onChange={(event) => chooseFiles(event.target.files)} /><UploadCloud size={21}/><span><b>Upload supporting evidence</b><small>PDF or image files. ABBYY OCR will extract the text before analysis.</small></span></label>
      {uploads.length > 0 && <div className="scenario-upload-list">{uploads.map((upload) => <div key={upload.name} className={`scenario-upload-item ${upload.status}`}><FileText size={15}/><span>{upload.name}</span>{upload.status === 'ready' ? <CheckCircle2 size={15}/> : upload.status === 'extracting' || upload.status === 'uploading' ? <LoaderCircle className="spin" size={15}/> : <small>{upload.status === 'selected' ? 'Ready to upload' : upload.error || upload.status}</small>}</div>)}</div>}
      <div className="scenario-safety">Direct document context only: scenario evidence is processed through ABBYY and is not sent to Qdrant.</div>
      {error && <div className="error-box">{error}</div>}
      <div className="modal-actions"><button type="button" className="secondary-button" onClick={onClose} disabled={loading}>Cancel</button><button className="primary-button" disabled={loading || !caseId || !selected}>Run analysis</button></div>
    </form>
  </div>;
}

function ScenarioProgressModal({ phase, completedDocuments, totalDocuments }: { phase: RunPhase; completedDocuments: number; totalDocuments: number }) {
  const percent = phase === 'preparing' ? 20 : phase === 'extracting' ? Math.min(65, 30 + Math.round((completedDocuments / Math.max(totalDocuments, 1)) * 35)) : phase === 'analysing' ? 84 : 96;
  const extractionComplete = phase === 'analysing' || phase === 'finalising';
  const analysisActive = phase === 'analysing' || phase === 'finalising';
  return <div className="modal-backdrop scenario-progress-backdrop"><section className="modal scenario-progress-modal" aria-live="polite">
    <p className="eyebrow">ABBYADV CASE INTELLIGENCE</p><h2>Building your document-grounded analysis</h2><p className="muted">Keep this window open while AbbyAdv reads the evidence and prepares the advocate review.</p>
    <div className="scenario-progress-meter"><div><span>{percent}%</span><b>{phase === 'extracting' ? 'ABBYY is processing the supporting evidence' : phase === 'analysing' ? 'Legal agents are analysing the record' : phase === 'finalising' ? 'Preparing the advocate work product' : 'Understanding the case context'}</b></div><i><em style={{ width: `${percent}%` }}/></i></div>
    <div className="scenario-progress-stages">
      <ProgressStage icon={<BrainCircuit size={18}/>} title="Case understanding" detail="0–25% · Combining form inputs and matter context." complete={phase !== 'preparing'} active={phase === 'preparing'} />
      <ProgressStage icon={<FileSearch size={18}/>} title="ABBYY evidence processing" detail={totalDocuments ? '25–65% · Reading and structuring the uploaded evidence.' : '25–65% · No additional evidence was attached.'} complete={extractionComplete} active={phase === 'extracting'} />
      <ProgressStage icon={<Scale size={18}/>} title="Legal analysis" detail="65–90% · Applying the selected practice-area strategy." complete={phase === 'finalising'} active={analysisActive} />
      <ProgressStage icon={<CheckCircle2 size={18}/>} title="Advocate work product" detail="90–100% · Organising findings, reliefs and next steps." complete={false} active={phase === 'finalising'} />
    </div>
    <p className="scenario-progress-note">Your evidence is processed through ABBYY for this analysis and is not added to Qdrant.</p>
  </section></div>;
}

function ProgressStage({ icon, title, detail, complete, active }: { icon: ReactNode; title: string; detail: string; complete: boolean; active: boolean }) {
  return <div className={`scenario-progress-stage ${complete ? 'complete' : ''} ${active ? 'active' : ''}`}><span>{complete ? <CheckCircle2 size={18}/> : active ? <LoaderCircle className="spin" size={18}/> : icon}</span><div><b>{title}</b><small>{detail}</small></div></div>;
}

export function ScenarioResultModal({ result, onClose }: { result: ScenarioResult; onClose: () => void }) {
  const list = (items: unknown): string[] => Array.isArray(items) ? items.filter((item): item is string => typeof item === 'string' && item.trim().length > 0) : [];
  const strengths = result.strength_analysis && typeof result.strength_analysis === 'object' ? result.strength_analysis : {};
  const timeline = Array.isArray(result.timeline_builder) ? result.timeline_builder.filter((item) => item && typeof item.event === 'string') : [];
  const factMatrix = Array.isArray(result.fact_evidence_matrix) ? result.fact_evidence_matrix.filter((row) => row && typeof row.fact === 'string') : [];
  const issues = Array.isArray(result.issue_analysis) ? result.issue_analysis.filter((row) => row && typeof row.issue === 'string') : [];
  const rebuttals = Array.isArray(result.opponent_rebuttal) ? result.opponent_rebuttal.filter((row) => row && typeof row.opponent_argument === 'string') : [];
  const checklist = Array.isArray(result.filing_checklist) ? result.filing_checklist.filter((row) => row && typeof row.item === 'string') : [];
  return <div className="modal-backdrop"><section className="modal scenario-modal"><div className="modal-heading"><div><p className="eyebrow">DOCUMENT-GROUNDED SCENARIO RESULT</p><h2>{result.summary || 'Scenario analysis prepared for advocate review.'}</h2><p className="muted">Grounded in the scenario form, case metadata, and ABBYY-extracted evidence.</p></div><button className="icon-button" onClick={onClose}><X size={18}/></button></div><ResultSection title="Factual findings from the record" items={list(result.factual_findings)}/><FactEvidenceMatrix rows={factMatrix}/><ResultSection title="Key issues and case position" items={list(result.key_issues)}/><IssueAnalysisList issues={issues}/><ResultSection title="Evidence assessment" items={list(result.evidence_assessment)}/><ResultSection title="Missing evidence to obtain" items={list(result.missing_evidence)}/><ResultSection title="Potential strengths" items={list(strengths.potential_strengths)}/><ResultSection title="Risks / uncertainty" items={list(strengths.risks_or_uncertainties)}/><ResultSection title="Opponent's possible arguments and response" items={list(result.opponent_arguments)}/><OpponentRebuttalList rebuttals={rebuttals}/><ResultSection title="Recommended reliefs" items={list(result.recommended_reliefs)}/><ResultSection title="Next steps" items={list(result.next_steps)}/>{timeline.length > 0 && <div className="scenario-timeline"><b>Timeline builder</b>{timeline.map((item, index) => <span key={`${item.event}-${index}`}>{item.event}: {item.date || 'Date to verify'}</span>)}</div>}<FilingChecklist items={checklist}/><div className="modal-actions"><button className="primary-button" onClick={onClose}>Done</button></div></section></div>;
}

function ResultSection({ title, items = [] }: { title: string; items?: string[] }) { if (!items.length) return null; return <section className="scenario-result-section"><b>{title}</b><ul>{items.map((item, index) => <li key={`${title}-${index}`}>{item}</li>)}</ul></section>; }

function FactEvidenceMatrix({ rows }: { rows: FactEvidenceRow[] }) {
  if (!rows.length) return null;
  return <section className="scenario-result-section"><b>Fact / evidence matrix</b><table className="scenario-matrix"><thead><tr><th>Fact</th><th>Source</th><th>Status</th></tr></thead><tbody>{rows.map((row, index) => <tr key={`fact-${index}`}><td>{row.fact}</td><td>{row.source}</td><td><span className={`status-pill ${row.status === 'proven' ? 'success' : ''}`}>{row.status || 'unknown'}</span></td></tr>)}</tbody></table></section>;
}

function IssueAnalysisList({ issues }: { issues: IssueAnalysis[] }) {
  if (!issues.length) return null;
  return <section className="scenario-result-section"><b>Issue-wise application of law</b><div className="scenario-issue-list">{issues.map((issue, index) => <div className="scenario-issue-card" key={`issue-${index}`}><b>{issue.issue}</b><span><em>Facts:</em> {issue.facts}</span><span><em>Applicable law:</em> {issue.applicable_law}</span><span><em>Application:</em> {issue.application}</span><span><em>Conclusion:</em> {issue.conclusion}</span></div>)}</div></section>;
}

function OpponentRebuttalList({ rebuttals }: { rebuttals: OpponentRebuttal[] }) {
  if (!rebuttals.length) return null;
  return <section className="scenario-result-section"><b>Opponent rebuttal</b><div className="scenario-rebuttal-list">{rebuttals.map((row, index) => <div className="scenario-rebuttal-card" key={`rebuttal-${index}`}><span className="scenario-rebuttal-them"><em>They will argue:</em> {row.opponent_argument}</span><span className="scenario-rebuttal-us"><em>Our rebuttal:</em> {row.our_rebuttal}</span><span className="scenario-rebuttal-support"><em>Supporting facts:</em> {row.supporting_facts}</span></div>)}</div></section>;
}

function FilingChecklist({ items }: { items: FilingChecklistItem[] }) {
  if (!items.length) return null;
  return <section className="scenario-result-section"><b>Filing checklist</b><ul className="scenario-checklist">{items.map((item, index) => <li key={`checklist-${index}`}><span className={`status-pill ${item.status === 'done' ? 'success' : ''}`}>{item.status || 'pending'}</span><span>{item.item}{item.note ? <small> — {item.note}</small> : null}</span></li>)}</ul></section>;
}
