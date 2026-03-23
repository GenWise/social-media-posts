# GW Social Media — Reference & Guardrails

## Sheet

- **ID**: `1ersqOc7F9-BxDNji9hJ2Ti9dA4G5-zQDNW3i9O8LIXg`
- **URL**: https://docs.google.com/spreadsheets/d/1ersqOc7F9-BxDNji9hJ2Ti9dA4G5-zQDNW3i9O8LIXg
- **Tabs**: POSTS_MASTER · IDEA_BANK · CONTROL_PANEL
- **MCP email**: `rajesh@genwise.in`
- **Access**: All genwise.in accounts have editor access

## Platforms

| Code | Platform | Account |
|------|----------|---------|
| TW | Twitter / X | @Genwise_ (blue-tick: 25k chars, 120s video self-cap) |
| LI | LinkedIn | Genwise page (rajesh.panchanathan@gmail.com) |
| YT | YouTube | GenWise channel |

## ID format

```
Idea level:  GW-YYYYMMDD-###          e.g. GW-20260322-001
Variant:     GW-YYYYMMDD-###-TW/LI/YT  e.g. GW-20260322-001-TW
```

## Write modes (skills)

Procedural rules live in global skills — available from any repo:

| Mode | Skill | Trigger |
|------|-------|---------|
| Extract ideas | `gw-extracting-ideas` | Processing a transcript, Zoom, or feedback |
| Generate posts | `gw-generating-posts` | Promoting ideas to POSTS_MASTER |
| Polish copy | `gw-polishing-posts` | Rewriting hook/body/final_post_text |
| Validate | `gw-validating-posts` | Checking posts before scheduling |

## Absolute guardrails (all modes, no exceptions)

- **NEVER** modify a row where `lock_status = LOCKED`
- **NEVER** delete any row from any tab
- **NEVER** write to `posted_time`, `post_url`, `impressions`, `engagements` (posting automation only)
- **NEVER** write `final_post_text` as a formula — always explicit text
- **NEVER** modify CONTROL_PANEL content

## Pipeline

```
Source (Zoom/transcript/video)
  → gw-extracting-ideas  → IDEA_BANK (DRAFT)
  → gw-generating-posts  → POSTS_MASTER (DRAFT, one row per platform)
  → gw-polishing-posts   → POSTS_MASTER (refined copy)
  → gw-validating-posts  → platform_constraints_ok = VALID
  → Human: status = SCHEDULED
  → Posting automation   → status = POSTED, post_url filled
```

## Posting methods

| Platform | Method |
|----------|--------|
| YouTube | `mcp__youtube__youtube-upload` + upload SRT |
| Twitter | `mcp__x-twitter__create_tweet` (OAuth 1.0a) |
| LinkedIn | Manual (API not yet integrated) |

## Credentials

- Twitter: OAuth 1.0a via `~/code/x-mcp-server/.env` (TWITTER_WORK_* from ~/.env)
- Service account (Sheets): `~/.config/gcp/service-account-key.json`
