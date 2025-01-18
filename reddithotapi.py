import praw
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import matplotlib.pyplot as plt

# 필요한 NLTK 리소스 다운로드
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    print("Downloading 'punkt'...")
    nltk.download("punkt")

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    print("Downloading 'stopwords'...")
    nltk.download("stopwords")

# Reddit API 설정
reddit = praw.Reddit(
    client_id = "KhFRvc5ikIsitYphPDZhaw",
    client_secret = "NexE-3ZuKy2oeDtAIyM2nlJpGxz6eA",
    user_agent = "YOUR_USER_AGENT",
)

# 특정 서브레딧에서 Hot Posts 가져오기
subreddit = reddit.subreddit("datascience")  # 원하는 서브레딧 지정
hot_posts = subreddit.hot(limit=100)  # 상위 100개의 핫 게시물 가져오기

# 단어 저장용 리스트
all_words = []

# Hot Posts에서 단어 추출
for post in hot_posts:
    print(f"Title: {post.title}")  # 제목 출력 (선택)
    tokens = word_tokenize(post.title)  # 제목에서 단어 추출
    filtered_tokens = [
        word.lower() for word in tokens if word.isalnum()  # 알파벳/숫자만 포함
        and word.lower() not in stopwords.words("english")  # 불용어 제거
    ]
    all_words.extend(filtered_tokens)  # 단어 리스트에 추가

# 단어 빈도 계산
word_freq = Counter(all_words)

# 상위 10개 단어 출력
print("\nTop 10 Words in Hot Posts:")
for word, freq in word_freq.most_common(10):
    print(f"{word}: {freq}")

# 단어 빈도 시각화
most_common_words = word_freq.most_common(10)
words, counts = zip(*most_common_words)

plt.bar(words, counts)
plt.xlabel("Words")
plt.ylabel("Frequency")
plt.title("Top 10 Words in Hot Reddit Posts")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
