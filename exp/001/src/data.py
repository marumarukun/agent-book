import polars as pl
from sklearn.preprocessing import LabelEncoder

INPUT_DIR = "data/input"


def load_data():
    # データ読み込み
    train = pl.read_csv(f"../{INPUT_DIR}/train.csv", try_parse_dates=True)
    test = pl.read_csv(f"../{INPUT_DIR}/test.csv", try_parse_dates=True)
    return train, test
