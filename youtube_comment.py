"""
Post comments on YouTube videos as Luna's account via Playwright.

No OAuth credentials needed. Uses persistent browser session (like !share song).
First run: Browser opens, log in to Luna's YouTube account. Session saved.
After that: Comments post automatically.

Requires: pip install playwright && playwright install chromium
"""

import re
from pathlib import Path

# Persistent browser data (saves Luna's YouTube login)
USER_DATA_DIR = Path(__file__).resolve().parent / ".youtube_browser_data"

# Seconds to keep browser open for login (first time or when session expired)
LOGIN_WAIT_SECONDS = 8


def extract_video_id(url_or_id: str) -> str:
    """Extract YouTube video ID from URL or return as-is if already an ID."""
    if not url_or_id or len(url_or_id) < 5:
        return ""
    s = url_or_id.strip()
    m = re.search(r"youtu\.be/([a-zA-Z0-9_-]{11})", s)
    if m:
        return m.group(1)
    m = re.search(r"[?&]v=([a-zA-Z0-9_-]{11})", s)
    if m:
        return m.group(1)
    if len(s) == 11 and re.match(r"^[a-zA-Z0-9_-]+$", s):
        return s
    return ""


def post_comment(video_id: str, comment_text: str):
    """
    Post a comment on a YouTube video via Playwright.
    Returns (success, message).
    """
    video_id = extract_video_id(video_id)
    if not video_id:
        return False, "Invalid YouTube video URL or ID"
    comment_text = (comment_text or "").strip()
    if not comment_text:
        return False, "Comment text is empty"
    if len(comment_text) > 10000:
        return False, "Comment too long (max 10000 chars)"

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False, "Install: pip install playwright && playwright install chromium"

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    USER_DATA_DIR.mkdir(exist_ok=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
            viewport={"width": 1200, "height": 900},
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(video_url, wait_until="domcontentloaded", timeout=30000)

        # Keep browser open so user can log in if needed
        page.wait_for_timeout(LOGIN_WAIT_SECONDS * 1000)

        # Scroll down to load comment section (YouTube loads it lazily on scroll)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1500)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        page.wait_for_timeout(2000)

        # Scroll comments section into view if it exists
        try:
            page.evaluate("""() => {
                const comments = document.querySelector('ytd-comments') || document.querySelector('#comments');
                if (comments) comments.scrollIntoView({ behavior: 'smooth' });
            }""")
            page.wait_for_timeout(2000)
        except Exception:
            pass

        # Step 1: Click placeholder or container to expand comment box
        placeholder_selectors = [
            '#simplebox-placeholder',
            '#placeholder-area',
            '#labelAndInputContainer',
            'ytd-commentbox #simplebox-placeholder',
            'ytd-commentbox #placeholder-area',
            '[placeholder="Add a comment..."]',
        ]
        placeholder_clicked = False
        for sel in placeholder_selectors:
            try:
                el = page.locator(sel).first
                if el.is_visible(timeout=2000):
                    el.click()
                    placeholder_clicked = True
                    page.wait_for_timeout(800)
                    break
            except Exception:
                continue

        if not placeholder_clicked:
            # Try clicking the contenteditable directly
            try:
                box = page.locator('ytd-commentbox [contenteditable="true"]').first
                if box.is_visible(timeout=2000):
                    box.click()
                    placeholder_clicked = True
                    page.wait_for_timeout(500)
            except Exception:
                pass

        # Step 2: Focus contenteditable and type (keyboard works better for contenteditable)
        contenteditable_selectors = [
            '#contenteditable-root',
            'ytd-commentbox #contenteditable-root',
            'ytd-commentbox [contenteditable="true"]',
            'ytd-commentbox div[contenteditable="true"]',
            'div[contenteditable="true"]',
        ]
        typed = False
        # Try get_by_placeholder first (semantic, more stable)
        try:
            box = page.get_by_placeholder("Add a comment", exact=False)
            if box.is_visible(timeout=1500):
                box.click()
                page.wait_for_timeout(300)
                page.keyboard.type(comment_text, delay=30)
                typed = True
                page.wait_for_timeout(500)
        except Exception:
            pass
        if not typed:
            for sel in contenteditable_selectors:
                try:
                    box = page.locator(sel).first
                    if box.is_visible(timeout=2000):
                        box.click()
                        page.wait_for_timeout(300)
                        # Use keyboard.type for contenteditable (fill/type can fail)
                        page.keyboard.type(comment_text, delay=30)
                        typed = True
                        page.wait_for_timeout(500)
                        break
                except Exception:
                    continue

        if not typed:
            # Fallback: try locator.type
            for sel in contenteditable_selectors:
                try:
                    box = page.locator(sel).first
                    if box.is_visible(timeout=2000):
                        box.click()
                        page.wait_for_timeout(300)
                        box.press_sequentially(comment_text, delay=30)
                        typed = True
                        page.wait_for_timeout(500)
                        break
                except Exception:
                    continue

        # Step 3: Click submit button
        commented = False
        if typed:
            submit_selectors = [
                'ytd-button-renderer#submit-button button',
                '#submit-button',
                'ytd-commentbox ytd-button-renderer button',
                'button#submit-button',
                '[aria-label="Comment"]',
                'ytd-commentbox #submit-button',
            ]
            for sub_sel in submit_selectors:
                try:
                    btn = page.locator(sub_sel).first
                    if btn.is_visible(timeout=2000) and btn.is_enabled():
                        btn.click()
                        commented = True
                        break
                except Exception:
                    continue

        if not commented:
            if typed:
                print("⚠️ Comment typed but submit button not found. Check the browser.")
            else:
                print("⚠️ Log in to YouTube in the browser, then run !comment again.")
            try:
                input("\nPress Enter to close browser...")
            except (EOFError, KeyboardInterrupt):
                pass
            context.close()
            msg = "Could not submit comment." if typed else "Could not find comment box. Log in to YouTube and try again."
            return False, msg

        # Wait for comment to appear in the list
        page.wait_for_timeout(2000)

        # Like the video (scroll to top, click video like button)
        try:
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(500)
            # Video like: aria-label contains "like this video" (excludes dislike, comment like)
            video_like_clicked = page.evaluate("""() => {
                const btns = document.querySelectorAll('button[aria-label]');
                for (const btn of btns) {
                    const label = (btn.getAttribute('aria-label') || '').toLowerCase();
                    if (label.includes('like this video') && !label.includes('dislike')) {
                        btn.click();
                        return true;
                    }
                }
                // Fallback: segmented-like-button (video like container)
                const likeSeg = document.querySelector('#segmented-like-button button');
                if (likeSeg) { likeSeg.click(); return true; }
                return false;
            }""")
            if video_like_clicked:
                page.wait_for_timeout(500)
        except Exception:
            pass

        # Like the comment (first comment = Luna's, just posted)
        try:
            page.evaluate("""() => {
                const comments = document.querySelector('ytd-comments') || document.querySelector('#comments');
                if (comments) comments.scrollIntoView({ behavior: 'smooth' });
            }""")
            page.wait_for_timeout(1000)
            # First comment's like button - use JS to find button with "like this comment"
            comment_like_clicked = page.evaluate("""() => {
                const firstComment = document.querySelector('ytd-comment-renderer');
                if (!firstComment) return false;
                const btns = firstComment.querySelectorAll('button[aria-label]');
                for (const btn of btns) {
                    const label = (btn.getAttribute('aria-label') || '').toLowerCase();
                    if (label.includes('like this comment') || (label === 'like' && !label.includes('video'))) {
                        btn.click();
                        return true;
                    }
                }
                // Fallback: first like-looking button in comment (toggle-button-renderer)
                const likeBtn = firstComment.querySelector('ytd-toggle-button-renderer button');
                if (likeBtn) { likeBtn.click(); return true; }
                return false;
            }""")
            if comment_like_clicked:
                page.wait_for_timeout(500)
        except Exception:
            pass

        context.close()

    return True, "Comment posted!"
