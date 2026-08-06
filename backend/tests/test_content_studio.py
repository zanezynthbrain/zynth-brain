"""Content & Design Studio tests — packages, brand kit, pipeline, export (offline)."""

import pytest

from agents.content_studio import (
    BrandStrategistAgent,
    ContentCreatorAgent,
    DesignDirectorAgent,
    DesignerAgent,
    _reconcile,
    plan_to_sections,
    ratio_report,
    render_specs,
    run_content_studio,
)
from config.content_packages import PACKAGES, resolve_package
from utils.state import SharedMemory


# --- Packages: the contract the client is invoiced against -----------------

def test_every_package_type_mix_sums_to_its_post_count():
    for package in PACKAGES.values():
        assert sum(package.type_mix.values()) == package.posts_per_month, package.key
        assert package.designed_assets <= package.posts_per_month
        assert package.copy_only_posts == package.posts_per_month - package.designed_assets


def test_design_ratio_reporting():
    growth = PACKAGES["growth_16"]
    assert growth.design_ratio == "11:16"
    assert growth.design_ratio_pct == 69
    assert growth.posts_per_week == 4.0


@pytest.mark.parametrize(
    "spec,expected",
    [
        ("8", "starter_8"), (8, "starter_8"), ("starter", "starter_8"),
        ("10", "core_10"), ("16", "growth_16"), ("growth_16", "growth_16"),
        ("30", "dominate_30"), ("daily", "dominate_30"),
        ("16 posts per month", "growth_16"),
        (None, "growth_16"), ("nonsense", "growth_16"),
        ("12", "core_10"),  # odd ask snaps to the closest tier
    ],
)
def test_resolve_package(spec, expected):
    assert resolve_package(spec).key == expected


def test_package_prompt_block_states_the_ratio():
    block = PACKAGES["dominate_30"].as_prompt_block()
    assert "19:30" in block and "30 feed posts/month" in block
    assert "10× short_video" in block


# --- Brand kit --------------------------------------------------------------

def test_brand_block_uses_stored_profile_and_flags_unknown_brands(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    from utils import brands as BR

    block = BR.brand_block("ZYNTH")
    assert "authoritative" in block and "The Intelligence of Creativity" in block

    missing = BR.brand_block("Some Brand That Isn't On File")
    assert "No stored profile" in missing and "do NOT" in missing


def test_add_brand_persists_and_updates(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    from utils import brands as BR

    BR.add_brand({"brand": "Golden Duck", "industry": "F&B",
                  "target_audience": "Yangon office workers 25-35"})
    found = BR.find("golden duck")
    assert found and found["industry"] == "F&B"

    BR.add_brand({"brand": "Golden Duck", "tone": "playful but premium"})
    updated = BR.find("Golden Duck")
    assert updated["tone"] == "playful but premium"
    assert updated["industry"] == "F&B"  # existing fields survive an update
    assert len([b for b in BR.all_brands() if b["brand"] == "Golden Duck"]) == 1


def test_add_brand_requires_a_name(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    from utils import brands as BR
    with pytest.raises(ValueError):
        BR.add_brand({"industry": "F&B"})


# --- Reconciliation: the package wins, not the model ------------------------

def test_reconcile_trims_and_holds_the_design_ratio():
    package = PACKAGES["starter_8"]  # 8 posts, 6 designed, 2 boosted
    content = {"posts": [
        {"content_type": "static_post", "needs_design": True, "boost": True} for _ in range(12)
    ]}

    result = _reconcile(content, package)
    posts = result["posts"]

    assert len(posts) == package.posts_per_month
    assert sum(1 for p in posts if p["needs_design"]) == package.designed_assets
    assert sum(1 for p in posts if p.get("boost")) == package.boosted_posts
    assert [p["ref"] for p in posts[:3]] == ["P01", "P02", "P03"]
    assert any("Trimmed" in note for note in result["package_adjustments"])


def test_reconcile_promotes_posts_to_reach_the_ratio():
    package = PACKAGES["starter_8"]
    content = {"posts": [{"content_type": "text_led"} for _ in range(8)]}

    result = _reconcile(content, package)

    assert sum(1 for p in result["posts"] if p.get("needs_design")) == package.designed_assets
    assert any("Promoted" in note for note in result["package_adjustments"])


def test_reconcile_reports_a_short_month_instead_of_faking_posts():
    package = PACKAGES["growth_16"]
    content = {"posts": [{"content_type": "static_post"} for _ in range(9)]}

    result = _reconcile(content, package)

    assert len(result["posts"]) == 9
    assert any("slot(s) left open" in note for note in result["package_adjustments"])


def test_ratio_report_counts_the_month():
    package = PACKAGES["starter_8"]
    content = {"posts": [
        {"content_type": "short_video", "platform": "TikTok", "pillar": "Proof",
         "needs_design": True, "boost": True},
        {"content_type": "text_led", "platform": "Facebook", "pillar": "Proof"},
    ]}

    report = ratio_report(content, package)

    assert report["posts_planned"] == 2 and report["designed_assets"] == 1
    assert report["design_ratio"] == "1:2" and report["design_ratio_pct"] == 50
    assert report["contracted_ratio"] == "6:8" and report["on_contract"] is False
    assert report["by_platform"] == {"TikTok": 1, "Facebook": 1}
    assert report["short_videos"] == 1 and report["boosted"] == 1


# --- Agents + pipeline (mock mode) ------------------------------------------

@pytest.mark.parametrize("agent_cls,required", [
    (BrandStrategistAgent, ["brand_platform", "audience", "content_pillars", "owned_strategy"]),
    (ContentCreatorAgent, ["month_theme", "posts", "story_plan"]),
    (DesignDirectorAgent, ["art_direction", "palette", "typography", "templates"]),
    (DesignerAgent, ["design_specs"]),
])
async def test_studio_agents_run_and_satisfy_their_schema(agent_cls, required):
    agent = agent_cls()
    memory = SharedMemory(client_brief={"brand": "Golden Duck"})

    result = await agent.run(memory, brand="ZYNTH", brief="premium snack brand, Yangon")

    assert result.success is True
    for field in required:
        assert field in result.data
    assert await memory.get(agent.agent_key) == result.data


async def test_agents_carry_their_operating_spec_and_brand_profile():
    system = BrandStrategistAgent().build_system_prompt()
    assert "OPERATING SPEC" in system and "Owned-Channel Strategist" in system

    prompt = await ContentCreatorAgent().build_user_prompt(
        SharedMemory(), brand="ZYNTH", brief="test", package=PACKAGES["growth_16"]
    )
    assert "BRAND PROFILE" in prompt
    assert "EXACTLY 16 posts" in prompt and "EXACTLY 11" in prompt


async def test_studio_reads_upstream_campaign_and_research_context():
    memory = SharedMemory()
    await memory.set("cmo", {"campaign_ideas": [{"name": "Snack Season"}]})
    await memory.set("research_seo", {"high_intent_keywords": [{"keyword": "salted egg snack"}]})

    prompt = await BrandStrategistAgent().build_user_prompt(memory, brand="ZYNTH", brief="x")

    assert "WHAT THE REST OF THE AGENCY HAS ALREADY DECIDED" in prompt
    assert "Snack Season" in prompt and "salted egg snack" in prompt


async def test_run_content_studio_end_to_end(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    memory = SharedMemory(client_brief={"agency": "ZYNTH"})

    plan = await run_content_studio(
        "premium salted egg snacks, Yangon, gifting occasion",
        memory, brand="ZYNTH", package="8", month="September",
    )

    assert plan["package"]["key"] == "starter_8"
    assert plan["ratio"]["posts_contracted"] == 8
    assert set(plan) >= {"strategy", "content", "design_system", "designs", "ratio", "render_specs"}
    # Every specialist wrote its namespace, so downstream agents can read them.
    for key in ("brand_strategist", "content_creator", "design_director", "designer"):
        assert await memory.get(key)
    summary = await memory.get("content_studio")
    assert summary["package"] == "starter_8"


async def test_plan_to_sections_builds_the_document(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    memory = SharedMemory()
    plan = await run_content_studio("test brief", memory, brand="ZYNTH", package="8")

    sections = plan_to_sections(plan)
    headings = [s["heading"] for s in sections]

    assert headings[:4] == [
        "Brand Strategy", "Audience & Insight",
        "Owned-Channel Strategy", "The Month — Content Calendar",
    ]
    assert "Visual System" in headings and "Design Specifications" in headings
    calendar = next(s for s in sections if s["heading"] == "The Month — Content Calendar")
    assert calendar["tables"] and calendar["tables"][0]["headers"][0] == "Ref"
    scope = next(s for s in sections if s["heading"].startswith("Scope"))
    assert "50% deposit" in scope["body"]


def test_parse_studio_request_finds_brand_and_package(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    from agents.content_studio import parse_studio_request
    from utils import brands as BR

    BR.add_brand({"brand": "Golden Duck", "industry": "F&B"})

    brand, package, brief = parse_studio_request("Golden Duck 16 gifting season push")
    assert brand == "Golden Duck" and package == "growth_16"
    assert brief == "Golden Duck gifting season push"

    # No stored brand and no tier → brief only, on the default package.
    brand, package, brief = parse_studio_request("new bubble tea brand, Yangon, Gen-Z")
    assert brand == "" and package == "growth_16"
    assert brief.startswith("new bubble tea")

    # Tier words work too, and the number can lead.
    assert parse_studio_request("30 daily presence for a gym")[1] == "dominate_30"
    assert parse_studio_request("starter package for a cafe")[1] == "starter_8"


def test_render_specs_skips_prompt_less_designs():
    designs = {"design_specs": [
        {"ref": "P01", "render_prompt": "navy studio scene, #12203A", "format": "portrait"},
        {"ref": "P02", "render_prompt": "  "},
        {"ref": "P03"},
    ]}
    specs = render_specs(designs)
    assert len(specs) == 1 and specs[0]["label"] == "P01" and specs[0]["format"] == "portrait"


# --- Orchestrator wiring ----------------------------------------------------

def test_studio_workflows_are_registered_and_acyclic():
    from agents import build_content_studio, build_default_agents
    from agents.orchestrator import WORKFLOWS, _topological_groups

    for name in ("content_studio", "brand_content_month"):
        groups = _topological_groups(WORKFLOWS[name])
        order = [step.agent_key for group in groups for step in group]
        assert order.index("brand_strategist") < order.index("content_creator")
        assert order.index("design_director") < order.index("designer")
        # the Burmese and the motion specs both wait on the finished calendar
        assert order.index("content_creator") < order.index("myanmar_copy_chief")
        assert order.index("content_creator") < order.index("motion_designer")

    studio = build_content_studio()
    assert set(studio) == {
        "brand_strategist", "content_creator", "design_director", "designer",
        "myanmar_copy_chief", "motion_designer",
    }
    # content_studio is runnable from the CLI/HTTP agent registry.
    registry = {**build_default_agents(), **studio}
    assert all(s.agent_key in registry for s in WORKFLOWS["content_studio"])


async def test_workflow_with_unregistered_agent_fails_loudly():
    from agents import OrchestratorAgent, build_default_agents

    orchestrator = OrchestratorAgent(agents=build_default_agents())
    with pytest.raises(ValueError, match="brand_strategist"):
        await orchestrator.run_workflow({"company": "Acme"}, workflow="content_studio")


async def test_content_studio_workflow_runs_through_the_qa_gate():
    from agents import OrchestratorAgent, build_content_studio

    orchestrator = OrchestratorAgent(agents=build_content_studio())
    report = await orchestrator.run_workflow({"brand": "ZYNTH"}, workflow="content_studio")

    assert set(report.agent_results) == {
        "brand_strategist", "content_creator", "design_director", "designer",
        "myanmar_copy_chief", "motion_designer",
    }
    assert all(r.success for r in report.agent_results.values())


# --- Image generation gating ------------------------------------------------

def test_imagegen_is_off_without_a_key_and_says_why():
    from utils import imagegen

    assert imagegen.is_configured() is False
    assert "OPENAI_API_KEY" in imagegen.status_note()


async def test_render_batch_returns_reasons_not_exceptions():
    from utils import imagegen

    results = await imagegen.render_batch([{"prompt": "a scene", "label": "P01"}])

    assert len(results) == 1
    assert results[0].ok is False and results[0].error
    assert await imagegen.render_batch([]) == []


def test_size_for_format_maps_platform_shapes():
    from utils.imagegen import size_for

    assert size_for("story 1080x1920") == "1024x1536"
    assert size_for("landscape 1200x627") == "1536x1024"
    assert size_for("square 1080x1080") == "1024x1024"
    assert size_for("9:16") == "1024x1536"
    assert size_for("") == "1024x1024"
