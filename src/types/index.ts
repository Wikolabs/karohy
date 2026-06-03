export type ServiceOption = "home_visit" | "video_call" | "in_office";

export interface ServiceDetail {
  name: string;
  price: number;
  currency: string;
  duration_min: number;
  options: ServiceOption[];
}

export interface Prestataire {
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
  // Lot 3+ enrichment fields
  organization?: string;
  specialties?: string[];
  bio?: string;
  cover_photo_base64?: string;
  services_detail?: ServiceDetail[];
  latitude?: number | null;
  longitude?: number | null;
  address?: string;
}

export interface SearchResult {
  prestataire: Prestataire;
  similarity_score: number;
}

export interface SearchRequest {
  text?: string;
  image_base64?: string;
}

export interface User {
  id: string;
  username: string;
  full_name: string;
  email: string;
}

export const OPTION_LABELS: Record<ServiceOption, { fr: string; emoji: string }> = {
  home_visit: { fr: "Visite à domicile", emoji: "🏠" },
  video_call: { fr: "Visio", emoji: "📹" },
  in_office: { fr: "En cabinet", emoji: "🏢" },
};
