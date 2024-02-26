from extract.youtube_crawler import YoutubeCrawler
from transfer.youtube_preprocessor import YoutubePreprocessor
from load.youtube_loader import YoutubeLoader
import time


if __name__ == "__main__":
    
    youtubeCrawler = YoutubeCrawler()
    youtubeCrawler.set_webdriver()
    
    youtubePreprocessor = YoutubePreprocessor()
    youtubePreprocessor.set_gemini_api()
    
    cook_name_file_path = "cook_basic.csv"
    cook_name_list = youtubeCrawler.get_cook_name_list(cook_name_file_path)
    
    for n in range(5):
        youtubeCrawler.set_youtube_api(n)
        for i in range(n*100, len(cook_name_list)): # api 당 최대 100개의 음식명 검색 가능.
            print('*'*80)
            print('cook_name_list index:', i)
            cook_name = cook_name_list[i]
            try:
                video_link_list = youtubeCrawler.search_cook_name(cook_name)
            except:
                break
            for j in range(len(video_link_list)):
                print('video_link_list index:', j)
                video_link = video_link_list[j]
                try:
                    (video_thumbnail, video_title, channel_img, channel_name, channel_link, channel_subscribers_count, video_thumbsup_count, video_views_count, video_uploaded_date, video_text) = youtubeCrawler.get_video_infos(video_link)
                except:
                    youtubeCrawler.set_webdriver()
                    continue
                time.sleep(0.01)
                """
                1. cook_name
                2. video_link
                3. video_title
                4. video_thumbnail
                5. video_thumbsup_count
                6. video_views_count
                7. video_uploaded_date
                8. video_text
                9. channel_link
                10. channel_name
                11. channel_img
                12. channel_subscribers_count
                """
                # 채널 관련 데이터
                channel_link = youtubePreprocessor.preprocess_text(channel_link)
                channel_name = youtubePreprocessor.preprocess_text(channel_name)
                channel_img = youtubePreprocessor.preprocess_text(channel_img)
                channel_subscribers_count = youtubePreprocessor.convert_to_number(channel_subscribers_count)
                
                # 유튜브 비디오 관련 데이터
                video_link = youtubePreprocessor.preprocess_text(video_link)
                video_title = youtubePreprocessor.preprocess_text(video_title)
                video_thumbnail = youtubePreprocessor.preprocess_text(video_thumbnail)
                video_thumbsup_count = youtubePreprocessor.convert_to_number(video_thumbsup_count)
                video_views_count = youtubePreprocessor.convert_to_number(video_views_count)
                video_uploaded_date = youtubePreprocessor.convert_to_date(video_uploaded_date)
                video_text = youtubePreprocessor.preprocess_text(video_text)
                
                # 레시피 관련 데이터. 예) [[재료명1, 첨가량1], [재료명2, 첨가량2], ...]
                ingredient_and_amount_list = youtubePreprocessor.convert_to_ingredient_and_amount(video_text)
                
                # db write 코드 작성
                
                
                
    youtubeCrawler.quit_webdriver()