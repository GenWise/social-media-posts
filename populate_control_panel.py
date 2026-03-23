import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

SPREADSHEET_ID = "1ersqOc7F9-BxDNji9hJ2Ti9dA4G5-zQDNW3i9O8LIXg"
SERVICE_ACCOUNT_FILE = os.path.expanduser("~/.config/gcp/service-account-key.json")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

rows = [
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

def main():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()

    range_name = f"CONTROL_PANEL!A1:D{len(rows)}"

    body = {
        "values": rows
    }

    result = sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=range_name,
        valueInputOption="RAW",
        body=body
    ).execute()

    updated_cells = result.get("updatedCells", 0)
    updated_rows = result.get("updatedRows", 0)
    print(f"Success: {updated_rows} rows written, {updated_cells} cells updated.")
    print(f"Range: {result.get('updatedRange')}")

if __name__ == "__main__":
    main()
