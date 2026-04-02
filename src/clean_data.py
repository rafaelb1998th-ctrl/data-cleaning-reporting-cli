import pandas as pd


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^\w]", "", regex=True)
    )
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates()


def standardise_dates(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    if column_name in df.columns:
        df[column_name] = pd.to_datetime(
            df[column_name], errors="coerce", format="mixed"
        )
    return df


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    df = clean_column_names(df)
    rows_before_dedup = len(df)
    df = remove_duplicates(df)
    duplicates_removed = rows_before_dedup - len(df)
    df = standardise_dates(df, "join_date")
    stats = {"duplicates_removed": duplicates_removed}
    return df, stats
