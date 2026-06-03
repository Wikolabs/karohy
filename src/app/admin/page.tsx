"use client";

import { useState, useEffect, useRef, FormEvent, ChangeEvent, CSSProperties, ReactNode } from "react";
import { useRouter } from "next/navigation";

const primary = "#dc2626";

interface Prestataire {
  id: string;
  name: string;
  specialty: string;
  description: string;
  services: string[];
  city: string;
  country: string;
  hourly_rate: number;
  phone: string;
  email: string;
  rating: number;
  image_base64: string;
  created_at: string;
}

const emptyForm = {
  name: "",
  specialty: "",
  description: "",
  services: "",
  city: "",
  country: "",
  hourly_rate: "",
  phone: "",
  email: "",
};

export default function AdminPage() {
  const router = useRouter();
  const [prestataires, setPrestataires] = useState<Prestataire[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState("");
  const [form, setForm] = useState(emptyForm);

  useEffect(() => {
    fetchPrestataires();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function fetchPrestataires() {
    try {
      const res = await fetch("/api/prestataires");
      if (res.status === 401 || res.status === 403) {
        router.push("/login?redirect=/admin");
        return;
      }
      const data = await res.json();
      setPrestataires(Array.isArray(data) ? data : []);
    } catch {
      setError("Impossible de charger les prestataires");
    } finally {
      setLoading(false);
    }
  }

  function handleImageChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setSubmitting(true);

    const fd = new FormData();
    fd.append("name", form.name);
    fd.append("specialty", form.specialty);
    fd.append("description", form.description);
    fd.append("services", form.services);
    fd.append("city", form.city);
    fd.append("country", form.country);
    fd.append("hourly_rate", form.hourly_rate || "0");
    fd.append("phone", form.phone);
    fd.append("email", form.email);
    if (imageFile) fd.append("image", imageFile);

    try {
      const res = await fetch("/api/prestataires", { method: "POST", body: fd });
      if (!res.ok) {
        const d = await res.json().catch(() => ({}));
        throw new Error(d.detail || `Erreur ${res.status}`);
      }
      setSuccess("Prestataire ajouté !");
      setForm(emptyForm);
      setImageFile(null);
      setImagePreview("");
      if (fileRef.current) fileRef.current.value = "";
      fetchPrestataires();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur inconnue");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleLogout() {
    await fetch("/api/auth/logout", { method: "POST" });
    router.push("/");
  }

  return (
    <main style={{ minHeight: "100vh", background: "#fef2f2", fontFamily: "system-ui, sans-serif" }}>
      {/* Header */}
      <nav style={{ background: "#fff", borderBottom: "1px solid #fecaca", position: "sticky", top: 0, zIndex: 50 }}>
        <div style={{ maxWidth: 1100, margin: "0 auto", padding: "0 24px", height: 64, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <a href="/" style={{ display: "flex", alignItems: "center", gap: 6, textDecoration: "none" }}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/karohy-logo.png" alt="Karohy" style={{ height: 52, width: "auto", objectFit: "contain" }} />
            <span style={{ fontWeight: 800, fontSize: 15, color: "#999" }}>.mg</span>
          </a>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <span style={{ fontSize: 13, color: "#888", fontWeight: 600 }}>Administration</span>
            <button onClick={handleLogout} style={{ fontSize: 13, fontWeight: 600, color: primary, background: "none", border: "1px solid #fecaca", borderRadius: 6, padding: "6px 14px", cursor: "pointer" }}>
              Déconnexion
            </button>
          </div>
        </div>
      </nav>

      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "40px 24px" }}>
        <h1 style={{ fontWeight: 800, fontSize: 26, color: "#111", marginBottom: 4 }}>Gestion des prestataires</h1>
        <p style={{ color: "#888", marginBottom: 40, fontSize: 15 }}>
          {loading ? "Chargement…" : `${prestataires.length} prestataire${prestataires.length !== 1 ? "s" : ""} dans la base`}
        </p>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1.5fr", gap: 32, alignItems: "start" }}>
          {/* ADD FORM */}
          <div style={{ background: "#fff", borderRadius: 16, padding: "32px 28px", border: "1px solid #fecaca", boxShadow: "0 2px 16px rgba(220,38,38,0.06)" }}>
            <h2 style={{ fontWeight: 700, fontSize: 18, color: "#111", marginBottom: 24 }}>Ajouter un prestataire</h2>
            <form onSubmit={handleSubmit}>
              <Field label="Nom *">
                <input type="text" value={form.name} onChange={(e) => setForm(f => ({ ...f, name: e.target.value }))} required placeholder="Jean Dupont" style={inputStyle} />
              </Field>
              <Field label="Spécialité *">
                <input type="text" value={form.specialty} onChange={(e) => setForm(f => ({ ...f, specialty: e.target.value }))} required placeholder="Développeur React Senior" style={inputStyle} />
              </Field>
              <Field label="Description *">
                <textarea value={form.description} onChange={(e) => setForm(f => ({ ...f, description: e.target.value }))} required rows={3} placeholder="Présentation, expériences, secteurs…" style={{ ...inputStyle, resize: "vertical" as const }} />
              </Field>
              <Field label="Services (séparés par virgule)">
                <input type="text" value={form.services} onChange={(e) => setForm(f => ({ ...f, services: e.target.value }))} placeholder="React, Node.js, PostgreSQL" style={inputStyle} />
              </Field>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <Field label="Ville">
                  <input type="text" value={form.city} onChange={(e) => setForm(f => ({ ...f, city: e.target.value }))} placeholder="Antananarivo" style={inputStyle} />
                </Field>
                <Field label="Pays">
                  <input type="text" value={form.country} onChange={(e) => setForm(f => ({ ...f, country: e.target.value }))} placeholder="Madagascar" style={inputStyle} />
                </Field>
              </div>
              <Field label="Tarif horaire (€/h)">
                <input type="number" value={form.hourly_rate} onChange={(e) => setForm(f => ({ ...f, hourly_rate: e.target.value }))} placeholder="45" min={0} style={inputStyle} />
              </Field>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <Field label="Téléphone">
                  <input type="tel" value={form.phone} onChange={(e) => setForm(f => ({ ...f, phone: e.target.value }))} placeholder="+261 34 00 000 00" style={inputStyle} />
                </Field>
                <Field label="Email">
                  <input type="email" value={form.email} onChange={(e) => setForm(f => ({ ...f, email: e.target.value }))} placeholder="jean@example.com" style={inputStyle} />
                </Field>
              </div>
              <Field label="Photo">
                <input ref={fileRef} type="file" accept="image/*" onChange={handleImageChange} style={{ fontSize: 13, color: "#555" }} />
                {imagePreview && (
                  <div style={{ marginTop: 8 }}>
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={imagePreview} alt="preview" style={{ width: 80, height: 80, objectFit: "cover", borderRadius: 8, border: "1px solid #fecaca" }} />
                  </div>
                )}
              </Field>

              {error && <div style={{ background: "#fee2e2", color: primary, borderRadius: 8, padding: "10px 14px", fontSize: 14, marginBottom: 16 }}>{error}</div>}
              {success && <div style={{ background: "#dcfce7", color: "#16a34a", borderRadius: 8, padding: "10px 14px", fontSize: 14, marginBottom: 16 }}>{success}</div>}

              <button type="submit" disabled={submitting} style={{ width: "100%", background: submitting ? "#f87171" : primary, color: "#fff", padding: "12px", borderRadius: 8, fontWeight: 700, fontSize: 15, border: "none", cursor: submitting ? "not-allowed" : "pointer", marginTop: 8 }}>
                {submitting ? "Ajout en cours…" : "Ajouter le prestataire"}
              </button>
            </form>
          </div>

          {/* LIST */}
          <div>
            <h2 style={{ fontWeight: 700, fontSize: 18, color: "#111", marginBottom: 16 }}>Prestataires ({prestataires.length})</h2>
            {loading ? (
              <p style={{ color: "#aaa", fontSize: 14 }}>Chargement…</p>
            ) : prestataires.length === 0 ? (
              <div style={{ background: "#fff", border: "1px solid #fecaca", borderRadius: 12, padding: 24, textAlign: "center", color: "#aaa", fontSize: 15 }}>
                Aucun prestataire. Ajoutez le premier !
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 10, maxHeight: "75vh", overflowY: "auto" }}>
                {prestataires.map((p) => (
                  <div key={p.id} style={{ background: "#fff", border: "1px solid #fecaca", borderRadius: 12, padding: "14px 18px", display: "flex", gap: 14, alignItems: "flex-start" }}>
                    {p.image_base64 ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img src={`data:image/jpeg;base64,${p.image_base64}`} alt={p.name} style={{ width: 52, height: 52, borderRadius: 8, objectFit: "cover", flexShrink: 0, border: "1px solid #fecaca" }} />
                    ) : (
                      <div style={{ width: 52, height: 52, borderRadius: 8, background: "#fee2e2", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, fontSize: 22 }}>👤</div>
                    )}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontWeight: 700, fontSize: 14, color: "#111" }}>{p.name}</div>
                      <div style={{ fontSize: 13, color: primary, fontWeight: 600 }}>{p.specialty}</div>
                      {(p.city || p.country) && (
                        <div style={{ fontSize: 12, color: "#aaa" }}>{[p.city, p.country].filter(Boolean).join(", ")}</div>
                      )}
                      <div style={{ marginTop: 5, display: "flex", flexWrap: "wrap", gap: 4 }}>
                        {p.services.slice(0, 3).map((s) => (
                          <span key={s} style={{ background: "#fee2e2", color: primary, fontSize: 11, fontWeight: 600, padding: "2px 8px", borderRadius: 999 }}>{s}</span>
                        ))}
                      </div>
                    </div>
                    {p.hourly_rate > 0 && (
                      <div style={{ fontWeight: 800, fontSize: 14, color: primary, flexShrink: 0 }}>{p.hourly_rate}€/h</div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}

const inputStyle: CSSProperties = {
  width: "100%",
  padding: "10px 14px",
  borderRadius: 8,
  border: "1px solid #e5e7eb",
  fontSize: 14,
  outline: "none",
  boxSizing: "border-box",
  fontFamily: "inherit",
};

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div style={{ marginBottom: 14 }}>
      <label style={{ display: "block", fontSize: 13, fontWeight: 600, color: "#444", marginBottom: 6 }}>{label}</label>
      {children}
    </div>
  );
}
