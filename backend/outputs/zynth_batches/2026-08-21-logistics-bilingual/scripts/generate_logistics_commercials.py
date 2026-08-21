from pathlib import Path
import json

ROOT=Path('/home/ubuntu/zynth-brain/backend/outputs/zynth_batches/2026-08-21-logistics-bilingual')
campaigns=json.loads((ROOT/'data/campaigns.json').read_text(encoding='utf-8'))['campaigns']
raw=[
('The Handover','လွှဲပြောင်းချိန်','B2B brand film','A clear handover is a promise that stays legible','A paper handover note crosses three hands; the film pauses at every ownership decision before a calm, clear next step.','quiet precision, paper texture, cobalt route lines','client-approved office, counter and controlled mock handover set','Ask for your handover discovery session'),
('A Clear Message','ရှင်းလင်းတဲ့ စာတို','SME service film','A customer message should travel with the same care as the parcel','A merchant writes one simple message; the film follows the question through a fictional, staged last-mile handover.','warm merchant realism with clean amber notification motifs','proposed/TBC small business counter and simulated delivery set','Map your customer communication question'),
('The Question That Travels','ခရီးသွားတဲ့ မေးခွန်း','Process-led explainer film','The most useful cold-chain question is who owns the next decision','A labelled question card moves through a non-product tabletop scenario, revealing that care is an ownership conversation.','restrained clinical teal, macro detail, quiet human tension','controlled tabletop studio; no real food, medicine or cold-chain product','Start an operational-readiness conversation'),
('Before the Peak','အလုပ်များမတိုင်မီ','Executive planning film','The best time to plan a rush is before it becomes a rush','A calendar fills with fictional demand markers; two leaders choose a meeting before the screen turns urgent.','editorial executive clarity, deep blue, measured kinetic type','proposed/TBC office, boardroom and abstract planning interface','Book a planning conversation'),
('The Return That Restarts','ပြန်လာခြင်းက ပြန်စတင်ခြင်း','Customer-experience film','A return can become the first signal of a better system','A folded return note is not treated as failure; different hands read, clarify and build a more human next step.','soft neutral realism, tactile paper, warm reset palette','controlled studio with fictional packaging only','Explore your return-journey question'),
('Known. Confirmed. Decided.','သိပြီး။ အတည်ပြုပြီး။ ဆုံးဖြတ်ပြီး။','Trade decision film','Clarity begins when a question is placed in the right column','Three words appear on a glass board as a team separates facts, confirmations and decisions before the next meeting.','premium monochrome with copper marking cues','proposed/TBC meeting room and non-sensitive graphic display','Request a discovery briefing'),
('The Signal at 6:12','၆:၁၂ မှာ ရောက်လာတဲ့ အချက်ပြ','Operations-simulation film','A signal matters when someone knows the next step','At 6:12 a fictional alert appears; the film follows the calm human routing of a simulated exception, not a real dispatch event.','kinetic graphite, lime signal accents, controlled screen language','simulated operations desk and abstract route board','See your operations-discovery route'),
('Hands on the Route','လမ်းကြောင်းပေါ်က လက်များ','Human-centred culture film','Every route is completed by people making careful decisions','A dispatch colleague, driver, customer-service colleague and receiver each make one small decision that keeps the handover respectful.','documentary warmth, natural light, human detail','proposed/TBC controlled locations; no driving, live work or employment claim','Listen to the people behind the route'),
('Small Motions','အသေးစိတ် လှုပ်ရှားမှုများ','Warehouse process film','Control is made from small motions that make sense together','A fictional item moves through a controlled mock pick, check and handover sequence, where every motion is deliberately visible.','architectural precision, soft industrial daylight, macro choreography','client-approved mock-up or controlled warehouse zone; no live operations assumed','Request a process-review conversation'),
('The Next Decision','နောက်တစ်ကြိမ် ဆုံးဖြတ်ချက်','CRM reactivation film','When the route changes, the next decision can still be clear','An unsent email becomes a three-option choice: reopen, re-scope or pause; the protagonist chooses a respectful next meeting.','calm executive warmth, paper and interface textures','bilingual email/UI mock-up and controlled office setting','Choose your next logistics conversation')]

def frames(title,territory,hook,cta,location):
    beats=[
('0:00–0:03','Tension establishes','A single controlled detail introduces the uncertainty at the centre of the logistics decision.','Macro insert; 85mm; shallow focus; slow push-in','Sparse room tone; one restrained percussive tick','What happens next?'),
('0:03–0:06','Human owner appears','A protagonist notices the small point where a handover, message or decision could become unclear.','Medium profile; 50mm; static composition','Subtle fabric/paper/interface foley',''),
('0:06–0:09','Question becomes visible','The question is written, selected or placed on a non-sensitive fictional process surface.','Top-down; 35mm; deliberate lock-off','Pencil, marker or interface tap','What do we know?'),
('0:09–0:12','Context widens','A second team member or workflow touchpoint reveals that coordination is shared.','Over-shoulder transition to a two-shot; gentle slider','Ambience rises; no real dispatch/radio content',''),
('0:12–0:16','Choice point','The protagonist separates what is known, what needs confirmation and what action is next.','Insert sequence; 50mm and macro; match cuts','Musical pulse begins','Know. Confirm. Decide.'),
('0:16–0:20','System is human','Hands exchange a fictional card, update a simulated board or align around a mock route.','Tracking medium shot; 35mm; controlled blocking','Soft handover foley; warm chord',''),
('0:20–0:24','Territory visualised','The territory line becomes a restrained graphic language across paper, glass or a mock interface.','Graphic overlay on live action; no live customer data','Music opens; elegant motion accent',territory),
('0:24–0:28','Proof moment','The group pauses to check a simple fictional checklist before continuing.','Wide-to-insert; 24mm then 85mm; no speed ramp','Quiet breath, pen click','A clearer next step'),
('0:28–0:32','Human outcome','The protagonist receives acknowledgement—not a delivery, performance or service guarantee.','Warm close-up; 85mm; natural light','Music resolves; restrained dialogue-free smile',''),
('0:32–0:36','Invitation','A clean client-approved question card creates the bridge to a discovery conversation.','Front-on graphic/live-action hybrid; 50mm','Single audio lift','Start with the question.'),
('0:36–0:40','CTA hold','Bilingual CTA resolves against a neutral, client-approved visual field.','Static end-frame; graphic-safe area held for cutdowns','Music tail; accessibility-ready subtitle space',cta),
('0:40–0:45','End card / versions','Master end card includes brand, legal, local-language and aspect-ratio placeholders; no claim until approved.','Flat graphic; 16:9 master with 9:16 and 1:1 safe areas','Brand sound only if rights-cleared','[CLIENT BRAND] | Proposed/TBC')]
    out=[]
    for n,b in enumerate(beats,1):
        out.append({'frame':n,'duration':b[0],'beat':b[1],'visual':b[2],'camera':b[3],'sound':b[4],'onScreen':b[5],'location':location})
    return out

items=[]
for i,(title,title_mm,fmt,territory,hook,style,location,cta) in enumerate(raw,1):
    c=campaigns[i-1]
    items.append({'id':f'COM-2026-LOGISTICS-{i:02d}','titleEn':title,'titleMm':title_mm,'linkedCampaign':c['id'],'format':fmt,'territory':territory,'hook':hook,'tension':c['commercialTension'],'objective':'Create a client-approved discovery-conversation CTA through a controlled creative treatment; no operational or performance result is promised.','cta':cta,'visualStyle':style,'location':location,'storyboardStatus':'12-frame detailed storyboard complete; all production elements proposed/TBC','storyboard':frames(title,territory,hook,cta,location)})
(ROOT/'data/commercials.json').write_text(json.dumps({'batchCode':'ZYNTH-20260821-LOGISTICS-BILINGUAL','commercials':items},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('commercial concepts:',len(items),'storyboard frames:',sum(len(x['storyboard']) for x in items))
