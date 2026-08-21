import { useEffect, useState } from 'react';
import { ArrowLeft, ArrowRight, BriefcaseBusiness, Pencil, Plus, WandSparkles } from 'lucide-react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import CaseCreateModal from '../components/CaseCreateModal';
import ClientFormModal from '../components/ClientFormModal';
import { apiFetch } from '../lib/api';
import { initials } from '../lib/format';
import type { ClientProfile } from '../lib/clientProfile';

type Matter = { id: string; case_name: string; matter_type: string };
type Scenario = { id: string };

export default function ClientDetailPage() {
  const { clientId } = useParams(); const navigate = useNavigate();
  const [client, setClient] = useState<ClientProfile | null>(null); const [caseCount, setCaseCount] = useState(0); const [scenarioCount, setScenarioCount] = useState(0);
  const [loading, setLoading] = useState(true); const [error, setError] = useState(''); const [caseModal, setCaseModal] = useState(false); const [editModal, setEditModal] = useState(false);
  useEffect(() => { if (!clientId) return; void (async () => { setLoading(true); setError(''); try { const profile = await apiFetch<ClientProfile>(`/api/clients/${clientId}`); const matters = await apiFetch<Matter[]>(`/api/clients/${clientId}/cases`); const scenarios = await Promise.all(matters.map((matter) => apiFetch<Scenario[]>(`/api/cases/${matter.id}/scenarios`).catch(() => []))); setClient(profile); setCaseCount(matters.length); setScenarioCount(scenarios.flat().length); } catch (reason) { setError(reason instanceof Error ? reason.message : 'Unable to load client'); } finally { setLoading(false); } })(); }, [clientId]);
  if (loading) return <div className="loading-card"><span className="loader" /> Loading client</div>;
  if (!client || !clientId) return <div className="empty-card"><h3>Client not found</h3><p>{error || 'This client is unavailable.'}</p><Link className="primary-button" to="/clients">Back to clients</Link></div>;
  return <div className="client-detail-page"><Link to="/clients" className="back-link"><ArrowLeft size={15} /> Back to clients</Link>{error && <div className="error-box">{error}</div>}<section className="client-detail-header"><div className="client-detail-title"><div className="avatar client-avatar detail-avatar">{initials(client.full_name)}</div><div><p className="eyebrow">CLIENT PROFILE</p><h1>{client.full_name}</h1><div className="client-header-meta"><span>{client.email || 'No email added'}</span>{client.phone && <><i /> <span>{client.phone}</span></>}{client.city || client.state ? <><i /> <span>{[client.city, client.state].filter(Boolean).join(', ')}</span></> : null}<i /><span className="status-pill success">{client.status}</span></div></div></div><div className="client-header-actions"><button className="secondary-button" onClick={() => setEditModal(true)}><Pencil size={15} /> Edit client</button><button className="primary-button" onClick={() => setCaseModal(true)}><Plus size={17} /> New case</button></div></section><section className="client-summary-grid"><Link className="client-summary-card" to={`/clients/${client.id}/cases`}><div><div className="summary-icon"><BriefcaseBusiness size={22} /></div><h2>Cases</h2><p>Manage legal matters, parties and case progress.</p><span>View cases <ArrowRight size={15} /></span></div><strong>{caseCount}</strong></Link><Link className="client-summary-card" to={`/clients/${client.id}/scenarios`}><div><div className="summary-icon"><WandSparkles size={22} /></div><h2>Legal scenarios</h2><p>Run structured analysis grounded in each matter.</p><span>View scenarios <ArrowRight size={15} /></span></div><strong>{scenarioCount}</strong></Link></section><ClientFormModal open={editModal} client={client} onClose={() => setEditModal(false)} onSaved={setClient} /><CaseCreateModal open={caseModal} clientId={clientId} defaultState={client.state} onClose={() => setCaseModal(false)} onCreated={(matter) => navigate(`/cases/${matter.id}`)} /></div>;
}
