import ChatInterface from "@/components/ChatInterface";

export default function Home() {
  const primary = "#dc2626";
  const bgLight = "#fef2f2";

  return (
    <main style={{ fontFamily: "var(--font-body)", background: `linear-gradient(160deg, ${bgLight} 0%, #fff 60%)`, minHeight: "100vh" }}>
      {/* NAVBAR */}
      <nav
        className="sticky top-0 z-50 border-b border-red-100"
        style={{ background: "rgba(255,255,255,0.78)", backdropFilter: "blur(16px)", WebkitBackdropFilter: "blur(16px)" }}
      >
        <div className="mx-auto px-3 sm:px-5 max-w-[1200px] h-16 sm:h-[76px] flex items-center justify-between">
          <a href="/" className="flex items-center no-underline" aria-label="Karohy">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/karohy-logo.png"
              alt="Karohy"
              className="object-contain"
              style={{ height: "clamp(44px, 9vw, 68px)", width: "auto" }}
            />
          </a>
          <div className="flex items-center gap-1.5 sm:gap-3">
            <a
              href="/admin"
              className="hidden sm:inline-block text-xs sm:text-sm font-semibold text-gray-500 hover:text-red-600 px-2.5 sm:px-3 py-1.5 rounded-md border border-gray-200 hover:border-red-300"
            >
              Admin
            </a>
            <a
              href="https://wa.me/261386626100?text=Bonjour%2C%20je%20souhaite%20discuter%20de%20Karohy%20avec%20Wikolabs."
              target="_blank"
              rel="noopener noreferrer"
              className="text-white font-semibold rounded-full no-underline"
              style={{ background: "#25d366", padding: "8px 12px", fontSize: 13 }}
            >
              <span className="sm:hidden" aria-label="WhatsApp">💬</span>
              <span className="hidden sm:inline">WhatsApp</span>
            </a>
            <a
              href="https://cal.com/wikolabs-team/30min"
              target="_blank"
              rel="noopener noreferrer"
              className="text-white font-semibold rounded-full no-underline"
              style={{ background: primary, padding: "8px 14px", fontSize: 13 }}
            >
              <span className="sm:hidden" aria-label="Cal.com">📅</span>
              <span className="hidden sm:inline">Réserver un appel</span>
            </a>
          </div>
        </div>
      </nav>

      {/* CHATBOT-CENTRIC HERO · all descriptive content lives inside ChatInterface */}
      <section className="px-3 sm:px-6 pt-6 pb-12 sm:pb-16">
        <div style={{ maxWidth: 1100, margin: "0 auto" }}>
          <div
            className="bg-white border border-red-100 sm:border-red-200 rounded-2xl sm:rounded-3xl overflow-hidden"
            style={{
              boxShadow: "0 18px 56px rgba(220,38,38,0.12), 0 4px 16px rgba(0,0,0,0.06)",
            }}
          >
            <ChatInterface />
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
