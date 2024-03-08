import googleapiclient.discovery
import googleapiclient.errors
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import os
from dotenv import load_dotenv
import psycopg2


class YoutubeCrawler:
    def __init__(self):
        self.GOOGLE_API_KEY = None
        self.youtube = None
        self.driver = None
    
    def set_webdriver(self):
        self.driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
    
    def quit_webdriver(self):
        self.driver.quit()
        
    def set_youtube_api(self, n):
        load_dotenv('../../../resources/secret.env')
        self.GOOGLE_API_KEY = os.getenv(f'GOOGLE_API_KEY{n}')
        
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # 보안 통신(SSL/TLS)을 사용하지 않고 HTTP를 통해 OAuth 인증을 수행.
        self.youtube = googleapiclient.discovery.build(
            'youtube', 'v3', developerKey=self.GOOGLE_API_KEY)
    
    def get_menu_id_and_name_list(self, cursor):
        try:
            # Execute query to select all names and ids from the menu table
            cursor.execute("SELECT id, name FROM menu ORDER BY 1 LIMIT 808") # 상위 808개의 레시피 추출.
            menu_infos = cursor.fetchall()
            return menu_infos
        except (Exception, psycopg2.Error) as error:
            print("Error while reading menu info:", error)
            return []

    def search_menu_name(self, menu_name):
        try:
            print("Youtube Data API를 호출합니다.")
    
            request = self.youtube.search().list(
                part="id",
                maxResults=10,
                q=menu_name + " 레시피"
            )
            response = request.execute()
            
            print(f"<{menu_name} 레시피에 대한 검색 완료>")
            video_url_list = []
            for item in response["items"]:
                youtube_video_id = item["id"]["videoId"]
                video_url = "https://www.youtube.com/watch?v="+youtube_video_id
                video_url_list.append(video_url)
            
            return video_url_list
            
        except Exception as e:
            print(f"에러 발생 >> {e}")
            raise

    def get_video_infos(self, video_url):
        try:
            print(f"{video_url}에 대한 동영상 정보를 추출합니다.")
            
            self.driver.get(video_url)
            self.driver.implicitly_wait(10)
            
            # 영상 정보 더보기 버튼 클릭.
            expand_btn_element = self.driver.find_element(By.ID, "expand")
            expand_btn_element.send_keys(Keys.ENTER)
            self.driver.implicitly_wait(60)
            
            thumbnail_element = self.driver.find_element(By.XPATH, "/html/body/div[1]/link[2]")
            thumbnail = thumbnail_element.get_attribute("href")
            
            title_element = self.driver.find_element(By.XPATH, "/html/head/meta[3]")
            title = title_element.get_attribute("content")
            
            channel_img_element = self.driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[2]/div[1]/ytd-video-owner-renderer/a/yt-img-shadow/img")
            channel_img = channel_img_element.get_attribute("src")
            
            channel_name_element = self.driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[2]/div[1]/ytd-video-owner-renderer/div[1]/ytd-channel-name/div/div/yt-formatted-string/a")
            channel_name = channel_name_element.text
            channel_link = channel_name_element.get_attribute("href")
            
            channel_subscribers_count_element = self.driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[2]/div[1]/ytd-video-owner-renderer/div[1]/yt-formatted-string")
            channel_subscribers_count = channel_subscribers_count_element.text
            
            thumbsup_count_element = self.driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[2]/div[2]/div/div/ytd-menu-renderer/div[1]/segmented-like-dislike-button-view-model/yt-smartimation/div/div/like-button-view-model/toggle-button-view-model/button-view-model/button/div[2]")
            thumbsup_count = thumbsup_count_element.text
            
            views_count_element = self.driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[4]/div[1]/div/ytd-watch-info-text/div/yt-formatted-string/span[1]")
            views_count = views_count_element.text
            
            uploaded_date_element = self.driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[4]/div[1]/div/ytd-watch-info-text/div/yt-formatted-string/span[3]")
            uploaded_date = uploaded_date_element.text
            
            video_text_element = self.driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[4]/div[1]/div/ytd-text-inline-expander/yt-attributed-string")
            video_text = video_text_element.text
            
            return (thumbnail, title, channel_img, channel_name, channel_link, channel_subscribers_count, thumbsup_count, views_count, uploaded_date, video_text)
            
        except Exception as e:
            print(f"에러 발생 >> {e}")
            raise

    def query_to_gemini(self, query_string):
        response = self.gemini.generate_content(query_string)
        return response.text    