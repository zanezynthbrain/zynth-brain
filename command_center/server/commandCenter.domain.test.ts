import { describe, expect, it } from "vitest";
import { proposals } from "../drizzle/schema";
import { INDUSTRY_SEED } from "./commandCenterSeed";

describe("ZYNTH command-center operating model", () => {
  it("covers the requested Myanmar industry universe with all four priority tiers", () => {
    const codes = INDUSTRY_SEED.map(([code]) => code);
    const tiers = new Set(INDUSTRY_SEED.map(([, , , tier]) => tier));

    expect(INDUSTRY_SEED.length).toBeGreaterThanOrEqual(20);
    expect(codes).toEqual(expect.arrayContaining([
      "fnb", "hospitality", "financial", "beauty", "automotive-ev", "telecom-tech",
      "real-estate", "manufacturing", "healthcare", "education", "ngo", "retail",
      "entertainment", "logistics",
    ]));
    expect(tiers).toEqual(new Set(["Tier 1", "Tier 2", "Tier 3", "Tier 4"]));
  });

  it("preserves the exact proposal-stage vocabulary requested by the CEO workflow", () => {
    expect(proposals.stage.enumValues).toEqual([
      "Draft", "Review", "Pitched", "Negotiating", "Won", "Lost", "On Hold",
    ]);
  });
});
