import { useState } from 'react';
import type { FormEvent } from 'react';
import { FileText, UploadCloud, X } from 'lucide-react';
import { apiFetch, jsonBody } from '../lib/api';

type Matter = { id: string; case_name: string };
type UploadTicket = { document_id: string; upload_url: string };
type Props = { open: boolean; clientId: string; defaultState?: string | null; onClose: () => void; onCreated: (matter: Matter) => void };

export default function CaseCreateModal({ open, clientId, defaultState, onClose, onCreated }: Props) {
  const [caseName, setCaseName] = useState(''); const [matterType, setMatterType] = useState('civil'); const [clientRole, setClientRole] = useState('petitioner');
  const [oppositeParty, setOppositeParty] = useState(''); const [state, setState] = useState(defaultState || ''); const [courtReference, setCourtReference] = useState(''); const [courtName, setCourtName] = useState('');
  const [stage, setStage] = useState('initial_consultation'); const [facts, setFacts] = useState(''); const [relief, setRelief] = useState(''); const [nextHearing, setNextHearing] = useState(''); const [limitationDate, setLimitationDate] = useState('');
  const [files, setFiles] = useState<File[]>([]); const [saving, setSaving] = useState(false); const [uploadingFile, setUploadingFile] = useState(''); const [error, setError] = useState('');
  if (!open) return null;

  const addFiles = (selectedFiles: FileList | null) => {
    const selected = Array.from(selectedFiles || []);
    setFiles((current) => [...current, ...selected.filter((file) => !current.some((existing) => existing.name === file.name && existing.size === file.size))]);
  };
  const removeFile = (file: File) => setFiles((current) => current.filter((item) => !(item.name === file.name && item.size === file.size)));

  async function submit(event: FormEvent) {
    event.preventDefault(); setSaving(true); setError('');
    try {
      const matter = await apiFetch<Matter>(`/api/clients/${clientId}/cases`, jsonBody({ case_name: caseName, matter_type: matterType, client_role: clientRole, opposite_party_name: oppositeParty || null, state: state || null, jurisdiction: state || null, court_name: courtName || null, case_number: courtReference || null, current_stage: stage, facts_summary: facts, relief_sought: relief || null, next_hearing_date: nextHearing || null, limitation_date: limitationDate || null }));
      for (const file of files) {
        try {
          setUploadingFile(file.name);
          const ticket = await apiFetch<UploadTicket>('/api/documents/upload-url', jsonBody({ client_id: clientId, case_id: matter.id, file_name: file.name, mime_type: file.type || 'application/octet-stream', document_type: 'supporting_document' }));
          const body = new FormData(); body.append('', file, file.name); body.append('cacheControl', '3600');
          const upload = await fetch(ticket.upload_url, { method: 'PUT', headers: { 'x-upsert': 'false' }, body });
          if (!upload.ok) throw new Error(`storage upload returned ${upload.status}`);
          await apiFetch(`/api/documents/${ticket.document_id}/process`, { method: 'POST' });
        } catch (uploadError) {
          const detail = uploadError instanceof Error ? uploadError.message : 'unknown upload error';
          throw new Error(`Could not upload ${file.name}: ${detail}`);
        }
      }
      onCreated(matter);
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Could not create case'); }
    finally { setSaving(false); setUploadingFile(''); }
  }

  return <div className="modal-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget && !saving) onClose(); }}><form className="modal case-create-modal" onSubmit={submit}>
    <div className="modal-heading"><div><p className="eyebrow">NEW MATTER</p><h2>Create a case</h2><p className="muted">Add the minimum context AbbyAdv needs for case-aware chat.</p></div><button type="button" className="icon-button" onClick={onClose} disabled={saving}><X size={18}/></button></div>
    <div className="case-form-section"><h3>Matter basics</h3><div className="case-form-grid"><label>Case / matter name *<input required value={caseName} onChange={(event) => setCaseName(event.target.value)} placeholder="e.g. Sharma v. Mehta"/></label><label>Matter type *<select value={matterType} onChange={(event) => setMatterType(event.target.value)}><option value="civil">Civil</option><option value="property">Property</option><option value="criminal">Criminal</option><option value="family">Family</option><option value="commercial">Commercial</option><option value="employment">Employment</option><option value="consumer">Consumer</option></select></label><label>Client role *<select value={clientRole} onChange={(event) => setClientRole(event.target.value)}><option value="petitioner">Petitioner / plaintiff</option><option value="respondent">Respondent / defendant</option><option value="complainant">Complainant</option><option value="accused">Accused</option><option value="appellant">Appellant</option><option value="other">Other</option></select></label><label>Current stage *<select value={stage} onChange={(event) => setStage(event.target.value)}><option value="initial_consultation">Initial consultation</option><option value="pre_litigation">Pre-litigation</option><option value="drafting">Drafting</option><option value="filed">Filed</option><option value="pending">Pending</option></select></label></div></div>
    <div className="case-form-section"><h3>Chat context</h3><div className="case-form-grid"><label>Opposite party<input value={oppositeParty} onChange={(event) => setOppositeParty(event.target.value)} placeholder="Person, company, or authority"/></label><label>State / jurisdiction<input value={state} onChange={(event) => setState(event.target.value)} placeholder="e.g. Karnataka"/></label><label>Court / FIR / CNR reference<input value={courtReference} onChange={(event) => setCourtReference(event.target.value)} placeholder="If already available"/></label><label>Court name<input value={courtName} onChange={(event) => setCourtName(event.target.value)} placeholder="Optional"/></label></div><label className="case-textarea">Brief facts *<textarea required rows={4} value={facts} onChange={(event) => setFacts(event.target.value)} placeholder="What happened, key facts, and the client’s immediate concern."/></label><label className="case-textarea">Relief or outcome sought<textarea rows={3} value={relief} onChange={(event) => setRelief(event.target.value)} placeholder="What does the client want to achieve?"/></label></div>
    <div className="case-form-section"><h3>Dates and documents</h3><div className="case-form-grid"><label>Next hearing<input type="date" value={nextHearing} onChange={(event) => setNextHearing(event.target.value)}/></label><label>Limitation date<input type="date" value={limitationDate} onChange={(event) => setLimitationDate(event.target.value)}/></label></div><label className="drop-label"><span>Supporting documents <small>(optional)</small></span><div className="mini-drop"><UploadCloud size={18}/><span>{files.length ? `${files.length} file(s) selected` : 'Attach PDFs, images, orders, notices, FIRs, contracts, or evidence'}</span><input type="file" multiple accept=".pdf,.docx,.txt,.md,.csv,.json,.png,.jpg,.jpeg,.tif,.tiff" onChange={(event) => { addFiles(event.target.files); event.currentTarget.value = ''; }}/></div></label>{files.length > 0 && <div className="selected-files">{files.map((file) => <button type="button" onClick={() => removeFile(file)} key={`${file.name}-${file.size}`} title="Remove file"><FileText size={13}/>{file.name}<X size={12}/></button>)}</div>}</div>
    {error && <div className="error-box">{error}</div>}<div className="modal-actions"><button type="button" className="secondary-button" onClick={onClose} disabled={saving}>Cancel</button><button className="primary-button" disabled={saving}>{saving ? (uploadingFile ? `Uploading ${uploadingFile}...` : 'Creating...') : 'Create case'}</button></div>
  </form></div>;
}
