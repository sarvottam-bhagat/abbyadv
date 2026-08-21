import { useEffect, useMemo, useState } from 'react';
import { Eye, Pencil, Plus, Search, Trash2, Users } from 'lucide-react';
import { Link } from 'react-router-dom';
import ClientFormModal from '../components/ClientFormModal';
import { apiFetch } from '../lib/api';
import { initials } from '../lib/format';
import type { ClientProfile } from '../lib/clientProfile';

export default function ClientsPage() {
  const [clients, setClients] = useState<ClientProfile[]>([]);
  const [query, setQuery] = useState('');
  const [status, setStatus] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<ClientProfile | null>(null);

  const load = async () => {
    setLoading(true);
    try { setClients(await apiFetch<ClientProfile[]>('/api/clients')); }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Unable to load clients'); }
    finally { setLoading(false); }
  };
  useEffect(() => { void load(); }, []);
  const visible = useMemo(() => clients.filter((client) => {
    const needle = query.toLowerCase().trim();
    const matchesSearch = !needle || [client.full_name, client.email, client.city, client.state].some((value) => (value || '').toLowerCase().includes(needle));
    return matchesSearch && (status === 'all' || client.status === status);
  }), [clients, query, status]);
  const openCreate = () => { setEditing(null); setModalOpen(true); };
  const openEdit = async (client: ClientProfile) => {
    try { setEditing(await apiFetch<ClientProfile>(`/api/clients/${client.id}`)); setModalOpen(true); }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Unable to load client profile'); }
  };
  const onSaved = (saved: ClientProfile) => setClients((current) => current.some((client) => client.id === saved.id) ? current.map((client) => client.id === saved.id ? saved : client) : [saved, ...current]);
  const archive = async (client: ClientProfile) => {
    if (!window.confirm(`Archive ${client.full_name}?`)) return;
    try { await apiFetch(`/api/clients/${client.id}`, { method: 'DELETE' }); setClients((current) => current.map((item) => item.id === client.id ? { ...item, status: 'archived' } : item)); }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Unable to archive client'); }
  };

  return <div className="clients-page"><div className="page-heading"><div><p className="eyebrow">YOUR PRACTICE</p><h1>Clients</h1><p className="muted">Manage client profiles and the matters connected to them.</p></div><button className="primary-button" onClick={openCreate}><Plus size={17} /> Add client</button></div><div className="clients-table-card"><div className="clients-toolbar"><div className="search-box"><Search size={17} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search by name, email, city, or state..." /></div><select className="status-filter" value={status} onChange={(event) => setStatus(event.target.value)}><option value="all">All statuses</option><option value="active">Active</option><option value="archived">Archived</option></select></div>{error && <div className="error-box">{error}</div>}{loading ? <div className="loading-card"><span className="loader" /> Loading clients</div> : visible.length === 0 ? <div className="empty-card"><div className="empty-icon"><Users size={25} /></div><h3>{query || status !== 'all' ? 'No matching clients' : 'No clients yet'}</h3><p>{query || status !== 'all' ? 'Try another search or status filter.' : 'Add your first client to start organizing matters.'}</p>{!query && status === 'all' && <button className="primary-button" onClick={openCreate}><Plus size={16} /> Add client</button>}</div> : <div className="table-scroll"><table className="clients-table"><thead><tr><th>Client</th><th>Location</th><th>Type</th><th>Status</th><th>Risk</th><th>Actions</th></tr></thead><tbody>{visible.map((client) => <tr key={client.id}><td><div className="client-cell"><div className="avatar client-avatar">{initials(client.full_name)}</div><div><b>{client.full_name}</b><span>{client.email || 'No email added'}</span></div></div></td><td className="client-location">{client.city || client.state || '—'}{client.city && client.state ? `, ${client.state}` : ''}</td><td><span className="table-muted">{client.client_type === 'company' ? 'Organization' : 'Individual'}</span></td><td><span className={`status-pill ${client.status === 'active' ? 'success' : ''}`}>{client.status}</span></td><td><span className={`risk-pill ${client.risk_level}`}>{client.risk_level || 'normal'}</span></td><td><div className="client-actions"><Link className="table-action" to={`/clients/${client.id}`} title="View client"><Eye size={16} /></Link><button className="table-action" title="Edit client" onClick={() => void openEdit(client)}><Pencil size={15} /></button><button className="table-action danger" title="Archive client" onClick={() => void archive(client)}><Trash2 size={15} /></button></div></td></tr>)}</tbody></table></div>}</div><div className="clients-footer">Showing {visible.length} of {clients.length} clients</div><ClientFormModal open={modalOpen} client={editing} onClose={() => setModalOpen(false)} onSaved={onSaved} /></div>;
}
