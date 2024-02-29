/*psql 접속 후 절차
1. 데이터베이스 생성 및 접속 전환*/
CREATE DATABASE raw_data;
/*  psql 명령 정리
접속한 데이터베이스 전환: \c raw_data
접속한 데이터베이스 내 모든 테이블 목록 조회: \dt
*/

/* 2. create table
service db schema에서 NOT NULL, UNIQUE 등의 조건 많이 추가*/
CREATE TABLE IF NOT EXISTS channel (
    id SERIAL PRIMARY KEY,
    name VARCHAR(1024),
    url VARCHAR(1024),
    subscribers_count BIGINT,
    img_src VARCHAR(2048),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP);

CREATE TABLE IF NOT EXISTS menu (
    id SERIAL PRIMARY KEY,
    name VARCHAR(2048) NOT NULL,
    category VARCHAR(2048),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP);

CREATE TABLE IF NOT EXISTS ingredient (
    id SERIAL PRIMARY KEY,
    name VARCHAR(512) NOT NULL,
    volume FLOAT,
    unit VARCHAR(64),
    vague VARCHAR(128),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS unit_conversion (
    conversion_id SERIAL PRIMARY KEY,
    unit_name VARCHAR(64),
    conversion_name VARCHAR(64),
    converted_vol FLOAT);

CREATE TABLE IF NOT EXISTS product (
    id SERIAL PRIMARY KEY,
    ingredient_id INTEGER NOT NULL,
    name VARCHAR(1024) NOT NULL,
    date DATE, /*created_at, updated_at으로 충분치 않을까 염려해서 생성한 칼럼*/
    unit_price FLOAT,
    url VARCHAR(2048),
    img_src VARCHAR(2048),
    rank SMALLINT,
    rating_total_count SMALLINT,
    badage_rocket VARCHAR(64),
    discount_rate FLOAT,
    storage_method VARCHAR(128),
    expiration_date DATE,
    is_bulk BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    FOREIGN KEY (ingredient_id) REFERENCES ingredient (id));

CREATE TABLE IF NOT EXISTS recipe (
    id SERIAL PRIMARY KEY,
    youtube_video_id INTEGER NOT NULL,
    menu_id INTEGER NOT NULL,
    full_text TEXT,
    total_price FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    FOREIGN KEY (menu_id) REFERENCES menu (id));

CREATE TABLE IF NOT EXISTS recipe_ingredient (
    id SERIAL PRIMARY KEY,
    ingredient_id INTEGER NOT NULL,
    recipe_id INTEGER NOT NULL,
    FOREIGN KEY (ingredient_id) REFERENCES ingredient (id),
    FOREIGN KEY (recipe_id) REFERENCES recipe (id));

CREATE TABLE IF NOT EXISTS youtube_video (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER NOT NULL,
    recipe_id INTEGER NOT NULL,
    title VARCHAR(512) NOT NULL,
    url VARCHAR(2048),
    thumbnail_src VARCHAR(2048),
    views BIGINT,
    thumbsup_count BIGINT,
    uploaded_str VARCHAR(64),
    uploaded_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    FOREIGN KEY (channel_id) REFERENCES channel (id));

ALTER TABLE recipe ADD CONSTRAINT recipe_to_youtube FOREIGN KEY (youtube_video_id) REFERENCES youtube_video (id);
ALTER TABLE recipe ALTER COLUMN youtube_video_id SET NOT NULL;

ALTER TABLE youtube_video ADD CONSTRAINT youtube_to_recipe FOREIGN KEY (recipe_id) REFERENCES recipe (id);
ALTER TABLE youtube_video ALTER COLUMN recipe_id SET NOT NULL;

DROP TABLE unit_conversion;
CREATE TABLE IF NOT EXISTS unit_conversion (
    conversion_id SERIAL PRIMARY KEY,
    ingredient_name VARCHAR(128),
    unit_name VARCHAR(64),
    converted_vol FLOAT);