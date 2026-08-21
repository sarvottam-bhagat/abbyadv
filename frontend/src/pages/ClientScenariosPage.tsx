import { useEffect, useMemo, useState } from 'react';
import { ArrowLeft, Eye, Search, WandSparkles } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { apiFetch } from '../lib/api';
import type { ClientProfile } from '../lib/clientProfile';
import { ScenarioResult, ScenarioResultModal, ScenarioRunModal } from '../components/ScenarioRunModal';

type Matter = { id: string; case_name: string };
type Scenario = { id: string; case_id: string; name: string; event_type: string; status: string; result?: ScenarioResult | null };

export default function ClientScenariosPage() {
  const { clientId } = useParams();
  const [client, setClient] = useState<ClientProfile | null>(null); const [cases, setCases] = useState<Matter[]>([]); const [scenarios, setScenarios] = useState<Scenario[]>([]); const [query, setQuery] = useState(''); const [runOpen, setRunOpen] = useState(false); const [selected, setSelected] = useState<ScenarioResult | null>(null);
  const load = async () => {
    if (!clientId) return;
    const [profile, matters] = await Promise.all([apiFetch<ClientProfile>(`/api/clients/${clientId}`), apiFetch<Matter[]>(`/api/clients/${clientId}/cases`)]);
    const activity = await Promise.all(matters.map((matter) => apiFetch<Scenario[]>(`/api/cases/${matter.id}/scenarios`).catch(() => [])));
    setClient(profile); setCases(matters); setScenarios(activity.flat());
  };
  useEffect(() => { void load(); }, [clientId]);
  const visible = useMemo(() => scenarios.filter((scenario) => `${scenario.name} ${scenario.event_type}`.toLowerCase().includes(query.toLowerCase())), [query, scenarios]);
  const caseName = (caseId: string) => cases.find((matter) => matter.id === caseId)?.case_name || 'Case';
  return <div className="client-child-page"><Link to={`/clients/${clientId}`} className="back-link"><ArrowLeft size={15}/> Back to {client?.full_name || 'client'}</Link><div className="child-heading"><p className="eyebrow">CLIENT SCENARIOS</p><h1>Legal scenarios</h1><p className="muted">ABBYY document-grounded analysis across {client?.full_name || 'this client'}’s matters.</p></div><div className="clients-table-card"><div className="clients-toolbar"><div className="search-box"><Search size={17}/><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search scenarios..."/></div></div><div className="table-scroll"><table className="clients-table"><thead><tr><th>Scenario</th><th>Case</th><th>Analysis type</th><th>Status</th><th>Action</th></tr></thead><tbody>{visible.map((scenario) => <tr key={scenario.id} className={scenario.status === 'success' && scenario.result ? 'scenario-row-clickable' : undefined} onClick={() => scenario.status === 'success' && scenario.result && setSelected(scenario.result)}><td><div className="client-cell"><div className="case-symbol"><WandSparkles size={16}/></div><div><b>{scenario.name}</b><span>Document-grounded review</span></div></div></td><td className="table-muted">{caseName(scenario.case_id)}</td><td className="table-muted">{scenario.event_type.replaceAll('_', ' ')}</td><td><span className={`status-pill ${scenario.status === 'success' ? 'success' : ''}`}>{scenario.status}</span></td><td>{scenario.status === 'success' && scenario.result ? <button className="table-action scenario-view-action" title="View analysis" onClick={(event) => { event.stopPropagation(); setSelected(scenario.result!); }}><Eye size={17}/><span>View analysis</span></button> : <span className="table-muted">—</span>}</td></tr>)}</tbody></table></div>{!visible.length && <div className="empty-inline"><WandSparkles size={21}/><span>No scenarios yet</span><small>Upload evidence and run a structured review for one of this client’s cases.</small></div>}</div><button className="scenario-fab" onClick={() => setRunOpen(true)}><span>Run new scenario</span><WandSparkles size={20}/></button>{runOpen && clientId && <ScenarioRunModal clientId={clientId} cases={cases} onClose={() => setRunOpen(false)} onCreated={() => { setRunOpen(false); void load(); }}/>} {selected && <ScenarioResultModal result={selected} onClose={() => setSelected(null)}/>}</div>;
}
