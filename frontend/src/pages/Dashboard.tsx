import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";

type Application = { id: number; application_type: string; status: string; created_at: string };
type Document = { id: number; document_type: string; filename: string; status: string };

function Dashboard() {
  const navigate = useNavigate();
  const [applications, setApplications] = useState<Application[]>([]);
  const [selected, setSelected] = useState<Application | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [applicationType, setApplicationType] = useState("");
  const [documentType, setDocumentType] = useState("identity");
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);

  async function loadApplications() {
    const response = await api.get<Application[]>("/applications");
    setApplications(response.data);
  }

  async function selectApplication(application: Application) {
    setSelected(application);
    const response = await api.get<Document[]>(`/applications/${application.id}/documents`);
    setDocuments(response.data);
  }

  useEffect(() => {
    let active = true;
    api.get<Application[]>("/applications")
      .then((response) => {
        if (active) setApplications(response.data);
      })
      .catch(() => {
        if (active) setMessage("Unable to load applications.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  async function createApplication(event: FormEvent) {
    event.preventDefault();
    try {
      await api.post("/applications", { application_type: applicationType });
      setApplicationType("");
      await loadApplications();
      setMessage("Application created.");
    } catch {
      setMessage("Unable to create application.");
    }
  }

  async function updateApplication(event: FormEvent) {
    event.preventDefault();
    if (!selected) return;
    try {
      const response = await api.put<Application>(`/applications/${selected.id}`, { application_type: selected.application_type });
      setSelected(response.data);
      await loadApplications();
      setMessage("Application updated.");
    } catch {
      setMessage("Unable to update application.");
    }
  }

  async function uploadDocument(event: FormEvent) {
    event.preventDefault();
    if (!selected || !file) {
      setMessage("Choose a file before uploading.");
      return;
    }
    const formData = new FormData();
    formData.append("document_type", documentType);
    formData.append("file", file);
    try {
      await api.post(`/applications/${selected.id}/documents`, formData);
      setFile(null);
      const input = document.getElementById("document-file") as HTMLInputElement | null;
      if (input) input.value = "";
      await selectApplication(selected);
      setMessage("Document uploaded.");
    } catch {
      setMessage("Upload failed. Use a PDF, PNG, or JPEG smaller than 10 MB.");
    }
  }

  function logout() {
    localStorage.removeItem("access_token");
    navigate("/");
  }

  return (
    <main className="page">
      <header className="topbar"><h1>Dashboard</h1><button onClick={logout}>Log out</button></header>
      <form className="card form" onSubmit={createApplication}>
        <h2>New application</h2>
        <label>Application type<input value={applicationType} onChange={(event) => setApplicationType(event.target.value)} placeholder="e.g. Student application" required /></label>
        <button type="submit">Create application</button>
      </form>
      {message && <p className="message">{message}</p>}
      <section className="card">
        <h2>Your applications</h2>
        {loading ? <p>Loading...</p> : applications.length === 0 ? <p>No applications yet.</p> : (
          <ul className="application-list">{applications.map((application) => (
            <li key={application.id}><button className="link-button" onClick={() => selectApplication(application)}>#{application.id} {application.application_type}</button><span>{application.status}</span></li>
          ))}</ul>
        )}
      </section>
      {selected && (
        <section className="card">
          <h2>Application #{selected.id}</h2>
          <form className="form inline-form" onSubmit={updateApplication}>
            <label>Application type<input value={selected.application_type} onChange={(event) => setSelected({ ...selected, application_type: event.target.value })} required /></label>
            <button type="submit">Update</button>
          </form>
          <form className="form" onSubmit={uploadDocument}>
            <h3>Upload document</h3>
            <label>Document type<select value={documentType} onChange={(event) => setDocumentType(event.target.value)}><option value="identity">Identity</option><option value="address">Address</option><option value="transcript">Transcript</option><option value="other">Other</option></select></label>
            <input id="document-file" type="file" accept=".pdf,.png,.jpg,.jpeg" onChange={(event) => setFile(event.target.files?.[0] ?? null)} required />
            <button type="submit">Upload</button>
          </form>
          <h3>Uploaded documents</h3>
          {documents.length === 0 ? <p>No documents uploaded.</p> : <ul>{documents.map((document) => <li key={document.id}>{document.document_type}: {document.filename} ({document.status})</li>)}</ul>}
        </section>
      )}
    </main>
  );
}

export default Dashboard;
