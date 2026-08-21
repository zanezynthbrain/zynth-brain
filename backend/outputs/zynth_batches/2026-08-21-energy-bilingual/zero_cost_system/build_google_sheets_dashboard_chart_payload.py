from pathlib import Path
import json

OUT = Path('/home/ubuntu/zynth-brain/backend/outputs/zynth_batches/2026-08-21-energy-bilingual/zero_cost_system/native_sheet_dashboard_chart_payload.json')
OVERVIEW = 906936946
CAMPAIGNS = 1092968073

def source(sheet, sr, er, sc, ec):
    return {'sheetId': sheet, 'startRowIndex': sr, 'endRowIndex': er, 'startColumnIndex': sc, 'endColumnIndex': ec}

def chart_request(title, chart_type, domain_source, series_source, row, col, legend='NO_LEGEND'):
    return {
        'addChart': {
            'chart': {
                'spec': {
                    'title': title,
                    'basicChart': {
                        'chartType': chart_type,
                        'legendPosition': legend,
                        'axis': [
                            {'position': 'BOTTOM_AXIS', 'title': ''},
                            {'position': 'LEFT_AXIS', 'title': 'MMK' if 'Budget' in title or 'Contribution' in title else ''}
                        ],
                        'domains': [{'domain': {'sourceRange': {'sources': [domain_source]}}}],
                        'series': [{'series': {'sourceRange': {'sources': [series_source]}}, 'targetAxis': 'BOTTOM_AXIS' if chart_type == 'BAR' else 'LEFT_AXIS'}],
                        'headerCount': 1,
                    }
                },
                'position': {
                    'overlayPosition': {
                        'anchorCell': {'sheetId': OVERVIEW, 'rowIndex': row, 'columnIndex': col},
                        'widthPixels': 620,
                        'heightPixels': 340,
                    }
                }
            }
        }
    }

requests = [
    chart_request(
        'Recommended Campaign Budget (MMK)', 'BAR',
        source(CAMPAIGNS, 6, 16, 1, 2), # Campaign record IDs, B7:B16
        source(CAMPAIGNS, 6, 16, 13, 14), # Recommended budget, N7:N16
        35, 1
    ),
    chart_request(
        'Base Scenario Contribution (MMK)', 'COLUMN',
        source(CAMPAIGNS, 6, 16, 1, 2),
        source(CAMPAIGNS, 6, 16, 17, 18), # Contribution, R7:R16
        35, 9
    ),
    chart_request(
        'Base Scenario ROI by Campaign', 'COLUMN',
        source(CAMPAIGNS, 6, 16, 1, 2),
        source(CAMPAIGNS, 6, 16, 18, 19), # Base ROI, S7:S16
        52, 1
    ),
]
OUT.write_text(json.dumps({'requests': requests, 'includeSpreadsheetInResponse': False}, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print(OUT)
print('Requests:', len(requests))
