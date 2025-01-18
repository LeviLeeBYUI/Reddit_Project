import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import pos_tag
from collections import Counter
import matplotlib.pyplot as plt
import nltk
import re
from sklearn.feature_extraction.text import CountVectorizer

# 필요한 NLTK 리소스 다운로드
nltk.download("punkt")
nltk.download("stopwords")
nltk.download("vader_lexicon")
nltk.download("averaged_perceptron_tagger_eng")

# 불용어 설정
stop_words = set(stopwords.words("english"))

# 감정 분석 객체 초기화
sia = SentimentIntensityAnalyzer()

# URL 및 특수 문자 제거 함수
def preprocess_text(text):
    # Null 체크
    if not isinstance(text, str):
        return ""

    # 원본 텍스트 출력 (디버깅용)
    print(f"Original Text: {text}")

    # URL 제거
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)

    # 특수 문자 제거
    text = re.sub(r"[^\w\s]", "", text)  # 단어 문자(\w)와 공백(\s)만 허용

    # 여분의 공백 제거
    text = re.sub(r"\s+", " ", text).strip()

    # 처리된 텍스트 출력 (디버깅용)
    print(f"Processed Text: {text}")

    return text

# 명사만 추출하는 함수
def filter_nouns(text):
    tokens = word_tokenize(text)
    # 품사 태깅
    tagged_tokens = pos_tag(tokens)
    # 명사만 추출
    nouns = [word for word, pos in tagged_tokens if pos in ["NN", "NNS", "NNP", "NNPS"]]
    return nouns

# 데이터 로드
posts_df = pd.read_csv("reddit_posts.csv")
comments_df = pd.read_csv("reddit_comments.csv")

# 1. 각 서브레딧의 주요 트렌드 비교
def analyze_trends(posts_df):
    subreddit_keywords = {}

    for subreddit in posts_df["subreddit"].unique():
        subreddit_posts = posts_df[posts_df["subreddit"] == subreddit]
        all_words = []

        for body in subreddit_posts["body"].dropna():
            # 텍스트 전처리
            cleaned_text = preprocess_text(body)

            # 명사만 추출
            nouns = filter_nouns(cleaned_text)

            # 명사 추출 결과 출력 (디버깅용)
            print(f"Nouns: {nouns}")

            # 불용어 제거 및 소문자 변환
            filtered_tokens = [
                word.lower() for word in nouns if word.lower() not in stop_words
            ]
            all_words.extend(filtered_tokens)

        # 상위 10개 키워드 추출
        subreddit_keywords[subreddit] = Counter(all_words).most_common(10)

    print("\nTop keywords per subreddit:")
    for subreddit, keywords in subreddit_keywords.items():
        print(f"{subreddit}: {keywords}")

    return subreddit_keywords
# 2. 댓글 기반 사용자 감정 분포 분석
def analyze_comment_sentiments(comments_df):
    # 댓글의 감정 점수 계산
    comments_df["sentiment"] = comments_df["comment_body"].apply(
        lambda text: sia.polarity_scores(text)["compound"]
    )

    # 감정 분포 계산
    sentiment_distribution = comments_df["sentiment"].apply(
        lambda score: "positive" if score > 0.05 else "negative" if score < -0.05 else "neutral"
    ).value_counts()

    print("\nSentiment distribution in comments:")
    print(sentiment_distribution)

    # 감정 분포 시각화
    sentiment_distribution.plot(kind="bar", color=["green", "red", "gray"])
    plt.title("Comment Sentiment Distribution")
    plt.xlabel("Sentiment")
    plt.ylabel("Number of Comments")
    plt.show()

    return comments_df

# 3. 시간 흐름에 따른 주요 키워드 변화
def analyze_keyword_trends(posts_df):
    # 날짜 변환
    posts_df["created_date"] = pd.to_datetime(posts_df["created_utc"], unit="s")
    posts_df["date"] = posts_df["created_date"].dt.date

    # 날짜별 주요 키워드 추출
    keyword_trends = {}
    for date in posts_df["date"].unique():
        daily_posts = posts_df[posts_df["date"] == date]
        all_words = []
        for body in daily_posts["body"].dropna():
            # 텍스트 전처리
            cleaned_text = preprocess_text(body)
            tokens = word_tokenize(cleaned_text)
            filtered_tokens = [
                word.lower() for word in tokens if word.isalnum() and word.lower() not in stop_words
            ]
            all_words.extend(filtered_tokens)

        # 상위 5개 키워드 저장
        keyword_trends[date] = Counter(all_words).most_common(5)

    print("\nKeyword trends over time:")
    for date, keywords in keyword_trends.items():
        print(f"{date}: {keywords}")

    return keyword_trends

# 4. n-grams 기반 주요 단어 조합 분석
def analyze_ngrams(posts_df, ngram_range=(2, 2), top_n=10):
    subreddit_ngrams = {}

    for subreddit in posts_df["subreddit"].unique():
        subreddit_posts = posts_df[posts_df["subreddit"] == subreddit]
        all_text = " ".join(subreddit_posts["body"].dropna().apply(preprocess_text))

        # CountVectorizer를 사용하여 n-grams 추출
        vectorizer = CountVectorizer(ngram_range=ngram_range, stop_words="english")
        ngrams = vectorizer.fit_transform([all_text])
        ngram_counts = Counter(dict(zip(vectorizer.get_feature_names_out(), ngrams.toarray().flatten())))

        # 상위 n개의 n-grams 추출
        subreddit_ngrams[subreddit] = ngram_counts.most_common(top_n)

    print("\nTop n-grams per subreddit:")
    for subreddit, ngrams in subreddit_ngrams.items():
        print(f"{subreddit}: {ngrams}")

    return subreddit_ngrams

# 실행
if __name__ == "__main__":
    # 주요 트렌드 분석
    subreddit_keywords = analyze_trends(posts_df)

    # 댓글 감정 분석
    comments_df = analyze_comment_sentiments(comments_df)

    # 키워드 시간 흐름 분석
    keyword_trends = analyze_keyword_trends(posts_df)

    # n-grams 분석
    subreddit_ngrams = analyze_ngrams(posts_df, ngram_range=(2, 2), top_n=10)

    # 전처리된 데이터를 저장
    print("Processed Data Saved: reddit_posts_preprocessed.csv, reddit_comments_preprocessed.csv")