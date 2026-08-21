from pathlib import Path
import json

path = Path('/home/ubuntu/zynth-brain/backend/outputs/variety_registry.json')
data = json.loads(path.read_text(encoding='utf-8'))
batch_code = 'ZYNTH-20260821-BEAUTY-BILINGUAL'
selected_at = '2026-08-21T07:50:00Z'

if not any(x.get('batch_code') == batch_code for x in data.get('selection_log', [])):
    data.setdefault('cycles', []).append({
        'industry': 'Beauty and cosmetics',
        'industryCode': 'beauty',
        'run_id': selected_at,
        'count': 10,
        'batch_code': batch_code,
        'production_status': 'registered_research_pending',
        'channel_scope': 'Integrated activation plus social media and TikTok preparation'
    })
    data.setdefault('selection_log', []).append({
        'batch_code': batch_code,
        'industryCode': 'beauty',
        'industry': 'Beauty and cosmetics',
        'selection_status': 'registered_research_pending',
        'selected_at': selected_at,
        'prior_immediate_industryCode': 'logistics',
        'selection_rationale': 'beauty is an allowed command-center industry code explicitly requested by the user and differs from the immediately prior logistics batch. The batch is reserved before research to preserve lifecycle integrity. Earlier 2026-08-20 adjacent beauty/wellness ideation does not replace this new dedicated cosmetics batch.',
        'required_campaign_proposal_count': 10,
        'required_commercial_storyboard_count': 10,
        'campaign_channel_requirement': 'Every campaign must include a social-media preparation workstream and a TikTok-specific preparation workstream where appropriate; these do not replace the separate commercial/storyboard track.',
        'two_hour_sprint_model': True
    })
    data['updated'] = selected_at
    data['registry_note'] = ('Beauty/cosmetics was reserved on 2026-08-21 as the user-requested next two-hour batch after Logistics. '
                             'It will produce ten integrated campaign proposals with social/TikTok preparation and ten separate commercial storyboards. '
                             'No schedule change was made.').strip()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('registered', batch_code)
else:
    print('already registered', batch_code)
