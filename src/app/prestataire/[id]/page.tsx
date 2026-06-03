"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getPrestataire } from "@/services/api";
import { connectToPrestataire } from "@/services/auth";
import { OPTION_LABELS, type Prestataire, type ServiceOption } from "@/types";
import LoginModal from "@/components/LoginModal";

export default function PrestataireProfilePage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const id = params?.id;

  const [data, setData] = useState<Prestataire | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loginOpen, setLoginOpen] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    (async () => {
      try {
        const p = await getPrestataire(id);
        setData(p);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Profil introuvable");
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  const doConnect = async () => {
    if (!data) return;
    setConnecting(true);
    try {
      const res = await connectToPrestataire(data.id);
      setToast(`Demande envoyée à ${res.prestataire_name}`);
      setTimeout(() => setToast(null), 4000);
    } catch (err) {
      const e = err as Error & { code?: string };
      if (e.code === "LOGIN_REQUIRED") {
        setLoginOpen(true);
      } else {
        setToast(e.message || "Erreur");
        setTimeout(() => setToast(null), 4000);
      }
    } finally {
      setConnecting(false);
    }
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-red-50/30 flex items-center justify-center">
        <div className="text-gray-500">Chargement…</div>
      </main>
    );
  }

  if (error || !data) {
    return (
      <main className="min-h-screen bg-red-50/30 flex flex-col items-center justify-center gap-3 p-6 text-center">
        <p className="text-gray-700 font-medium">{error || "Profil introuvable"}</p>
        <button onClick={() => router.push("/")} className="text-red-600 underline">Retour à l&apos;accueil</button>
      </main>
    );
  }

  const options = (() => {
    const set = new Set<ServiceOption>();
    for (const sd of data.services_detail || []) for (const opt of sd.options) set.add(opt);
    return [...set];
  })();

  const formatPrice = (price: number, currency: string) => {
    if (price === 0) return "Sur devis";
    return `${price.toLocaleString("fr-FR")} ${currency || "€"}`;
  };

  return (
    <main className="min-h-screen bg-red-50/30 pb-20">
      {/* Top bar */}
      <nav className="bg-white border-b border-red-100 sticky top-0 z-30">
        <div className="max-w-5xl mx-auto px-5 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/karohy-logo.png" alt="Karohy" style={{ height: 48, objectFit: "contain" }} />
          </Link>
          <Link href="/" className="text-sm text-gray-600 hover:text-red-600">← Retour</Link>
        </div>
      </nav>

      {/* Cover photo */}
      <div className="relative h-56 sm:h-72 bg-gradient-to-br from-red-100 to-red-50 overflow-hidden">
        {data.cover_photo_base64 ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={`data:image/jpeg;base64,${data.cover_photo_base64}`}
            alt=""
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_40%,rgba(220,38,38,0.18),transparent_60%)]" />
        )}
      </div>

      <div className="max-w-5xl mx-auto px-5 -mt-16 relative z-10">
        {/* Header card with profile photo overlapping cover */}
        <div className="bg-white rounded-2xl shadow-lg border border-red-100 p-5 sm:p-7 flex flex-col sm:flex-row gap-5 sm:gap-7 items-center sm:items-start">
          <div className="w-28 h-28 sm:w-32 sm:h-32 rounded-2xl bg-gradient-to-br from-red-100 to-white border-4 border-white shadow-md overflow-hidden shrink-0 -mt-12 sm:-mt-16">
            {data.image_base64 ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={`data:image/jpeg;base64,${data.image_base64}`}
                alt={data.name}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-red-200 text-4xl">👤</div>
            )}
          </div>

          <div className="flex-1 text-center sm:text-left">
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900" style={{ fontFamily: "var(--font-display)" }}>
              {data.name}
            </h1>
            {data.organization && (
              <p className="text-sm text-gray-600 mt-1">{data.organization}</p>
            )}
            <p className="text-sm font-semibold text-red-600 mt-1">{data.specialty}</p>
            {(data.city || data.address) && (
              <p className="text-sm text-gray-500 mt-2 flex items-center justify-center sm:justify-start gap-1.5">
                <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
                </svg>
                {data.address || `${data.city}${data.country ? `, ${data.country}` : ""}`}
              </p>
            )}
            {data.rating > 0 && (
              <div className="mt-2 inline-flex items-center gap-1.5 text-sm font-medium text-amber-600">
                <span>{"★".repeat(Math.round(data.rating))}</span>
                <span className="text-gray-600">{data.rating.toFixed(1)} / 5</span>
              </div>
            )}
            {/* Quick options badges */}
            {options.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-4 justify-center sm:justify-start">
                {options.map((o) => (
                  <span key={o} className="inline-flex items-center gap-1.5 text-xs bg-red-50 text-red-700 border border-red-200 px-3 py-1.5 rounded-full font-semibold">
                    <span>{OPTION_LABELS[o].emoji}</span>
                    <span>{OPTION_LABELS[o].fr}</span>
                  </span>
                ))}
              </div>
            )}
          </div>

          <div className="flex flex-col gap-2 w-full sm:w-auto sm:min-w-[180px]">
            <button
              onClick={doConnect}
              disabled={connecting}
              className="bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-5 rounded-xl disabled:opacity-50 transition-colors"
            >
              {connecting ? "..." : "Connecter →"}
            </button>
            {data.phone && (
              <a
                href={`tel:${data.phone}`}
                className="text-center bg-white border border-gray-200 hover:border-red-400 text-gray-700 hover:text-red-700 font-semibold py-2.5 px-5 rounded-xl transition-colors text-sm"
              >
                📞 {data.phone}
              </a>
            )}
          </div>
        </div>

        {/* Specialties chips */}
        {data.specialties && data.specialties.length > 0 && (
          <section className="mt-6 bg-white rounded-2xl border border-red-100 p-5 sm:p-6">
            <h2 className="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-3">Spécialités</h2>
            <div className="flex flex-wrap gap-2">
              {data.specialties.map((s) => (
                <span key={s} className="text-sm bg-red-50 text-red-700 border border-red-200 px-3 py-1.5 rounded-full font-medium">
                  {s}
                </span>
              ))}
            </div>
          </section>
        )}

        {/* Bio */}
        {(data.bio || data.description) && (
          <section className="mt-6 bg-white rounded-2xl border border-red-100 p-5 sm:p-6">
            <h2 className="font-bold text-gray-900 mb-3" style={{ fontFamily: "var(--font-display)" }}>À propos</h2>
            <p className="text-gray-700 leading-relaxed whitespace-pre-line">{data.bio || data.description}</p>
          </section>
        )}

        {/* Services with prices + options */}
        {data.services_detail && data.services_detail.length > 0 && (
          <section className="mt-6 bg-white rounded-2xl border border-red-100 p-5 sm:p-6">
            <h2 className="font-bold text-gray-900 mb-4" style={{ fontFamily: "var(--font-display)" }}>Services & tarifs</h2>
            <div className="space-y-3">
              {data.services_detail.map((sd, i) => (
                <div key={i} className="bg-gray-50 border border-gray-100 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 text-sm">{sd.name}</h3>
                    {sd.duration_min > 0 && (
                      <p className="text-xs text-gray-500 mt-0.5">{sd.duration_min} min</p>
                    )}
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {sd.options.map((o) => (
                        <span key={o} className="inline-flex items-center gap-1 text-[11px] bg-white border border-gray-200 text-gray-700 px-2 py-0.5 rounded-full">
                          {OPTION_LABELS[o].emoji} {OPTION_LABELS[o].fr}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-red-600 font-bold text-base whitespace-nowrap">{formatPrice(sd.price, sd.currency)}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Location (with placeholder map) */}
        {(data.latitude && data.longitude) || data.address ? (
          <section className="mt-6 bg-white rounded-2xl border border-red-100 p-5 sm:p-6">
            <h2 className="font-bold text-gray-900 mb-3" style={{ fontFamily: "var(--font-display)" }}>Localisation</h2>
            {data.address && (
              <p className="text-gray-700 text-sm mb-3">📍 {data.address}</p>
            )}
            {data.latitude && data.longitude && (
              <div className="rounded-xl overflow-hidden border border-gray-200">
                <iframe
                  className="w-full h-64"
                  src={`https://www.openstreetmap.org/export/embed.html?bbox=${data.longitude - 0.005},${data.latitude - 0.005},${data.longitude + 0.005},${data.latitude + 0.005}&layer=mapnik&marker=${data.latitude},${data.longitude}`}
                  title="Map"
                />
              </div>
            )}
          </section>
        ) : null}
      </div>

      <LoginModal
        open={loginOpen}
        onClose={() => setLoginOpen(false)}
        onSuccess={() => { setLoginOpen(false); doConnect(); }}
        context={`Connexion à ${data.name}`}
      />

      {toast && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-emerald-600 text-white text-sm font-medium px-5 py-3 rounded-full shadow-lg z-[1200]">
          {toast}
        </div>
      )}
    </main>
  );
}
