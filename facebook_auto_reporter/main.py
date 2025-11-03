import logging
import sys
import os
import json
import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
from config import Config

class FacebookAutoReporter:
    def __init__(self, job_id=None, jobs_dict=None):
        self.job_id = job_id
        self.jobs_dict = jobs_dict
        self.config = Config()
        self.setup_logging()
        self.driver = None
        self.reporting_results = []
    
    def setup_logging(self):
        """Logging setup করুন"""
        os.makedirs('./logs', exist_ok=True)
        logging.basicConfig(
            level=getattr(logging, self.config.LOG_LEVEL),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.LOG_FILE),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_driver(self):
        """Enhanced WebDriver setup with stealth capabilities"""
        try:
            # Use undetected chromedriver for better evasion
            options = uc.ChromeOptions()
            
            if self.config.HEADLESS_MODE:
                options.add_argument("--headless=new")
            
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument(f"--user-agent={self.config.USER_AGENT}")
            options.add_argument("--window-size=1920,1080")
            
            # Use existing Chrome profile if specified
            if self.config.CHROME_PROFILE_PATH:
                options.add_argument(f"--user-data-dir={self.config.CHROME_PROFILE_PATH}")
            
            # Exclude switches to avoid detection
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = uc.Chrome(options=options)
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("WebDriver initialized successfully with stealth mode")
            return True
        except Exception as e:
            self.logger.error(f"WebDriver initialization failed: {e}")
            return False
    
    def login_to_facebook(self):
        """Enhanced Facebook login with proper error handling"""
        try:
            self.logger.info("Attempting Facebook login...")
            self.driver.get("https://www.facebook.com/login")
            time.sleep(5)
            
            # Wait for email field
            email_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            email_input.send_keys(self.config.FACEBOOK_USERNAME)
            time.sleep(2)
            
            # Password field
            password_input = self.driver.find_element(By.ID, "pass")
            password_input.send_keys(self.config.FACEBOOK_PASSWORD)
            time.sleep(2)
            
            # Login button
            login_button = self.driver.find_element(By.ID, "loginbutton")
            login_button.click()
            
            # Wait for login to complete - check for elements that appear after login
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Facebook']"))
            )
            
            self.logger.info("Successfully logged into Facebook")
            return True
            
        except TimeoutException:
            self.logger.error("Facebook login timed out")
            return False
        except Exception as e:
            self.logger.error(f"Facebook login failed: {e}")
            return False
    
    def load_targets(self):
        """Target URLs load করুন"""
        try:
            with open('data/targets.json', 'r') as f:
                targets = json.load(f)
            self.logger.info(f"Loaded {len(targets)} targets")
            return targets
        except Exception as e:
            self.logger.error(f"Failed to load targets: {e}")
            return []
    
    def navigate_to_profile(self, profile_url):
        """Navigate to Facebook profile"""
        try:
            self.driver.get(profile_url)
            time.sleep(5)
            
            # Check if profile exists
            if "this page isn't available" in self.driver.page_source.lower():
                self.logger.warning(f"Profile not available: {profile_url}")
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"Failed to navigate to profile {profile_url}: {e}")
            return False
    
    def find_report_option(self):
        """Find and click report option on profile"""
        try:
            # Look for report/friend options
            try:
                # Try different report button selectors
                report_buttons = self.driver.find_elements(By.XPATH, "//span[contains(text(), '...') or contains(text(), 'More')]")
                for button in report_buttons:
                    if button.is_displayed():
                        button.click()
                        time.sleep(2)
                        break
            except:
                pass
            
            # Look for report option in dropdown
            try:
                report_option = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Report') or contains(text(), 'Find support or report')]")
                report_option.click()
                time.sleep(3)
                return True
            except:
                self.logger.warning("Report option not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Error finding report option: {e}")
            return False
    
    def submit_report(self, violation_type="Fake Profile"):
        """Submit report with specified violation type"""
        try:
            # Select violation type
            try:
                fake_profile_option = self.driver.find_element(By.XPATH, f"//span[contains(text(), '{violation_type}')]")
                fake_profile_option.click()
                time.sleep(2)
            except:
                # If specific option not found, select first available
                try:
                    first_option = self.driver.find_element(By.XPATH, "//div[@role='radio']")
                    first_option.click()
                    time.sleep(2)
                except:
                    pass
            
            # Submit report
            try:
                submit_buttons = self.driver.find_elements(By.XPATH, "//div[@role='button' and contains(text(), 'Submit')]")
                for button in submit_buttons:
                    if button.is_displayed():
                        button.click()
                        time.sleep(3)
                        break
            except:
                pass
                
            self.logger.info(f"Report submitted for violation: {violation_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error submitting report: {e}")
            return False
    
    def process_target(self, target_url, index, total):
        """Single target process করুন"""
        try:
            self.logger.info(f"Processing target: {target_url} ({index+1}/{total})")
            
            # Update job progress
            if self.jobs_dict and self.job_id:
                self.jobs_dict[self.job_id]['progress'] = int((index / total) * 100)
            
            # Navigate to profile
            if not self.navigate_to_profile(target_url):
                return False
            
            # Find and click report option
            if not self.find_report_option():
                return False
            
            # Submit report
            if self.submit_report():
                result = {
                    'target_url': target_url,
                    'status': 'reported',
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                self.reporting_results.append(result)
                self.logger.info(f"Successfully reported: {target_url}")
                return True
            else:
                self.logger.warning(f"Failed to report: {target_url}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error processing target {target_url}: {e}")
            return False
    
    def run_batch_reporting(self):
        """Batch reporting run করুন"""
        try:
            self.logger.info("Starting batch reporting process...")
            
            # Initialize driver
            if not self.setup_driver():
                self.logger.error("Failed to initialize WebDriver")
                return False
            
            # Login to Facebook
            if not self.login_to_facebook():
                self.logger.error("Failed to login to Facebook")
                return False
            
            # Load targets
            targets = self.load_targets()
            if not targets:
                self.logger.error("No targets to process")
                return False
            
            # Process targets
            processed_count = 0
            success_count = 0
            total_targets = len(targets)
            
            for i, target in enumerate(targets):
                if processed_count >= self.config.MAX_REPORTS_PER_SESSION:
                    self.logger.info("Maximum reports per session reached")
                    break
                
                success = self.process_target(target, i, total_targets)
                if success:
                    success_count += 1
                processed_count += 1
                
                # Update job results
                if self.jobs_dict and self.job_id:
                    self.jobs_dict[self.job_id]['results'] = self.reporting_results
                
                # Delay between reports
                time.sleep(self.config.DELAY_BETWEEN_REPORTS)
            
            self.logger.info(f"Batch reporting completed. Processed: {processed_count}, Success: {success_count}")
            
            # Save results
            self.save_results()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Batch reporting failed: {e}")
            traceback.print_exc()
            return False
        finally:
            # Cleanup
            if self.driver:
                self.driver.quit()
    
    def save_results(self):
        """Save reporting results to file"""
        try:
            os.makedirs('data/reports', exist_ok=True)
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            
            # Save as JSON
            json_path = f'data/reports/report_results_{timestamp}.json'
            with open(json_path, 'w') as f:
                json.dump(self.reporting_results, f, indent=2)
            
            self.logger.info(f"Results saved to {json_path}")
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")

if __name__ == "__main__":
    reporter = FacebookAutoReporter()
    reporter.run_batch_reporting()