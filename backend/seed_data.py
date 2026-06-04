"""Mock Malagasy prestataires across multiple categories, vectorised on startup."""
from __future__ import annotations

import asyncio
import logging
import time

from google.genai.errors import ClientError

from embedding_service import EmbeddingService
from models import Prestataire, ServiceDetail
from vector_store import PGVectorStore

logger = logging.getLogger(__name__)


# Tana districts with approximate coordinates (lat, lng)
TANA_GEO = {
    "Analakely":       (-18.9100, 47.5210),
    "Ankorondrano":    (-18.8800, 47.5230),
    "Ivandry":         (-18.8580, 47.5530),
    "Antaninarenina":  (-18.9143, 47.5219),
    "Antanimena":      (-18.9000, 47.5180),
    "67ha":            (-18.9300, 47.5100),
    "Itaosy":          (-18.9200, 47.4600),
    "Tanjombato":      (-18.9700, 47.5300),
    "Ambohimanarina":  (-18.8500, 47.5050),
    "Ambatobe":        (-18.8650, 47.5680),
    "Soanierana":      (-18.9450, 47.5360),
    "Soavimbahoaka":   (-18.8950, 47.5460),
}


def _tana(quartier: str) -> tuple[float, float]:
    return TANA_GEO.get(quartier, (-18.8792, 47.5079))


SEED_PRESTATAIRES: list[Prestataire] = [
    # ── Plomberie (3) ────────────────────────────────────────────────────────
    Prestataire(
        name="Rakoto Andry",
        organization="Andry Plomberie SARL",
        specialty="Plomberie",
        category="plumbing",
        description="Plombier expérimenté à Antananarivo. Réparations urgences, installation sanitaire, chauffe-eau solaire. Intervention sous 1h dans Tana.",
        services=["fuites", "débouchage", "chauffe-eau", "robinetterie", "installation sanitaire"],
        specialties=["Urgence 24/7", "Chauffe-eau solaire", "Plomberie écologique"],
        bio="Maître plombier depuis 2010. Spécialisé urgences nocturnes et installations chauffe-eau solaire à Tana. Devis gratuit sous 30 min. Garantie 12 mois.",
        city="Antananarivo", country="Madagascar", address="Lot II M 23 Ankorondrano",
        latitude=_tana("Ankorondrano")[0], longitude=_tana("Ankorondrano")[1],
        languages=["mg", "fr"],
        emergency_available=True, verified=True, rating=4.7,
        years_experience=14, response_time_hours=1, team_size=3,
        accepts_payment=["cash", "mvola", "orange_money"],
        certifications=["CAP Plomberie", "Habilitation chauffe-eau"],
        service_radius_km=15,
        hourly_rate=25000, min_price=15000, max_price=400000, currency="Ar",
        phone="+261 34 12 345 67", email="rakoto@andryplomberie.mg",
        services_detail=[
            ServiceDetail(name="Diagnostic urgence", price=15000, currency="Ar", duration_min=30, options=["home_visit", "video_call"]),
            ServiceDetail(name="Réparation fuite", price=45000, currency="Ar", duration_min=60, options=["home_visit"]),
            ServiceDetail(name="Pose chauffe-eau solaire", price=380000, currency="Ar", duration_min=240, options=["home_visit"]),
        ],
    ),
    Prestataire(
        name="Naina Plombier",
        specialty="Plomberie",
        category="plumbing",
        description="Plombier indépendant, intervention rapide dans tout Antananarivo. Spécialité fuites et installation cuisine/salle de bain.",
        services=["fuites", "installation", "rénovation cuisine"],
        bio="6 ans d'expérience. Disponible week-end. Travail soigné, prix abordables.",
        city="Antananarivo", country="Madagascar", address="Itaosy lot 134",
        latitude=_tana("Itaosy")[0], longitude=_tana("Itaosy")[1],
        languages=["mg", "fr"],
        rating=4.3, years_experience=6, response_time_hours=4,
        accepts_payment=["cash", "mvola"],
        hourly_rate=18000, min_price=10000, max_price=180000, currency="Ar",
        phone="+261 33 22 111 09",
        services_detail=[
            ServiceDetail(name="Intervention dépannage", price=20000, currency="Ar", duration_min=45, options=["home_visit"]),
        ],
    ),

    # ── Électricité (2) ──────────────────────────────────────────────────────
    Prestataire(
        name="Hery Andrianjafy",
        organization="Hery Élec SARL",
        specialty="Électricité",
        category="electrical",
        description="Électricien certifié JIRAMA, installations résidentielles et tertiaires. Mise aux normes, domotique, panneaux solaires.",
        services=["installation électrique", "mise aux normes", "domotique", "panneaux solaires"],
        specialties=["Solaire off-grid", "Domotique", "Mise aux normes JIRAMA"],
        bio="Diplômé IST Antananarivo. Certifié JIRAMA. Installations résidentielles et solaire off-grid pour zones rurales.",
        city="Antananarivo", country="Madagascar", address="Ivandry lot II 45",
        latitude=_tana("Ivandry")[0], longitude=_tana("Ivandry")[1],
        languages=["mg", "fr", "en"],
        verified=True, rating=4.8, years_experience=12, response_time_hours=2,
        team_size=4, emergency_available=True,
        accepts_payment=["cash", "mvola", "card", "bank_transfer"],
        certifications=["JIRAMA", "BTS Électrotechnique"],
        service_radius_km=30,
        hourly_rate=35000, min_price=20000, max_price=2500000, currency="Ar",
        phone="+261 34 56 789 01", email="hery@heryelec.mg",
        services_detail=[
            ServiceDetail(name="Diagnostic installation", price=20000, currency="Ar", duration_min=45, options=["home_visit", "in_office"]),
            ServiceDetail(name="Pose tableau électrique", price=380000, currency="Ar", duration_min=180, options=["home_visit"]),
            ServiceDetail(name="Kit solaire 500W complet", price=2200000, currency="Ar", duration_min=480, options=["home_visit"]),
        ],
    ),
    Prestataire(
        name="Tahina Élec",
        specialty="Électricité",
        category="electrical",
        description="Dépannage électrique rapide. Spécialiste petite installation maison.",
        services=["dépannage", "prises", "interrupteurs", "éclairage LED"],
        city="Antananarivo", country="Madagascar", address="67ha",
        latitude=_tana("67ha")[0], longitude=_tana("67ha")[1],
        languages=["mg", "fr"],
        rating=4.1, years_experience=4,
        accepts_payment=["cash", "mvola"],
        hourly_rate=15000, min_price=10000, max_price=150000, currency="Ar",
        phone="+261 32 11 234 56",
    ),

    # ── Beauté / Coiffure (3) ────────────────────────────────────────────────
    Prestataire(
        name="Salon Voahangy",
        organization="Salon Voahangy",
        specialty="Coiffure",
        category="beauty",
        description="Salon de coiffure femme spécialisé cheveux crépus, tissage, défrisage et événementiel mariage.",
        services=["coupe", "tissage", "défrisage", "coloration", "coiffure mariage"],
        specialties=["Cheveux crépus", "Tissage premium", "Coiffure mariage", "Soin capillaire"],
        bio="Salon ouvert depuis 2015 à Analakely. Équipe de 5 coiffeuses. Spécialité cheveux afro-malgaches.",
        city="Antananarivo", country="Madagascar", address="Rue Rainibetsimisaraka, Analakely",
        latitude=_tana("Analakely")[0], longitude=_tana("Analakely")[1],
        languages=["mg", "fr"],
        verified=True, rating=4.6, years_experience=10, team_size=5,
        accepts_payment=["cash", "mvola", "orange_money", "card"],
        hourly_rate=0, min_price=15000, max_price=350000, currency="Ar",
        phone="+261 34 78 901 23", email="salon.voahangy@mg.com",
        services_detail=[
            ServiceDetail(name="Coupe femme", price=25000, currency="Ar", duration_min=45, options=["in_office", "home_visit"]),
            ServiceDetail(name="Tissage complet", price=120000, currency="Ar", duration_min=180, options=["in_office"]),
            ServiceDetail(name="Forfait mariage", price=320000, currency="Ar", duration_min=240, options=["home_visit"]),
        ],
    ),
    Prestataire(
        name="Manuhair Vola",
        specialty="Manucure & soins ongles",
        category="beauty",
        description="Spécialiste manucure, pose ongles gel, French nails, déco artistique. Intervention à domicile possible.",
        services=["manucure", "pose ongles", "French", "nail art"],
        bio="3 ans dans le métier, formée à Réunion. Style minimaliste et créatif.",
        city="Antananarivo", country="Madagascar", address="Ankorondrano",
        latitude=_tana("Ankorondrano")[0], longitude=_tana("Ankorondrano")[1],
        languages=["mg", "fr"],
        rating=4.5, years_experience=3,
        accepts_payment=["mvola", "orange_money"],
        hourly_rate=0, min_price=20000, max_price=80000, currency="Ar",
        phone="+261 33 44 567 89",
        services_detail=[
            ServiceDetail(name="Manucure simple", price=20000, currency="Ar", duration_min=45, options=["home_visit", "in_office"]),
            ServiceDetail(name="Pose gel + nail art", price=75000, currency="Ar", duration_min=120, options=["home_visit", "in_office"]),
        ],
    ),
    Prestataire(
        name="Mialy Massage",
        specialty="Massage bien-être",
        category="healthcare",
        description="Masseuse formée à la kinésithérapie traditionnelle malgache (kabarana). Massages relaxants et thérapeutiques.",
        services=["massage relaxant", "kabarana", "réflexologie", "massage prénatal"],
        specialties=["Kabarana traditionnel", "Massage prénatal", "Réflexologie plantaire"],
        bio="Diplôme IFP. 8 ans d'expérience. Mélange techniques modernes et savoir-faire malgache.",
        city="Antananarivo", country="Madagascar", address="Ivandry",
        latitude=_tana("Ivandry")[0], longitude=_tana("Ivandry")[1],
        languages=["mg", "fr"],
        verified=True, rating=4.9, years_experience=8,
        accepts_payment=["cash", "mvola"],
        hourly_rate=0, min_price=40000, max_price=120000, currency="Ar",
        phone="+261 34 91 234 56",
        services_detail=[
            ServiceDetail(name="Massage 60 min", price=70000, currency="Ar", duration_min=60, options=["home_visit", "in_office"]),
            ServiceDetail(name="Massage 90 min + huiles", price=110000, currency="Ar", duration_min=90, options=["home_visit", "in_office"]),
        ],
    ),

    # ── Construction (3) ─────────────────────────────────────────────────────
    Prestataire(
        name="Rabe Maçon",
        organization="Rabe BTP",
        specialty="Maçonnerie",
        category="construction",
        description="Entreprise BTP spécialisée construction maison individuelle, agrandissement et rénovation.",
        services=["construction maison", "agrandissement", "rénovation", "carrelage", "toiture"],
        specialties=["Maison clé en main", "Rénovation patrimoine", "Carrelage"],
        bio="Équipe de 12 maçons. Réalise 30+ chantiers/an sur Tana et périphérie. Devis détaillé en 48h.",
        city="Antananarivo", country="Madagascar", address="Tanjombato",
        latitude=_tana("Tanjombato")[0], longitude=_tana("Tanjombato")[1],
        languages=["mg", "fr"],
        verified=True, rating=4.4, years_experience=20, team_size=12,
        accepts_payment=["cash", "bank_transfer", "mvola"],
        certifications=["Inscription registre BTP Madagascar"],
        hourly_rate=0, min_price=500000, max_price=120000000, currency="Ar",
        phone="+261 34 65 789 12",
        services_detail=[
            ServiceDetail(name="Visite chantier + devis", price=0, currency="Ar", duration_min=90, options=["home_visit"]),
            ServiceDetail(name="Mur parpaing 10 m²", price=850000, currency="Ar", duration_min=480, options=["home_visit"]),
        ],
    ),
    Prestataire(
        name="Naivo Peintre",
        specialty="Peinture & finition",
        category="construction",
        description="Peintre en bâtiment, intérieur et façade. Travail soigné, finitions premium.",
        services=["peinture intérieure", "façade", "papier peint", "enduit décoratif"],
        bio="10 ans dans la peinture résidentielle. Travail propre, respect des délais.",
        city="Antananarivo", country="Madagascar", address="Soavimbahoaka",
        latitude=_tana("Soavimbahoaka")[0], longitude=_tana("Soavimbahoaka")[1],
        languages=["mg", "fr"],
        rating=4.5, years_experience=10, team_size=2,
        accepts_payment=["cash", "mvola", "orange_money"],
        hourly_rate=15000, min_price=80000, max_price=4000000, currency="Ar",
        phone="+261 33 87 456 23",
    ),
    Prestataire(
        name="Soa Carrelage",
        specialty="Pose carrelage & faïence",
        category="construction",
        description="Pose de carrelage sol et mur, faïence salle de bain et cuisine. Travaux propres et alignés.",
        services=["carrelage sol", "faïence cuisine", "salle de bain", "extérieur terrasse"],
        city="Antananarivo", country="Madagascar", address="Antaninarenina",
        latitude=_tana("Antaninarenina")[0], longitude=_tana("Antaninarenina")[1],
        languages=["mg", "fr"],
        rating=4.6, years_experience=8,
        accepts_payment=["cash", "mvola"],
        hourly_rate=20000, min_price=120000, max_price=2500000, currency="Ar",
        phone="+261 34 22 988 76",
    ),

    # ── Mécanique auto / moto (2) ────────────────────────────────────────────
    Prestataire(
        name="Garage Tafita",
        organization="Garage Tafita SARL",
        specialty="Mécanique automobile",
        category="mechanic",
        description="Garage tous véhicules, vidange, embrayage, suspension, climatisation. Spécialiste Renault, Peugeot, Toyota.",
        services=["vidange", "embrayage", "suspension", "diagnostic OBD", "climatisation auto"],
        specialties=["Renault", "Peugeot", "Toyota Hilux", "Diagnostic OBD II"],
        bio="Garage Antaninarenina depuis 2008. Équipe de 6 mécaniciens diplômés. Devis transparent.",
        city="Antananarivo", country="Madagascar", address="Antaninarenina, près du marché",
        latitude=_tana("Antaninarenina")[0], longitude=_tana("Antaninarenina")[1],
        languages=["mg", "fr"],
        verified=True, rating=4.5, years_experience=17, team_size=6,
        accepts_payment=["cash", "mvola", "bank_transfer"],
        hourly_rate=20000, min_price=30000, max_price=4500000, currency="Ar",
        phone="+261 34 11 223 34", email="contact@garagetafita.mg",
        services_detail=[
            ServiceDetail(name="Vidange complète", price=85000, currency="Ar", duration_min=60, options=["in_office"]),
            ServiceDetail(name="Diagnostic électronique", price=40000, currency="Ar", duration_min=45, options=["in_office", "video_call"]),
        ],
    ),
    Prestataire(
        name="Faly Moto",
        specialty="Mécanique moto & scooter",
        category="mechanic",
        description="Spécialiste mécanique deux-roues, entretien, embrayage, carburateur, électrique scooter et motos chinoises.",
        services=["entretien moto", "réparation", "carburateur", "transmission"],
        city="Antananarivo", country="Madagascar", address="Ambohimanarina",
        latitude=_tana("Ambohimanarina")[0], longitude=_tana("Ambohimanarina")[1],
        languages=["mg"],
        rating=4.4, years_experience=7,
        accepts_payment=["cash", "mvola"],
        hourly_rate=12000, min_price=8000, max_price=350000, currency="Ar",
        phone="+261 33 77 119 22",
    ),

    # ── Tech / Dev web (2) ───────────────────────────────────────────────────
    Prestataire(
        name="Andry Dev",
        organization="Andry Studio",
        specialty="Développeur web fullstack",
        category="tech",
        description="Développeur web freelance React, Next.js, Node.js. Sites e-commerce, vitrines, dashboards. Travail à distance worldwide.",
        services=["site vitrine", "e-commerce", "dashboard", "API REST", "mobile app"],
        specialties=["React/Next.js", "Node.js", "PostgreSQL", "Stripe payment", "Mobile money integration"],
        bio="MSc Informatique. 7 ans dev fullstack. Spécialiste paiement mobile money MGA pour startups locales.",
        city="Antananarivo", country="Madagascar",
        latitude=_tana("Ankorondrano")[0], longitude=_tana("Ankorondrano")[1],
        languages=["mg", "fr", "en"],
        verified=True, rating=5.0, years_experience=7, response_time_hours=4,
        accepts_payment=["mvola", "card", "bank_transfer"],
        certifications=["MSc Informatique", "AWS Certified"],
        hourly_rate=80000, min_price=300000, max_price=25000000, currency="Ar",
        phone="+261 34 91 882 17", email="andry@andry.dev",
        services_detail=[
            ServiceDetail(name="Site vitrine 5 pages", price=1800000, currency="Ar", duration_min=2400, options=["video_call"]),
            ServiceDetail(name="Audit + devis", price=0, currency="Ar", duration_min=45, options=["video_call"]),
            ServiceDetail(name="Maintenance mensuelle", price=350000, currency="Ar", duration_min=0, options=["video_call"]),
        ],
    ),
    Prestataire(
        name="Sandratra Mobile",
        specialty="Développeur mobile Flutter",
        category="tech",
        description="Apps mobiles Flutter cross-platform iOS + Android. Intégration paiement Mvola, Orange Money, Airtel Money.",
        services=["app Flutter", "intégration paiement mobile", "publication stores"],
        bio="5 ans Flutter. 12+ apps publiées sur Play Store.",
        city="Antananarivo", country="Madagascar",
        latitude=_tana("Ivandry")[0], longitude=_tana("Ivandry")[1],
        languages=["mg", "fr", "en"],
        rating=4.8, years_experience=5,
        accepts_payment=["mvola", "card", "bank_transfer"],
        hourly_rate=65000, min_price=400000, max_price=18000000, currency="Ar",
        phone="+261 33 90 712 45",
    ),

    # ── Photographie / événement (2) ────────────────────────────────────────
    Prestataire(
        name="Lova Photo",
        organization="Lova Studio",
        specialty="Photographe événement",
        category="photo",
        description="Photographe mariage, événementiel et corporate. Studio à Antaninarenina et déplacement national.",
        services=["mariage", "événementiel", "portrait corporate", "produit"],
        specialties=["Mariage", "Corporate", "Studio packshot"],
        bio="12 ans dans la photo événementielle. Équipement Sony A7R V + lumières studio.",
        city="Antananarivo", country="Madagascar", address="Antaninarenina",
        latitude=_tana("Antaninarenina")[0], longitude=_tana("Antaninarenina")[1],
        languages=["mg", "fr", "en"],
        verified=True, rating=4.8, years_experience=12, team_size=2,
        accepts_payment=["cash", "mvola", "card", "bank_transfer"],
        hourly_rate=0, min_price=350000, max_price=12000000, currency="Ar",
        phone="+261 34 56 234 11", email="lova@lovaphoto.mg",
        services_detail=[
            ServiceDetail(name="Mariage demi-journée", price=2500000, currency="Ar", duration_min=240, options=["home_visit"]),
            ServiceDetail(name="Packshot produit (10 visuels)", price=550000, currency="Ar", duration_min=180, options=["in_office", "home_visit"]),
        ],
    ),
    Prestataire(
        name="Riva Photographer",
        specialty="Photo de famille",
        category="photo",
        description="Photos de famille en extérieur, séances grossesse, nouveau-né. Style naturel et lumineux.",
        services=["photo famille", "maternité", "nouveau-né", "anniversaire"],
        city="Antananarivo", country="Madagascar", address="Ambatobe",
        latitude=_tana("Ambatobe")[0], longitude=_tana("Ambatobe")[1],
        languages=["mg", "fr"],
        rating=4.6, years_experience=4,
        accepts_payment=["mvola", "orange_money"],
        hourly_rate=0, min_price=180000, max_price=900000, currency="Ar",
        phone="+261 33 27 451 80",
    ),

    # ── Couture & artisanat (2) ──────────────────────────────────────────────
    Prestataire(
        name="Atelier Bao",
        organization="Atelier Bao",
        specialty="Couture sur mesure",
        category="tailoring",
        description="Atelier de couture, robes lamba, costumes hommes, retouches, broderie traditionnelle malgache.",
        services=["robe sur mesure", "costume", "retouche", "broderie", "lamba"],
        specialties=["Lamba traditionnel", "Robe mariage", "Costume sur mesure"],
        bio="Atelier familial depuis 1998. Maîtrise du tissage lamba akotofahana.",
        city="Antananarivo", country="Madagascar", address="Analakely, rue de la victoire",
        latitude=_tana("Analakely")[0], longitude=_tana("Analakely")[1],
        languages=["mg", "fr"],
        verified=True, rating=4.7, years_experience=26, team_size=4,
        accepts_payment=["cash", "mvola"],
        hourly_rate=0, min_price=15000, max_price=1500000, currency="Ar",
        phone="+261 34 33 444 12",
        services_detail=[
            ServiceDetail(name="Retouche standard", price=15000, currency="Ar", duration_min=60, options=["in_office"]),
            ServiceDetail(name="Robe sur mesure", price=380000, currency="Ar", duration_min=600, options=["in_office"]),
        ],
    ),
    Prestataire(
        name="Hanta Couturière",
        specialty="Couture femme",
        category="tailoring",
        description="Couture femme rapide, retouches express. Spécialité tenues bureau et soirée.",
        services=["retouche", "robe", "jupe", "blazer"],
        city="Antananarivo", country="Madagascar", address="Soanierana",
        latitude=_tana("Soanierana")[0], longitude=_tana("Soanierana")[1],
        languages=["mg"],
        rating=4.3, years_experience=6,
        accepts_payment=["cash", "mvola"],
        hourly_rate=0, min_price=10000, max_price=400000, currency="Ar",
        phone="+261 33 99 232 14",
    ),

    # ── Restauration / traiteur (2) ──────────────────────────────────────────
    Prestataire(
        name="Traiteur Vary",
        organization="Vary Traiteur",
        specialty="Cuisine malgache traditionnelle",
        category="food",
        description="Traiteur cuisine malgache et internationale pour événements. Romazava, ravitoto, ro-mavo... Service buffet 50-500 personnes.",
        services=["buffet", "cocktail dînatoire", "plats malgaches", "wedding cake"],
        specialties=["Cuisine malgache authentique", "Buffet événementiel", "Wedding cake"],
        bio="Cheffe formée Institut Hôtelier d'Antananarivo. 15 ans en traiteur de luxe.",
        city="Antananarivo", country="Madagascar", address="Ankorondrano",
        latitude=_tana("Ankorondrano")[0], longitude=_tana("Ankorondrano")[1],
        languages=["mg", "fr", "en"],
        verified=True, rating=4.9, years_experience=15, team_size=10,
        accepts_payment=["cash", "mvola", "card", "bank_transfer"],
        hourly_rate=0, min_price=25000, max_price=15000000, currency="Ar",
        phone="+261 34 88 901 32", email="vary@varytraiteur.mg",
        services_detail=[
            ServiceDetail(name="Buffet par personne", price=45000, currency="Ar", duration_min=0, options=["home_visit"]),
            ServiceDetail(name="Cocktail dînatoire 100 pers.", price=4500000, currency="Ar", duration_min=240, options=["home_visit"]),
        ],
    ),
    Prestataire(
        name="Chef Mahery",
        specialty="Chef à domicile",
        category="food",
        description="Chef privé pour repas à domicile, dîners romantiques, anniversaires. Cuisine fusion malgache-française.",
        services=["chef à domicile", "menu sur mesure", "dîner romantique"],
        city="Antananarivo", country="Madagascar", address="Ivandry",
        latitude=_tana("Ivandry")[0], longitude=_tana("Ivandry")[1],
        languages=["mg", "fr"],
        rating=4.7, years_experience=8,
        accepts_payment=["mvola", "card"],
        hourly_rate=0, min_price=180000, max_price=1500000, currency="Ar",
        phone="+261 33 56 123 45",
        services_detail=[
            ServiceDetail(name="Dîner 2 personnes", price=320000, currency="Ar", duration_min=240, options=["home_visit"]),
        ],
    ),

    # ── Tourisme / Guide (1) ─────────────────────────────────────────────────
    Prestataire(
        name="Faly Guide",
        specialty="Guide touristique Madagascar",
        category="tourism",
        description="Guide professionnel, circuits sur mesure Madagascar : RN7, baobabs, Nosy Be, Andasibe. Anglais et français.",
        services=["circuits Madagascar", "trek nature", "réservation lodges", "transport 4x4"],
        specialties=["RN7 Tana-Tulear", "Baobabs Morondava", "Andasibe forêt", "Nosy Be"],
        bio="Guide certifié ONTM. 18 ans d'expérience. Véhicule 4x4 et équipement camping inclus.",
        city="Antananarivo", country="Madagascar",
        languages=["mg", "fr", "en"],
        verified=True, rating=5.0, years_experience=18,
        accepts_payment=["cash", "mvola", "card", "bank_transfer"],
        certifications=["Guide ONTM officiel"],
        hourly_rate=0, min_price=200000, max_price=18000000, currency="Ar",
        phone="+261 34 22 558 90", email="faly@falyguide.mg",
        services_detail=[
            ServiceDetail(name="Journée guidée Tana", price=350000, currency="Ar", duration_min=480, options=["home_visit", "video_call"]),
            ServiceDetail(name="Circuit RN7 8 jours", price=12000000, currency="Ar", duration_min=0, options=["video_call"]),
        ],
    ),

    # ── Tutorat scolaire (1) ────────────────────────────────────────────────
    Prestataire(
        name="Tahiana Maths",
        specialty="Tutorat maths & physique",
        category="tutoring",
        description="Cours particuliers maths/physique lycée et préparation bac. À domicile ou en visio.",
        services=["maths lycée", "physique", "prépa bac", "prépa concours"],
        bio="Diplômé Polytechnique Antananarivo. 5 ans d'expérience tutorat.",
        city="Antananarivo", country="Madagascar", address="Antanimena",
        latitude=_tana("Antanimena")[0], longitude=_tana("Antanimena")[1],
        languages=["mg", "fr"],
        rating=4.8, years_experience=5,
        accepts_payment=["mvola", "orange_money"],
        hourly_rate=25000, min_price=20000, max_price=50000, currency="Ar",
        phone="+261 34 78 100 23",
        services_detail=[
            ServiceDetail(name="Cours individuel 1h", price=25000, currency="Ar", duration_min=60, options=["home_visit", "video_call"]),
            ServiceDetail(name="Forfait 10 cours", price=220000, currency="Ar", duration_min=600, options=["home_visit", "video_call"]),
        ],
    ),

    # ── Jardinage / Nettoyage (1) ───────────────────────────────────────────
    Prestataire(
        name="Jardin Voara",
        specialty="Jardinage & espaces verts",
        category="gardening",
        description="Entretien jardins, taille haie, élagage, création potager, gazon synthétique.",
        services=["taille", "élagage", "potager", "gazon", "irrigation"],
        bio="Équipe de 4 jardiniers. Matériel pro. Contrats mensuels possibles.",
        city="Antananarivo", country="Madagascar", address="Tanjombato",
        latitude=_tana("Tanjombato")[0], longitude=_tana("Tanjombato")[1],
        languages=["mg", "fr"],
        rating=4.4, years_experience=11, team_size=4,
        accepts_payment=["cash", "mvola", "bank_transfer"],
        hourly_rate=12000, min_price=80000, max_price=2500000, currency="Ar",
        phone="+261 33 49 887 22",
    ),

    # ── Déménagement (1) ────────────────────────────────────────────────────
    Prestataire(
        name="Mavo Transport",
        organization="Mavo Transport SARL",
        specialty="Déménagement & transport",
        category="moving",
        description="Déménagement résidentiel et professionnel. Camion 5T, équipe formée, emballage et démontage.",
        services=["déménagement", "transport lourd", "emballage", "stockage"],
        bio="Camion 5T avec hayon élévateur. 6 manutentionnaires expérimentés. Devis sous 24h.",
        city="Antananarivo", country="Madagascar", address="Tanjombato",
        latitude=_tana("Tanjombato")[0], longitude=_tana("Tanjombato")[1],
        languages=["mg", "fr"],
        verified=True, rating=4.5, years_experience=9, team_size=6,
        accepts_payment=["cash", "mvola", "bank_transfer"],
        hourly_rate=0, min_price=350000, max_price=8000000, currency="Ar",
        phone="+261 34 90 654 21", email="mavo@mavotransport.mg",
        services_detail=[
            ServiceDetail(name="Devis déménagement", price=0, currency="Ar", duration_min=60, options=["home_visit", "video_call"]),
            ServiceDetail(name="Déménagement F3 intra-Tana", price=850000, currency="Ar", duration_min=480, options=["home_visit"]),
        ],
    ),
]


async def load_seed_prestataires(store: PGVectorStore, embed_svc: EmbeddingService) -> None:
    """Embed and insert seed prestataires only if the table is empty."""
    current = await store.count
    if current and current >= len(SEED_PRESTATAIRES):
        logger.info("Seed skipped · %d prestataires already in DB", current)
        return
    logger.info("Seeding %d prestataires (current=%d)…", len(SEED_PRESTATAIRES), current)
    success = 0
    for i, p in enumerate(SEED_PRESTATAIRES, start=1):
        try:
            embedding = embed_svc.embed_prestataire(p)
        except ClientError as e:
            logger.warning("Embedding skipped for %s: %s", p.name, e)
            continue
        except Exception as e:  # noqa: BLE001
            logger.warning("Embedding failed for %s: %s", p.name, e)
            continue
        await store.add(p, embedding)
        success += 1
        if i % 5 == 0:
            await asyncio.sleep(0.4)  # gentle pacing for the embedding rate limits
    logger.info("Seed complete · %d/%d prestataires inserted", success, len(SEED_PRESTATAIRES))
