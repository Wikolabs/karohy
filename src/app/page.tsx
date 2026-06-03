import ChatInterface from "@/components/ChatInterface";

export default function Home() {
  const primary = "#dc2626";
  const bgLight = "#fef2f2";

  return (
    <main style={{ fontFamily: "var(--font-body)", background: `linear-gradient(160deg, ${bgLight} 0%, #fff 60%)`, minHeight: "100vh" }}>
      {/* NAVBAR */}
      <nav style={{ background: "rgba(255,255,255,0.78)", backdropFilter: "blur(16px)", WebkitBackdropFilter: "blur(16px)", borderBottom: "1px solid #fecaca", position: "sticky", top: 0, zIndex: 50 }}>
        <div style={{ maxWidth: 1200, margin: "0 auto", padding: "0 24px", height: 76, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <a href="/" style={{ display: "flex", alignItems: "center", textDecoration: "none" }} aria-label="Karohy">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/karohy-logo.png" alt="Karohy" style={{ height: 68, width: "auto", objectFit: "contain" }} />
          </a>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <a
              href="/admin"
              style={{ fontSize: 13, fontWeight: 600, color: "#999", textDecoration: "none", padding: "6px 12px", borderRadius: 6, border: "1px solid #e5e7eb" }}
            >
              Admin
            </a>
            <a
              href="https://wa.me/261386626100?text=Bonjour%2C%20je%20souhaite%20discuter%20de%20Karohy%20avec%20Wikolabs."
              target="_blank"
              rel="noopener noreferrer"
              style={{ background: "#25d366", color: "#fff", padding: "10px 18px", borderRadius: 100, fontWeight: 600, fontSize: 13.5, textDecoration: "none" }}
            >
              WhatsApp
            </a>
            <a
              href="https://cal.com/wikolabs-team/30min"
              target="_blank"
              rel="noopener noreferrer"
              style={{ background: primary, color: "#fff", padding: "10px 22px", borderRadius: 100, fontWeight: 600, fontSize: 13.5, textDecoration: "none" }}
            >
              Réserver un appel
            </a>
          </div>
        </div>
      </nav>

      {/* CHATBOT-CENTRIC HERO — all descriptive content lives inside ChatInterface */}
      <section style={{ padding: "48px 24px 96px" }}>
        <div style={{ maxWidth: 1100, margin: "0 auto" }}>
          <div
            style={{
              background: "#fff",
              border: "1px solid #fecaca",
              borderRadius: 24,
              boxShadow: "0 18px 56px rgba(220,38,38,0.12), 0 4px 16px rgba(0,0,0,0.06)",
              overflow: "hidden",
            }}
          >
            <ChatInterface />
          </div>
        </div>
      </section>

      {/* SLIM CTA STRIP */}
      <section style={{ background: primary, padding: "56px 24px" }}>
        <div style={{ maxWidth: 720, margin: "0 auto", textAlign: "center" }}>
          <h2 style={{ fontFamily: "var(--font-display)", fontSize: "clamp(1.5rem, 3vw, 2.1rem)", fontWeight: 800, color: "#fff", marginBottom: 14, lineHeight: 1.2 }}>
            Connectez les bons prestataires
          </h2>
          <p style={{ color: "rgba(255,255,255,0.85)", fontSize: 16, marginBottom: 28 }}>
            Démo gratuite. Mise en place en 48h.
          </p>
          <div style={{ display: "flex", gap: 10, justifyContent: "center", flexWrap: "wrap" }}>
            <a
              href="https://cal.com/wikolabs-team/30min"
              target="_blank"
              rel="noopener noreferrer"
              style={{ background: "#fff", color: primary, padding: "13px 26px", borderRadius: 100, fontWeight: 700, fontSize: 14.5, textDecoration: "none" }}
            >
              📅 Réserver un appel
            </a>
            <a
              href="https://wa.me/261386626100?text=Bonjour%2C%20je%20souhaite%20discuter%20de%20Karohy%20avec%20Wikolabs."
              target="_blank"
              rel="noopener noreferrer"
              style={{ background: "#25d366", color: "#fff", padding: "13px 26px", borderRadius: 100, fontWeight: 700, fontSize: 14.5, textDecoration: "none" }}
            >
              💬 WhatsApp
            </a>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer style={{ background: "#111", padding: "40px 24px", textAlign: "center" }}>
        <div style={{ maxWidth: 800, margin: "0 auto" }}>
          <div style={{ display: "inline-flex", alignItems: "center", background: "#fff", borderRadius: 12, padding: "6px 16px" }}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/karohy-logo.png" alt="Karohy" style={{ height: 36, width: "auto", objectFit: "contain" }} />
          </div>
          <p style={{ color: "#999", marginTop: 14, fontSize: 14 }}>
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
            <a href="https://cal.com/wikolabs-team/30min" target="_blank" rel="noopener noreferrer" style={{ color: "#aaa", textDecoration: "none" }}>Réserver un appel</a>
          </p>
          <p style={{ color: "#555", marginTop: 8, fontSize: 13 }}>© {new Date().getFullYear()} Wikolabs. Tous droits réservés.</p>
        </div>
      </footer>
    </main>
  );
}
