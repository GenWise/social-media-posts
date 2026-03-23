import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

SHEET_ID = "1ersqOc7F9-BxDNji9hJ2Ti9dA4G5-zQDNW3i9O8LIXg"
SA_KEY = os.path.expanduser("~/.config/gcp/service-account-key.json")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds = service_account.Credentials.from_service_account_file(SA_KEY, scopes=SCOPES)
service = build("sheets", "v4", credentials=creds)
sheets = service.spreadsheets()

# ── helper ───────────────────────────────────────────────────────────────────

def get_last_row(sheet_name):
    result = sheets.values().get(
        spreadsheetId=SHEET_ID,
        range=f"'{sheet_name}'!A:A"
    ).execute()
    values = result.get("values", [])
    return len(values)

def append_rows(sheet_name, rows):
    body = {"values": rows}
    result = sheets.values().append(
        spreadsheetId=SHEET_ID,
        range=f"'{sheet_name}'!A1",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()
    return result

# ── IDEA_BANK ─────────────────────────────────────────────────────────────────

idea_row = [
    "GW-20260321-001",
    "CM:5f04a940-f82f-4778-b0db-a8b569bd7506",
    "zoom",
    '"If I had to do it again — I would not even think about it. It\'s a yes. 100 times." Agastya Iyer attended GenWise GSP in Grade 9 at Shiv Nadar School, Faridabad. Now doing undergrad in Mathematics at IISER, Mohali. 6 hours/day of maths — head hurt but most fun ever. Came back with a notebook full of phone numbers and lifelong friends across India, US and UK.',
    "GSP",
    "testimonial",
    "GSP testimonial student mathematics tribe friends",
    "Agastya Iyer",
    "HIGH",
    "HIGH",
    "strong",
    "high",
    "TRUE",
    "TRUE",
    "Video posted YT 2026-03-21. Twitter cut 113s, LI 184s. CM id: 5f04a940-f82f-4778-b0db-a8b569bd7506",
    "2026-03-21",
    "video-editing session"
]

idea_last = get_last_row("IDEA_BANK")
print(f"IDEA_BANK last row before append: {idea_last}")

idea_result = append_rows("IDEA_BANK", [idea_row])
updated_range = idea_result.get("updates", {}).get("updatedRange", "unknown")
updated_rows = idea_result.get("updates", {}).get("updatedRows", 0)
print(f"IDEA_BANK: appended {updated_rows} row(s) → {updated_range}")

# ── POSTS_MASTER ──────────────────────────────────────────────────────────────

yt_tweet_text = '''"In a thousand lifetimes — yes." | Agastya Iyer | GenWise Gifted Summer Program

Agastya Iyer attended GenWise GSP in Grade 9 at Shiv Nadar School, Faridabad. He's now doing an undergrad in Mathematics at IISER, Mohali.

He spent 6 hours a day doing mathematics. His head hurt — but it was the most fun he ever had.

He came back with a notebook full of phone numbers — and friends he's still in touch with across India, the US and UK.

This is what "finding your tribe" feels like.

Some Summers are just summers. This GenWise Summer Program Changes Everything.

2-3 weeks of Deep Learning with world-class mentors, bold ideas explored beyond the textbook, and friendships that last a lifetime!

Give Your Child This Summer! → https://genwise.in/gsp

#GiftedYouth #GenWise #GSP #GiftedSummerProgram'''

tw_final_text = '''"If I had to do it again — I would not even think about it. It's a yes. 100 times."

Agastya Iyer attended GenWise GSP in Grade 9 at Shiv Nadar School, Faridabad. He's now doing an undergrad in Mathematics at IISER, Mohali.

He spent 6 hours a day doing mathematics. His head hurt — but it was the most fun he ever had.

He came back with a notebook full of phone numbers — and friends he's still in touch with across India, the US and UK.

This is what "finding your tribe" feels like.

Some Summers are just summers. This GenWise Summer Program Changes Everything.

2-3 weeks of Deep Learning with world-class mentors, bold ideas explored beyond the textbook, and friendships that last a lifetime!

Give Your Child This Summer!

@vishnu_agni @sjpatil @ngkabra @rpanchanathan @ashishponders

#GiftedYouth #GenWise #GSP #GiftedSummerProgram'''

li_final_text = '''"If I had to do it again — I would not even think about it. It's a yes. 100 times."

Agastya Iyer attended the GenWise Gifted Summer Program (GSP) in Grade 9 at Shiv Nadar School, Faridabad. He went on to pursue an undergraduate degree in Mathematics at IISER, Mohali.

He spent 6 hours a day doing mathematics. His head hurt. But it was the most fun he'd ever had in his life.

He came home with a notebook full of phone numbers — and friends he still stays in touch with from across India, the US, and the UK.

This is what "finding your tribe" looks like.

Some summers are forgettable. The GenWise Summer Program is not one of them.

2–3 weeks of deep engagement with world-class mentors, ideas explored well beyond the textbook, and connections that last a lifetime.

If your child is intellectually curious, driven, and ready for a real challenge — this summer could change everything.

#GiftedYouth #GenWise #GSP #GiftedSummerProgram #GiftedEducation #SummerProgram'''

rows = [
    # YT — POSTED, LOCKED
    [
        "GW-20260321-001",
        "GW-20260321-001",
        "YT",
        "LOCKED",
        "POSTED",
        "rajesh",
        "system",
        "2026-03-21",
        '"If I had to do it again — I would not even think about it. It\'s a yes. 100 times."',
        "Agastya Iyer attended GenWise GSP in Grade 9 at Shiv Nadar School, Faridabad. He's now doing an undergrad in Mathematics at IISER, Mohali. He spent 6 hours a day doing mathematics. His head hurt — but it was the most fun he ever had. He came back with a notebook full of phone numbers — and friends he's still in touch with across India, the US and UK.",
        "Give Your Child This Summer! → https://genwise.in/gsp",
        "#GiftedYouth #GenWise #GSP #GiftedSummerProgram",
        "@vishnu_agni @sjpatil @ngkabra @rpanchanathan @ashishponders",
        yt_tweet_text,
        "v1",
        "Agastya Iyer",
        "video",
        "https://drive.google.com/file/d/1qseTJD2E7993zXAKmFEZBnxnv98f0kN2/view",
        "https://youtube.com/watch?v=s7m4phgGUMo",
        "184",
        "16:9",
        "",
        "YT",
        "VALID",
        "",
        "GSP",
        "testimonial",
        "story",
        "",
        "CM:5f04a940-f82f-4778-b0db-a8b569bd7506",
        "",
        "2026-03-21",
        "https://youtube.com/watch?v=s7m4phgGUMo",
        "",
        "",
        "",
        'YT title: "In a thousand lifetimes — yes." | Agastya Iyer | GenWise Gifted Summer Program'
    ],
    # TW — READY, EDITABLE
    [
        "GW-20260321-001",
        "GW-20260321-001",
        "TW",
        "EDITABLE",
        "READY",
        "rajesh",
        "system",
        "2026-03-22",
        '"If I had to do it again — I would not even think about it. It\'s a yes. 100 times."',
        "Agastya Iyer attended GenWise GSP in Grade 9 at Shiv Nadar School, Faridabad. He's now doing an undergrad in Mathematics at IISER, Mohali. He spent 6 hours a day doing mathematics. His head hurt — but it was the most fun he ever had. He came back with a notebook full of phone numbers — and friends he's still in touch with across India, the US and UK. This is what finding your tribe feels like.",
        "Give Your Child This Summer!",
        "#GiftedYouth #GenWise #GSP #GiftedSummerProgram",
        "@vishnu_agni @sjpatil @ngkabra @rpanchanathan @ashishponders",
        tw_final_text,
        "v1",
        "Agastya Iyer",
        "video",
        "",
        "",
        "113",
        "16:9",
        "",
        "TW",
        "VALID",
        "",
        "GSP",
        "testimonial",
        "story",
        "",
        "CM:5f04a940-f82f-4778-b0db-a8b569bd7506",
        "",
        "",
        "",
        "",
        "",
        "",
        "Local: ~/code/video-editing/agastya-iyer/AgastyaIyer_ShivNadar_GSP_Student_Twitter.mp4"
    ],
    # LI — DRAFT, EDITABLE
    [
        "GW-20260321-001",
        "GW-20260321-001",
        "LI",
        "EDITABLE",
        "DRAFT",
        "rajesh",
        "system",
        "2026-03-22",
        '"If I had to do it again — I would not even think about it. It\'s a yes. 100 times."',
        "Agastya Iyer attended the GenWise Gifted Summer Program (GSP) in Grade 9 at Shiv Nadar School, Faridabad. He went on to pursue an undergraduate degree in Mathematics at IISER, Mohali. He spent 6 hours a day doing mathematics. His head hurt. But it was the most fun he'd ever had in his life. He came home with a notebook full of phone numbers — and friends he still stays in touch with from across India, the US, and the UK.",
        "If your child is intellectually curious, driven, and ready for a real challenge — this summer could change everything.",
        "#GiftedYouth #GenWise #GSP #GiftedSummerProgram #GiftedEducation #SummerProgram",
        "",
        li_final_text,
        "v1",
        "Agastya Iyer",
        "video",
        "https://drive.google.com/file/d/1JNrHMxUcs_IUulcVsbPx3mjq2MpGrC8-/view",
        "",
        "184",
        "16:9",
        "",
        "LI",
        "NEEDS_REVIEW",
        "",
        "GSP",
        "testimonial",
        "story",
        "",
        "CM:5f04a940-f82f-4778-b0db-a8b569bd7506",
        "",
        "",
        "",
        "",
        "",
        "",
        "LinkedIn copy adapted from Twitter draft. Review before posting."
    ]
]

posts_last = get_last_row("POSTS_MASTER")
print(f"POSTS_MASTER last row before append: {posts_last}")

posts_result = append_rows("POSTS_MASTER", rows)
updated_range_p = posts_result.get("updates", {}).get("updatedRange", "unknown")
updated_rows_p = posts_result.get("updates", {}).get("updatedRows", 0)
print(f"POSTS_MASTER: appended {updated_rows_p} row(s) → {updated_range_p}")

print("\nDone.")
