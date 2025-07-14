import pandas as pd
import os


def inspect_csv_files(data_path="data/raw"):
    """실제 CSV 파일들의 구조를 확인"""

    files_to_check = [
        "transaction_data.csv",
        "product.csv",
        "hh_demographic.csv",
        "coupon.csv",
        "campaign_table.csv",
        "campaign_desc.csv",
        "causal_data.csv",
        "coupon_redempt.csv",
    ]

    print("📊 실제 데이터 파일 구조 분석")
    print("=" * 60)

    file_info = {}

    for filename in files_to_check:
        file_path = os.path.join(data_path, filename)

        if os.path.exists(file_path):
            try:
                # 처음 5행만 읽어서 구조 파악
                df = pd.read_csv(file_path, nrows=5)

                print(f"\n📁 {filename}")
                print(f"   컬럼 수: {len(df.columns)}")
                print(f"   컬럼명: {list(df.columns)}")
                print(f"   샘플 데이터:")
                for col in df.columns:
                    sample_values = df[col].dropna().head(3).tolist()
                    print(f"     {col}: {sample_values}")

                # 전체 행 수 확인
                full_df = pd.read_csv(file_path)
                print(f"   총 행 수: {len(full_df):,}")

                file_info[filename] = {
                    "columns": list(df.columns),
                    "sample_data": df.head().to_dict(),
                    "total_rows": len(full_df),
                }

            except Exception as e:
                print(f"   ❌ 읽기 실패: {e}")
                file_info[filename] = {"error": str(e)}
        else:
            print(f"\n❌ {filename} - 파일이 존재하지 않음")
            file_info[filename] = {"error": "File not found"}

    print("\n" + "=" * 60)
    print("📋 분석 완료! 위 정보를 바탕으로 실제 데이터 로더를 만들겠습니다.")

    return file_info


if __name__ == "__main__":
    # 실제 데이터 구조 확인
    file_info = inspect_csv_files()

    # 추천사항 출력
    print("\n💡 다음 단계:")
    print("1. 위에서 확인된 실제 컬럼명을 바탕으로 data_loader.py 수정")
    print("2. 존재하지 않는 컬럼들은 추천 엔진에서 제외")
    print("3. 실제 데이터만으로 추천 시스템 구축")
