import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { supabase, type Session } from '../lib/supabase';

type AuthContextValue = { session: Session | null; loading: boolean; demo: boolean; signOut: () => Promise<void> };
const AuthContext = createContext<AuthContextValue>({ session: null, loading: true, demo: false, signOut: async () => undefined });

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(Boolean(supabase));
  useEffect(() => {
    if (!supabase) return;
    supabase.auth.getSession().then(({ data }) => { setSession(data.session); setLoading(false); });
    const { data } = supabase.auth.onAuthStateChange((_event, next) => setSession(next));
    return () => data.subscription.unsubscribe();
  }, []);
  const value = useMemo(() => ({ session, loading, demo: !supabase, signOut: async () => { await supabase?.auth.signOut(); setSession(null); } }), [loading, session]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
export const useAuth = () => useContext(AuthContext);
