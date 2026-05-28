"use client";

import { useState, useEffect, useRef, FormEvent, ChangeEvent } from "react";
import { useRouter } from "next/navigation";

const primary = "#dc2626";

interface Prestataire {
  id: number;
  title: string;
  description: string;
  characteristics: string[];
  price: number;
  image_base64?: string;
  created_at: string;
}

export default function AdminPage() {
  const router = useRouter();
  const [prestataires, setPrestataires] = useState<Prestataire[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const [form, setForm] = useState({
    title: "",
    description: "",
    characteristics: "",
    price: "",
    image_base64: "",
  });

  useEffect(() => {
    fetchPrestataires();
  }, []);

  async function fetchPrestataires() {
    try {
      const res = await fetch("/api/products");
      if (res.status === 401 || res.status === 403) { router.push("/login?redirect=/admin"); return; }
      const data = await res.json();
      setPrestataires(data);
    } catch {
      setError("Impossible de charger les prestataires");
    } finally {
      setLoading(false);
    }
  }

  function handleImageChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      // Strip data URI prefix — backend expects raw base64
      const base64 = result.split(",")[1] ?? result;
      setForm((f) => ({ ...f, image_base64: base64 }));
    };
    reader.readAsDataURL(file);
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setSubmitting(true);

    const characteristics = form.characteristics
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    const body: Record<string, unknown> = {
      title: form.title,
      description: form.description,
      characteristics,
      price: parseFloat(form.price) || 0,
    };
    if (form.image_base64) body.image_base64 = form.image_base64;

    try {
      const res = await fetch("/api/products", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const d = await res.json().catch(() => ({}));
        throw new Error(d.detail || "Erreur lors de l'ajout");
      }
      setSuccess("Prestataire ajouté avec succès !");
      setForm({ title: "", description: "", characteristics: "", price: "", image_base64: "" });
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
            <img src="/karohy-logo.png" alt="Karohy.mg" style={{ height: 52, width: "auto", objectFit: "contain" }} />
            <span style={{ fontWeight: 800, fontSize: 15, color: "#999" }}>.mg</span>
          </a>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <span style={{ fontSize: 13, color: "#888", fontWeight: 600 }}>Administration</span>
            <button
              onClick={handleLogout}
              style={{ fontSize: 13, fontWeight: 600, color: "#dc2626", background: "none", border: "1px solid #fecaca", borderRadius: 6, padding: "6px 14px", cursor: "pointer" }}
            >
              Déconnexion
            </button>
          </div>
        </div>
      </nav>

      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "40px 24px" }}>
        <h1 style={{ fontWeight: 800, fontSize: 26, color: "#111", marginBottom: 8 }}>Gestion des prestataires</h1>
        <p style={{ color: "#888", marginBottom: 40, fontSize: 15 }}>
          {prestataires.length} prestataire{prestataires.length !== 1 ? "s" : ""} dans la base
        </p>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1.5fr", gap: 32, alignItems: "start" }}>
          {/* ADD FORM */}
          <div style={{ background: "#fff", borderRadius: 16, padding: "32px 28px", border: "1px solid #fecaca", boxShadow: "0 2px 16px rgba(220,38,38,0.06)" }}>
            <h2 style={{ fontWeight: 700, fontSize: 18, color: "#111", marginBottom: 24 }}>Ajouter un prestataire</h2>

            <form onSubmit={handleSubmit}>
              <Field label="Nom *">
                <input
                  type="text"
                  value={form.title}
                  onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
                  required
                  placeholder="Ex: Jean Dupont — Dev React Senior"
                  style={inputStyle}
                />
              </Field>

              <Field label="Description *">
                <textarea
                  value={form.description}
                  onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                  required
                  rows={4}
                  placeholder="Présentation du prestataire, expériences, secteurs…"
                  style={{ ...inputStyle, resize: "vertical" }}
                />
              </Field>

              <Field label="Compétences / spécialités">
                <input
                  type="text"
                  value={form.characteristics}
                  onChange={(e) => setForm((f) => ({ ...f, characteristics: e.target.value }))}
                  placeholder="React, Node.js, PostgreSQL (séparés par virgule)"
                  style={inputStyle}
                />
              </Field>

              <Field label="TJM (€/jour)">
                <input
                  type="number"
                  value={form.price}
                  onChange={(e) => setForm((f) => ({ ...f, price: e.target.value }))}
                  placeholder="450"
                  min={0}
                  style={inputStyle}
                />
              </Field>

              <Field label="Photo de profil">
                <input
                  ref={fileRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageChange}
                  style={{ fontSize: 14, color: "#555" }}
                />
                {form.image_base64 && (
                  <div style={{ marginTop: 8 }}>
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={`data:image/jpeg;base64,${form.image_base64}`}
                      alt="preview"
                      style={{ width: 80, height: 80, objectFit: "cover", borderRadius: 8, border: "1px solid #fecaca" }}
                    />
                  </div>
                )}
              </Field>

              {error && (
                <div style={{ background: "#fee2e2", color: primary, borderRadius: 8, padding: "10px 14px", fontSize: 14, marginBottom: 16 }}>
                  {error}
                </div>
              )}
              {success && (
                <div style={{ background: "#dcfce7", color: "#16a34a", borderRadius: 8, padding: "10px 14px", fontSize: 14, marginBottom: 16 }}>
                  {success}
                </div>
              )}

              <button
                type="submit"
                disabled={submitting}
                style={{ width: "100%", background: submitting ? "#f87171" : primary, color: "#fff", padding: "12px", borderRadius: 8, fontWeight: 700, fontSize: 15, border: "none", cursor: submitting ? "not-allowed" : "pointer", marginTop: 8 }}
              >
                {submitting ? "Ajout en cours…" : "Ajouter le prestataire"}
              </button>
            </form>
          </div>

          {/* LIST */}
          <div>
            <h2 style={{ fontWeight: 700, fontSize: 18, color: "#111", marginBottom: 16 }}>Prestataires existants</h2>
            {loading ? (
              <p style={{ color: "#aaa", fontSize: 14 }}>Chargement…</p>
            ) : prestataires.length === 0 ? (
              <div style={{ background: "#fff", border: "1px solid #fecaca", borderRadius: 12, padding: 24, textAlign: "center", color: "#aaa", fontSize: 15 }}>
                Aucun prestataire pour l&apos;instant. Ajoutez le premier !
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                {prestataires.map((p) => (
                  <div key={p.id} style={{ background: "#fff", border: "1px solid #fecaca", borderRadius: 12, padding: "16px 20px", display: "flex", gap: 14, alignItems: "flex-start" }}>
                    {p.image_base64 ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={`data:image/jpeg;base64,${p.image_base64}`}
                        alt={p.title}
                        style={{ width: 52, height: 52, borderRadius: 8, objectFit: "cover", flexShrink: 0, border: "1px solid #fecaca" }}
                      />
                    ) : (
                      <div style={{ width: 52, height: 52, borderRadius: 8, background: "#fee2e2", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, fontSize: 22 }}>
                        👤
                      </div>
                    )}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontWeight: 700, fontSize: 15, color: "#111" }}>{p.title}</div>
                      <div style={{ fontSize: 13, color: "#666", marginTop: 2, display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>
                        {p.description}
                      </div>
                      <div style={{ marginTop: 6, display: "flex", flexWrap: "wrap", gap: 4 }}>
                        {p.characteristics.slice(0, 4).map((c) => (
                          <span key={c} style={{ background: "#fee2e2", color: primary, fontSize: 11, fontWeight: 600, padding: "2px 8px", borderRadius: 999 }}>{c}</span>
                        ))}
                      </div>
                    </div>
                    {p.price > 0 && (
                      <div style={{ fontWeight: 800, fontSize: 15, color: primary, flexShrink: 0 }}>{p.price}€/j</div>
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

const inputStyle: React.CSSProperties = {
  width: "100%",
  padding: "10px 14px",
  borderRadius: 8,
  border: "1px solid #e5e7eb",
  fontSize: 14,
  outline: "none",
  boxSizing: "border-box",
  fontFamily: "inherit",
};

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <label style={{ display: "block", fontSize: 13, fontWeight: 600, color: "#444", marginBottom: 6 }}>{label}</label>
      {children}
    </div>
  );
}
