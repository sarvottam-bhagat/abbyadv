import { useRef, useState } from 'react';
import { FileUp, LoaderCircle } from 'lucide-react';
import { apiFetch, jsonBody } from '../lib/api';

type Props = { clientId: string; caseId: string; onUploaded: () => void };

export function CaseDocumentUpload({ clientId, caseId, onUploaded }: Props) {
  const inputRef = useRef<HTMLInputElement>(null); const [uploading, setUploading] = useState(false); const [label, setLabel] = useState(''); const [error, setError] = useState('');
  async function upload(files: FileList | null) {
    const selected = Array.from(files || []); if (!selected.length) return;
    setUploading(true); setError('');
    try {
      for (const file of selected) {
        setLabel(file.name);
        const ticket = await apiFetch<{ document_id: string; upload_url: string }>('/api/documents/upload-url', jsonBody({ client_id: clientId, case_id: caseId, file_name: file.name, mime_type: file.type || 'application/octet-stream', document_type: 'supporting_document' }));
        const body = new FormData(); body.append('', file, file.name); body.append('cacheControl', '3600');
        const stored = await fetch(ticket.upload_url, { method: 'PUT', headers: { 'x-upsert': 'false' }, body });
        if (!stored.ok) throw new Error(`Could not upload ${file.name} (${stored.status}).`);
        await apiFetch(`/api/documents/${ticket.document_id}/process`, { method: 'POST' });
      }
      onUploaded();
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Unable to upload documents.'); }
    finally { setUploading(false); setLabel(''); if (inputRef.current) inputRef.current.value = ''; }
  }
  return <div className="case-upload-control"><input ref={inputRef} type="file" hidden multiple accept=".pdf,.docx,.txt,.md,.csv,.json,.png,.jpg,.jpeg,.tif,.tiff" onChange={(event) => void upload(event.target.files)}/><button type="button" className="secondary-button" onClick={() => inputRef.current?.click()} disabled={uploading}>{uploading ? <LoaderCircle className="spin" size={15}/> : <FileUp size={15}/>}{uploading ? `Uploading ${label}...` : 'Upload documents'}</button>{error && <small className="case-upload-error">{error}</small>}</div>;
}
