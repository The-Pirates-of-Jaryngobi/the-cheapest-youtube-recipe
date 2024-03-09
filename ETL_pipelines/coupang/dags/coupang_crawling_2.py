from airflow import DAG
from airflow.models import Variable
from airflow.decorators import task
from bs4 import BeautifulSoup
from urllib.parse import quote
from datetime import timedelta, datetime
import requests
import csv
import boto3
import os
import psycopg2
import logging
import re
import time

# 상품명을 기반으로 쿠팡에서 상품 검색 요청을 보내는 함수
def ingredientNameRequests(ingredient_name):
    logger = logging.getLogger('ingredientNameRequests')
    
    encoded_string = quote(ingredient_name, encoding='utf-8')
    logger.info(f"Ingredient Name: {ingredient_name}, Encoded String: {encoded_string}")

    url = f"https://www.coupang.com/np/search?component=&q={encoded_string}&channel=user"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3"
    }

    retries = 3
    delay = 5

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Error occurred while making a request of ingredient_name: {e}")
        
        if attempt < retries - 1:
            logger.info(f"Retrying in {delay} seconds...")
            time.sleep(delay)

    logger.error("Max retries reached. Could not retrieve data.")
    return None

# 쿠팡에서 받은 응답을 파싱하여 상품 세부 정보를 추출하는 함수
def ingredientsDetailResult(response, ingredient_name, ingredient_result):
    logger = logging.getLogger('ingredientsDetailResult')
    try:
        bsObj = BeautifulSoup(response.content, "html.parser")
        ul = bsObj.find("ul", id="productList") 
        lis = ul.find_all("li") 
    except Exception as e:
        logger.error('Failed to search ingredient_name on coupang')
        return ingredient_result

    rank_number = 10
    rank_number_list = [i for i in range(1, rank_number+1)]
    rank_class_name = None

    for li in lis:
        ingredient_detail = []

        if rank_class_name == None and len(rank_number_list) != 0:
            rank = rank_number_list.pop(0)
            rank_class_name = 'number no-' + str(rank)
            

        if li.find('span', class_=rank_class_name) != None:
            ingredient_detail.append(ingredient_name)

            rank = int(li.find('span', class_=rank_class_name).text)
            ingredient_detail.append(rank)

            current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            ingredient_detail.append(current_time)

            product_title = li.find('div', class_='name').text if li.find('div', class_='name') else None
            ingredient_detail.append(product_title)

            origial_price = int(li.find('del', class_='base-price').text.replace(',', '')) if li.find('del', class_='base-price') else None
            ingredient_detail.append(origial_price)

            price = int(li.find('strong', class_='price-value').text.replace(',', '')) if li.find('strong', class_='price-value') else None
            ingredient_detail.append(price)

            unit_price_string = li.find('span', class_='unit-price').text.replace(' ', '').replace(',', '')[1:-1] if li.find('span', class_='unit-price') else None
            if unit_price_string != None:
                numbers = re.findall(r'\d+', unit_price_string)
                unit_and_unit_price = [int(num) for num in numbers]
                unit = unit_and_unit_price[0]
                unit_price = unit_and_unit_price[1]
                measure = re.findall(r'\d+(.*?)당', unit_price_string)[0]
                gram_price = unit_price / unit if measure in ('g', 'ml') else None
                ingredient_detail.append(unit)
                ingredient_detail.append(measure)
                ingredient_detail.append(unit_price)
                ingredient_detail.append(gram_price)
            else:
                ingredient_detail.append(None)
                ingredient_detail.append(None)
                ingredient_detail.append(None)
                ingredient_detail.append(None)
                
            discount_rate = li.find('span', class_='instant-discount-rate').text if li.find('span', class_='instant-discount-rate') else None
            ingredient_detail.append(discount_rate)

            badage_rocket = '로켓배송' if li.find('span', class_='badge rocket') else None
            ingredient_detail.append(badage_rocket)

            review_count = int(li.find('span', class_='rating-total-count').text[1:-1]) if li.find('span', class_='rating-total-count') else None
            ingredient_detail.append(review_count)

            url = 'https://www.coupang.com'+li.find('a', href=True)['href'] if li.find('a', href=True) else None
            ingredient_detail.append(url)

            if li.find('img', class_='search-product-wrap-img').get('data-img-src') is not None:
                image = 'https:' + li.find('img', class_='search-product-wrap-img').get('data-img-src')
            elif li.find('img', class_='search-product-wrap-img').get('src') is not None:
                image = 'https:' + li.find('img', class_='search-product-wrap-img').get('src')
            else:
                image = None
            ingredient_detail.append(image)

            ingredient_result.append(ingredient_detail)
            rank_class_name = None

            logger.info(f"Ingredient Detail: {ingredient_detail}")

            if len(rank_number_list) == 0:
                return ingredient_result

    return ingredient_result

# Airflow DAG 태스크: DB에서 상품명을 가져오는 함수
@task
def import_ingredient_name_table():
    conn = psycopg2.connect(
        dbname=Variable.get('dbname'),
        user=Variable.get('user'),
        password=Variable.get('password'),
        host=Variable.get('host'),
        port='5432'
    )

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ingredient")
    table = cursor.fetchall()
    conn.close()

    youtube_dataset = [list(row) for row in table]
    ingredient_name_list = []

    for row in youtube_dataset:
        ingredient_name_list.append(row[2])

    ingredient_name_list = set(ingredient_name_list)
    ingredient_name_list = list(ingredient_name_list)
    ingredient_name_list.sort()
    ingredient_name_list = ingredient_name_list[(len(ingredient_name_list)//10)*1:(len(ingredient_name_list)//10)*2]
    
    return ingredient_name_list

# Airflow DAG 태스크: CSV 파일에서 상품명을 가져오는 함수
@task
def import_csv():
    dag_folder = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(
        dag_folder, 'youtube_preprocessed_dataset_2024-02-23-15-56.csv')
    ingredient_name_list = []
    with open(file_path, 'r', encoding='utf-8') as file:
        youtube_dataset = [line.strip().split(',')
                           for line in file.readlines()]
        ingredient_name_list = []
        for data in youtube_dataset:
            if len(data) != 0:
                ingredient_name_list.append(data[0])

        ingredient_name_list = set(ingredient_name_list)
        ingredient_name_list = list(ingredient_name_list)
        ingredient_name_list.sort()
        
    return ingredient_name_list

# Airflow DAG 태스크: 상품명을 기반으로 상품 정보를 추출 및 변환하는 함수
@task
def extract_and_transform(ingredient_name_list):
    ingredient_result = [['ingredient_name', 'rank', 'time_stamp', 'product_title', 'origial_price',
                          'price','unit','measure', 'unit_price', 'gram_price', 'discount_rate', 'badage_rocket', 'review_count', 'url', 'image']]
    while len(ingredient_name_list) != 0:
        ingredient_name = ingredient_name_list.pop(0)
        ingredient_response = ingredientNameRequests(ingredient_name)
        ingredient_result = ingredientsDetailResult(
            ingredient_response, ingredient_name, ingredient_result)
    return ingredient_result

# Airflow DAG 태스크: 추출 및 변환된 상품 정보를 CSV 파일에 쓰는 함수
@task
def write_to_csv(ingredient_result):
    current_time = datetime.utcnow()
    file_name = f'ingredient_result_2_{current_time.strftime("%Y-%m-%d_%H-%M-%S")}.csv'
    with open(file_name, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows(ingredient_result)
    return file_name

# Airflow DAG 태스크: CSV 파일을 S3에 업로드하는 함수
@task
def load_to_s3(file_name):
    aws_access_key_id = Variable.get('aws_access_key_id')
    aws_secret_access_key = Variable.get('aws_secret_access_key')

    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)

    bucket_name = 'de-6-1-bucket'
    local_file_path = file_name
    s3_folder_key = 'coupang/'
    s3_file_key = s3_folder_key + local_file_path
    s3.upload_file(local_file_path, bucket_name, s3_file_key)

# Airflow DAG 태스크: RDS에 상품 정보를 로드하는 함수
@task
def load_to_rds(ingredient_result):
    conn = psycopg2.connect(
        dbname=Variable.get('dbname'),
        user=Variable.get('user'),
        password=Variable.get('password'),
        host=Variable.get('host'),
        port='5432'
    )

    cur = conn.cursor()
    drop_create_table_query = """
    DROP TABLE IF EXISTS product_2;
    CREATE TABLE product_2 (
        ingredient_name varchar(255),
        rank integer,
        time_stamp varchar(255),
        product_title varchar(255),
        origial_price integer,
        price integer,
        unit integer,
        measure varchar(255),
        unit_price integer,
        gram_price float,
        discount_rate varchar(255),
        badage_rocket varchar(255),
        review_count integer,
        url varchar(255),
        image varchar(255)
    )
    """

    insert_query = """
    INSERT INTO product_2 (
        ingredient_name,
        rank,
        time_stamp,
        product_title,
        origial_price,
        price,
        unit,
        measure,
        unit_price,
        gram_price,
        discount_rate,
        badage_rocket,
        review_count,
        url,
        image
    ) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    try:
        cur = conn.cursor()
        cur.execute(drop_create_table_query)
        cur.executemany(insert_query, ingredient_result[1:])
        conn.commit()
        cur.close()
        conn.close()
        print("Table created or replaced and data inserted successfully!")

    except Exception as e:
        print("Error:", e)


with DAG(
    dag_id='coupang_crawling_2',
    start_date=datetime(2024, 3, 1),
    schedule='* 5 * * *',
    catchup=False,
    default_args={
        'retries': 3,
        'retry_delay': timedelta(minutes=2),
    }
) as dag:

    ingredient_name_list = import_ingredient_name_table()
    ingredient_result = extract_and_transform(ingredient_name_list)
    file_name = write_to_csv(ingredient_result)
    load_to_s3(file_name)
    load_to_rds(ingredient_result)
