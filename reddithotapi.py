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
    config = read_config("config.txt")
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
def fetch_hot_posts(reddit, subreddits, limit=500):
    all_posts = []

    for subreddit_name in subreddits:
        print(f"Collecting data from subreddit: {subreddit_name}")
        subreddit = reddit.subreddit(subreddit_name)

        try:
            for post in subreddit.hot(limit=limit):
                all_posts.append({
                    "id": post.id,
                    "title": post.title,
                    "selftext": post.selftext,
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "created_utc": post.created_utc,
                    "subreddit": post.subreddit.display_name
                })
            print(f"Fetched {len(all_posts)} posts from subreddit: {subreddit_name}")
        except Exception as e:
            print(f"Error while fetching posts from {subreddit_name}: {e}")

    return all_posts

# 데이터 저장
def save_to_csv(posts, output_file):
    df = pd.DataFrame(posts)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)  # 경로가 없으면 생성
    df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")

# 실행
if __name__ == "__main__":
    # Reddit API 연결
    reddit = fetch_reddit_data()

    # 서브레딧 리스트 설정
    subreddits = ["datascience", "machinelearning", "bigdata", "analytics", "dataengineer"]

    # 데이터 수집
    posts = fetch_hot_posts(reddit, subreddits)

    # 데이터 저장
    output_file = os.path.join(os.getcwd(), "data/reddit_raw.csv")
    save_to_csv(posts, output_file)
    

print("Current working directory:", os.getcwd())

