#!/usr/bin/env python3
"""Static quality audit for ZYNTH skill and agent operating assets.

This is intentionally a structural evaluator, not an LLM judge. It makes gaps
visible and repeatable: a high score means a skill exposes the minimum operating
contracts required to be executable; it does not claim the domain advice is true.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".claude" / "skills"
AGENTS = ROOT / "backend" / "agents"
OUT = ROOT / "docs" / "ZYNTH_OPERATING_ASSET_AUDIT.md"


def lines(path: Path) -> int:
    return len(path.read_text(encoding="utf-8", errors="ignore").splitlines())


def has_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, re.I | re.M) for pattern in patterns)


def assess_skill(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    folder = path.parent
    n = len(text.splitlines())
    checks = {
        "trigger": has_any(text, [r"^description:", r"\buse (this|for)\b", r"\btrigger"]),
        "brief": has_any(text, [r"\bbrief\b", r"\binput", r"\bqualif"]),
        "workflow": has_any(text, [r"\bworkflow\b", r"\bprocess\b", r"\bsteps?\b", r"\bmethod\b"]),
        "output": has_any(text, [r"\boutput\b", r"\bdeliverable", r"output.contract"]),
        "quality": has_any(text, [r"\bquality\b", r"\bself.check", r"\breview\b", r"\bcritic\b", r"\bstandards?\b"]),
        "guardrail": has_any(text, [r"\bguardrails?\b", r"\bnever\b", r"\bapproval\b", r"\bdo not\b"]),
        "commercial": has_any(text, [r"\bbudget\b", r"\bcost", r"\bmargin\b", r"\bprice", r"\bROI\b", r"\bKPI"]),
        "references": any(p.is_dir() and p.name in {"references", "prompts"} for p in folder.rglob("*")) or "references/" in text,
        "depth": n >= 120 or any(p.is_dir() and p.name in {"references", "prompts"} for p in folder.rglob("*")) and n >= 60,
    }
    score = sum(bool(v) for v in checks.values())
    absent = [name for name, ok in checks.items() if not ok]
    severity = "Strong base" if score >= 8 else "Needs strengthening" if score >= 6 else "Rebuild priority"
    return {
        "name": folder.name, "lines": n,
        "references": sum(1 for p in folder.rglob("*") if p.is_file() and any(parent.name in {"references", "prompts"} for parent in p.parents)),
        "scripts": sum(1 for p in folder.rglob("*") if p.is_file() and any(parent.name == "scripts" for parent in p.parents)),
        "score": f"{score}/9", "severity": severity, "absent": ", ".join(absent) or "—",
    }


def assess_agent(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    n = len(text.splitlines())
    checks = {
        "base-agent": "BaseAgent" in text,
        "schema": "schema" in text.lower() or "json" in text.lower(),
        "quality": any(s in text.lower() for s in ("critic", "quality", "validate", "review")),
        "error-control": any(s in text.lower() for s in ("try:", "except", "AgentError", "raise")),
        "tests": (ROOT / "backend" / "tests" / f"test_{path.stem}.py").exists(),
    }
    score = sum(checks.values())
    return {
        "name": path.stem, "lines": n, "score": f"{score}/5",
        "absent": ", ".join(k for k, v in checks.items() if not v) or "—",
    }


def main() -> None:
    skill_rows = [assess_skill(p) for p in sorted(SKILLS.glob("*/SKILL.md"))]
    agent_rows = [assess_agent(p) for p in sorted(AGENTS.glob("*.py")) if p.name != "__init__.py"]
    weak = [r for r in skill_rows if r["severity"] == "Rebuild priority"]
    medium = [r for r in skill_rows if r["severity"] == "Needs strengthening"]

    out = [
        "# ZYNTH Operating Asset Audit", "",
        "## Method", "",
        "This static review tests whether each skill exposes the minimum operating contract required for repeatable agency work: a clear trigger, qualification/brief, workflow, output, quality gate, guardrails, commercial or outcome discipline, supporting references, and adequate depth. It is a **gap detector**, not evidence that the underlying advice is true; rates, laws, vendors, market facts, and client claims must still be verified at the point of use.", "",
        f"**Skills assessed:** {len(skill_rows)}. **Rebuild priority:** {len(weak)}. **Needs strengthening:** {len(medium)}. **Strong base:** {len(skill_rows) - len(weak) - len(medium)}.", "",
        "## Skill Scorecard", "",
        "| Skill | Lines | Refs | Scripts | Score | Status | Missing operating controls |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for r in skill_rows:
        out.append(f"| `{r['name']}` | {r['lines']} | {r['references']} | {r['scripts']} | {r['score']} | {r['severity']} | {r['absent']} |")
    out.extend([
        "", "## Agent Architecture Scorecard", "",
        "This scorecard reviews implementation affordances, not the strategic quality of the prompts or skills each agent may call.", "",
        "| Agent | Lines | Score | Missing engineering controls |", "|---|---:|---:|---|",
    ])
    for r in agent_rows:
        out.append(f"| `{r['name']}` | {r['lines']} | {r['score']} | {r['absent']} |")
    out.extend([
        "", "## Priority Interpretation", "",
        "A short skill is not automatically poor. It becomes an implementation risk when it offers a broad promise such as ‘deliver end to end’ but lacks concrete inputs, output contract, process, quality gate, safeguards, and references. Rebuild-priority skills should become concise navigation files with the detailed methods, templates, schemas, and rate/market references stored in their own `references/`, `templates/`, and `scripts/` folders.",
    ])
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
