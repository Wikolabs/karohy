import ChatInterface from "@/components/ChatInterface";

export default function Home() {
  const primary = "#dc2626";
  const bgLight = "#fef2f2";

  const metrics = [
    { value: "<1s", label: "temps de matching" },
    { value: "Vision IA", label: "recherche par image" },
    { value: "3072", label: "dimensions vectorielles" },
    { value: "Groq", label: "LLaMA 3.3 70B chat" },
  ];

  const features = [
    {
      icon: "🎯",
      title: "Matching sémantique",
      desc: "Décrivez votre besoin en langage naturel. L'IA comprend le contexte, la spécialité, la localisation et trouve les prestataires les plus pertinents en moins d'une seconde.",
    },
    {
      icon: "📸",
      title: "Recherche par image",
      desc: "Montrez un exemple visuel de ce que vous cherchez. Gemini Flash 2.5 analyse l'image et identifie les prestataires dont le profil correspond visuellement à votre besoin.",
    },
    {
      icon: "💬",
      title: "Chat IA intégré",
      desc: "Affinez votre recherche en conversant avec l'assistant Groq LLaMA 3.3 70B. Il contextualise votre demande et recommande parmi les prestataires disponibles.",
    },
  ];

  const steps = [
    {
      num: "01",
      title: "Constituez votre annuaire",
      desc: "Ajoutez vos prestataires avec photo, spécialité, services et localisation. L'IA vectorise chaque profil en 3072 dimensions via Gemini Embeddings.",
    },
    {
      num: "02",
      title: "Décrivez votre besoin",
      desc: "Texte ou image — l'IA comprend votre recherche, extrait les dimensions sémantiques clés et interroge la base vectorielle PostgreSQL pgvector.",
    },
    {
      num: "03",
      title: "Match garanti",
      desc: "Les prestataires les plus pertinents s'affichent avec score et fiche complète. L'assistant chat affine si besoin en temps réel.",
    },
  ];

  return (
    <main style={{ fontFamily: "var(--font-body)" }}>
      {/* NAVBAR */}
      <nav style={{ background: "#fff", borderBottom: "1px solid #fecaca", position: "sticky", top: 0, zIndex: 50 }}>
        <div style={{ maxWidth: 1100, margin: "0 auto", padding: "0 24px", height: 64, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <a href="/" style={{ display: "flex", alignItems: "center", gap: 6, textDecoration: "none" }}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/karohy-logo.png" alt="Karohy.mg" style={{ height: 52, width: "auto", objectFit: "contain" }} />
            <span style={{ fontFamily: "var(--font-display)", fontWeight: 800, fontSize: 15, color: "#999" }}>.mg</span>
          </a>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <a
              href="/admin"
              style={{ fontSize: 13, fontWeight: 600, color: "#999", textDecoration: "none", padding: "6px 12px", borderRadius: 6, border: "1px solid #e5e7eb" }}
            >
              Admin
            </a>
            <a
              href="https://calendly.com/wikolabs"
              target="_blank"
              rel="noopener noreferrer"
              style={{ background: primary, color: "#fff", padding: "10px 22px", borderRadius: 8, fontWeight: 600, fontSize: 14, textDecoration: "none" }}
            >
              Demander une démo
            </a>
          </div>
        </div>
      </nav>

      {/* HERO */}
      <section style={{ background: `linear-gradient(135deg, ${bgLight} 0%, #fff 60%)`, padding: "80px 24px 60px" }}>
        <div style={{ maxWidth: 800, margin: "0 auto", textAlign: "center" }}>
          <span style={{ display: "inline-block", background: "#fee2e2", color: primary, borderRadius: 999, padding: "6px 18px", fontSize: 13, fontWeight: 600, marginBottom: 24 }}>
            Matching prestataires IA
          </span>
          <h1 style={{ fontFamily: "var(--font-display)", fontSize: "clamp(2rem, 5vw, 3.2rem)", fontWeight: 800, lineHeight: 1.15, color: "#111", marginBottom: 32 }}>
            Trouvez le bon prestataire.<br />
            <span style={{ color: primary }}>En quelques secondes.</span>
          </h1>
          <div style={{ display: "flex", gap: 12, justifyContent: "center", flexWrap: "wrap", marginBottom: 56 }}>
            <a
              href="#demo"
              style={{ background: primary, color: "#fff", padding: "14px 32px", borderRadius: 10, fontWeight: 700, fontSize: 16, textDecoration: "none" }}
            >
              Lancer la recherche →
            </a>
            <a
              href="https://calendly.com/wikolabs"
              target="_blank"
              rel="noopener noreferrer"
              style={{ background: "#fff", color: primary, padding: "14px 32px", borderRadius: 10, fontWeight: 700, fontSize: 16, textDecoration: "none", border: `2px solid ${primary}` }}
            >
              Demander une démo
            </a>
            <a
              href="https://wa.me/261386626100?text=Bonjour%2C%20je%20souhaite%20discuter%20de%20Karohy.mg%20avec%20Wikolabs."
              target="_blank"
              rel="noopener noreferrer"
              style={{ background: "#25d366", color: "#fff", padding: "14px 32px", borderRadius: 10, fontWeight: 700, fontSize: 16, textDecoration: "none" }}
            >
              WhatsApp
            </a>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 16 }}>
            {metrics.map((m) => (
              <div key={m.label} style={{ background: "#fff", border: "1px solid #fecaca", borderRadius: 12, padding: "20px 16px", boxShadow: "0 2px 8px rgba(220,38,38,0.06)" }}>
                <div style={{ fontFamily: "var(--font-display)", fontSize: 28, fontWeight: 800, color: primary }}>{m.value}</div>
                <div style={{ fontSize: 13, color: "#666", marginTop: 4 }}>{m.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section style={{ background: "#fff", padding: "72px 24px" }}>
        <div style={{ maxWidth: 1100, margin: "0 auto" }}>
          <h2 style={{ fontFamily: "var(--font-display)", fontSize: "clamp(1.5rem, 3vw, 2.2rem)", fontWeight: 800, textAlign: "center", color: "#111", marginBottom: 48 }}>
            Ce que Karohy.mg fait pour vous
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 24 }}>
            {features.map((f) => (
              <div key={f.title} style={{ background: bgLight, border: "1px solid #fecaca", borderRadius: 16, padding: "32px 28px" }}>
                <div style={{ fontSize: 32, marginBottom: 16 }}>{f.icon}</div>
                <h3 style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 18, color: "#111", marginBottom: 12 }}>{f.title}</h3>
                <p style={{ color: "#555", lineHeight: 1.7, fontSize: 15 }}>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* LIVE DEMO */}
      <section id="demo" style={{ background: bgLight, padding: "72px 24px" }}>
        <div style={{ maxWidth: 1100, margin: "0 auto" }}>
          <h2 style={{ fontFamily: "var(--font-display)", fontSize: "clamp(1.5rem, 3vw, 2.2rem)", fontWeight: 800, textAlign: "center", color: "#111", marginBottom: 16 }}>
            Essayez maintenant
          </h2>
          <p style={{ textAlign: "center", color: "#666", fontSize: 16, marginBottom: 40 }}>
            Interface live — cherchez un prestataire par texte ou par image, directement ici.
          </p>
          <div style={{ borderRadius: 20, overflow: "hidden", boxShadow: "0 8px 48px rgba(220,38,38,0.12)", border: "1px solid #fecaca", height: 700 }}>
            <ChatInterface />
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section style={{ background: "#fff", padding: "72px 24px" }}>
        <div style={{ maxWidth: 900, margin: "0 auto" }}>
          <h2 style={{ fontFamily: "var(--font-display)", fontSize: "clamp(1.5rem, 3vw, 2.2rem)", fontWeight: 800, textAlign: "center", color: "#111", marginBottom: 48 }}>
            Comment ça fonctionne
          </h2>
          <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
            {steps.map((s) => (
              <div key={s.num} style={{ background: bgLight, border: "1px solid #fecaca", borderRadius: 16, padding: "28px 32px", display: "flex", gap: 24, alignItems: "flex-start" }}>
                <span style={{ fontFamily: "var(--font-display)", fontSize: 36, fontWeight: 900, color: "#fca5a5", minWidth: 56 }}>{s.num}</span>
                <div>
                  <h3 style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 18, color: "#111", marginBottom: 8 }}>{s.title}</h3>
                  <p style={{ color: "#555", lineHeight: 1.7, fontSize: 15 }}>{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section style={{ background: primary, padding: "72px 24px", textAlign: "center" }}>
        <div style={{ maxWidth: 600, margin: "0 auto" }}>
          <h2 style={{ fontFamily: "var(--font-display)", fontSize: "clamp(1.6rem, 3vw, 2.4rem)", fontWeight: 800, color: "#fff", marginBottom: 16 }}>
            Connectez les bons prestataires
          </h2>
          <p style={{ color: "#fecaca", fontSize: 17, marginBottom: 40 }}>
            Démo gratuite. Mise en place en 48h.
          </p>
          <div style={{ display: "flex", gap: 12, justifyContent: "center", flexWrap: "wrap" }}>
            <a
              href="#demo"
              style={{ background: "#fff", color: primary, padding: "14px 32px", borderRadius: 10, fontWeight: 700, fontSize: 16, textDecoration: "none" }}
            >
              Lancer la recherche →
            </a>
            <a
              href="https://calendly.com/wikolabs"
              target="_blank"
              rel="noopener noreferrer"
              style={{ background: "transparent", color: "#fff", padding: "14px 32px", borderRadius: 10, fontWeight: 700, fontSize: 16, textDecoration: "none", border: "2px solid rgba(255,255,255,0.6)" }}
            >
              Demander une démo
            </a>
            <a
              href="https://wa.me/261386626100?text=Bonjour%2C%20je%20souhaite%20discuter%20de%20Karohy.mg%20avec%20Wikolabs."
              target="_blank"
              rel="noopener noreferrer"
              style={{ background: "#25d366", color: "#fff", padding: "14px 32px", borderRadius: 10, fontWeight: 700, fontSize: 16, textDecoration: "none" }}
            >
              WhatsApp
            </a>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer style={{ background: "#111", padding: "40px 24px", textAlign: "center" }}>
        <div style={{ maxWidth: 800, margin: "0 auto" }}>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 6, background: "#fff", borderRadius: 10, padding: "6px 14px" }}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/karohy-logo.png" alt="Karohy.mg" style={{ height: 32, width: "auto", objectFit: "contain" }} />
            <span style={{ fontFamily: "var(--font-display)", fontWeight: 800, fontSize: 15, color: "#666" }}>.mg</span>
          </div>
          <p style={{ color: "#999", marginTop: 12, fontSize: 14 }}>
            by{" "}
            <a href="https://wikolabs.com" target="_blank" rel="noopener noreferrer" style={{ color: "#ccc", textDecoration: "none" }}>
              Wikolabs
            </a>
          </p>
          <p style={{ color: "#777", marginTop: 8, fontSize: 13, display: "flex", gap: 16, justifyContent: "center", flexWrap: "wrap" }}>
            <a href="mailto:team@wikolabs.com" style={{ color: "#aaa", textDecoration: "none" }}>team@wikolabs.com</a>
            <span>·</span>
            <a href="tel:+261386626100" style={{ color: "#aaa", textDecoration: "none" }}>+261 38 66 261 00</a>
            <span>·</span>
            <a href="https://calendly.com/wikolabs" target="_blank" rel="noopener noreferrer" style={{ color: "#aaa", textDecoration: "none" }}>Prendre RDV</a>
          </p>
          <p style={{ color: "#555", marginTop: 8, fontSize: 13 }}>© {new Date().getFullYear()} Wikolabs. Tous droits réservés.</p>
        </div>
      </footer>
    </main>
  );
}
