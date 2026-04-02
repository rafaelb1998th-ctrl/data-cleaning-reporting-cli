from pathlib import Path


def _section_header(title: str) -> list[str]:
    return ["", title, "-" * len(title)]


def generate_report(
    validation_results: dict,
    output_path: str,
    *,
    duplicates_removed: int = 0,
    min_salary_review: float | None = None,
) -> None:
    lines: list[str] = []
    lines.append("DATA QUALITY REPORT")
    lines.append("=" * 44)
    lines.append(f"Duplicate rows removed: {duplicates_removed}")
    lines.append(f"Total rows after cleaning: {validation_results['row_count']}")
    lines.extend(_section_header("Missing values by column"))
    for column, count in validation_results["missing_values"].items():
        lines.append(f"  {column}: {count}")

    missing_dates = validation_results["rows_missing_join_date"]
    lines.extend(_section_header("Rows with missing join dates"))
    lines.append(f"  Count: {len(missing_dates)}")

    invalid_emails = validation_results["invalid_emails"]
    lines.extend(_section_header("Rows with invalid or empty emails"))
    lines.append(f"  Count: {len(invalid_emails)}")

    salary = validation_results["salary_issues"]
    lines.extend(_section_header("Salary validation"))
    lines.append(f"  Missing salary: {len(salary['missing'])}")
    lines.append(f"  Non-numeric salary: {len(salary['non_numeric'])}")
    lines.append(f"  Negative salary: {len(salary['negative'])}")
    if min_salary_review is not None:
        lines.append(
            f"  Below review threshold ({min_salary_review:g}): "
            f"{len(salary['below_threshold'])}"
        )
    else:
        lines.append("  Below review threshold: (not configured)")

    Path(output_path).write_text("\n".join(lines) + "\n", encoding="utf-8")
