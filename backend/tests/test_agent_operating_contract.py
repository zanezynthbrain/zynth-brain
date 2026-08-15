"""The shared operating contract must reach every BaseAgent specialist prompt."""

from agents.copywriter import ContentCopywriterAgent


def test_specialist_prompt_inherits_zynth_operating_non_negotiables():
    prompt = ContentCopywriterAgent().build_system_prompt()
    for phrase in (
        "ZYNTH OPERATING NON-NEGOTIABLES",
        "Separate confirmed facts, supplied claims, assumptions",
        "three genuinely distinct territories",
        "commercially viable, measurable and safe",
        "Preserve founder and project-owner approval gates",
    ):
        assert phrase in prompt
