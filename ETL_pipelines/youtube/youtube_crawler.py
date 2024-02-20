import googleapiclient.discovery
import googleapiclient.errors
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import os
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai

class YoutubeCrawler:
    def __init__(self):
        self.GOOGLE_API_KEY = None
        self.youtube = None
        self.gemini = None
        self.driver = None
    
    def set_webdriver(self):
        self.driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
    
    def quit_webdriver(self):
        self.driver.quit()
        
    def set_youtube_api(self):
        load_dotenv('../../resource/secret.env')
        self.GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
        
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # 보안 통신(SSL/TLS)을 사용하지 않고 HTTP를 통해 OAuth 인증을 수행.
        self.youtube = googleapiclient.discovery.build(
            'youtube', 'v3', developerKey=self.GOOGLE_API_KEY)
    
    def set_gemini_api(self):
        genai.configure(api_key=self.GOOGLE_API_KEY)
        self.gemini = genai.GenerativeModel('gemini-pro')
    
    def get_cook_name_list(self, file_path):
        try:
            print(f"{file_path}에서 요리명 정보를 읽습니다.")
            
            df = pd.read_csv(file_path)
            cook_name_list = df["식품명"].tolist()
            
            print(f"총 요리명 수: {len(cook_name_list)}")
            print("*"*80)
            
            return cook_name_list
            
        except Exception as e:
            print(f"에러 발생 >> {e}")

    def search_cook_name(self, cook_name):
        try:
            print("Youtube Data API를 호출합니다.")
    
            request = self.youtube.search().list(
                part="id",
                maxResults=10,
                q=cook_name + " 레시피"
            )
            response = request.execute()
            
            print(f"<{cook_name} 레시피에 대한 검색 결과>")
            video_url_list = []
            for item in response["items"]:
                youtube_video_id = item["id"]["videoId"]
                video_url = "https://www.youtube.com/watch?v="+youtube_video_id
                video_url_list.append(video_url)
            
            print(f"총 동영상 수 : {len(video_url_list)}")
            print("*"*80)
            
            return video_url_list
            
        except Exception as e:
            print(f"에러 발생 >> {e}")
            raise

    def get_video_infos(self, video_url):
        try:
            print(f"{video_url}에 대한 동영상 정보를 추출합니다.")
            
            self.driver.get(video_url)
            self.driver.implicitly_wait(60)
            
            # 영상 정보 더보기 버튼 클릭.
            expand_btn_element = self.driver.find_element(By.ID, "expand")
            expand_btn_element.send_keys(Keys.ENTER)
            self.driver.implicitly_wait(60)
            
            thumbnail_element = self.driver.find_element(By.XPATH, "/html/body/div[1]/link[2]")
            thumbnail = thumbnail_element.get_attribute("href")
            print(f"thumbnail : {thumbnail}")
            print("-"*60)
            
            title_element = self.driver.find_element(By.XPATH, "/html/head/meta[3]")
            title = title_element.get_attribute("content")
            print(f"title : {title}")
            print("-"*60)
            
            channel_img_element = self.driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[2]/div[1]/ytd-video-owner-renderer/a/yt-img-shadow/img")
            channel_img = channel_img_element.get_attribute("src")
            print(f"channel_img : {channel_img}")
            print("-"*60)
            
            channel_name_element = self.driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[2]/div[1]/ytd-video-owner-renderer/div[1]/ytd-channel-name/div/div/yt-formatted-string/a")
            channel_name = channel_name_element.text
            print(f"channel_name : {channel_name}")
            print("-"*60)
            
            subscribers_count_element = self.driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[2]/div[1]/ytd-video-owner-renderer/div[1]/yt-formatted-string")
            subscribers_count = subscribers_count_element.text
            print(f"subscribers_count : {subscribers_count}")
            print("-"*60)
            
            thumbsup_count_element = self.driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[2]/div[2]/div/div/ytd-menu-renderer/div[1]/segmented-like-dislike-button-view-model/yt-smartimation/div/div/like-button-view-model/toggle-button-view-model/button-view-model/button/div[2]")
            thumbsup_count = thumbsup_count_element.text
            print(f"thumbsup_count : {thumbsup_count}")
            print("-"*60)
            
            views_count_element = self.driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[4]/div[1]/div/ytd-watch-info-text/div/yt-formatted-string/span[1]")
            views_count = views_count_element.text
            print(f"views_count : {views_count}")
            print("-"*60)
            
            uploaded_date_element = self.driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[4]/div[1]/div/ytd-watch-info-text/div/yt-formatted-string/span[3]")
            uploaded_date = uploaded_date_element.text
            print(f"uploaded_date : {uploaded_date}")
            print("-"*60)
            
            text_element = self.driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[4]/div[1]/div/ytd-text-inline-expander/yt-attributed-string")
            text = text_element.text
            print(f"text : {text}")
            print("-"*60)
            
            print("*"*80)
            
            return [thumbnail, title, channel_img, channel_name, subscribers_count, thumbsup_count, views_count, uploaded_date, text]
            
        except Exception as e:
            print(f"에러 발생 >> {e}")
            raise

    def query_to_gemini(self, query_string):
        response = self.gemini.generate_content(query_string)
        return response.text

if __name__ == "__main__":
    
    youtubeCrawler = YoutubeCrawler()
    youtubeCrawler.set_webdriver()
    youtubeCrawler.set_youtube_api()
    youtubeCrawler.set_gemini_api()
        
    cook_name_file_path = "cook_basic.csv"
    cook_name_list = youtubeCrawler.get_cook_name_list(cook_name_file_path)
    
    for i in range(3):
        cook_name = cook_name_list[i]
        video_url_list = youtubeCrawler.search_cook_name(cook_name)
        for j in range(3):
            video_url = video_url_list[j]
            video_infos = youtubeCrawler.get_video_infos(video_url)
            query_string = video_infos[-1] + '\n 위 정보에서 "(재료명1, 첨가량1)\n(재료명2, 첨가량2)\n(재료명3, 첨가량3)" 형식으로 정보 리스트 내용만 반환해줘.'
            print(query_string)
            gemini_return_values = youtubeCrawler.query_to_gemini(video_infos[-1])
            print('-'*100)
            print('gemini 호출 결과 : ', gemini_return_values)
            print('-'*100)
            
    youtubeCrawler.quit_webdriver()