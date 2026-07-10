"""Yangon market seed data for the Operations Agent.

This is a curated starting database of venues, hotels, and supplier
categories in Yangon. The Operations Agent builds on this, researches
current pricing, and develops negotiation strategies. All prices are
estimates — mark as needing verification before client proposals.

ရန်ကုန်မြို့ရှိ event venue, hotel, supplier အချက်အလက်များ။
Operations Agent မှ ဒီ data ကို အသုံးပြုပြီး pricing နဲ့ vendor list ပြုလုပ်မည်။
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Venue:
    name: str
    category: str  # "hotel_ballroom", "convention_center", "rooftop", "outdoor"
    area: str      # Township/area in Yangon
    capacity_standing: int
    capacity_seated: int
    est_price_range: str  # e.g. "1M-3M MMK / day"
    features: list[str]
    contact_note: str = "Contact directly for current rates"
    verified: bool = False


@dataclass
class Supplier:
    name: str
    category: str  # "av_sound", "catering", "printing", "decoration", "photography", "transport"
    area: str
    est_price_range: str
    services: list[str]
    notes: str = ""


YANGON_VENUES: list[Venue] = [
    Venue(
        name="Sule Shangri-La Yangon",
        category="hotel_ballroom",
        area="Downtown (Kyauktada)",
        capacity_standing=800,
        capacity_seated=500,
        est_price_range="5M-15M MMK / event",
        features=["AV equipment", "catering", "parking", "5-star service", "central location", "breakout rooms"],
    ),
    Venue(
        name="Park Royal Yangon – Ballroom",
        category="hotel_ballroom",
        area="Mingalar Taung Nyunt",
        capacity_standing=600,
        capacity_seated=400,
        est_price_range="4M-12M MMK / event",
        features=["AV equipment", "in-house catering", "valet parking", "modern facilities"],
    ),
    Venue(
        name="Chatrium Hotel Royale – Grand Ballroom",
        category="hotel_ballroom",
        area="Strand Road (Botahtaung)",
        capacity_standing=1000,
        capacity_seated=700,
        est_price_range="6M-18M MMK / event",
        features=["riverside view", "large ballroom", "multiple breakout rooms", "AV", "catering"],
    ),
    Venue(
        name="Novotel Yangon Max",
        category="hotel_ballroom",
        area="Mingalar Taung Nyunt",
        capacity_standing=500,
        capacity_seated=350,
        est_price_range="3M-9M MMK / event",
        features=["modern AV", "catering", "parking", "corporate-friendly"],
    ),
    Venue(
        name="Pullman Yangon Centrepoint",
        category="hotel_ballroom",
        area="Tarmway",
        capacity_standing=700,
        capacity_seated=500,
        est_price_range="5M-14M MMK / event",
        features=["large ballroom", "AV equipment", "catering", "near airport"],
    ),
    Venue(
        name="Junction City Convention Hall",
        category="convention_center",
        area="Pabedan (Bogyoke area)",
        capacity_standing=2000,
        capacity_seated=1500,
        est_price_range="8M-25M MMK / event",
        features=["large exhibition space", "central Yangon", "high foot traffic", "mall integration"],
    ),
    Venue(
        name="Myanmar Convention Centre (MCC)",
        category="convention_center",
        area="Naypyitaw / Yangon (branch)",
        capacity_standing=3000,
        capacity_seated=2000,
        est_price_range="15M-50M MMK / event",
        features=["government-grade facility", "massive space", "full AV", "suitable for expos"],
    ),
    Venue(
        name="Sedona Hotel – Crystal Hall",
        category="hotel_ballroom",
        area="Inya Lake area (Kamaryut)",
        capacity_standing=600,
        capacity_seated=400,
        est_price_range="4M-10M MMK / event",
        features=["lake view", "garden option", "AV", "catering", "established venue"],
    ),
    Venue(
        name="Inya Lake Hotel – Inya Ballroom",
        category="hotel_ballroom",
        area="Inya Lake (Kamaryut)",
        capacity_standing=500,
        capacity_seated=350,
        est_price_range="3M-8M MMK / event",
        features=["historic venue", "lakeside setting", "garden available", "classic feel"],
    ),
    Venue(
        name="Pan Pacific Serviced Suites – Event Space",
        category="hotel_ballroom",
        area="Pabedan",
        capacity_standing=200,
        capacity_seated=150,
        est_price_range="2M-5M MMK / event",
        features=["boutique feel", "central", "ideal for corporate/boardroom events"],
    ),
    Venue(
        name="Zawana Garden – Outdoor Venue",
        category="outdoor",
        area="Bahan",
        capacity_standing=800,
        capacity_seated=500,
        est_price_range="2M-6M MMK / event",
        features=["garden setting", "flexible layout", "tent/marquee options", "photo-friendly"],
    ),
    Venue(
        name="Rose Garden Hotel",
        category="hotel_ballroom",
        area="Insein Road",
        capacity_standing=400,
        capacity_seated=300,
        est_price_range="2M-5M MMK / event",
        features=["mid-range budget", "outdoor garden", "in-house catering"],
    ),
]

YANGON_SUPPLIERS: list[Supplier] = [
    # AV & Sound
    Supplier(
        name="[Category: AV & Sound Supplier]",
        category="av_sound",
        area="Yangon",
        est_price_range="500K-3M MMK / event",
        services=["PA systems", "LED walls", "lighting rigs", "stage setup", "live streaming", "projectors"],
        notes="Research current vendors: ask event venues for referrals",
    ),
    # Catering
    Supplier(
        name="[Category: Catering Company]",
        category="catering",
        area="Yangon",
        est_price_range="15K-50K MMK per person",
        services=["cocktail reception", "seated dinner", "buffet", "coffee break", "branded plating"],
        notes="Many hotels offer in-house catering; external caterers 20-30% cheaper",
    ),
    # Printing & Branding
    Supplier(
        name="[Category: Print & Branding Supplier]",
        category="printing",
        area="Yangon",
        est_price_range="100K-2M MMK depending on volume",
        services=["backdrop printing", "roll-up banners", "flyers", "branded merchandise", "signage", "photo walls"],
        notes="Hledan area has many print shops; large-format printers in industrial zones",
    ),
    # Decoration & Flowers
    Supplier(
        name="[Category: Decoration & Floral]",
        category="decoration",
        area="Yangon",
        est_price_range="500K-5M MMK / event",
        services=["floral arrangements", "table centerpieces", "entrance arches", "themed decor", "prop rental"],
    ),
    # Photography & Videography
    Supplier(
        name="[Category: Photography & Video]",
        category="photography",
        area="Yangon",
        est_price_range="500K-3M MMK / event",
        services=["event photography", "videography", "live stream", "drone footage", "same-day edit"],
    ),
    # Transportation
    Supplier(
        name="[Category: Transport & Logistics]",
        category="transport",
        area="Yangon",
        est_price_range="100K-1M MMK depending on fleet",
        services=["guest transport", "VIP vehicles", "equipment logistics", "airport transfers"],
    ),
    # Entertainment
    Supplier(
        name="[Category: Entertainment & MC]",
        category="entertainment",
        area="Yangon",
        est_price_range="300K-2M MMK",
        services=["MC / host", "live band", "DJ", "cultural performances", "celebrity appearances"],
    ),
    # Security
    Supplier(
        name="[Category: Security Services]",
        category="security",
        area="Yangon",
        est_price_range="50K-200K MMK per guard per event",
        services=["event security", "crowd management", "VIP escort", "access control"],
    ),
]

YANGON_MARKET_CONTEXT = {
    "currency": "MMK (Myanmar Kyat)",
    "key_event_districts": ["Pabedan", "Mingalar Taung Nyunt", "Bahan", "Kamaryut", "Botahtaung"],
    "peak_event_season": "October–February (cool dry season)",
    "major_local_holidays": [
        "Thingyan (Water Festival) – April",
        "Myanmar New Year – April 17",
        "Independence Day – January 4",
        "Union Day – February 12",
        "Tazaungdaing Festival – November",
    ],
    "typical_corporate_event_lead_time": "4-8 weeks minimum",
    "typical_campaign_categories": [
        "product launches",
        "brand activations",
        "corporate dinners / galas",
        "trade exhibitions",
        "charity fundraisers",
        "award ceremonies",
        "press conferences",
        "pop-up activations",
    ],
    "payment_norms": "50% deposit upfront, balance 7 days before event",
    "negotiation_notes": (
        "Vendors expect negotiation; budget for 15-20% room to negotiate. "
        "Bundle services for better rates. Long-term retainers give 10-30% discount."
    ),
}


def get_venues_by_capacity(min_seated: int = 0) -> list[Venue]:
    return [v for v in YANGON_VENUES if v.capacity_seated >= min_seated]


def get_venues_by_category(category: str) -> list[Venue]:
    return [v for v in YANGON_VENUES if v.category == category]


def get_suppliers_by_category(category: str) -> list[Supplier]:
    return [s for s in YANGON_SUPPLIERS if s.category == category]
