import pandas as pd

from math_q_agent.config import RANDOM_DATA, PRACTICE_DATA

# 초기값은 None으로 설정
problem_df = None  

def merge_csv_to_dataframe():
    """
    두 개의 CSV 파일을 읽어 하나의 DataFrame으로 합칩니다.
    
    :param file1: 첫 번째 CSV 파일 경로
    :param file2: 두 번째 CSV 파일 경로
    :return: 합쳐진 DataFrame
    """
    global problem_df
    try:
        # CSV 파일 읽기
        random_df = pd.read_csv(RANDOM_DATA)
        practice_df = pd.read_csv(PRACTICE_DATA)
        
        # 데이터프레임 합치기
        problem_df = pd.concat([random_df, practice_df], ignore_index=True)
        print(f"Successfully merged DataFrames with shape: {problem_df.shape}")
        
        return problem_df
    except Exception as e:
        print(f"Failed to merge CSV files: {e}")
        return []

def get_problem_df():
    """
    글로벌로 선언된 problem_df 반환하는 함수.
    
    :return: 합쳐진 DataFrame
    """
    global problem_df
    if problem_df is None:
        problem_df = merge_csv_to_dataframe()
    return problem_df