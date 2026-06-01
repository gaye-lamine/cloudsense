import asyncio
import os
import time
import shutil
import subprocess
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

async def smooth_mouse_glide(page, selector_or_coords, steps=25):
    """
    Moves the mouse cursor smoothly to a target element or coordinates
    to simulate a real human hand on screen.
    """
    if isinstance(selector_or_coords, str):
        # Target is a selector, get its bounding box
        el = page.locator(selector_or_coords).first
        box = await el.bounding_box()
        if box:
            x = box["x"] + box["width"] / 2
            y = box["y"] + box["height"] / 2
        else:
            return
    else:
        # Target is coordinates (x, y)
        x, y = selector_or_coords
        
    # Perform smooth movement
    await page.mouse.move(x, y, steps=steps)
    await asyncio.sleep(0.1)

async def run_filmmaker():
    github_owner = os.getenv("GITHUB_REPO_OWNER", "gaye-lamine")
    github_repo = os.getenv("GITHUB_REPO_NAME", "cloudsense")
    github_url = f"https://github.com/{github_owner}/{github_repo}/pulls"
    
    # Step 0: Wipe the database first to start with a clean 0-anomaly state
    print("🧹 Wiping database to starting clean sheet state...")
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    subprocess.run(["./venv/bin/python", "scratch/clean_database.py"], env=env)
    
    print("🎬 Starting CloudSense Automated Filmmaker...")
    
    async with async_playwright() as p:
        # Launch Chromium with video recording enabled
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir="scratch/recordings/",
            record_video_size={"width": 1280, "height": 720}
        )
        
        page = await context.new_page()
        
        # ────────────────────────────────────────────────────────
        # 🎬 ACT 1 (0:00 - 0:15): Opening & Introduction (0 anomalies)
        # ────────────────────────────────────────────────────────
        print("🎥 Act 1: Dashboard Landing & Title Intro...")
        await page.goto("http://localhost:5173/")
        await page.wait_for_load_state("networkidle")
        
        # Move mouse slowly to the center and hover over brand name
        await page.mouse.move(100, 100) # Start top-left
        await smooth_mouse_glide(page, ".brand-name")
        await asyncio.sleep(6.0) # Wait for the rest of intro
        
        # ────────────────────────────────────────────────────────
        # 🎬 ACT 2 (0:15 - 0:35): Credentials Security Check
        # ────────────────────────────────────────────────────────
        print("🎥 Act 2: Highlight Credentials banner & Sidebar Footer...")
        # Hover slowly over the emerald green credentials status alert banner
        await smooth_mouse_glide(page, ".connection-status-banner")
        await asyncio.sleep(5.0)
        
        # Hover down to the sidebar footer status badge
        await smooth_mouse_glide(page, ".sidebar-footer")
        await asyncio.sleep(5.0)
        
        # ────────────────────────────────────────────────────────
        # 🎬 ACT 3 (0:35 - 0:55): Run Audit & Console Logs
        # ────────────────────────────────────────────────────────
        print("🎥 Act 3: Click 'Run Audit Cycle' & Stream SRE Logs...")
        # Hover and click "Run Audit Cycle" button (which is ENABLED now because 0 anomalies!)
        await smooth_mouse_glide(page, ".btn-primary")
        await page.locator(".btn-primary").click()
        print("🚀 Clicked Run Audit Cycle successfully!")
        await asyncio.sleep(2.0)
        
        # Click the "Agent Console" sidebar tab
        await smooth_mouse_glide(page, "text=Agent Console")
        await page.locator("text=Agent Console").click()
        
        # Move mouse to the center of the console and scroll slowly
        await page.mouse.move(600, 400)
        # Wait 25 seconds for the scan to run and complete, streaming SRE/FinOps logs!
        await asyncio.sleep(25.0) 
        
        # ────────────────────────────────────────────────────────
        # 🎬 ACT 4 (0:55 - 1:15): Anomalies Audit & Analysis
        # ────────────────────────────────────────────────────────
        print("🎥 Act 4: Return to Dashboard & Audit Anomalies...")
        # Click back on Dashboard
        await smooth_mouse_glide(page, "text=Dashboard")
        await page.locator("text=Dashboard").click()
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(3.0)
        
        # Scroll down slowly to the cost anomalies section
        for _ in range(8):
            await page.mouse.wheel(0, 50)
            await asyncio.sleep(0.3)
            
        # Hover over the first detected anomaly and its severity badge
        await smooth_mouse_glide(page, ".severity-badge >> nth=0")
        await asyncio.sleep(5.0)
        await smooth_mouse_glide(page, ".saving-tag >> nth=0")
        await asyncio.sleep(12.0)
        
        # ────────────────────────────────────────────────────────
        # 🎬 ACT 5 (1:15 - 1:35): Approve & SRE Emergency Rollback
        # ────────────────────────────────────────────────────────
        print("🎥 Act 5: Approve PR & Trigger SRE Emergency Rollback...")
        # Scroll to the HITL Column
        for _ in range(4):
            await page.mouse.wheel(0, 50)
            await asyncio.sleep(0.2)
            
        # Hover over the Git Diff area
        await smooth_mouse_glide(page, ".git-diff-container >> nth=0")
        await asyncio.sleep(3.0)
        
        # Hover and click "Approve & Deploy"
        await smooth_mouse_glide(page, ".btn-approve >> nth=0")
        await page.locator(".btn-approve >> nth=0").click()
        print("👍 PR Approved! Waiting for deployment verification...")
        await asyncio.sleep(4.0)
        
        # Hover and click the red "Rollback" button
        await smooth_mouse_glide(page, "text=Rollback")
        await page.locator("text=Rollback").click()
        print("🚨 Rollback clicked! Streaming emergency revert logs...")
        
        # Click back on Agent Console to see the rollback SRE logs in action
        await smooth_mouse_glide(page, "text=Agent Console")
        await page.locator("text=Agent Console").click()
        await asyncio.sleep(13.0)
        
        # ────────────────────────────────────────────────────────
        # 🎬 ACT 6 (1:35 - 1:45): Real GitHub Verification
        # ────────────────────────────────────────────────────────
        print("🎥 Act 6: Redirect to real GitHub Repository pulls...")
        # Open a new page for GitHub repo pulls
        github_page = await context.new_page()
        await github_page.goto(github_url)
        await github_page.wait_for_load_state("networkidle")
        await asyncio.sleep(10.0) # Show the real active PRs
        
        # Close everything
        await context.close()
        await browser.close()
        
        # Find the generated video path
        video = page.video
        if video:
            video_path = await video.path()
            target_path = "scratch/demo_autopilot.webm"
            shutil.copy(video_path, target_path)
            shutil.copy(video_path, "/Users/mac/.gemini/antigravity/brain/a51ad01d-1d93-4a09-a2c9-73b8e4fd143d/demo_autopilot.webm")
            print(f"\n🎉 SUCCESS! Video recorded beautifully!")
            print(f"👉 Local video saved to: {target_path}")
            print(f"👉 Artifact copy saved to: /Users/mac/.gemini/antigravity/brain/a51ad01d-1d93-4a09-a2c9-73b8e4fd143d/demo_autopilot.webm")

if __name__ == "__main__":
    asyncio.run(run_filmmaker())
