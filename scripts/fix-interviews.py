#!/usr/bin/env python3
from google.oauth2 import service_account
from googleapiclient.discovery import build

SHEET_ID = "1o6XXLhpxFVZL5SlDKP8a56Y17brgmD7HWzAGe1Ei4Co"
SA_KEY_FILE = "config/sterl-sheets-key.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds = service_account.Credentials.from_service_account_file(SA_KEY_FILE, scopes=SCOPES)
svc = build("sheets", "v4", credentials=creds)

meta = svc.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
sheet_ids = {s["properties"]["title"]: s["properties"]["sheetId"] for s in meta["sheets"]}
interviews_sid = sheet_ids["Interviews"]

# Delete rows bottom-to-top: 8 (Aaron Lee dupe), 7 (Casper dupe), 5 (Venn), 4 (Katalyze), 3 (Phoenix), 2 (Ramp)
rows_to_delete = sorted([2, 3, 4, 5, 7, 8], reverse=True)

requests = []
for r in rows_to_delete:
    idx = r - 1
    requests.append({
        "deleteDimension": {
            "range": {
                "sheetId": interviews_sid,
                "dimension": "ROWS",
                "startIndex": idx,
                "endIndex": idx + 1
            }
        }
    })

svc.spreadsheets().batchUpdate(spreadsheetId=SHEET_ID, body={"requests": requests}).execute()
print("Interviews cleaned.")

# Fix Wealthsimple outreach row — mark Passed
outreach_rows = svc.spreadsheets().values().get(
    spreadsheetId=SHEET_ID, range="Outreach!A2:H200"
).execute().get("values", [])

for i, row in enumerate(outreach_rows):
    row_str = " ".join(row).lower()
    if "wealthsimple" in row_str and ("rachel" in row_str or "vino" in row_str):
        sheet_row = i + 2
        svc.spreadsheets().values().update(
            spreadsheetId=SHEET_ID,
            range=f"Outreach!F{sheet_row}",
            valueInputOption="RAW",
            body={"values": [["Passed"]]}
        ).execute()
        print(f"Outreach row {sheet_row} marked Passed (Wealthsimple).")

print("Done.")
