import sys
from playwright.sync_api import sync_playwright
from datetime import datetime
from job_extractor import save_job_to_csv, parse_job_details, check_job_already_scraped, check_job_already_scraped_by_url, extract_job_preview_info

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

def main():
    search_text = sys.argv[1] if len(sys.argv) > 1 else ""
    max_jobs = int(sys.argv[2]) if len(sys.argv) > 2 else None  # Optional job limit
    
    print("🚀 Starting browser automation...")
    sys.stdout.flush()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("📡 Navigating to hiring.cafe...")
        sys.stdout.flush()
        
        page.goto("https://hiring.cafe")
 
        if search_text:
            page.wait_for_timeout(1000)
            page.type("#query-search-v4", search_text, delay=100)  # 100ms delay between keystrokes
            page.press("#query-search-v4", "Enter")
            print(f"Entered search text: {search_text}")
            sys.stdout.flush()
            page.wait_for_selector("button:has-text('Relevance')")
            relevance_button = page.locator("button:has-text('Relevance')")
            if relevance_button.is_visible():
                relevance_button.click()
                page.wait_for_timeout(1000)
                most_recent = page.locator("span:has-text('Most Recent')")
                if most_recent.is_visible():
                    most_recent.click()
                    print("✓ Changed sort order to 'Most Recent'")
                    page.wait_for_timeout(1000)
            
            page.wait_for_selector("div.grid.grid-cols-1.gap-x-4")
            
            grid_xpath = "//div[contains(@class, 'grid') and contains(@class, 'grid-cols-1') and contains(@class, 'gap-x-4')]"
            
            processed_jobs = 0
            jobs_scraped_this_session = 0
            
            if max_jobs:
                print(f"🎯 Job limit set: Will process maximum {max_jobs} jobs")
            else:
                print("♾️  No job limit set: Will process all available jobs")
            
            while True:
                # Count current job elements
                current_count = len(page.locator(f"{grid_xpath}/*").all())
                print(f"\n=== Page Load: Found {current_count} total job listings ({current_count - processed_jobs} new) ===")
                
                if current_count <= processed_jobs:
                    print("No new jobs found, stopping pagination")
                    break
                
                # Check if we've reached the job limit
                if max_jobs and jobs_scraped_this_session >= max_jobs:
                    print(f"🎯 Reached job limit of {max_jobs}. Stopping.")
                    break
                
                # Calculate how many jobs to process in this batch
                jobs_to_process = current_count - processed_jobs
                if max_jobs:
                    remaining_jobs = max_jobs - jobs_scraped_this_session
                    jobs_to_process = min(jobs_to_process, remaining_jobs)
                    print(f"🎯 Processing {jobs_to_process} jobs (limit: {remaining_jobs} remaining)")
                
                # Process new jobs (from processed_jobs to processed_jobs + jobs_to_process)
                end_index = processed_jobs + jobs_to_process
                for index in range(processed_jobs, end_index):
                    try:
                        current_elements = page.locator(f"{grid_xpath}/*").all()
                        if index >= len(current_elements):
                            continue
                            
                        element = current_elements[index]
                        
                        job_title, company, location = extract_job_preview_info(element)
                        
                        if check_job_already_scraped(job_title, company, location, search_text):
                            print(f"Job {index + 1} already scraped - SKIPPING: {job_title} at {company}")
                            continue

                        element.hover()
                        
                        element.click()
                        
                        full_view_button = page.locator("span:has-text('Full View')")
                        full_view_button.click()
                        
                        page.wait_for_load_state()
                        page.wait_for_load_state()
                        current_url = page.url
                        
                        # Extract ALL job data from hiring.cafe page BEFORE clicking apply
                        job_data = {}
                        
                        try:
                            # Extract basic job information from hiring.cafe page
                            job_title = page.locator("h2.font-extrabold.text-3xl.text-gray-800.mb-4").text_content()
                            job_data['job_title'] = job_title.strip()
                            
                            company_name = page.locator(".text-xl.font-semibold.text-gray-700.flex-none").text_content()
                            job_data['company'] = company_name.strip()
                            
                            posted_time = page.locator(".text-xs.text-cyan-700.font-bold.flex-none").text_content()
                            job_data['posted'] = posted_time.strip()
                            
                            location_elements = page.locator("div:has(svg path[d*='M15 10.5a3 3 0 1 1-6 0']) span").all()
                            if location_elements:
                                location = location_elements[0].text_content()
                                job_data['location'] = location.strip()
                            else:
                                job_data['location'] = "Not found"
                                print("Location: Not found")
                            
                            job_details = page.locator(".flex.flex-wrap.gap-3 span").all_text_contents()
                            print(f"Job Details: {', '.join(job_details)}")
                            
                            salary, work_type, employment_type = parse_job_details(job_details)
                            job_data['salary'] = salary
                            job_data['work_type'] = work_type
                            job_data['employment_type'] = employment_type
                            
                            job_data['hiring_cafe_url'] = current_url
                            job_data['search_query'] = search_text
                            job_data['extracted_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            
                            print(f"✅ Extracted job data: {job_title} at {company_name}")
                            sys.stdout.flush()
                            
                        except Exception as e:
                            print(f"Error extracting basic job details: {e}")
                        
                        # Extract job description with the specific structure
                        try:
                            page.wait_for_timeout(1000)  # Give more time for content to load
                            
                            job_description_html = "Job description not found"
                            
                            try:
                                job_desc_container = page.locator("div.flex.flex-col.items-center.mt-4.md\\:mt-8.mb-16.w-full.border.max-w-2xl.rounded-xl")
                                page.wait_for_selector("div.flex.flex-col.items-center.mt-4.md\\:mt-8.mb-16.w-full.border.max-w-2xl.rounded-xl", timeout=5000)
                                
                                if job_desc_container.count() > 0:
                                    # Get the main content div that contains the actual description
                                    content_div = job_desc_container.locator("div.max-w-sm.md\\:max-w-md.lg\\:max-w-full.overflow-auto.px-4")
                                    
                                    if content_div.count() > 0:
                                        job_description_html = content_div.inner_html()
                                        print(f"📄 Extracted job description ({len(job_description_html)} characters)")
                                    else:
                                        print("⚠️ Job description content div not found, trying alternative selector")
                                else:
                                    print("⚠️ Job description container not found, trying alternative selector")
                            except Exception as e:
                                print(f"First selector failed: {e}")
                            
                            # Fallback: Try looking for any prose article that might contain job description
                            if job_description_html == "Job description not found":
                                try:
                                    prose_article = page.locator("article.prose")
                                    if prose_article.count() > 0:
                                        job_description_html = prose_article.first.inner_html()
                                        print(f"📄 Extracted job description via fallback ({len(job_description_html)} characters)")
                                    else:
                                        print("⚠️ No prose article found either")
                                except Exception as e:
                                    print(f"Fallback selector failed: {e}")
                                    
                        except Exception as desc_error:
                            job_description_html = f"Error extracting job description: {str(desc_error)}"
                            print(f"❌ Error extracting job description: {desc_error}")
                        
                        # Add job description to job data
                        job_data['job_description'] = job_description_html
                        
                        apply_now_button = page.locator("text=Apply now")
                        
                        current_pages = len(page.context.pages)
                        
                        page.wait_for_timeout(1000)
                        apply_now_button.click()
                        
                        page.wait_for_timeout(3000)
                        
                        all_pages = page.context.pages
                        new_pages = all_pages[current_pages:]
                        print(f"Tabs before: {current_pages}, Tabs after: {len(all_pages)}, New tabs: {len(new_pages)}")
                        
                        # Extract external URL from new tabs and add to job_data
                        try:
                            if len(new_pages) >= 2:
                                third_tab = new_pages[-1]  
                                third_tab.wait_for_load_state("networkidle")
                                external_url = third_tab.url
                                job_data['external_url'] = external_url
                                print(f"External link from third tab: {external_url}")
                            elif len(new_pages) >= 1:
                                # Only one tab opened, try to get URL from it
                                single_tab = new_pages[0]
                                single_tab.wait_for_load_state("networkidle")
                                external_url = single_tab.url
                                job_data['external_url'] = external_url
                                print(f"External link from single tab: {external_url}")
                            else:
                                job_data['external_url'] = "Not found"
                                print("No new tabs opened")
                            
                            # Always close any new tabs with multiple strategies
                            for new_page in new_pages:
                                try:
                                    tab_url = new_page.url
                                    print(f"Attempting to close tab: {tab_url}")
                                    
                                    # Strategy 1: Normal close
                                    new_page.close()
                                    print(f"✓ Closed tab: {tab_url}")
                                    
                                except Exception as close_error:
                                    print(f"✗ Normal close failed for {tab_url}: {close_error}")
                                    
                                    # Strategy 2: Force close with wait
                                    try:
                                        new_page.wait_for_timeout(500)
                                        new_page.close()
                                        print(f"✓ Force closed tab: {tab_url}")
                                    except Exception as force_error:
                                        print(f"✗ Force close failed for {tab_url}: {force_error}")
                                        
                                        # Strategy 3: Try to navigate away then close
                                        try:
                                            new_page.goto("about:blank")
                                            new_page.wait_for_timeout(500)
                                            new_page.close()
                                            print(f"✓ Navigate+close worked for {tab_url}")
                                        except Exception as nav_error:
                                            print(f"✗ Navigate+close failed for {tab_url}: {nav_error}")
                                            print(f"⚠️  Tab {tab_url} could not be closed - will try in final cleanup")
                            
                            print(f"Remaining tabs: {len(page.context.pages)}")
                            
                        except Exception as tab_error:
                            print(f"Error handling tabs: {tab_error}")
                            # Force close any new tabs
                            for new_page in new_pages:
                                try:
                                    new_page.close()
                                except:
                                    pass
                        
                        # Check for duplicates by external URL before saving
                        if job_data and job_data.get('external_url'):
                            if check_job_already_scraped_by_url(job_data['external_url'], search_text):
                                print(f"Job {index + 1} already scraped (by URL) - SKIPPING: {job_data.get('external_url')}")
                            else:
                                save_job_to_csv(job_data, search_text)
                                jobs_scraped_this_session += 1
                                print(f"Job {index + 1} data saved to CSV! (Total scraped: {jobs_scraped_this_session})")
                                sys.stdout.flush()
                        elif job_data:
                            save_job_to_csv(job_data, search_text)
                            jobs_scraped_this_session += 1
                            print(f"Job {index + 1} data saved to CSV (no external URL)! (Total scraped: {jobs_scraped_this_session})")
                            sys.stdout.flush()
                        
                        try:
                            close_button = page.locator("div.flex.items-center.space-x-2 > button.rounded-lg.p-2.text-black.hover\\:bg-gray-200.flex-none.outline-none").first
                            if close_button.is_visible():
                                close_button.click()
                                print("Clicked close button to return to search results")
                            else:
                                page.keyboard.press("Escape")
                                print("Pressed Escape to return to search results")
                            
                            page.wait_for_timeout(2000)
                            
                            page.wait_for_selector(f"{grid_xpath}", timeout=5000)
                            
                        except Exception as close_e:
                            print(f"Error returning to search results: {close_e}")
                            print("Continuing to next job...")

                    except Exception as e:
                        print(f"Error processing job {index + 1}: {e}")
                        try:
                            page.keyboard.press("Escape")
                            page.wait_for_timeout(1000)
                        except:
                            pass
                        print("Continuing to next job...")
                
                # Final cleanup: close any extra tabs that might be open
                try:
                    all_current_pages = page.context.pages
                    if len(all_current_pages) > 1:
                        print(f"🧹 Final cleanup: Found {len(all_current_pages)} total tabs, closing extras...")
                        
                        # Keep only the first tab (main tab)
                        for i in range(len(all_current_pages) - 1, 0, -1):  # Work backwards
                            extra_tab = all_current_pages[i]
                            try:
                                tab_url = extra_tab.url
                                print(f"🧹 Cleanup: Attempting to close extra tab: {tab_url}")
                                
                                # Aggressive cleanup strategies
                                try:
                                    # Try immediate close
                                    extra_tab.close()
                                    print(f"✓ Cleanup: Closed {tab_url}")
                                except:
                                    try:
                                        # Try navigating to blank first
                                        extra_tab.goto("about:blank")
                                        extra_tab.wait_for_timeout(200)
                                        extra_tab.close()
                                        print(f"✓ Cleanup: Force closed {tab_url}")
                                    except:
                                        try:
                                            # Try bringing main tab to front and closing
                                            page.bring_to_front()
                                            extra_tab.close()
                                            print(f"✓ Cleanup: Focus+close worked for {tab_url}")
                                        except:
                                            print(f"⚠️  Cleanup: Could not close stubborn tab: {tab_url}")
                                            
                            except Exception as tab_error:
                                print(f"❌ Cleanup: Error with tab {i}: {tab_error}")
                        
                        # Final count
                        final_count = len(page.context.pages)
                        print(f"🧹 Cleanup complete: {final_count} tab(s) remaining")
                        
                except Exception as cleanup_error:
                    print(f"❌ Error in final cleanup: {cleanup_error}")
                
                # Update processed jobs count for this batch
                processed_jobs = current_count
                
                # After processing all current jobs, scroll down to load more
                print(f"\n📜 Scrolling to load more jobs... (processed {processed_jobs} so far)")
                
                try:
                    # Scroll to bottom of the page
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(3000)  # Wait for new jobs to load
                    
                    # Check if more jobs loaded
                    new_count = len(page.locator(f"{grid_xpath}/*").all())
                    if new_count > current_count:
                        print(f"📜 New jobs loaded! Total now: {new_count} (was {current_count})")
                        # Continue the while loop to process new jobs
                    else:
                        print(f"📜 No new jobs loaded after scrolling. Reached end.")
                        break
                        
                except Exception as scroll_error:
                    print(f"❌ Error scrolling: {scroll_error}")
                    break
            
            print(f"\n🎉 Completed processing all job listings!")
            print(f"📊 Total jobs processed: {processed_jobs}")
            print(f"✅ Total jobs saved to CSV: {jobs_scraped_this_session}")
        
        # Don't keep browser open when run from command center
        # Only wait for input if running standalone
        if sys.stdout.isatty():
            try:
                input("Press Enter to close browser...")
            except EOFError:
                pass
        
        browser.close()

if __name__ == "__main__":
    main()