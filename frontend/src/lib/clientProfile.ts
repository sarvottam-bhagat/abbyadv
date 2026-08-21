export type ClientProfile = {
  id: string;
  full_name: string;
  email?: string | null;
  phone?: string | null;
  alternate_phone?: string | null;
  client_type: string;
  organization_name?: string | null;
  address?: string | null;
  city?: string | null;
  state?: string | null;
  postal_code?: string | null;
  country?: string | null;
  date_of_birth?: string | null;
  occupation?: string | null;
  id_type?: string | null;
  id_number?: string | null;
  preferred_contact_method?: string | null;
  referred_by?: string | null;
  status: string;
  risk_level: string;
  notes?: string | null;
  tags?: string[] | null;
  created_at?: string;
};

export type ClientForm = {
  full_name: string; email: string; phone: string; alternate_phone: string; client_type: string; organization_name: string;
  address: string; city: string; state: string; postal_code: string; country: string; date_of_birth: string;
  occupation: string; id_type: string; id_number: string; preferred_contact_method: string; referred_by: string;
  risk_level: string; notes: string;
};

export const emptyClientForm: ClientForm = {
  full_name: '', email: '', phone: '', alternate_phone: '', client_type: 'individual', organization_name: '',
  address: '', city: '', state: '', postal_code: '', country: 'IN', date_of_birth: '', occupation: '',
  id_type: '', id_number: '', preferred_contact_method: 'email', referred_by: '', risk_level: 'normal', notes: '',
};

export function clientFormFrom(profile: ClientProfile): ClientForm {
  return {
    full_name: profile.full_name,
    email: profile.email || '', phone: profile.phone || '', alternate_phone: profile.alternate_phone || '',
    client_type: profile.client_type || 'individual', organization_name: profile.organization_name || '',
    address: profile.address || '', city: profile.city || '', state: profile.state || '', postal_code: profile.postal_code || '',
    country: profile.country || 'IN', date_of_birth: profile.date_of_birth || '', occupation: profile.occupation || '',
    id_type: profile.id_type || '', id_number: profile.id_number || '', preferred_contact_method: profile.preferred_contact_method || 'email',
    referred_by: profile.referred_by || '', risk_level: profile.risk_level || 'normal', notes: profile.notes || '',
  };
}

export function clientPayload(form: ClientForm) {
  return {
    ...form,
    email: form.email || null,
    date_of_birth: form.date_of_birth || null,
    tags: [],
  };
}
