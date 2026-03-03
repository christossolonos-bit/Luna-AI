"""
Share a random song from your YouTube channel to X (Twitter) via browser automation.

Usage:
    python share_song_to_x.py

First run: You'll need to log in to X manually when the browser opens.
After that, your session is saved and the script will post automatically.

Requires: pip install playwright && playwright install chromium
"""

import random
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.request import urlopen, Request

# Your YouTube channel ID (from https://www.youtube.com/channel/UCqIjEHOABb8fwbKbjDhVRuA)
YOUTUBE_CHANNEL_ID = "UCqIjEHOABb8fwbKbjDhVRuA"
YOUTUBE_RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}"

# Credentials path (shared with !comment for YouTube API - OAuth credentials.json)
YOUTUBE_CREDENTIALS_PATH = Path(__file__).parent / "credentials.json"
YOUTUBE_TOKEN_PATH = Path(__file__).parent / "youtube_token.json"

# Persistent browser data (saves your X login)
USER_DATA_DIR = Path(__file__).parent / ".x_browser_data"


def get_random_video_from_channel():
    """Fetch RSS feed and return (video_url, title) for a random video."""
    try:
        req = Request(YOUTUBE_RSS_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=15) as resp:
            xml = resp.read().decode()
        root = ET.fromstring(xml)
        atom = "http://www.w3.org/2005/Atom"
        entries = root.findall(f".//{{{atom}}}entry")
        if not entries:
            return None
        entry = random.choice(entries)
        # Get video URL from link rel="alternate" or from entry id (yt:video:XXX)
        video_url = None
        for link in entry.findall(f"{{{atom}}}link"):
            href = link.get("href") or ""
            if href and "youtube.com/watch" in href:
                video_url = href
                break
        if not video_url:
            vid_el = entry.find(f"{{{atom}}}id")
            if vid_el is not None and vid_el.text and "video:" in vid_el.text:
                video_url = f"https://www.youtube.com/watch?v={vid_el.text.split(':')[-1]}"
        if not video_url:
            return None
        title_el = entry.find(f"{{{atom}}}title")
        title = (title_el.text or "").strip() if title_el is not None and title_el.text else "My music"
        return (video_url, title)
    except Exception as e:
        print(f"❌ Failed to fetch YouTube RSS: {e}")
        return None


def post_to_x(video_url: str, title: str, interactive: bool = True) -> bool:
    """Open X in browser and post the video link. Returns True on success.
    interactive=False skips input() prompts (for Discord/automation)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ Install Playwright: pip install playwright && playwright install chromium")
        return False

    USER_DATA_DIR.mkdir(exist_ok=True)
    tweet_text = f"🎵 {title}\n\n{video_url}"

    with sync_playwright() as p:
        # Use persistent context so login is saved
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
            viewport={"width": 1200, "height": 800},
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=30000)

        # Wait for page to load - user may need to log in
        page.wait_for_timeout(3000)

        # Try to find and click the compose / "Post" button
        compose_selectors = [
            '[data-testid="SideNav_NewTweet_Button"]',
            'a[href="/compose/post"]',
            '[aria-label="Post"]',
            'a[href="/compose/tweet"]',
        ]
        clicked = False
        for sel in compose_selectors:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=2000):
                    btn.click()
                    clicked = True
                    break
            except Exception:
                continue

        if not clicked:
            print("⚠️ Could not find Post button. Log in to X in the browser — waiting up to 2 minutes...")
            if interactive:
                input("Press Enter after logging in, or Ctrl+C to exit...")
                return post_to_x(video_url, title, interactive=True)  # Retry
            # Non-interactive: wait and retry every 5s for up to 2 minutes so user can log in
            for attempt in range(24):  # 24 * 5s = 120s
                page.wait_for_timeout(5000)
                for sel in compose_selectors:
                    try:
                        btn = page.locator(sel).first
                        if btn.is_visible(timeout=1000):
                            btn.click()
                            clicked = True
                            break
                    except Exception:
                        continue
                if clicked:
                    break
                print(f"   Still waiting... ({attempt * 5}s)")
            if not clicked:
                print("❌ Timed out. Log in to X first, then run !share song again.")
                context.close()
                return False

        page.wait_for_timeout(2000)

        # Find the tweet text box and type
        textbox_selectors = [
            '[data-testid="tweetTextarea_0"]',
            'div[role="textbox"][data-testid="tweetTextarea_0"]',
            '[contenteditable="true"][data-testid="tweetTextarea_0"]',
            'div[contenteditable="true"]',
        ]
        typed = False
        for sel in textbox_selectors:
            try:
                box = page.locator(sel).first
                if box.is_visible(timeout=2000):
                    box.click()
                    page.wait_for_timeout(300)
                    box.fill("")
                    box.type(tweet_text, delay=30)
                    typed = True
                    break
            except Exception:
                continue

        if not typed:
            print("❌ Could not find tweet compose box.")
            if interactive:
                input("Press Enter to close browser...")
            context.close()
            return False

        page.wait_for_timeout(1000)

        # Click Post button
        post_selectors = [
            '[data-testid="tweetButton"]',
            '[data-testid="tweetButtonInline"]',
            'button:has-text("Post")',
        ]
        for sel in post_selectors:
            try:
                post_btn = page.locator(sel).first
                if post_btn.is_visible(timeout=2000) and post_btn.is_enabled():
                    post_btn.click()
                    print("✅ Tweet posted!")
                    page.wait_for_timeout(2000)
                    break
            except Exception:
                continue

        if interactive:
            input("Press Enter to close browser...")
        context.close()
        return True


def main():
    print("🎵 Fetching random video from your channel...")
    result = get_random_video_from_channel()
    if not result:
        print("❌ No videos found.")
        return
    url, title = result
    print(f"📺 Selected: {title}")
    print(f"🔗 {url}")
    print("\n🌐 Opening X... (log in if needed, then the script will post)")
    post_to_x(url, title)


if __name__ == "__main__":
    main()
