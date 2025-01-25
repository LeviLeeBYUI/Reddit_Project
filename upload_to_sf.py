import snowflake.connector
import pandas as pd
import os

# 설정 파일 읽기 함수
def read_config(file_path):
    config = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.strip().split('=')
                config[key] = value
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        exit(1)
    except ValueError:
        print("Error: Invalid format in the config file. Ensure each line is 'key=value'.")
        exit(1)
    return config

# Snowflake로 데이터 업로드
def upload_to_snowflake(processed_file_path, config):
    try:
        conn = snowflake.connector.connect(
            user=config["snowflake_user"],
            password=config["snowflake_password"],
            account=config["snowflake_account"],
            warehouse=config["snowflake_warehouse"],
            database=config["snowflake_database"],
            schema=config["snowflake_schema"]
        )
        print("Connected to Snowflake.")

        # 데이터 로드
        df = pd.read_csv(processed_file_path)
        print(f"Loaded data from {processed_file_path}. Rows: {len(df)}")

        # NaN 값을 처리
        df = df.fillna(value={
            "title": "",
            "selftext": "",
            "score": 0,
            "num_comments": 0,
            "created_utc": "1970-01-01 00:00:00",
            "subreddit": "",
            "title_length": 0,
            "selftext_length": 0
        })

        # created_utc를 문자열로 변환
        df["created_utc"] = pd.to_datetime(df["created_utc"], errors='coerce')
        df["created_utc"] = df["created_utc"].astype(str)

        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reddit_processed_data (
            id STRING,
            title STRING,
            selftext STRING,
            score INT,
            num_comments INT,
            created_utc TIMESTAMP,
            subreddit STRING,
            title_length INT,
            selftext_length INT
        );
        """)

        # 데이터 업로드
        for _, row in df.iterrows():
            cursor.execute("""
            INSERT INTO reddit_processed_data (id, title, selftext, score, num_comments, created_utc, subreddit, title_length, selftext_length)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                row["id"],
                row["title"],
                row["selftext"],
                row["score"],
                row["num_comments"],
                row["created_utc"],
                row["subreddit"],
                row["title_length"],
                row["selftext_length"]
            ))

        print(f"Data uploaded to Snowflake. Total rows: {len(df)}")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error uploading data to Snowflake: {e}")

if __name__ == "__main__":
    config_file = os.path.join(os.getcwd(), "config.txt")
    processed_file_path = os.path.join(os.getcwd(), "data/reddit_processed.csv")

    config = read_config(config_file)
    upload_to_snowflake(processed_file_path, config)
