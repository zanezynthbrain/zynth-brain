import { z } from "zod";
import { createVideoProject, getDashboardData, getPrompt, listProposals, markNotificationRead, updateProposalStage, updateVideoApproval, updateVideoDetails, updateVideoStage } from "../db/commandCenter";
import { protectedProcedure, router } from "../_core/trpc";

const proposalStage = z.enum(["Draft", "Review", "Pitched", "Negotiating", "Won", "Lost", "On Hold"]);
const languageStatus = z.enum(["English", "English–Myanmar hybrid", "Both"]);

export const commandCenterRouter = router({
  dashboard: protectedProcedure.query(() => getDashboardData()),
  proposals: router({
    list: protectedProcedure.input(z.object({ industryId: z.number().optional(), stage: proposalStage.optional(), languageStatus: languageStatus.optional(), campaignType: z.string().optional(), seasonalWindow: z.string().optional(), owner: z.string().optional() })).query(({ input }) => listProposals(input)),
    updateStage: protectedProcedure.input(z.object({ id: z.number(), stage: proposalStage })).mutation(async ({ input, ctx }) => {
      await updateProposalStage(input.id, input.stage, ctx.user.name || "ZYNTH CEO");
      return { ok: true };
    }),
  }),
  notifications: router({
    markRead: protectedProcedure.input(z.object({ id: z.number() })).mutation(async ({ input }) => { await markNotificationRead(input.id); return { ok: true }; }),
  }),
  prompts: router({
    get: protectedProcedure.input(z.object({ id: z.number() })).query(({ input }) => getPrompt(input.id)),
  }),
  videos: router({
    create: protectedProcedure.input(z.object({ industryId: z.number(), title: z.string().min(3).max(255), titleMyanmar: z.string().max(255).optional(), tagline: z.string().min(3).max(255), clientName: z.string().min(2).max(255), productionHouse: z.string().min(2).max(255), talentPlan: z.string().min(2).max(4000), storyline: z.string().min(10).max(8000), deliverables: z.string().min(3).max(4000), storyboardStatus: z.string().min(3).max(120).optional(), timelineStart: z.date().optional(), timelineDue: z.date().optional(), approvalStatus: z.enum(["Not started", "Client review", "Approved", "Changes requested"]).optional(), approvalNotes: z.string().max(5000).optional(), budgetMmk: z.number().int().positive().optional() })).mutation(({ input }) => createVideoProject(input)),
    updateStage: protectedProcedure.input(z.object({ id: z.number(), stage: z.enum(["Storyboard", "Pre-production", "Production", "Post-production", "Delivery"]) })).mutation(async ({ input, ctx }) => { await updateVideoStage(input.id, input.stage, ctx.user.name || "ZYNTH CEO"); return { ok: true }; }),
    updateApproval: protectedProcedure.input(z.object({ id: z.number(), approvalStatus: z.enum(["Not started", "Client review", "Approved", "Changes requested"]), approvalNotes: z.string().max(5000).optional() })).mutation(async ({ input, ctx }) => { await updateVideoApproval(input.id, input.approvalStatus, input.approvalNotes, ctx.user.name || "ZYNTH CEO"); return { ok: true }; }),
    updateDetails: protectedProcedure.input(z.object({ id: z.number(), storyboardStatus: z.string().min(3).max(120), timelineStart: z.date().optional(), timelineDue: z.date().optional() })).mutation(async ({ input, ctx }) => { await updateVideoDetails(input.id, input.storyboardStatus, input.timelineStart, input.timelineDue, ctx.user.name || "ZYNTH CEO"); return { ok: true }; }),
  }),
});
