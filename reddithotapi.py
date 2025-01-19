import praw
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

# Reddit API 데이터 가져오기 함수
def fetch_reddit_data():
    # `config.txt` 파일에서 Reddit API 정보 읽기
    config = read_config("config.txt")  # 파일 경로 수정
    print("Loaded configuration:", config)  # 디버깅용 출력

    # Reddit API 초기화
    try:
        reddit = praw.Reddit(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            user_agent=config["user_agent"]
        )
        print("Reddit API connection successful.")
    except KeyError as e:
        print(f"Error: Missing configuration key: {e}")
        exit(1)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

    return reddit

# 핫 게시물 데이터 가져오기
def fetch_hot_posts(reddit, subreddit_name, limit=500):
    subreddit = reddit.subreddit(subreddit_name)
    posts = []

    try:
        for post in subreddit.hot(limit=limit):
            posts.append({
                "id": post.id,
                "title": post.title,
                "selftext": post.selftext,
                "score": post.score,
                "num_comments": post.num_comments,
                "created_utc": post.created_utc,
                "subreddit": post.subreddit.display_name
            })
        print(f"Fetched {len(posts)} posts from subreddit: {subreddit_name}")
    except Exception as e:
        print(f"Error while fetching posts: {e}")
        exit(1)

    return posts

# 데이터 저장
def save_to_csv(posts, output_file):
    # DataFrame 생성
    df = pd.DataFrame(posts)

    # 제목이나 본문이 비어 있는 경우 제거
    df = df.dropna(subset=["title", "selftext"])

    # CSV 저장
    try:
        df.to_csv(output_file, index=False)
        print(f"Data saved to {output_file}")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")
        exit(1)

# 메인 실행
if __name__ == "__main__":
    # Reddit API 초기화
    reddit = fetch_reddit_data()

    # 서브레딧 이름 및 데이터 수집
    subreddit_name = "datascience"  # 원하는 서브레딧 이름
    posts = fetch_hot_posts(reddit, subreddit_name, limit=500)

    # 데이터 저장
    output_file = os.path.join(os.getcwd(), "reddit_hot_posts.csv")
    save_to_csv(posts, output_file)
[]