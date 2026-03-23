"""
setup_sheets.py
Populates 3 tabs in the GenWise social media Google Spreadsheet.
"""

import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = "/Users/rajeshpanchanathan/.config/gcp/service-account-key.json"
SPREADSHEET_ID = "1ersqOc7F9-BxDNji9hJ2Ti9dA4G5-zQDNW3i9O8LIXg"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

POSTS_MASTER_SHEET_ID = 757503755

def get_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)

def rename_sheet(service, sheet_id, new_title):
    body = {
        "requests": [
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
                        "title": new_title,
                    },
                    "fields": "title",
                }
            }
        ]
    }
    resp = service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body=body
    ).execute()
    return resp

def write_range(service, range_name, values):
    body = {"values": values}
    resp = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=range_name,
        valueInputOption="RAW",
        body=body,
    ).execute()
    return resp

def clear_range(service, range_name):
    service.spreadsheets().values().clear(
        spreadsheetId=SPREADSHEET_ID, range=range_name, body={}
    ).execute()

def main():
    service = get_service()

    # ---------- TAB 1: Rename Posts -> POSTS_MASTER, write headers ----------
    print("Tab 1: Renaming 'Posts' to 'POSTS_MASTER'...")
    rename_sheet(service, POSTS_MASTER_SHEET_ID, "POSTS_MASTER")
    print("  Renamed successfully.")

    posts_headers = [[
        "post_id", "idea_id", "variant_id", "lock_status", "status", "owner",
        "last_updated_by", "last_updated_at", "hook", "body", "cta", "hashtags",
        "mentions", "final_post_text", "render_version", "person_featured",
        "media_type", "media_drive_url", "media_public_url", "duration_sec",
        "aspect_ratio", "srt_url", "platform", "platform_constraints_ok",
        "error_message", "offering", "post_type", "content_angle", "campaign",
        "source_asset_id", "scheduled_time", "posted_time", "post_url",
        "impressions", "engagements", "retry_count", "notes"
    ]]
    write_range(service, "POSTS_MASTER!A1:AK1", posts_headers)
    print(f"  Headers written: {len(posts_headers[0])} columns.")

    # ---------- TAB 2: IDEA_BANK headers + seed rows ----------
    print("\nTab 2: Writing IDEA_BANK headers...")
    idea_bank_headers = [[
        "idea_id", "source_asset_id", "source_type", "raw_text", "offering",
        "rough_post_type", "tags", "person_featured", "priority", "energy",
        "emotion", "reuse_potential", "processed", "selected_for_post",
        "notes", "created_at", "created_by"
    ]]
    write_range(service, "IDEA_BANK!A1:Q1", idea_bank_headers)
    print(f"  Headers written: {len(idea_bank_headers[0])} columns.")

    today = "2026-03-22"
    idea_rows = [
        [
            "GW-20260322-001",
            "https://clubgw.genwise.in/threads/how-harvard-makes-600m/",
            "manual",
            "How does Harvard make $600M a year from people who AREN'T the smartest in the world? Our students cracked the game theory behind elite college money-making. The answer involves secret admissions, online courses, and a brand strategy Mercedes could never pull off.",
            "ClubGW", "thread_highlight",
            "#ClubGW #Economics #GenWise #CuriousMinds",
            "", "MEDIUM", "HIGH", "mild", "high", "FALSE", "FALSE",
            "Game theory of elite college money-making - Thread: How Harvard Makes $600M",
            today, "system-migration",
        ],
        [
            "GW-20260322-002",
            "https://clubgw.genwise.in/threads/the-pomato-when-science-gets-weird/",
            "manual",
            "What happens when you graft a tomato onto a potato plant? You get a POMATO - cherry tomatoes on top, potatoes below. Same genus (Solanum), completely different vibes. Our students dove deep into why potatoes were once decorative houseplants and how the Irish Famine connects to all of this.",
            "ClubGW", "thread_highlight",
            "#ClubGW #Science #GenWise #CuriousMinds",
            "", "MEDIUM", "HIGH", "mild", "high", "FALSE", "FALSE",
            "Tomatoes + potatoes = botanical abomination - Thread: The Pomato",
            today, "system-migration",
        ],
        [
            "GW-20260322-003",
            "https://clubgw.genwise.in/threads/is-mathematics-discovery-or-invention/",
            "manual",
            "Is mathematics discovered or invented? 'The formula has always worked, regardless of whether we were around' - but we created the system to understand it. Watch our students debate whether sqrt(-1) is a human construct or a fundamental truth about reality.",
            "ClubGW", "thread_highlight",
            "#ClubGW #Philosophy #GenWise #CuriousMinds",
            "", "MEDIUM", "HIGH", "mild", "high", "FALSE", "FALSE",
            "Philosophical debate: discovery vs invention - Thread: Is Mathematics Discovery or Invention?",
            today, "system-migration",
        ],
        [
            "GW-20260322-004",
            "https://clubgw.genwise.in/threads/what-exactly-is-fire/",
            "manual",
            "What exactly IS fire? Plasma? Gas? Pure energy? One student asked. Then the chemistry nerds showed up. Turns out what we see as 'fire' is just photons released during oxidation. And violet flames are hottest because... wavelength physics.",
            "ClubGW", "thread_highlight",
            "#ClubGW #Chemistry #GenWise #CuriousMinds",
            "", "MEDIUM", "HIGH", "mild", "high", "FALSE", "FALSE",
            "Plasma, gas, or pure energy? - Thread: What Exactly is Fire?",
            today, "system-migration",
        ],
    ]
    write_range(service, "IDEA_BANK!A2:Q5", idea_rows)
    print(f"  Seed rows written: {len(idea_rows)} rows.")

    # ---------- TAB 3: CONTROL_PANEL ----------
    print("\nTab 3: Clearing and writing CONTROL_PANEL...")
    clear_range(service, "CONTROL_PANEL!A:Z")

    control_rows = [
        ["SECTION", "VALUE", "NOTES", ""],
        ["--- STATUS ---", "", "", ""],
        ["status", "IDEA", "Raw idea, not yet developed", ""],
        ["status", "DRAFT", "Content written, not validated", ""],
        ["status", "READY", "Validated, approved to schedule", ""],
        ["status", "SCHEDULED", "Queued for posting", ""],
        ["status", "POSTED", "Live on platform", ""],
        ["status", "FAILED", "Post attempt failed, see error_message", ""],
        ["--- PLATFORM ---", "", "", ""],
        ["platform", "TW", "Twitter / X (@Genwise_)", ""],
        ["platform", "LI", "LinkedIn (Genwise page)", ""],
        ["platform", "YT", "YouTube (GenWise channel)", ""],
        ["--- VARIANT_ID ---", "", "", ""],
        ["variant_id", "TW", "Twitter variant", ""],
        ["variant_id", "LI", "LinkedIn variant", ""],
        ["variant_id", "YT", "YouTube variant", ""],
        ["--- OFFERING ---", "", "", ""],
        ["offering", "GSP", "Gifted Summer Program (students)", ""],
        ["offering", "TNP365", "Think & Ponder 365 (students)", ""],
        ["offering", "GenAI", "Generative AI (students + teachers)", ""],
        ["offering", "M3", "My Misconception Mentor (teachers)", ""],
        ["offering", "ClubGW", "Club GW threads / general content", ""],
        ["offering", "General", "GenWise brand, not offering-specific", ""],
        ["--- POST_TYPE ---", "", "", ""],
        ["post_type", "testimonial", "Student/teacher/parent testimonial", ""],
        ["post_type", "announcement", "New course, cohort, registration open", ""],
        ["post_type", "snippet", "Clip or excerpt from a program session", ""],
        ["post_type", "POV", "Opinion / perspective piece", ""],
        ["post_type", "clip", "Short video extract", ""],
        ["post_type", "thread_highlight", "Notable Club GW thread/discussion", ""],
        ["post_type", "behind_scenes", "Inside view of program/team", ""],
        ["--- CONTENT_ANGLE ---", "", "", ""],
        ["content_angle", "insight", "Non-obvious truth or reframe", ""],
        ["content_angle", "story", "Narrative arc with person featured", ""],
        ["content_angle", "authority", "Expertise / credibility signal", ""],
        ["content_angle", "contrarian", "Challenges common assumption", ""],
        ["content_angle", "tactical", "Actionable, how-to", ""],
        ["--- PRIORITY ---", "", "", ""],
        ["priority", "HIGH", "Post this week", ""],
        ["priority", "MEDIUM", "Post this month", ""],
        ["priority", "LOW", "Backlog, no urgency", ""],
        ["--- ENERGY ---", "", "", ""],
        ["energy", "HIGH", "Exciting, momentum-building content", ""],
        ["energy", "LOW", "Reflective, thoughtful, slower content", ""],
        ["--- EMOTION ---", "", "", ""],
        ["emotion", "strong", "Emotionally resonant - pride, joy, awe, nostalgia", ""],
        ["emotion", "mild", "Moderately emotional", ""],
        ["emotion", "none", "Informational / neutral tone", ""],
        ["--- REUSE_POTENTIAL ---", "", "", ""],
        ["reuse_potential", "high", "Can be adapted across platforms, evergreen", ""],
        ["reuse_potential", "medium", "Moderate shelf life", ""],
        ["reuse_potential", "low", "Time-sensitive or one-platform only", ""],
        ["--- MEDIA_TYPE ---", "", "", ""],
        ["media_type", "video", "MP4 file", ""],
        ["media_type", "image", "JPG/PNG", ""],
        ["media_type", "text", "No media attachment", ""],
        ["--- ASPECT_RATIO ---", "", "", ""],
        ["aspect_ratio", "16:9", "Landscape - YouTube, LinkedIn native", ""],
        ["aspect_ratio", "9:16", "Portrait / Reels - future Instagram/Shorts", ""],
        ["aspect_ratio", "1:1", "Square - LinkedIn feed", ""],
        ["--- PLATFORM CONSTRAINTS ---", "", "", ""],
        ["PLATFORM", "MAX_CHARS", "MAX_VIDEO_SEC", "NOTES"],
        ["TW", "280", "120", "No native doc embeds; MP4 required; thread = multiple tweets"],
        ["LI", "3000", "600", "Soft limit; native video preferred; links reduce reach"],
        ["YT", "", "", "Title 100 chars; description 5000; SRT required for accessibility"],
        ["--- LOCK_STATUS ---", "", "", ""],
        ["lock_status", "LOCKED", "Do not edit this row (Claude rule)", ""],
        ["lock_status", "EDITABLE", "Open for editing", ""],
        ["--- PLATFORM_CONSTRAINTS_OK ---", "", "", ""],
        ["platform_constraints_ok", "VALID", "Passes all platform checks", ""],
        ["platform_constraints_ok", "INVALID", "Fails check - see error_message", ""],
        ["platform_constraints_ok", "NEEDS_REVIEW", "Subjective - human review required", ""],
        ["--- HASHTAG LIBRARY ---", "", "", ""],
        ["HASHTAG", "CATEGORY", "NOTES", ""],
        ["#GenWise", "Brand", "Always include", ""],
        ["#GiftedYouth", "Audience", "", ""],
        ["#GSP", "Offering", "Gifted Summer Program", ""],
        ["#GiftedSummerProgram", "Offering", "Long form", ""],
        ["#TNP365", "Offering", "", ""],
        ["#GenAI", "Offering", "", ""],
        ["#M3", "Offering", "Teachers", ""],
        ["#ClubGW", "Community", "", ""],
        ["#CuriousMinds", "Audience", "", ""],
        ["#GiftedEducation", "Audience", "", ""],
        ["#DeepLearning", "Theme", "Not ML - refers to deep study", ""],
        ["#SummerProgram", "Theme", "", ""],
        ["#GiftedKids", "Audience", "", ""],
        ["#TalentedAndGifted", "Audience", "", ""],
        ["#LearningBeyondSchool", "Theme", "", ""],
        ["#ThinkDeeply", "Theme", "", ""],
        ["--- MENTION LIBRARY ---", "", "", ""],
        ["NAME", "HANDLE_TW", "ROLE_NOTES", ""],
        ["Rajesh Panchanathan", "@rpanchanathan", "Co-founder GenWise", ""],
        ["Vishnu Agnihotri", "@vishnu_agni", "Co-founder GenWise", ""],
        ["Shailesh Patil", "@sjpatil", "Co-founder GenWise", ""],
        ["Neelakantan Krishnaswami", "@ngkabra", "Co-founder GenWise", ""],
        ["Ashish Ponders", "@ashishponders", "Faculty / community", ""],
    ]

    write_range(service, f"CONTROL_PANEL!A1:D{len(control_rows)}", control_rows)
    print(f"  Rows written: {len(control_rows)} rows.")

    print("\n--- DONE ---")
    print(f"  POSTS_MASTER : 1 header row, {len(posts_headers[0])} columns")
    print(f"  IDEA_BANK    : 1 header row + {len(idea_rows)} seed rows = {1 + len(idea_rows)} total")
    print(f"  CONTROL_PANEL: {len(control_rows)} rows")

if __name__ == "__main__":
    main()
