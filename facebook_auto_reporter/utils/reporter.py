import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ReportingEngine:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)
        self.logger = logging.getLogger(__name__)
        
    def report_profile(self, profile_url, violation_data):
        """Profile report submit করুন"""
        try:
            self.logger.info(f"Reporting profile: {profile_url}")
            
            # Navigate to profile
            self.driver.get(profile_url)
            time.sleep(3)
            
            # Find and click three dots menu
            if not self.click_three_dots_menu():
                return False
                
            # Find and click report option
            if not self.click_report_option():
                return False
                
            # Select violation category
            if not self.select_violation_category(violation_data):
                return False
                
            # Provide additional details
            if not self.provide_additional_details(violation_data):
                return False
                
            # Submit report
            if not self.submit_report():
                return False
                
            self.logger.info(f"Successfully reported: {profile_url}")
            return True
            
        except Exception as e:
            self.logger.error(f"Reporting failed for {profile_url}: {e}")
            return False
    
    def click_three_dots_menu(self):
        """Three dots menu click করুন"""
        try:
            # Try different selectors for three dots menu
            selectors = [
                "//div[@aria-label='More options']",
                "//div[contains(@class, 'more_options')]",
                "//span[contains(text(), '...')]",
                "//button[contains(@aria-label, 'More')]"
            ]
            
            for selector in selectors:
                try:
                    menu_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    menu_button.click()
                    time.sleep(2)
                    return True
                except:
                    continue
                    
            self.logger.error("Could not find three dots menu")
            return False
            
        except Exception as e:
            self.logger.error(f"Three dots menu click failed: {e}")
            return False
    
    def click_report_option(self):
        """Report option click করুন"""
        try:
            # Try different report option texts
            report_texts = [
                "Find support or report profile",
                "Report profile",
                "Give feedback or report this profile",
                "Report"
            ]
            
            for text in report_texts:
                try:
                    report_option = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{text}')]"))
                    )
                    report_option.click()
                    time.sleep(2)
                    return True
                except:
                    continue
                    
            self.logger.error("Could not find report option")
            return False
            
        except Exception as e:
            self.logger.error(f"Report option click failed: {e}")
            return False
    
    def select_violation_category(self, violation_data):
        """Violation category select করুন"""
        try:
            category = violation_data.get('report_category', '')
            
            # Map to Facebook's actual category names
            category_mapping = {
                'Impersonation': "Pretending to Be Someone",
                'Fake Profile': "Fake Account",