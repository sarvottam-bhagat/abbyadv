import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { Bell, CalendarDays, ChevronRight, FileText, LayoutDashboard, LibraryBig, LogOut, Menu, MessageSquare, Moon, Search, Settings2, ShieldCheck, Sun, Users, X } from 'lucide-react';
import { useState } from 'react';
import { useAuth } from '../auth/AuthProvider';
import { initials } from '../lib/format';

const nav = [{to:'/', label:'Overview', icon:LayoutDashboard}, {to:'/clients', label:'Clients', icon:Users}, {to:'/chat', label:'AI workspace', icon:MessageSquare}, {to:'/scenarios', label:'Legal scenarios', icon:ShieldCheck}, {to:'/drafts', label:'Drafts', icon:FileText}];
export default function AppShell() {
  const [open, setOpen] = useState(false); const [dark, setDark] = useState(false); const { signOut } = useAuth(); const location = useLocation();
  return <div className={`app-shell ${dark ? 'dark' : ''}`}>
    <aside className={`sidebar ${open ? 'is-open' : ''}`}>
      <div className="brand"><div className="brand-mark">A</div><div><strong>AbbyAdv</strong><small>Legal workspace</small></div><button className="mobile-close" onClick={() => setOpen(false)}><X size={18}/></button></div>
      <div className="workspace-switch"><div className="avatar">AA</div><div><b>Advocate workspace</b><span>Personal practice</span></div><ChevronRight size={15}/></div>
      <nav className="nav-list">{nav.map(({to,label,icon:Icon}) => <NavLink key={to} to={to} onClick={() => setOpen(false)} className={({isActive}) => isActive ? 'nav-item active' : 'nav-item'}><Icon size={18}/><span>{label}</span></NavLink>)}</nav>
      <div className="nav-section">WORKSPACE</div><nav className="nav-list"><NavLink to="/knowledge-base" className="nav-item"><LibraryBig size={18}/><span>Knowledge base</span></NavLink><NavLink to="/research" className="nav-item"><Search size={18}/><span>Research</span></NavLink><NavLink to="/reports" className="nav-item"><CalendarDays size={18}/><span>Reports</span></NavLink></nav>
      <div className="sidebar-bottom"><button className="nav-item" onClick={() => setDark(!dark)}>{dark ? <Sun size={18}/> : <Moon size={18}/>}<span>{dark ? 'Light mode' : 'Dark mode'}</span></button><NavLink to="/profile" className="nav-item"><Settings2 size={18}/><span>Settings</span></NavLink><button className="profile-row" onClick={signOut}><div className="avatar small">AA</div><div><b>Advocate</b><span>Profile & sign out</span></div><LogOut size={16}/></button></div>
    </aside>
    {open && <div className="mobile-overlay" onClick={() => setOpen(false)} />}
    <main className="main-area"><header className="topbar"><button className="menu-button" onClick={() => setOpen(true)}><Menu size={21}/></button><div className="breadcrumbs"><span>AbbyAdv</span>{location.pathname !== '/' && <><ChevronRight size={14}/><b>{location.pathname.split('/')[1] || 'overview'}</b></>}</div><div className="top-actions"><button className="icon-button"><Bell size={18}/><i /></button><button className="avatar top-avatar">AA</button></div></header><div className="page-content"><Outlet /></div></main>
  </div>;
}
