from extract.youtube_crawler import YoutubeCrawler
from transform.youtube_preprocessor import YoutubePreprocessor
from load.youtube_loader import YoutubeLoader
from dotenv import load_dotenv
import time
import psycopg2
import os


if __name__ == "__main__":
    
    # 데이터베이스 연결
    database='test'
    load_dotenv('../../resources/secret.env')
    conn_info = {
    "host": os.getenv('DB_HOST'),
    "database": database,
    "user": os.getenv('DB_USER'),
    "password": os.getenv('DB_PASSWORD')
    }
    try:
        conn = psycopg2.connect(**conn_info)
        cursor = conn.cursor()
        print("Database connected successfully!")
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL:", error)
    
    youtubeCrawler = YoutubeCrawler()
    youtubeCrawler.set_webdriver()
    
    youtubePreprocessor = YoutubePreprocessor()
    youtubePreprocessor.set_gemini_api(0)
    
    youtubeLoader = YoutubeLoader(conn=conn, cursor=cursor)
    
    menu_id_and_name_list = youtubeCrawler.get_menu_id_and_name_list(cursor=cursor)
    
    for n in range(5):
        youtubeCrawler.set_youtube_api(n)
        # youtubePreprocessor.set_gemini_api(n)
        for i in range(n*100, len(menu_id_and_name_list)): # api 당 최대 100개의 음식명 검색 가능.
            print('*'*80)
            print('menu_id_and_name_list index:', i)
            menu_id = menu_id_and_name_list[i][0]
            menu_name = menu_id_and_name_list[i][1]
            try:
                video_link_list = youtubeCrawler.search_menu_name(menu_name)
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
                
                # 채널 관련 데이터
                channel_link = youtubePreprocessor.preprocess_text(channel_link)
                channel_name = youtubePreprocessor.preprocess_text(channel_name)
                channel_img = youtubePreprocessor.preprocess_text(channel_img)
                channel_subscribers_count = youtubePreprocessor.convert_to_number(channel_subscribers_count.strip()[:-1])
                
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
                try:
                    channel_id = youtubeLoader.write_to_channel(
                        name=channel_name, 
                        url=channel_link, 
                        subscribers_count=channel_subscribers_count, 
                        img_src=channel_img
                    )
                    youtube_video_id = youtubeLoader.write_to_youtube_video(
                        channel_id=channel_id, 
                        title=video_title,
                        url=video_link,
                        thumbnail_src=video_thumbnail,
                        views=video_views_count,
                        thumbsup_count=video_thumbsup_count,
                        uploaded_date=video_uploaded_date
                    )
                    recipe_id = youtubeLoader.write_to_recipe(
                        youtube_video_id=youtube_video_id,
                        menu_id=menu_id,
                        full_text=video_text
                    )
                    if ingredient_and_amount_list:
                        for k in range(len(ingredient_and_amount_list)):
                            ingredient_name = ingredient_and_amount_list[k][0]
                            ingredient_vague = ingredient_and_amount_list[k][1]
                            youtubeLoader.write_to_ingredient(
                                recipe_id=recipe_id,
                                name=ingredient_name,
                                vague=ingredient_vague
                            )
                except Exception as e:
                    print(f'에러 발생 : {e}')
                
    youtubeCrawler.quit_webdriver()
    
    if conn:
        cursor.close()
        conn.close()
        print("DB Connection closed.")
