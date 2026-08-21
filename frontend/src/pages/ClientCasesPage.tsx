import { useEffect, useMemo, useState } from 'react';
import { ArrowLeft, Eye, Gavel, Search } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { apiFetch } from '../lib/api';
import type { ClientProfile } from '../lib/clientProfile';

type Matter = { id: string; case_name: string; matter_type: string; case_status: string; current_stage?: string | null; court_name?: string | null; case_number?: string | null };

export default function ClientCasesPage() {
  const { clientId } = useParams(); const [client, setClient] = useState<ClientProfile | null>(null); const [cases, setCases] = useState<Matter[]>([]); const [query, setQuery] = useState('');
  useEffect(() => { if (!clientId) return; void Promise.all([apiFetch<ClientProfile>(`/api/clients/${clientId}`), apiFetch<Matter[]>(`/api/clients/${clientId}/cases`)]).then(([profile, matters]) => { setClient(profile); setCases(matters); }); }, [clientId]);
  const visible = useMemo(() => cases.filter((matter) => `${matter.case_name} ${matter.matter_type} ${matter.case_number || ''}`.toLowerCase().includes(query.toLowerCase())), [cases, query]);
  return <div className="client-child-page"><Link to={`/clients/${clientId}`} className="back-link"><ArrowLeft size={15} /> Back to {client?.full_name || 'client'}</Link><div className="child-heading"><p className="eyebrow">CLIENT CASES</p><h1>Cases</h1><p className="muted">Manage matters for {client?.full_name || 'this client'}.</p></div><div className="clients-table-card"><div className="clients-toolbar"><div className="search-box"><Search size={17} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search cases by name, type, or number..." /></div></div><div className="table-scroll"><table className="clients-table"><thead><tr><th>Case</th><th>Matter type</th><th>Case number</th><th>Stage</th><th>Status</th><th>Actions</th></tr></thead><tbody>{visible.map((matter) => <tr key={matter.id}><td><div className="client-cell"><div className="case-symbol"><Gavel size={16} /></div><div><b>{matter.case_name}</b><span>{matter.court_name || 'Court not added'}</span></div></div></td><td className="table-muted">{matter.matter_type}</td><td className="table-muted">{matter.case_number || '—'}</td><td className="table-muted">{matter.current_stage || 'Initial review'}</td><td><span className={`status-pill ${matter.case_status === 'active' ? 'success' : ''}`}>{matter.case_status}</span></td><td><Link className="table-action" title="Open case" to={`/cases/${matter.id}`}><Eye size={16} /></Link></td></tr>)}</tbody></table></div>{!visible.length && <div className="empty-inline"><Gavel size={21} /><span>No cases yet</span><small>Create a case from the client page.</small></div>}</div></div>;
}
