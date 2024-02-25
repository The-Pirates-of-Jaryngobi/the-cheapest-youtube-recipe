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


def ingredientNameRequests(product_name):
    encoded_string = quote(product_name, encoding='utf-8')
    print(product_name, encoded_string)
    url = f"https://www.coupang.com/np/search?component=&q={encoded_string}&channel=user"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
               "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3"}

    try:
        response = requests.get(url, headers=headers)
    except:
        response = None

    return response


def ingredientsDetailResult(response, ingredient_name, ingredient_result):
    try:
        bsObj = BeautifulSoup(response.content, "html.parser")
        ul = bsObj.find("ul", id="productList")  # 아이템 리스트부분 추출
        lis = ul.find_all("li")  # 각 아이템 추출
    except:
        print('검색안됨')
        return ingredient_result

    # baseurl = 'https://www.coupang.com'
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

            if li.find('span', class_=rank_class_name):
                rank = int(li.find('span', class_=rank_class_name).text)
                ingredient_detail.append(rank)
            else:
                rank = None
                ingredient_detail.append(rank)

            current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            ingredient_detail.append(current_time)

            if li.find('div', class_='name') != None:
                product_title = li.find('div', class_='name').text
                ingredient_detail.append(product_title)
            else:
                product_title = None
                ingredient_detail.append(product_title)

            if li.find('del', class_='base-price') != None:
                origial_price = int(
                    li.find('del', class_='base-price').text.replace(',', ''))
                ingredient_detail.append(origial_price)
            else:
                origial_price = None
                ingredient_detail.append(origial_price)

            if li.find('strong', class_='price-value') != None:
                price = int(
                    li.find('strong', class_='price-value').text.replace(',', ''))
                ingredient_detail.append(price)
            else:
                price = None
                ingredient_detail.append(price)

            if li.find('span', class_='unit-price') != None:
                unit_price = li.find('span', class_='unit-price').contents
                unit_price_str = ''
                for item in unit_price:
                    # 만약 현재 요소가 문자열이라면 출력합니다.
                    if isinstance(item, str):
                        unit_price_str += item
                    # 만약 현재 요소가 <em> 태그라면 그 안에 있는 텍스트를 출력합니다.
                    elif item.name == 'em':
                        unit_price_str += item.text
                ingredient_detail.append(unit_price_str.replace(
                    ' ', '').replace(',', '')[1:-1])
            else:
                unit_price = None
                ingredient_detail.append(unit_price)

            if li.find('span', class_='instant-discount-rate') != None:
                discount_rate = li.find(
                    'span', class_='instant-discount-rate').text
                ingredient_detail.append(discount_rate)
            else:
                discount_rate = None
                ingredient_detail.append(discount_rate)

            if li.find('span', class_='badge rocket') != None:
                badage_rocket = '로켓배송'
                ingredient_detail.append(badage_rocket)
            else:
                badage_rocket = None
                ingredient_detail.append(badage_rocket)

            if li.find('span', class_='rating-total-count') != None:
                review_count = int(
                    li.find('span', class_='rating-total-count').text[1:-1])
                ingredient_detail.append(review_count)
            else:
                review_count = None
                ingredient_detail.append(review_count)
                
            if li.find('a', href=True)['href'] != None:
                url = 'https://www.coupang.com'+li.find('a', href=True)['href']
                ingredient_detail.append(url)
            else:
                url = None
                ingredient_detail.append(url)

            if li.find('img', class_='search-product-wrap-img')['src']:
                image = 'https:' + \
                    li.find('img', class_='search-product-wrap-img')['src']
                ingredient_detail.append(image)
            else:
                image = None
                ingredient_detail.append(image)
                
            ingredient_result.append(ingredient_detail)
            rank_class_name = None
            print(ingredient_detail)

            if len(rank_number_list) == 0:
                return ingredient_result

    return ingredient_result


@task
def import_ingredient_name_table():
    # PostgreSQL 연결
    conn = psycopg2.connect(
        dbname=Variable.get('dbname'),
        user=Variable.get('user'),
        password=Variable.get('password'),
        host=Variable.get('host'),
        port='5432'
    )

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ingredient_name_test")
    table = cursor.fetchall()
    conn.close()

    youtube_dataset = [list(row) for row in table]
    ingredient_name_list = []

    for row in youtube_dataset:
        ingredient_name_list.append(row[2])

    ingredient_name_list = set(ingredient_name_list)
    ingredient_name_list = list(ingredient_name_list)

    return ingredient_name_list


@task
def import_csv():
    dag_folder = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(
        dag_folder, 'youtube_preprocessed_dataset_2024-02-23-15-56.csv')
    ingredient_name_list = []
    with open(file_path, 'r', encoding='utf-8') as file:
        # 파일을 열고 각 행을 리스트로 변환하여 데이터에 저장
        youtube_dataset = [line.strip().split(',')
                           for line in file.readlines()]
        ingredient_name_list = []
        for data in youtube_dataset:
            if len(data) != 0:
                ingredient_name_list.append(data[0])

        ingredient_name_list = set(ingredient_name_list)
        ingredient_name_list = list(ingredient_name_list)
        # print(ingredient_name_list)
        # print(len(ingredient_name_list))
    return ingredient_name_list


@task
def extract_and_transform(ingredient_name_list):
    ingredient_result = [['ingredient_name', 'rank', 'time_stamp', 'product_title', 'origial_price', 'price', 'unit_price', 'discount_rate', 'badage_rocket', 'review_count', 'url','image']]
    #ingredient_name_list = ["케챱", "고구마", '가지', '딸기', '바나나']

    while len(ingredient_name_list) != 0:
        ingredient_name = ingredient_name_list.pop(0)
        ingredient_response = ingredientNameRequests(ingredient_name)
        ingredient_result = ingredientsDetailResult(
            ingredient_response, ingredient_name, ingredient_result)
    return ingredient_result


@task
def write_to_csv(ingredient_result):
    current_time = datetime.utcnow()
    file_name = f'ingredient_result_{current_time.strftime("%Y-%m-%d_%H-%M-%S")}.csv'
    with open(file_name, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows(ingredient_result)

    return file_name


@task
def load_to_s3(aws_access_key_id, aws_secret_access_key, file_name):
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)

    bucket_name = 'de-6-1-bucket'
    local_file_path = file_name
    s3_folder_key = 'coupang/'
    s3_file_key = s3_folder_key + local_file_path
    s3.upload_file(local_file_path, bucket_name, s3_file_key)


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
    DROP TABLE IF EXISTS product;
    CREATE TABLE product (
        ingredient_name varchar(255),
        rank integer,
        time_stamp varchar(255),
        product_title varchar(255),
        origial_price integer,
        price integer,
        unit_price varchar(255),
        discount_rate varchar(255),
        badage_rocket varchar(255),
        review_count integer,
        url varchar(255),
        image varchar(255)
    )
    """
    
    insert_query = """
    INSERT INTO product (
        ingredient_name,
        rank,
        time_stamp,
        product_title,
        origial_price,
        price,
        unit_price,
        discount_rate,
        badage_rocket,
        review_count,
        url,
        image
    ) 
    VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s, %s,%s, %s)
    """

    try:
        # 커서 생성
        cur = conn.cursor()

        # 테이블 생성 또는 대체
        cur.execute(drop_create_table_query)

        # 데이터 삽입
        cur.executemany(insert_query, ingredient_result[1:])

        # 커밋
        conn.commit()

        # 커서 및 연결 닫기
        cur.close()
        conn.close()
        print("Table created or replaced and data inserted successfully!")

    except Exception as e:
        print("Error:", e)


with DAG(
    dag_id='coupang_crawling',
    start_date=datetime(2023, 12, 1),
    schedule='0 2 * * *',
    catchup=False,
    default_args={
        'retries': 1,
        'retry_delay': timedelta(minutes=0),
    }
) as dag:

    aws_access_key_id = Variable.get('aws_access_key_id')
    aws_secret_access_key = Variable.get('aws_secret_access_key')

    ingredient_name_list = import_ingredient_name_table()
    ingredient_result = extract_and_transform(ingredient_name_list)
    file_name = write_to_csv(ingredient_result)
    load_to_s3(aws_access_key_id, aws_secret_access_key, file_name)
    load_to_rds(ingredient_result)
