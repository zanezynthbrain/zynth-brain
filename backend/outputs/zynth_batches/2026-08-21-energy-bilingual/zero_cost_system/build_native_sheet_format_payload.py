from pathlib import Path
import json

ROOT = Path('/home/ubuntu/zynth-brain/backend/outputs/zynth_batches/2026-08-21-energy-bilingual/zero_cost_system')
out = ROOT / 'native_sheet_format_payload.json'

# Current native spreadsheet sheet IDs.
SHEETS = {
    'Overview': 906936946,
    'Campaigns': 1092968073,
    'Commercials': 1446208989,
    'Research & Sources': 635020585,
    'AI Council': 1799033697,
    'Ops': 1795615920,
    'Learning & Guide': 932426930,
}
LAST_COL = {
    'Overview': 12,
    'Campaigns': 23,
    'Commercials': 25,
    'Research & Sources': 16,
    'AI Council': 17,
    'Ops': 18,
    'Learning & Guide': 22,
}
MAX_ROW = {
    'Overview': 34,
    'Campaigns': 16,
    'Commercials': 16,
    'Research & Sources': 12,
    'AI Council': 16,
    'Ops': 12,
    'Learning & Guide': 34,
}

NAVY = {'red': 0.0902, 'green': 0.1961, 'blue': 0.3020}
TEAL_LIGHT = {'red': 0.9098, 'green': 0.9608, 'blue': 0.9490}
BLUE_LIGHT = {'red': 0.9020, 'green': 0.9529, 'blue': 1.0}
YELLOW_LIGHT = {'red': 1.0, 'green': 0.9922, 'blue': 0.9059}
ORANGE_LIGHT = {'red': 1.0, 'green': 0.9529, 'blue': 0.8784}
WHITE = {'red': 1.0, 'green': 1.0, 'blue': 1.0}
GRAY = {'red': 0.4, 'green': 0.4392, 'blue': 0.4706}


def grid(sheet_id, sr, er, sc, ec):
    return {'sheetId': sheet_id, 'startRowIndex': sr, 'endRowIndex': er, 'startColumnIndex': sc, 'endColumnIndex': ec}


def fmt(bg=None, fg=None, size=None, bold=None, italic=None, horizontal=None, wrap=None):
    f = {}
    if bg is not None:
        f['backgroundColor'] = bg
    tf = {}
    if fg is not None: tf['foregroundColor'] = fg
    if size is not None: tf['fontSize'] = size
    if bold is not None: tf['bold'] = bold
    if italic is not None: tf['italic'] = italic
    if tf: f['textFormat'] = tf
    if horizontal is not None: f['horizontalAlignment'] = horizontal
    if wrap is not None: f['wrapStrategy'] = wrap
    return f


def repeat(sheet, sr, er, sc, ec, form, fields='userEnteredFormat'):
    return {'repeatCell': {'range': grid(SHEETS[sheet], sr, er, sc, ec), 'cell': {'userEnteredFormat': form}, 'fields': fields}}


def merge(sheet, sr, er, sc, ec):
    return {'mergeCells': {'range': grid(SHEETS[sheet], sr, er, sc, ec), 'mergeType': 'MERGE_ALL'}}


def width(sheet, start, end, pixels):
    return {'updateDimensionProperties': {'range': {'sheetId': SHEETS[sheet], 'dimension': 'COLUMNS', 'startIndex': start, 'endIndex': end}, 'properties': {'pixelSize': pixels}, 'fields': 'pixelSize'}}


def freeze(sheet, rows):
    return {'updateSheetProperties': {'properties': {'sheetId': SHEETS[sheet], 'gridProperties': {'frozenRowCount': rows}}, 'fields': 'gridProperties.frozenRowCount'}}


def one_of_list(sheet, sr, er, sc, options):
    return {'setDataValidation': {'range': grid(SHEETS[sheet], sr, er, sc, sc+1), 'rule': {'condition': {'type': 'ONE_OF_LIST', 'values': [{'userEnteredValue': x} for x in options]}, 'showCustomUi': True, 'strict': True}}}

requests = []

# Global formatting and title/section/header treatment.
for name, sid in SHEETS.items():
    lc = LAST_COL[name]
    mr = MAX_ROW[name]
    requests += [
        repeat(name, 1, 2, 1, lc, fmt(fg=NAVY, size=20, bold=True, horizontal='LEFT', wrap='WRAP'), 'userEnteredFormat(textFormat,horizontalAlignment,wrapStrategy)'),
        repeat(name, 2, 3, 1, lc, fmt(fg=GRAY, size=10, italic=True, horizontal='LEFT', wrap='WRAP'), 'userEnteredFormat(textFormat,horizontalAlignment,wrapStrategy)'),
        repeat(name, 4, 5, 1, lc, fmt(bg=BLUE_LIGHT, fg=NAVY, size=12, bold=True, horizontal='LEFT', wrap='WRAP'), 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,wrapStrategy)'),
        width(name, 0, 1, 24),
        width(name, 1, lc, 150),
    ]
    # Merge title/subtitle/section cells B to last used column.
    requests += [merge(name, 1, 2, 1, lc), merge(name, 2, 3, 1, lc), merge(name, 4, 5, 1, lc)]
    # Standard body and header rows where row 6 is a table header.
    if name != 'Overview' and name != 'Learning & Guide':
        requests += [
            repeat(name, 5, 6, 1, lc, fmt(bg=NAVY, fg=WHITE, size=10, bold=True, horizontal='CENTER', wrap='WRAP'), 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,wrapStrategy)'),
            repeat(name, 6, mr, 1, lc, fmt(horizontal='LEFT', wrap='WRAP'), 'userEnteredFormat(horizontalAlignment,wrapStrategy)'),
            freeze(name, 6),
        ]
    if name == 'Learning & Guide':
        requests += [
            repeat(name, 5, 6, 1, 4, fmt(bg=NAVY, fg=WHITE, size=10, bold=True, horizontal='CENTER', wrap='WRAP'), 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,wrapStrategy)'),
            repeat(name, 16, 17, 1, 3, fmt(bg=NAVY, fg=WHITE, size=10, bold=True, horizontal='CENTER', wrap='WRAP'), 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,wrapStrategy)'),
            freeze(name, 6),
        ]

# Overview decision table starts at row 18 (0-index 17).
requests += [
    repeat('Overview', 17, 18, 1, 11, fmt(bg=NAVY, fg=WHITE, size=10, bold=True, horizontal='CENTER', wrap='WRAP'), 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,wrapStrategy)'),
    repeat('Overview', 18, 28, 1, 11, fmt(horizontal='LEFT', wrap='WRAP'), 'userEnteredFormat(horizontalAlignment,wrapStrategy)'),
    freeze('Overview', 18),
    width('Overview', 1, 4, 160), width('Overview', 4, 8, 150), width('Overview', 8, 10, 125),
]

# More practical widths.
requests += [
    width('Campaigns', 1, 2, 170), width('Campaigns', 2, 5, 230), width('Campaigns', 5, 8, 290), width('Campaigns', 8, 13, 170), width('Campaigns', 13, 19, 130), width('Campaigns', 19, 23, 160),
    width('Commercials', 1, 3, 170), width('Commercials', 3, 10, 260), width('Commercials', 10, 18, 180), width('Commercials', 18, 25, 150),
    width('Research & Sources', 1, 4, 210), width('Research & Sources', 4, 6, 350), width('Research & Sources', 6, 8, 180),
    width('AI Council', 1, 5, 170), width('AI Council', 5, 10, 290), width('AI Council', 10, 17, 190),
    width('Ops', 1, 6, 190), width('Ops', 6, 12, 240), width('Ops', 12, 18, 170),
    width('Learning & Guide', 1, 4, 320),
]

# Controlled dropdowns with no external service.
status = ['Draft','In Review','Needs Human Decision','Approved','On Hold','Live','Closed','Failed']
stage = ['G0 Brief Accepted','G1 Research Cleared','G2 Strategy Selected','G3 Creative Selected','G4 Feasibility Cleared','G5 Go / No-go','G6 Live Optimisation','G7 Learn & Archive']
confidence = ['High','Medium','Low','Needs review']
decision = ['Pending','Accept','Revise','Hold','Reject']
priority = ['Critical','High','Medium','Low']
requests += [
    one_of_list('Campaigns', 6, 500, 9, stage), one_of_list('Campaigns', 6, 500, 10, status), one_of_list('Campaigns', 6, 500, 20, confidence),
    one_of_list('Commercials', 6, 500, 14, stage), one_of_list('Commercials', 6, 500, 15, status), one_of_list('Commercials', 6, 500, 22, confidence),
    one_of_list('Research & Sources', 6, 500, 8, confidence), one_of_list('Research & Sources', 6, 500, 10, status),
    one_of_list('AI Council', 6, 500, 10, decision), one_of_list('AI Council', 6, 500, 11, decision),
    one_of_list('Ops', 6, 500, 8, priority), one_of_list('Ops', 6, 500, 10, status),
]

# Basic number formats for financial/scenario fields.
number_format = {'numberFormat': {'type': 'NUMBER', 'pattern': '#,##0'}}
percent_format = {'numberFormat': {'type': 'PERCENT', 'pattern': '0.0%'}}
requests += [
    repeat('Campaigns', 6, 500, 13, 14, number_format, 'userEnteredFormat.numberFormat'),
    repeat('Campaigns', 6, 500, 15, 16, percent_format, 'userEnteredFormat.numberFormat'),
    repeat('Campaigns', 6, 500, 16, 18, number_format, 'userEnteredFormat.numberFormat'),
    repeat('Campaigns', 6, 500, 18, 19, percent_format, 'userEnteredFormat.numberFormat'),
]

payload = {'requests': requests, 'includeSpreadsheetInResponse': False}
out.write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print(out)
print('Requests:', len(requests))
