import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { Toaster } from 'sonner';
import { AuthProvider } from './auth/AuthProvider';
import ProtectedRoute from './components/ProtectedRoute';
import AppShell from './components/AppShell';
import AuthPage from './pages/AuthPage';
import DashboardPage from './pages/DashboardPage';
import ClientsPage from './pages/ClientsPage';
import ClientDetailPage from './pages/ClientDetailPage';
import ClientCasesPage from './pages/ClientCasesPage';
import ClientScenariosPage from './pages/ClientScenariosPage';
import CaseWorkspacePage from './pages/CaseWorkspacePage';
import ChatPage from './pages/ChatPage';
import KnowledgeBasePage from './pages/KnowledgeBasePage';
import GenericPage from './pages/GenericPage';
import DraftsPage from './pages/DraftsPage';
import './index.css';
import './attachment.css';

export default function App() {
  return <AuthProvider><BrowserRouter><Routes><Route path="/auth" element={<AuthPage />} /><Route element={<ProtectedRoute />}><Route element={<AppShell />}><Route index element={<DashboardPage />} /><Route path="clients" element={<ClientsPage />} /><Route path="clients/:clientId" element={<ClientDetailPage />} /><Route path="clients/:clientId/cases" element={<ClientCasesPage />} /><Route path="clients/:clientId/scenarios" element={<ClientScenariosPage />} /><Route path="cases/:caseId" element={<CaseWorkspacePage />} /><Route path="chat" element={<ChatPage />} /><Route path="knowledge-base" element={<KnowledgeBasePage />} /><Route path="scenarios" element={<GenericPage title="Legal scenarios" kicker="LEGAL ENGINE" description="Run structured analysis against a matter." />} /><Route path="drafts" element={<DraftsPage />} /><Route path="research" element={<GenericPage title="Research" kicker="LEGAL RESEARCH" description="Keep research notes and sources connected to your matters." />} /><Route path="reports" element={<GenericPage title="Reports" kicker="REPORTING" description="Generate clear matter summaries for your practice." />} /><Route path="profile" element={<GenericPage title="Settings" kicker="YOUR WORKSPACE" description="Manage your profile and workspace preferences." />} /></Route></Route></Routes></BrowserRouter><Toaster position="bottom-right" /></AuthProvider>;
}
