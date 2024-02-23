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
from datetime import datetime
import time

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
        
    def set_youtube_api(self, n):
        load_dotenv('../../resource/secret.env')
        self.GOOGLE_API_KEY = os.getenv(f'GOOGLE_API_KEY{n}')
        
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
            
            print(f"총 요리 수: {len(cook_name_list)}")
            
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
            
            print(f"<{cook_name} 레시피에 대한 검색 완료>")
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
            channel_id = channel_name_element.get_attribute("href")
            
            subscribers_count_element = self.driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[2]/div[1]/ytd-video-owner-renderer/div[1]/yt-formatted-string")
            subscribers_count = subscribers_count_element.text
            
            thumbsup_count_element = self.driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[2]/div[2]/div/div/ytd-menu-renderer/div[1]/segmented-like-dislike-button-view-model/yt-smartimation/div/div/like-button-view-model/toggle-button-view-model/button-view-model/button/div[2]")
            thumbsup_count = thumbsup_count_element.text
            
            views_count_element = self.driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[4]/div[1]/div/ytd-watch-info-text/div/yt-formatted-string/span[1]")
            views_count = views_count_element.text
            
            uploaded_date_element = self.driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[4]/div[1]/div/ytd-watch-info-text/div/yt-formatted-string/span[3]")
            uploaded_date = uploaded_date_element.text
            
            text_element = self.driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[4]/div[1]/div/ytd-text-inline-expander/yt-attributed-string")
            text = text_element.text
            
            return (thumbnail, title, channel_img, channel_name, channel_id, subscribers_count, thumbsup_count, views_count, uploaded_date, text)
            
        except Exception as e:
            print(f"에러 발생 >> {e}")
            raise

    def query_to_gemini(self, query_string):
        response = self.gemini.generate_content(query_string)
        return response.text

if __name__ == "__main__":
    
    youtubeCrawler = YoutubeCrawler()
    youtubeCrawler.set_webdriver()
    youtubeCrawler.set_gemini_api()
    
    cook_name_file_path = "cook_basic.csv"
    cook_name_list = youtubeCrawler.get_cook_name_list(cook_name_file_path)
    
    column_list = ['cook_name', 'video_id', 'video_title', 'video_thumbnail', 'video_thumbsup_count', 'video_views_count', 'video_uploaded_date', 'video_text', 'channel_id', 'channel_name', 'channel_img', 'subsribers_count']
    row_list = []
    
    for n in range(5):
        youtubeCrawler.set_youtube_api(n)
        for i in range(n*100, len(cook_name_list)):
            print('*'*80)
            print('cook_name_list index:', i)
            cook_name = cook_name_list[i]
            try:
                video_url_list = youtubeCrawler.search_cook_name(cook_name)
            except:
                break
            for j in range(len(video_url_list)):
                print('video_url_list index:', j)
                video_url = video_url_list[j]
                try:
                    (thumbnail, title, channel_img, channel_name, channel_id, subscribers_count, thumbsup_count, views_count, uploaded_date, text) = youtubeCrawler.get_video_infos(video_url)
                except:
                    youtubeCrawler.set_webdriver()
                    continue
                time.sleep(0.01)
                row = [cook_name, video_url, title, thumbnail, thumbsup_count, views_count, uploaded_date, text, channel_id, channel_name, channel_img, subscribers_count]
                row_list.append(row)
    
    df = pd.DataFrame(row_list, columns=column_list)

    # CSV 파일 이름 설정
    csv_filename = f'../output_files/youtube_raw_dataset_{datetime.now().strftime("%Y-%m-%d-%H-%M")}.csv'

    # DataFrame을 CSV 파일로 저장
    df.to_csv(csv_filename, index=False)

    print(f"파일 '{csv_filename}'이 생성되었습니다.")
    
    youtubeCrawler.quit_webdriver()