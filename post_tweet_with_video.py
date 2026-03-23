"""
Post a tweet with a native video upload.
Handles: chunked upload with media_category, processing poll, retry on 503.
"""
import os, time, tweepy, requests
from requests_oauthlib import OAuth1
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.env"))

API_KEY              = os.getenv("TWITTER_WORK_API_KEY")
API_SECRET           = os.getenv("TWITTER_WORK_API_KEY_SECRET")
ACCESS_TOKEN         = os.getenv("TWITTER_WORK_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET  = os.getenv("TWITTER_WORK_ACCESS_TOKEN_SECRET")
BEARER_TOKEN         = os.getenv("TWITTER_WORK_BEARER_TOKEN")

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api  = tweepy.API(auth)
client = tweepy.Client(
    consumer_key=API_KEY, consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET
)


def upload_video(file_path: str) -> str:
    """Upload video with correct media_category and poll until succeeded."""
    print(f"Uploading: {file_path}")
    media = api.media_upload(
        filename=file_path,
        media_category="tweet_video",
        chunked=True,
    )
    media_id = media.media_id_string
    print(f"media_id: {media_id}")

    # Poll processing status
    while True:
        status = api.get_media_upload_status(media_id)
        info = getattr(status, "processing_info", None)
        if info is None:
            print("No processing_info — assuming ready.")
            break
        state = info.get("state")
        print(f"  state: {state}")
        if state == "succeeded":
            break
        if state == "failed":
            raise RuntimeError(f"Media processing failed: {info}")
        wait = info.get("check_after_secs", 3)
        print(f"  waiting {wait}s...")
        time.sleep(wait)

    return media_id


def post_tweet(text: str, media_id: str, retries: int = 5) -> dict:
    """Post tweet via raw v2 API — media_ids nested under 'media' as required."""
    oauth = OAuth1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    delay = 2
    for attempt in range(1, retries + 1):
        resp = requests.post(
            "https://api.twitter.com/2/tweets",
            json={"text": text, "media": {"media_ids": [str(media_id)]}},
            auth=oauth,
        )
        if resp.status_code == 201:
            tweet_id = resp.json()["data"]["id"]
            return {"success": True, "id": tweet_id, "url": f"https://x.com/Genwise_/status/{tweet_id}"}
        if resp.status_code in (503, 500) and attempt < retries:
            print(f"{resp.status_code} on attempt {attempt}, retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2
        else:
            return {"success": False, "status_code": resp.status_code, "error": resp.text}
    return {"success": False, "error": "Max retries exceeded"}


if __name__ == "__main__":
    VIDEO_PATH = "/Users/rajeshpanchanathan/code/video-editing/agastya-iyer/AgastyaIyer_ShivNadar_GSP_Student_Twitter.mp4"

    TWEET_TEXT = """\
"If I had to do it again — I would not even think about it. It's a yes. 100 times."

Agastya Iyer attended GenWise GSP in Grade 9 at Shiv Nadar School, Faridabad. He's now doing an undergrad in Mathematics at IISER, Mohali.

He spent 6 hours a day doing mathematics. His head hurt — but it was the most fun he ever had.

He came back with a notebook full of phone numbers — and friends he's still in touch with across India, the US and UK.

This is what "finding your tribe" feels like.

Some Summers are just summers. This GenWise Summer Program Changes Everything.

2-3 weeks of Deep Learning with world-class mentors, bold ideas explored beyond the textbook, and friendships that last a lifetime!

Give Your Child This Summer!

@vishnu_agni @sjpatil @ngkabra @rpanchanathan @ashishponders

#GiftedYouth #GenWise #GSP #GiftedSummerProgram"""

    media_id = upload_video(VIDEO_PATH)
    print("Waiting 5s after upload before tweeting...")
    time.sleep(5)
    result = post_tweet(TWEET_TEXT, media_id)
    print(result)
