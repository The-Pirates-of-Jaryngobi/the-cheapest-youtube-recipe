import psycopg2


class YoutubeLoader:
    def __init__(self, conn, cursor):
        self.conn = conn
        self.cursor = cursor
    
    def write_to_channel(self, name, url, subscribers_count, img_src):
        try:
            # Check if the channel with the same URL exists
            self.cursor.execute("SELECT id FROM channel WHERE url = %s", (url,))
            existing_channel = self.cursor.fetchone()
            
            if existing_channel:
                # If the channel already exists, return its ID
                channel_id = existing_channel[0]
                print("Channel with the same URL already exists. Returning existing channel ID:", channel_id)
            else:
                # If the channel doesn't exist, insert new data and return its ID
                insert_query = "INSERT INTO channel (name, url, subscribers_count, img_src) VALUES (%s, %s, %s, %s) RETURNING id"
                self.cursor.execute(insert_query, (name, url, subscribers_count, img_src))
                channel_id = self.cursor.fetchone()[0]
                self.conn.commit()
                print("New channel data inserted successfully. New channel ID:", channel_id)
            
            return channel_id
        except (Exception, psycopg2.Error) as error:
            print("Error while writing to channel table:", error)
            self.conn.rollback()
    
    def write_to_youtube_video(self, channel_id, title, url, thumbnail_src, views, thumbsup_count, uploaded_date):
        try:
            # Check if the video with the same URL exists
            self.cursor.execute("SELECT id FROM youtube_video WHERE url = %s", (url,))
            existing_video = self.cursor.fetchone()
            
            if existing_video:
                # If the video already exists, return its ID
                video_id = existing_video[0]
                print("Video with the same URL already exists. Returning existing video ID:", video_id)
            else:
                # If the video doesn't exist, insert new data and return its ID
                insert_query = "INSERT INTO youtube_video (channel_id, title, url, thumbnail_src, views, thumbsup_count, uploaded_date) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id"
                self.cursor.execute(insert_query, (channel_id, title, url, thumbnail_src, views, thumbsup_count, uploaded_date))
                video_id = self.cursor.fetchone()[0]
                self.conn.commit()
                print("New video data inserted successfully. New video ID:", video_id)
            
            return video_id
        except (Exception, psycopg2.Error) as error:
            print("Error while writing to youtube_video table:", error)
            self.conn.rollback()
    
    def write_to_recipe(self, youtube_video_id, menu_id, full_text):
        try:
            # Check if the recipe with the same youtube_video_id and menu_id exists
            self.cursor.execute("SELECT id FROM recipe WHERE youtube_video_id = %s AND menu_id = %s", (youtube_video_id, menu_id))
            existing_recipe = self.cursor.fetchone()
            
            if existing_recipe:
                # If the recipe already exists, do nothing
                recipe_id = existing_recipe[0]
                print("Recipe with the same youtube_video_id and menu_id already exists. Skipping insertion.")
            else:
                # If the recipe doesn't exist, insert new data
                insert_query = "INSERT INTO recipe (youtube_video_id, menu_id, full_text) VALUES (%s, %s, %s) RETURNING id"
                self.cursor.execute(insert_query, (youtube_video_id, menu_id, full_text))
                recipe_id = self.cursor.fetchone()[0]
                self.conn.commit()
                print("New recipe data inserted successfully. New recipe ID:", recipe_id)
            
            return recipe_id
        except (Exception, psycopg2.Error) as error:
            print("Error while writing to recipe table:", error)
            self.conn.rollback()
    
    def write_to_ingredient(self, recipe_id, name, vague):
        try:
            # Check if the ingredient with the same recipe_id and name exists
            self.cursor.execute("SELECT id FROM ingredient WHERE recipe_id = %s AND name = %s", (recipe_id, name))
            existing_ingredient = self.cursor.fetchone()
            
            if existing_ingredient:
                # If the ingredient already exists, do nothing
                print("Ingredient with the same recipe_id and name already exists. Skipping insertion.")
            else:
                # If the ingredient doesn't exist, insert new data
                insert_query = "INSERT INTO ingredient (recipe_id, name, vague) VALUES (%s, %s, %s) RETURNING id"
                self.cursor.execute(insert_query, (recipe_id, name, vague))
                ingredient_id = self.cursor.fetchone()[0]
                self.conn.commit()
                print("New ingredient data inserted successfully. New ingredient ID:", ingredient_id)
            
        except (Exception, psycopg2.Error) as error:
            print("Error while writing to ingredient table:", error)
            self.conn.rollback()