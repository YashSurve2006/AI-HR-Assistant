import asyncio
from playwright.async_api import async_playwright

async def capture_screenshots():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Use high resolution for professional screenshots
        context = await browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        page = await context.new_page()

        page.on("console", lambda msg: print(f"Browser console: {msg.text}"))
        page.on("pageerror", lambda err: print(f"Browser error: {err}"))

        print("Navigating to app...")
        await page.goto("http://127.0.0.1:5000")
        
        # 1. Wait for ALL data to load
        print("Waiting for data to load...")
        await page.wait_for_selector(".job-card", timeout=15000)
        await page.wait_for_selector(".feedback-item", timeout=15000)
        # Give charts time to animate
        await page.wait_for_timeout(2000)

        # Dashboard Light (Viewport)
        print("Capturing dashboard-light.png...")
        await page.evaluate("window.scrollTo(0,0)")
        await page.wait_for_timeout(500)
        await page.screenshot(path="images/dashboard-light.png")

        # Dashboard Dark (Viewport)
        print("Capturing dashboard-dark.png...")
        await page.click(".theme-toggle")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="images/dashboard-dark.png")

        # AI Chat Interface (Viewport)
        print("Capturing ai-chat.png...")
        await page.evaluate("document.getElementById('section-chat').scrollIntoView({behavior: 'smooth', block: 'center'})")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="images/ai-chat.png")

        # Job Directory (Viewport)
        print("Capturing job-directory.png...")
        await page.evaluate("document.getElementById('section-jobs').scrollIntoView({behavior: 'smooth', block: 'start'})")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="images/job-directory.png")

        # Employee Insights (Viewport)
        print("Capturing employee-insights.png...")
        await page.evaluate("document.getElementById('section-insights').scrollIntoView({behavior: 'smooth', block: 'start'})")
        await page.wait_for_timeout(2500)
        await page.screenshot(path="images/employee-insights.png")

        # Mobile View (Viewport)
        print("Capturing mobile-view.png...")
        mobile_context = await browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=3)
        mobile_page = await mobile_context.new_page()
        await mobile_page.goto("http://127.0.0.1:5000")
        await mobile_page.wait_for_selector(".job-card", timeout=15000)
        await mobile_page.wait_for_timeout(1000)
        await mobile_page.click(".theme-toggle") # dark mode
        await mobile_page.wait_for_timeout(1000)
        await mobile_page.screenshot(path="images/mobile-view.png")
        await mobile_context.close()

        # Resume Analyzer & Results
        print("Capturing resume results...")
        await page.evaluate("document.getElementById('section-chat').scrollIntoView({behavior: 'smooth', block: 'start'})")
        await page.wait_for_timeout(500)

        # Inject hidden input and trigger handleFileUpload directly!
        await page.evaluate('''
            const input = document.createElement('input');
            input.type = 'file';
            input.id = 'playwright-upload';
            input.style.display = 'none';
            document.body.appendChild(input);
            input.addEventListener('change', (e) => {
                if(e.target.files.length) {
                    window.__playwright_handleFileUpload(e.target.files[0]);
                }
            });
        ''')
        
        # Trigger file upload by attaching the file to the injected input
        await page.set_input_files("#playwright-upload", "D:\\Yash_Surve_Resume.docx")
        await page.wait_for_timeout(1000)
        await page.click("#chat-send")
        
        print("Waiting for resume analysis to complete...")
        # wait for the results card to appear
        await page.wait_for_selector(".rc-score-center", timeout=30000)
        await page.wait_for_timeout(2000)

        # Resume Results (Viewport)
        await page.evaluate("document.querySelector('.chat-messages').scrollTop = document.querySelector('.chat-messages').scrollHeight")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="images/resume-results.png")

        # Job Recommendations from the resume (Viewport)
        print("Capturing job-recommendations.png...")
        await page.evaluate("document.querySelector('.chat-messages').scrollTop = document.querySelector('.chat-messages').scrollHeight")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="images/job-recommendations.png")
        
        # Resume Analyzer Empty State (Viewport)
        print("Capturing resume-analyzer empty state...")
        await page.goto("http://127.0.0.1:5000")
        await page.click(".theme-toggle") # dark mode
        await page.wait_for_selector(".job-card", timeout=15000)
        await page.wait_for_timeout(1000)
        await page.evaluate("document.getElementById('section-chat').scrollIntoView({behavior: 'smooth', block: 'center'})")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="images/resume-analyzer.png")

        await browser.close()
        print("All screenshots captured successfully!")

if __name__ == '__main__':
    asyncio.run(capture_screenshots())
