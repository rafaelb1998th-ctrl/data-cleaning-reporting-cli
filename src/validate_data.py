import pandas as pd


def get_missing_values(df: pd.DataFrame) -> pd.Series:
    return df.isnull().sum()


def get_invalid_emails(df: pd.DataFrame, email_column: str = "email") -> pd.DataFrame:
    if email_column not in df.columns:
        return pd.DataFrame()

    pattern = r"^[^@]+@[^@]+\.[^@]+$"
    invalid_mask = ~df[email_column].fillna("").str.match(pattern)
    return df[invalid_mask]


def get_rows_missing_dates(
    df: pd.DataFrame, date_column: str = "join_date"
) -> pd.DataFrame:
    if date_column not in df.columns:
        return pd.DataFrame()
    return df[df[date_column].isna()]


def get_salary_validation(
    df: pd.DataFrame,
    salary_column: str = "salary",
    min_salary_review: float | None = None,
) -> dict[str, pd.DataFrame]:
    empty = {
        "missing": pd.DataFrame(),
        "non_numeric": pd.DataFrame(),
        "negative": pd.DataFrame(),
        "below_threshold": pd.DataFrame(),
    }
    if salary_column not in df.columns:
        return empty

    col = df[salary_column]
    numeric = pd.to_numeric(col, errors="coerce")
    str_series = col.astype(str).str.strip()
    true_missing = col.isna() | (str_series == "") | (str_series.str.lower() == "nan")

    non_numeric = df[~true_missing & numeric.isna()]
    missing = df[true_missing]
    valid_num = numeric.notna()
    negative = df[valid_num & (numeric < 0)]

    if min_salary_review is not None:
        below = df[valid_num & (numeric >= 0) & (numeric < min_salary_review)]
    else:
        below = pd.DataFrame()

    return {
        "missing": missing,
        "non_numeric": non_numeric,
        "negative": negative,
        "below_threshold": below,
    }


def validate_data(
    df: pd.DataFrame,
    *,
    join_date_column: str = "join_date",
    email_column: str = "email",
    salary_column: str = "salary",
    min_salary_review: float | None = None,
) -> dict:
    salary_issues = get_salary_validation(
        df,
        salary_column=salary_column,
        min_salary_review=min_salary_review,
    )
    return {
        "row_count": len(df),
        "missing_values": get_missing_values(df),
        "invalid_emails": get_invalid_emails(df, email_column=email_column),
        "rows_missing_join_date": get_rows_missing_dates(
            df, date_column=join_date_column
        ),
        "salary_issues": salary_issues,
    }

