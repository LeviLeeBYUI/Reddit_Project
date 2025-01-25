import pandas as pd
import os
import re

def preprocess_data(input_file, output_file):
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        print(f"Loading data from {input_file}...")
        if not os.path.exists(input_file):
            print(f"Error: Input file {input_file} does not exist.")
            return

        df = pd.read_csv(input_file)

        print(f"Initial data shape: {df.shape}")
        print("First few rows of the data:")
        print(df.head())

        # 결측값 처리
        print("Dropping rows with missing title or selftext...")
        df = df.dropna(subset=["title", "selftext"])
        print(f"Data shape after dropping NaN: {df.shape}")

        # 텍스트 정제 함수
        def clean_text(text):
            if isinstance(text, str):
                text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
                text = re.sub(r"[^A-Za-z0-9\s]+", "", text)
                return text.strip()
            return ""

        df["title"] = df["title"].apply(clean_text)
        df["selftext"] = df["selftext"].apply(clean_text)

        df["title_length"] = df["title"].apply(len)
        df["selftext_length"] = df["selftext"].apply(len)

        # created_utc 변환
        print("Converting 'created_utc' to timestamp...")
        df["created_utc"] = pd.to_datetime(df["created_utc"], unit='s')
        print("Converted 'created_utc' to datetime format.")
        print(df[["created_utc"]].head())  # 변환 확인

        # 결과 저장
        print(f"Saving cleaned data to {output_file}...")
        df.to_csv(output_file, index=False)
        print("Data preprocessing completed successfully.")
    except Exception as e:
        print(f"An error occurred during preprocessing: {e}")

if __name__ == "__main__":
    input_file = os.path.join(os.getcwd(), "data/reddit_raw.csv")
    output_file = os.path.join(os.getcwd(), "data/reddit_processed.csv")

    preprocess_data(input_file, output_file)
