import { useEffect, useMemo, useState } from 'react';
import { CheckCircle2, FileText, LibraryBig, Search, TriangleAlert } from 'lucide-react';
import { apiFetch } from '../lib/api';

type KnowledgeDocument = { id: string; file_name: string; document_type: string | null; client_name: string; case_name: string; processing_status: string; embedding_status: string; error_message: string | null; created_at: string };

function documentState(document: KnowledgeDocument) {
  if (document.processing_status === 'failed') return { label: 'Needs attention', className: 'failed', icon: TriangleAlert };
  if (document.processing_status === 'processed' && document.embedding_status === 'processed') return { label: 'Ready for chat', className: 'ready', icon: CheckCircle2 };
  return { label: 'Processing', className: 'processing', icon: FileText };
}

export default function KnowledgeBasePage() {
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]); const [query, setQuery] = useState(''); const [loading, setLoading] = useState(true);
  async function load() { try { setDocuments(await apiFetch<KnowledgeDocument[]>('/api/knowledge-base/documents')); } finally { setLoading(false); } }
  useEffect(() => { void load(); }, []);
  useEffect(() => { if (!documents.some((document) => document.processing_status === 'processing')) return; const timer = window.setInterval(() => { void Promise.all(documents.filter((document) => document.processing_status === 'processing').map((document) => apiFetch(`/api/documents/${document.id}/processing-status`).catch(() => null))).then(load); }, 5000); return () => window.clearInterval(timer); }, [documents]);
  const filtered = useMemo(() => documents.filter((document) => `${document.file_name} ${document.client_name} ${document.case_name}`.toLowerCase().includes(query.toLowerCase())), [documents, query]); const ready = documents.filter((document) => documentState(document).className === 'ready').length;
  return <section className="knowledge-page"><div className="page-heading"><div><p className="eyebrow">CASE KNOWLEDGE</p><h1>Knowledge base</h1><p className="muted">Every case document, linked to its client and prepared for case-aware chat.</p></div><div className="knowledge-ready"><CheckCircle2 size={16}/><b>{ready}</b> ready for chat</div></div><div className="knowledge-card"><div className="clients-toolbar"><div className="search-box"><Search size={17}/><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search documents, clients, or cases..." /></div></div>{loading ? <div className="loading-card"><span className="loader"/>Loading your knowledge base...</div> : filtered.length === 0 ? <div className="empty-card compact"><div className="empty-icon indigo"><LibraryBig size={23}/></div><h3>No case documents yet</h3><p>Upload supporting documents while creating a case. They will appear here and become available in chat after processing.</p></div> : <div className="table-scroll"><table className="knowledge-table"><thead><tr><th>Document</th><th>Client</th><th>Case</th><th>Type</th><th>Availability</th></tr></thead><tbody>{filtered.map((document) => { const state = documentState(document); const Icon = state.icon; return <tr key={document.id}><td><div className="knowledge-file"><div className="activity-icon"><FileText size={16}/></div><div><b>{document.file_name}</b><span>{new Date(document.created_at).toLocaleDateString()}</span></div></div></td><td>{document.client_name}</td><td>{document.case_name}</td><td><span className="risk-pill">{document.document_type?.replaceAll('_', ' ') || 'document'}</span></td><td><span className={`knowledge-status ${state.className}`}><Icon size={14}/>{state.label}</span>{document.error_message && <small className="knowledge-error">{document.error_message}</small>}</td></tr>; })}</tbody></table></div>}</div></section>;
}
