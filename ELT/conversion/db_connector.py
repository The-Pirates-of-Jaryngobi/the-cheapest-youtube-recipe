from dotenv import load_dotenv
import os
import psycopg2


class DBConnector:
    def __init__(self):
        self.conn = None
        self.cursor = None
    
    def set_connect_db(self):
        load_dotenv('../../resources/secret.env')
        conn_info = {
        "host": os.getenv('DB_HOST'),
        "database": 'service',
        "user": os.getenv('DB_USER'),
        "password": os.getenv('DB_PASSWORD')
        }
        try:
            self.conn = psycopg2.connect(**conn_info)
            self.cursor = self.conn.cursor()
            print("Database connected successfully!")
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL:", error)
    
    # ingredient 테이블로부터 "id"와 "vague" 칼럼 정보 리스트를 갖고 오는 함수
    def get_ingredient_data_list(self):
        try:
            query = "SELECT id, name, vague FROM ingredient;"
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            # 결과를 리스트 형태로 변환합니다. [ [id1, name1, vague1], [id2, name2, vague2], ... ]
            ingredient_data_list = [[result[0], result[1], result[2]] for result in results]
            return ingredient_data_list
        except (Exception, psycopg2.Error) as error:
            print("Error while getting from ingredient table:", error)
    
    # ingredient 테이블에 "volume"과 "unit" 칼럼 정보를 입력하는 함수
    def write_to_ingredient(self, ingredient_id, ingredient_volume, ingredient_unit):
        try:
            query = "UPDATE ingredient SET volume = %s, unit = %s WHERE id = %s"
            self.cursor.execute(query, (ingredient_volume, ingredient_unit, ingredient_id))
            self.conn.commit()
            print("Ingredient data inserted successfully.")
        except (Exception, psycopg2.Error) as error:
            print("Error while writing to ingredient table:", error)
            self.conn.rollback()
    
    # unit_conversion 테이블에서 "unit_name"에 대해서 쿼리하여 "converted_vol"과 "standard_unit"을 갖고 오는 함수
    def get_converted_volume_and_standard_unit(self, unit_name):
        try:
            query = "SELECT converted_vol, standard_unit FROM unit_conversion WHERE unit_name = %s"
            self.cursor.execute(query, (unit_name,))
            result = self.cursor.fetchone()
            if result:
                return float(result[0]), result[1]
            else:
                return False, False
        except (Exception, psycopg2.Error) as error:
            print("Error while getting from unit_conversion table:", error)
    
    # quantity_conversion 테이블에서 "ingredient_name"과 "unit_name"에 대해서 쿼리하여 "converted_gram"을 갖고 오는 함수
    def get_converted_gram(self, ingredient_name, unit_name):
        try:
            query = "SELECT converted_gram FROM quantity_conversion WHERE ingredient_name = %s AND unit_name = %s"
            self.cursor.execute(query, (ingredient_name, unit_name))
            result = self.cursor.fetchone()
            if result:
                return float(result[0])
            else:
                return False
        except (Exception, psycopg2.Error) as error:
            print("Error while getting from quantity_conversion table:", error)
    
    def close_db(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()
            print("DB Connection closed.")