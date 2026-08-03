"""Monthly content & design packages — what ZYNTH actually sells per month.

Every retainer is defined here ONCE so the strategist, the content creator,
the designer, the .docx export, and the price quoted to the client all agree
on the same numbers: how many posts, which content types, how many of those
posts need original design work (the content:design ratio), how many stories
and videos, revision rounds, and the price band.

Tiers (posts per month): 8 · 10 · 16 · 30.

Ratio language used across the studio:
  content_pieces  = every scheduled item that needs copy (feed posts)
  designed_assets = the subset that needs an original designed visual
                    (static, carousel frames, motion cover, thumbnail)
  ratio           = designed_assets : content_pieces, e.g. "6:8" (75%)

Prices are MMK/SGD bands at ZYNTH's standard margin (35% floor / 40% target).
They are BANDS — the strategist prices inside the band for the specific brand,
and every figure a client sees goes through the normal FX/market rules.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

# Content types the studio can schedule. Keep this list closed — the agents
# choose from it so the calendar, the design specs, and the .docx tables all
# speak the same vocabulary.
CONTENT_TYPES: list[str] = [
    "static_post",       # single designed image
    "carousel",          # 3-8 designed frames, one story arc
    "short_video",       # reel / TikTok, 9:16, 15-30s
    "story_set",         # 3-5 story frames, lightweight design
    "ugc_style",         # creator-look, low production, high trust
    "photo_post",        # real photography, minimal graphic treatment
    "text_led",          # copy-first, minimal design (quote, announcement)
    "engagement",        # poll, question, comment-bait
    "promo_offer",       # price/offer led, hard CTA
    "educational",       # how-to, explainer, tips
    "testimonial",       # proof, review, case result
    "behind_the_scenes",
]


@dataclass(frozen=True)
class ContentPackage:
    """One monthly retainer tier."""

    key: str
    name: str
    posts_per_month: int
    designed_assets: int          # posts needing original design work
    short_videos: int             # of the posts above, how many are video
    story_sets: int               # extra, on top of posts_per_month
    platforms: list[str]
    type_mix: dict[str, int]      # content_type -> count, sums to posts_per_month
    revision_rounds: int
    boosted_posts: int            # posts recommended for paid amplification
    reporting: str
    price_mmk: str
    price_sgd: str
    best_for: str
    #: Hours of ZYNTH effort assumed when checking the margin floor.
    effort_hours: float = 0.0

    @property
    def copy_only_posts(self) -> int:
        """Posts that need copy but no original designed asset."""
        return self.posts_per_month - self.designed_assets

    @property
    def design_ratio(self) -> str:
        """designed_assets : content_pieces, e.g. '6:8'."""
        return f"{self.designed_assets}:{self.posts_per_month}"

    @property
    def design_ratio_pct(self) -> int:
        if not self.posts_per_month:
            return 0
        return round(100 * self.designed_assets / self.posts_per_month)

    @property
    def posts_per_week(self) -> float:
        return round(self.posts_per_month / 4.0, 1)

    def as_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d.update(
            design_ratio=self.design_ratio,
            design_ratio_pct=self.design_ratio_pct,
            copy_only_posts=self.copy_only_posts,
            posts_per_week=self.posts_per_week,
        )
        return d

    def as_prompt_block(self) -> str:
        """The package as an instruction block for the studio agents."""
        mix = " · ".join(f"{count}× {name}" for name, count in self.type_mix.items() if count)
        return (
            f"PACKAGE: {self.name} ({self.key})\n"
            f"- Volume: {self.posts_per_month} feed posts/month (~{self.posts_per_week}/week) "
            f"+ {self.story_sets} story sets\n"
            f"- Content:design ratio: {self.design_ratio} "
            f"({self.design_ratio_pct}% of posts get an original designed asset; "
            f"{self.copy_only_posts} are copy-led/photo/UGC with light treatment)\n"
            f"- Video: {self.short_videos} short videos included\n"
            f"- Type mix (must match EXACTLY): {mix}\n"
            f"- Platforms: {', '.join(self.platforms)}\n"
            f"- Paid amplification: {self.boosted_posts} posts flagged to boost\n"
            f"- Revisions: {self.revision_rounds} round(s) · Reporting: {self.reporting}\n"
            f"- Investment band: {self.price_mmk} / {self.price_sgd} per month\n"
            f"- Best for: {self.best_for}"
        )


PACKAGES: dict[str, ContentPackage] = {
    "starter_8": ContentPackage(
        key="starter_8",
        name="Starter — 8 posts/month",
        posts_per_month=8,
        designed_assets=6,
        short_videos=2,
        story_sets=4,
        platforms=["Facebook", "Instagram"],
        type_mix={
            "static_post": 3,
            "carousel": 1,
            "short_video": 2,
            "educational": 1,
            "engagement": 1,
        },
        revision_rounds=1,
        boosted_posts=2,
        reporting="Monthly 1-page performance summary",
        price_mmk="MMK 1,800,000 – 2,600,000",
        price_sgd="S$750 – 1,100",
        best_for="SMEs proving the channel works before scaling",
        effort_hours=22,
    ),
    "core_10": ContentPackage(
        key="core_10",
        name="Core — 10 posts/month",
        posts_per_month=10,
        designed_assets=7,
        short_videos=3,
        story_sets=6,
        platforms=["Facebook", "Instagram", "TikTok"],
        type_mix={
            "static_post": 3,
            "carousel": 2,
            "short_video": 3,
            "educational": 1,
            "testimonial": 1,
        },
        revision_rounds=2,
        boosted_posts=3,
        reporting="Monthly report + mid-month check-in",
        price_mmk="MMK 2,400,000 – 3,400,000",
        price_sgd="S$1,000 – 1,450",
        best_for="Brands with a steady offer and one clear growth goal",
        effort_hours=28,
    ),
    "growth_16": ContentPackage(
        key="growth_16",
        name="Growth — 16 posts/month",
        posts_per_month=16,
        designed_assets=11,
        short_videos=5,
        story_sets=10,
        platforms=["Facebook", "Instagram", "TikTok", "LinkedIn"],
        type_mix={
            "static_post": 4,
            "carousel": 3,
            "short_video": 5,
            "educational": 2,
            "testimonial": 1,
            "promo_offer": 1,
        },
        revision_rounds=2,
        boosted_posts=5,
        reporting="Monthly report + fortnightly optimisation call",
        price_mmk="MMK 3,800,000 – 5,400,000",
        price_sgd="S$1,600 – 2,300",
        best_for="Brands pushing for share of voice across 3-4 platforms",
        effort_hours=44,
    ),
    "dominate_30": ContentPackage(
        key="dominate_30",
        name="Dominate — 30 posts/month",
        posts_per_month=30,
        designed_assets=19,
        short_videos=10,
        story_sets=20,
        platforms=["Facebook", "Instagram", "TikTok", "LinkedIn", "YouTube Shorts"],
        type_mix={
            "static_post": 6,
            "carousel": 5,
            "short_video": 10,
            "ugc_style": 3,
            "educational": 2,
            "testimonial": 2,
            "promo_offer": 1,
            "behind_the_scenes": 1,
        },
        revision_rounds=3,
        boosted_posts=9,
        reporting="Weekly dashboard + monthly strategic review",
        price_mmk="MMK 6,500,000 – 9,500,000",
        price_sgd="S$2,750 – 4,000",
        best_for="Daily-presence brands, launches, and category leaders",
        effort_hours=78,
    ),
}

#: Aliases the MD (or a client) is likely to type.
_ALIASES: dict[str, str] = {
    "8": "starter_8", "starter": "starter_8", "basic": "starter_8",
    "10": "core_10", "core": "core_10", "standard": "core_10",
    "16": "growth_16", "growth": "growth_16",
    "30": "dominate_30", "dominate": "dominate_30", "daily": "dominate_30",
}

DEFAULT_PACKAGE = "growth_16"


def resolve_package(spec: str | int | None) -> ContentPackage:
    """Resolve '16', 'growth', 'growth_16', 16 → the package. Falls back to default."""
    if spec is None:
        return PACKAGES[DEFAULT_PACKAGE]
    key = str(spec).strip().lower().replace("-", "_").replace(" ", "_")
    if key in PACKAGES:
        return PACKAGES[key]
    if key in _ALIASES:
        return PACKAGES[_ALIASES[key]]
    # "16 posts", "16/month", "16 posts per month"
    digits = "".join(ch for ch in key if ch.isdigit())
    if digits in _ALIASES:
        return PACKAGES[_ALIASES[digits]]
    if digits:
        # Closest tier by volume so an odd ask (12, 20) still gets a sane plan.
        target = int(digits)
        return min(PACKAGES.values(), key=lambda p: abs(p.posts_per_month - target))
    return PACKAGES[DEFAULT_PACKAGE]


def packages_table() -> list[list[str]]:
    """Rows for the comparison table rendered into client documents."""
    rows = []
    for p in PACKAGES.values():
        rows.append([
            p.name,
            str(p.posts_per_month),
            f"{p.design_ratio} ({p.design_ratio_pct}%)",
            str(p.short_videos),
            str(p.story_sets),
            ", ".join(p.platforms),
            p.price_mmk,
            p.price_sgd,
        ])
    return rows


PACKAGES_TABLE_HEADERS = [
    "Package", "Posts/mo", "Content:design", "Videos", "Story sets",
    "Platforms", "Investment (MMK)", "Investment (SGD)",
]


def packages_overview() -> str:
    """Short text summary of all tiers — used in help text and prompts."""
    return "\n".join(
        f"- {p.name}: {p.design_ratio} design ratio · {p.short_videos} videos · "
        f"{p.price_mmk} / {p.price_sgd}"
        for p in PACKAGES.values()
    )


__all__ = [
    "CONTENT_TYPES", "ContentPackage", "PACKAGES", "DEFAULT_PACKAGE",
    "resolve_package", "packages_table", "PACKAGES_TABLE_HEADERS", "packages_overview",
]
