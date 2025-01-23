import pandas as pd
import os
import re

def preprocess_data(input_file, output_file):
    try:
        # 디렉토리 생성
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 데이터 로드
        print(f"Loading data from {input_file}...")
        df = pd.read_csv(input_file)

        # 전처리 단계
        print("Starting preprocessing...")
        
        # 결측값 처리: 제목과 본문 중 하나라도 없는 행 제거
        df = df.dropna(subset=["title", "selftext"])
        
        # 특수문자 및 URL 제거
        def clean_text(text):
            if isinstance(text, str):
                # URL 제거
                text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
                # 특수문자 제거
                text = re.sub(r"[^A-Za-z0-9\s]+", "", text)
                return text.strip()
            return ""
        
        df["title"] = df["title"].apply(clean_text)
        df["selftext"] = df["selftext"].apply(clean_text)

        # 텍스트 길이 컬럼 추가
        df["title_length"] = df["title"].apply(len)
        df["selftext_length"] = df["selftext"].apply(len)

        # 전처리된 데이터 저장
        print(f"Saving cleaned data to {output_file}...")
        df.to_csv(output_file, index=False)
        print("Data preprocessing completed successfully.")

    except Exception as e:
        print(f"An error occurred during preprocessing: {e}")

if __name__ == "__main__":
    # 파일 경로 설정
    input_file = os.path.join(os.getcwd(), "data/reddit_raw.csv")
    output_file = os.path.join(os.getcwd(), "data/reddit_cleaned.csv")

    # 데이터 전처리 실행
    preprocess_data(input_file, output_file)
