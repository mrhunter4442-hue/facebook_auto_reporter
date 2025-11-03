import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ContentScraper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.logger = logging.getLogger(__name__)
        
    def scrape_profile_data(self, profile_url):
        """Profile data scrape করুন"""
        try:
            self.logger.info(f"Scraping data from: {profile_url}")
            self.driver.get(profile_url)
            time.sleep(3)
            
            profile_data = {
                'profile_info': self.extract_profile_info(),
                'posts': self.extract_recent_posts(),
                'images': self.extract_profile_images(),
                'friends_count': self.get_friends_count(),
                'timestamp': time.time()
            }
            
            return profile_data
            
        except Exception as e:
            self.logger.error(f"Scraping failed: {e}")
            return {'error': str(e)}
            
    def extract_profile_info(self):
        """Profile information extract করুন"""
        try:
            # Name extraction
            name_element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//h1"))
            )
            name = name_element.text
            
            # Bio extraction
            bio_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'bio')]")
            bio = bio_elements[0].text if bio_elements else ""
            
            return {
                'name': name,
                'bio': bio,
                'profile_url': self.driver.current_url
            }
        except Exception as e:
            self.logger.error(f"Profile info extraction failed: {e}")
            return {'name': 'Unknown', 'bio': '', 'error': str(e)}
    
    def extract_recent_posts(self):
        """Recent posts extract করুন"""
        posts = []
        try:
            # Scroll to load posts
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            post_elements = self.driver.find_elements(By.XPATH, "//div[contains(@data-ad-preview, 'message')]")
            
            for post in post_elements[:5]:  # First 5 posts
                try:
                    post_data = {
                        'text': post.text,
                        'timestamp': self.get_post_timestamp(post),
                        'reactions': self.get_post_reactions(post)
                    }
                    posts.append(post_data)
                except Exception as e:
                    self.logger.warning(f"Failed to extract post: {e}")
                    
        except Exception as e:
            self.logger.error(f"Posts extraction failed: {e}")
        
        return posts
    
    def get_post_timestamp(self, post_element):
        """Post timestamp extract করুন"""
        try:
            time_element = post_element.find_element(By.XPATH, ".//abbr")
            return time_element.get_attribute('title') or time_element.text
        except:
            return "Unknown"
    
    def get_post_reactions(self, post_element):
        """Post reactions extract করুন"""
        try:
            reaction_elements = post_element.find_elements(By.XPATH, ".//span[contains(@class, 'like')]")
            return len(reaction_elements)
        except:
            return 0
    
    def extract_profile_images(self):
        """Profile images extract করুন"""
        images = []
        try:
            img_elements = self.driver.find_elements(By.XPATH, "//img")
            for img in img_elements[:10]:  # First 10 images
                src = img.get_attribute('src')
                if src and 'facebook.com' in src:
                    images.append(src)
        except Exception as e:
            self.logger.error(f"Image extraction failed: {e}")
        
        return images
    
    def get_friends_count(self):
        """Friends count extract করুন"""
        try:
            friends_elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'friends')]")
            for element in friends_elements:
                text = element.text
                if 'friends' in text.lower():
                    return text
            return "Unknown"
        except:
            return "Unknown"