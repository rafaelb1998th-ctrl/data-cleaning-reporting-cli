import argparse
from pathlib import Path

from load_data import load_data
from clean_data import clean_data
from validate_data import validate_data
from report_generator import generate_report


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parent.parent
    default_input = project_root / "data" / "raw" / "sample_data.csv"
    parser = argparse.ArgumentParser(
        description="Clean CSV/Excel data and write a data quality report.",
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        default=str(default_input),
        help="Path to input CSV or XLSX file.",
    )
    parser.add_argument(
        "--min-salary",
        type=float,
        default=None,
        metavar="N",
        help="Flag salaries strictly below this value for review (optional).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parent.parent
    input_path = Path(args.input).expanduser().resolve()

    stem = input_path.stem
    cleaned_output = project_root / "data" / "cleaned" / f"{stem}_cleaned.csv"
    report_output = project_root / "reports" / f"{stem}_data_quality_report.txt"

    cleaned_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.parent.mkdir(parents=True, exist_ok=True)

    df = load_data(str(input_path))
    cleaned_df, cleaning_stats = clean_data(df)
    validation_results = validate_data(
        cleaned_df,
        min_salary_review=args.min_salary,
    )

    cleaned_df.to_csv(cleaned_output, index=False)
    generate_report(
        validation_results,
        str(report_output),
        duplicates_removed=cleaning_stats["duplicates_removed"],
        min_salary_review=args.min_salary,
    )

    print("Processing complete.")
    print(f"Cleaned data saved to: {cleaned_output}")
    print(f"Report saved to: {report_output}")


if __name__ == "__main__":
    main()
