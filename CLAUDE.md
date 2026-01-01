# Social Media Posts

Repo for managing social media content across GenWise properties.

## Purpose
Track and schedule social media posts for Club GW threads and other GenWise content.

## Google Sheet
- **Sheet ID**: `1ersqOc7F9-BxDNji9hJ2Ti9dA4G5-zQDNW3i9O8LIXg`
- **URL**: https://docs.google.com/spreadsheets/d/1ersqOc7F9-BxDNji9hJ2Ti9dA4G5-zQDNW3i9O8LIXg

## Columns
| Column | Description |
|--------|-------------|
| Thread Title | Source content title |
| Thread URL | Shareable link |
| Status | Draft / Scheduled / Posted |
| Platform | Instagram, LinkedIn, Twitter, WhatsApp, Facebook |
| Scheduled Date | When to post |
| Posted Date | Actual post date |
| Message | Post copy/caption |
| Hashtags | Relevant hashtags |
| Media | Image/video to use |
| Engagement | Likes/comments/shares (post-hoc) |
| Notes | Additional context |

## Credentials
- Service Account: `~/.config/gcp/service-account-key.json`
- Sheets API must be enabled in GCP project

## Usage
```bash
# Create sheet (first time)
python3 create_sheet.py

# Add new posts
python3 add_posts.py
```
