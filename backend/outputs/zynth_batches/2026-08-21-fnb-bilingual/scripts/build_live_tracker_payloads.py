from pathlib import Path
import json, re

ROOT=Path('/home/ubuntu/zynth-brain/backend/outputs/zynth_batches/2026-08-21-fnb-bilingual')
OUT=ROOT/'sync'/'live_tracker_payloads'; OUT.mkdir(parents=True,exist_ok=True)
ID='1lJd6DkGcKrCAiETw9qadftFZhc-uXDNBr8Q1JlHLqMo'
DRIVE='https://drive.google.com/drive/folders/1ro6elw2QGkIy7kxcw5zm5AScZRg3vaN_'
NOW='2026-08-21 UTC'
campaigns=json.loads((ROOT/'data/campaigns.json').read_text(encoding='utf-8'))['campaigns']
commercials=json.loads((ROOT/'data/commercials.json').read_text(encoding='utf-8'))['commercials']

def first_number(text):
    m=re.search(r'(\d+)',text or '')
    return int(m.group(1)) if m else 'TBC'

def write(name,range_,rows):
    payload={
        'params':{'spreadsheetId':ID,'range':range_,'valueInputOption':'USER_ENTERED','insertDataOption':'INSERT_ROWS','includeValuesInResponse':False},
        'json':{'majorDimension':'ROWS','values':rows}
    }
    (OUT/f'{name}.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

campaign_rows=[]
for c in campaigns:
    base=first_number(c['planningOutcomes']['base'].split('/')[-1])
    campaign_rows.append([
        c['id'],c['shortName'],c['titleMm'],c['format'],c['commercialTension'],c['audience'],c['conversionMechanism'],c['creativeTerritory'],
        'G2 Strategy Selected','Concept ready','ZYNTH Strategy Lead','G1 factual product and claims approval',c['budgetMMK']['recommended'],base,'TBC','TBC','TBC','TBC','1','Medium',DRIVE,NOW
    ])
write('01_campaigns','Campaigns!B:W',campaign_rows)

commercial_rows=[]
for c in commercials:
    commercial_rows.append([
        c['id'],c['linkedCampaign'],c['titleEn'],c['titleMm'],c['format'],c['territory'],c['hook']+' '+c['tension'],
        'Concept treatment; visual style to client approval','Proposed/TBC client-approved location','Treatment complete','12-frame storyboard complete','Not started',
        'All product facts, claims, cast, locations, food handling, music, subtitles and rights TBC','G3 Creative Selected','Concept storyboard ready','ZYNTH Creative Lead',
        'G5 script, rights, food safety and production pack approval','TBC','TBC','TBC','1','Medium',DRIVE,NOW
    ])
write('02_commercials','Commercials!B:Y',commercial_rows)

research_rows=[
['FNB-S01','USDA Foreign Agricultural Service','Government market-report landing page','Food-service industry scope/context','No detailed local demand or market-size claim retained','https://www.fas.usda.gov/data/gain/2025/02/burma-food-service-hotel-restaurant-institutional','11 Feb 2025','Medium','ZYNTH Research','Context only'],
['FNB-S02','Xinhua','Public media/event coverage','Traditional food-show mechanics and regional-product discovery context','Historical event only; no future event or partnership claim','https://english.news.cn/20260726/49ff2f8a557b4825a58978e89ccccc61/c.html','26 Jul 2026','Medium','ZYNTH Research','Cleared with limitation'],
['FNB-S04','Myanmar Government','Official calendar','Q4 2026 Thadingyut, Tazaungdaing, National Day and Christmas timing guardrails','Calendar only; no demand or operating-hours claim','https://myanmar.gov.mm/upcoming-holidays','21 Aug 2026','High','ZYNTH Research','Cleared'],
['FNB-S05','Myanmar eVisa / Ministry of Immigration and Population','Official calendar','Cross-check of Q4 2026 public holiday dates','Calendar only','https://evisa.moip.gov.mm/notice/public-holiday','21 Aug 2026','High','ZYNTH Research','Cleared'],
['FNB-S06','Tilleke & Gibbins','Public legal commentary','Myanmar-language label review reminder for priority consumer products','Not legal advice or a current product-by-product compliance determination','https://www.tilleke.com/insights/myanmar-language-labeling-required-wide-range-products/','26 Oct 2018','Medium','ZYNTH Research','Use with limitation'],
['FNB-S07','Myanmar International TV','Official local coverage','Historic competition, exhibition, sales and regional-product event format','Historical only; no future venue/organiser/partner claim','https://www.myanmaritv.com/news/tastes-golden-land-myanmar-traditional-food-competition-and-exhibition','26 Jul 2026','Medium','ZYNTH Research','Cleared with limitation'],
['FNB-S08','Myanmar Ministry of Information','Official publisher','Historic panel, association, demo and booth format context','No forecast, partnership or performance claim','https://www.moi.gov.mm/moi%3Aeng/news/21664','27 Jul 2026','Medium','ZYNTH Research','Cleared with limitation'],
['FNB-S09','Global New Light of Myanmar / MNA','Local public publisher','Historic culture, regional display and exchange format context','No future sponsor, endorsement or opportunity claim','https://www.gnlm.com.mm/myanmar-urged-to-cultivate-signature-foods/','26 Jul 2026','Medium','ZYNTH Research','Cleared with limitation'],
['FNB-S10','Inter Myanmar Channel','First-hand public video analysis','Observed skills, demo, controlled tasting, seating and stage mechanics','All date, organiser, sponsor, brand and popularity statements separately unverified','https://www.youtube.com/watch?v=mbh1472c2HI','21 Aug 2026','Low','ZYNTH Research','Use with limitation']]
write('03_research','Research & Sources!B:K',research_rows)

ai_rows=[
['AIC-2026-FNB-01','ZYNTH-20260821-FNB-BILINGUAL','Evidence','Manus internal structured review','v1.0','Batch feasibility review stored in Drive archive',9,'Public source scope and use limitations are documented','No future relationship or product claim is validated','Conditional advance to client selection workshop','Hold for human/client approval','Client evidence owner','Clear factual product/claims brief at G1',NOW],
['AIC-2026-FNB-02','ZYNTH-20260821-FNB-BILINGUAL','Strategy','Manus internal structured review','v1.0','Portfolio uniqueness review stored in batch validation',10,'Ten unique formats, tensions, mechanisms, territories and budget structures','Do not execute all ten without capacity and risk review','Conditional advance to selection workshop','Hold for human/client approval','Client commercial owner','Select maximum three initial campaign pilots',NOW],
['AIC-2026-FNB-03','ZYNTH-20260821-FNB-BILINGUAL','Creative','Manus internal structured review','v1.0','Ten commercial treatments and 120-frame storyboards stored in Drive archive',10,'Commercials are independent COM records with CTA and gates','Treatments are not shoot-ready or rights-cleared scripts','Hold for G5 production approval','Hold','Client brand/legal owner','Approve final script, claims, cast, location and rights',NOW],
['AIC-2026-FNB-04','ZYNTH-20260821-FNB-BILINGUAL','Operations','Manus internal structured review','v1.0','Food and experience risk register stored in Drive archive',10,'Required approval lists cover hygiene, allergy, consent, venue and rights','No venue, food safety or permit condition independently cleared','Hold for G4 feasibility approval','Hold','Client operations owner','Name food safety, venue, privacy and escalation owners',NOW],
['AIC-2026-FNB-05','ZYNTH-20260821-FNB-BILINGUAL','Measurement','Manus internal structured review','v1.0','Monitoring workbook and scenario rules stored in Drive archive',10,'KPIs focus on controlled actions and consented next steps','Scenarios are not financial forecasts or guarantees','Conditional advance to tracking','Hold for human/client approval','Client data/sales owner','Replace assumptions with funnel, margin, inventory, capacity and attribution data',NOW]
]
write('04_ai_council','AI Council!B:O',ai_rows)

ops_rows=[
['TSK-2026-FNB-001','ZYNTH-20260821-FNB-BILINGUAL','Task','G1 Research Cleared','Select up to three F&B campaign records for client feasibility scope','User / Final Approver','TBC','High','No client/product facts or commercial owner named','Needs Human Decision','Choose priority CMP IDs',DRIVE,NOW],
['APR-2026-FNB-001','ZYNTH-20260821-FNB-BILINGUAL','Approval','G4 Feasibility Cleared','Approve product facts, food/allergen/hygiene, venue, consent, claims, rights and permit owner matrix before any activation','Client operations / legal owner','TBC','Critical','F&B safety, claims and operational requirements','Needs Human Decision','No external activation authorised',DRIVE,NOW],
['TSK-2026-FNB-002','ZYNTH-20260821-FNB-BILINGUAL','Task','G5 Production Cleared','Select up to three COM records for final script, rights and production feasibility','User / Final Approver','TBC','High','Commercials are treatments, not production-approved scripts','Needs Human Decision','Choose priority COM IDs',DRIVE,NOW],
['TSK-2026-FNB-003','SYSTEM-ZYNTH','Task','G7 Learn & Archive','Review batch learning after human selection; update same CMP/COM IDs and versions','ZYNTH Data Owner','TBC','Medium','Manual tracker update and decision log required','Draft','Use F&B batch archive as baseline',DRIVE,NOW]
]
write('05_ops','Ops!B:N',ops_rows)
print('Wrote five live-tracker append payloads:', ', '.join(p.name for p in OUT.glob('*.json')))
