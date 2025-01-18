import praw
import pandas as pd

# 민감한 정보를 읽는 함수
def read_config(file_path):
    config = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.strip().split('=')
                config[key] = value
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
    except ValueError:
        print("Error: Invalid format in the config file. Ensure each line is 'key=value'.")
    return config

def fetch_reddit_data():
    # `pw.txt` 파일에서 Reddit API 정보 읽기
    config = read_config("pw.txt")  # 파일 경로 수정
    print("Loaded configuration:", config)  # 디버깅용 출력
    
    reddit = praw.Reddit(
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        user_agent=config["user_agent"]
    )
    
    print("Reddit API connection successful.")

    all_posts = []
    all_comments = []
    subreddits = ["datascience", "machinelearning", "bigdata", "analytics", "dataengineering"]

    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        print(f"Collecting data from subreddit: {subreddit_name}")

        for post in subreddit.hot(limit=50):
            print(f"Collected post: {post.title}")
            all_posts.append({
                "subreddit": subreddit_name,
                "title": post.title,
                "score": post.score,
                "id": post.id,
                "url": post.url,
                "created_utc": post.created_utc,
                "body": post.selftext,
            })

            # 댓글 데이터 수집
            post.comments.replace_more(limit=None)
            for comment in post.comments.list():
                print(f"Collected comment: {comment.body[:30]}")
                all_comments.append({
                    "post_id": post.id,
                    "comment_id": comment.id,
                    "comment_body": comment.body,
                    "comment_score": comment.score,
                    "created_utc": comment.created_utc,
                })

    # 게시물 데이터 저장
    try:
        posts_df = pd.DataFrame(all_posts)
        posts_df.to_csv("reddit_posts.csv", index=False)
        print("Post Data Saved: reddit_posts.csv")
    except Exception as e:
        print(f"Error saving post data: {e}")

    # 댓글 데이터 저장
    try:
        comments_df = pd.DataFrame(all_comments)
        comments_df.to_csv("reddit_comments.csv", index=False)
        print("Comment Data Saved: reddit_comments.csv")
    except Exception as e:
        print(f"Error saving comment data: {e}")

    return posts_df, comments_df

# 실행
fetch_reddit_data()