import asyncio
import os
import shutil
from playwright.async_api import async_playwright

async def main():
    target_dir = "/Users/mac/Desktop/sense-img"
    workspace_dir = "/Users/mac/Desktop/Workspace/cloudsense"
    
    # 1. Create target directory
    print(f"📁 Creating target directory: {target_dir}")
    os.makedirs(target_dir, exist_ok=True)
    
    # 2. Copy the video
    src_video = os.path.join(workspace_dir, "scratch/demo_autopilot.webm")
    dest_video = os.path.join(target_dir, "demo_autopilot.webm")
    if os.path.exists(src_video):
        print(f"🎥 Copying video from {src_video} to {dest_video}...")
        shutil.copy(src_video, dest_video)
    else:
        print(f"⚠️ Video source not found at {src_video}")
        
    # 3. Copy the subtitles
    src_srt = os.path.join(workspace_dir, "scratch/subtitles.srt")
    dest_srt = os.path.join(target_dir, "subtitles.srt")
    if os.path.exists(src_srt):
        print(f"📝 Copying subtitles from {src_srt} to {dest_srt}...")
        shutil.copy(src_srt, dest_srt)
    else:
        print(f"⚠️ Subtitles source not found at {src_srt}")

    # 4. Take screenshots
    print("📸 Initializing Playwright for high-definition screenshots...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Create a premium high-res context (1920x1080)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2  # High-density retina capture for crisp details
        )
        page = await context.new_page()
        
        # 4a. Dashboard Overview
        url = "http://localhost:5173/"
        print(f"🌐 Navigating to {url}...")
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        # Give a bit of extra time for any charts/animations or backend fetching
        print("⏳ Waiting 6 seconds for data and charts to fully render...")
        await asyncio.sleep(6)
        
        dashboard_img = os.path.join(target_dir, "dashboard_overview.png")
        print(f"📸 Capturing Dashboard Overview to {dashboard_img}...")
        await page.screenshot(path=dashboard_img)
        
        # 4b. Agent Console
        console_tab = "text=Agent Console"
        print(f"🖱️ Clicking on '{console_tab}' tab...")
        await page.locator(console_tab).click()
        print("⏳ Waiting 3 seconds for console logs to display...")
        await asyncio.sleep(3)
        
        console_img = os.path.join(target_dir, "agent_console.png")
        print(f"📸 Capturing Agent Console to {console_img}...")
        await page.screenshot(path=console_img)
        
        # 4c. Threshold Settings
        settings_tab = "text=Threshold Settings"
        print(f"🖱️ Clicking on '{settings_tab}' tab...")
        await page.locator(settings_tab).click()
        print("⏳ Waiting 3 seconds for settings to display...")
        await asyncio.sleep(3)
        
        settings_img = os.path.join(target_dir, "operational_settings.png")
        print(f"📸 Capturing Threshold Settings to {settings_img}...")
        await page.screenshot(path=settings_img)
        
        # Clean up
        await context.close()
        await browser.close()
        print("\n✨ All operations completed successfully!")
        print(f"📁 Open folder: {target_dir}")

if __name__ == "__main__":
    asyncio.run(main())
