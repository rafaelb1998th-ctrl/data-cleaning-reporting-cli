from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import pandas as pd


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", re.I)


def _read_table(
    path: Path,
    sheet: Optional[str],
) -> pd.DataFrame:
    suf = path.suffix.lower()
    if suf == ".csv":
        return pd.read_csv(path)
    if suf in (".xlsx", ".xlsm", ".xls"):
        return pd.read_excel(path, sheet_name=sheet or 0)
    raise SystemExit(f"Unsupported input type: {path.suffix}")


def _normalise_dates(df: pd.DataFrame, columns: Sequence[str]) -> Tuple[pd.DataFrame, List[str]]:
    notes: List[str] = []
    out = df.copy()
    for col in columns:
        if col not in out.columns:
            notes.append(f"Date column missing, skipped: {col}")
            continue
        before = out[col].astype(str)
        parsed = pd.to_datetime(out[col], errors="coerce", dayfirst=True, utc=False)
        out[col] = parsed.dt.date.astype(str).where(parsed.notna(), before)
        bad = parsed.isna().sum()
        if bad:
            notes.append(f"Column {col}: {bad} values could not be parsed as dates")
    return out, notes


def _email_keep_mask(series: pd.Series) -> Tuple[pd.Series, int]:
    def keep(v: object) -> bool:
        if pd.isna(v) or str(v).strip() == "":
            return True
        return bool(EMAIL_RE.match(str(v).strip()))

    empty = series.isna() | (series.astype(str).str.strip() == "")
    mask = series.map(keep)
    invalid = int((~empty & ~mask).sum())
    return mask, invalid


def run_clean(
    input_path: Path,
    output_path: Path,
    report_path: Path,
    sheet: Optional[str],
    date_cols: Sequence[str],
    email_col: Optional[str],
    salary_col: Optional[str],
    min_salary: Optional[float],
    dedupe_cols: Optional[Sequence[str]],
) -> None:
    input_path = input_path.expanduser().resolve()
    output_path = output_path.expanduser().resolve()
    report_path = report_path.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    df = _read_table(input_path, sheet)
    lines: List[str] = []
    lines.append("# Data quality report\n")
    lines.append(f"- Input: `{input_path}`\n")
    lines.append(f"- Rows (raw): {len(df)}\n")

    if dedupe_cols:
        subset = [c for c in dedupe_cols if c in df.columns]
        if subset:
            before = len(df)
            df = df.drop_duplicates(subset=subset, keep="first")
            lines.append(f"- Duplicates removed (subset {subset}): {before - len(df)}\n")
        else:
            lines.append("- Dedupe columns not found in data; skipped dedupe\n")

    dq_notes: List[str] = []
    if date_cols:
        df, dq_notes = _normalise_dates(df, date_cols)
    lines.extend(f"- {n}\n" for n in dq_notes)

    if email_col and email_col in df.columns:
        keep, invalid = _email_keep_mask(df[email_col])
        df = df.loc[keep]
        lines.append(f"- Invalid non-empty emails removed: {invalid}\n")
    elif email_col:
        lines.append(f"- Email column not found: {email_col}\n")

    if salary_col and min_salary is not None and salary_col in df.columns:
        s = pd.to_numeric(df[salary_col], errors="coerce")
        dropped = int((s.notna() & (s < min_salary)).sum())
        df = df.loc[s.isna() | (s >= min_salary)]
        lines.append(f"- Rows below min salary ({min_salary}): removed {dropped}\n")
    elif salary_col and min_salary is not None:
        lines.append(f"- Salary column not found: {salary_col}\n")

    lines.append(f"- Rows (final): {len(df)}\n")
    df.to_csv(output_path, index=False)
    lines.append(f"\nCleaned file written to `{output_path}`.\n")
    report_path.write_text("".join(lines), encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Clean CSV/Excel and emit a short quality report.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("clean", help="Run cleaning pipeline")
    p.add_argument("--input", "-i", type=Path, required=True)
    p.add_argument("--output", "-o", type=Path, required=True)
    p.add_argument("--report", "-r", type=Path, required=True)
    p.add_argument("--sheet", type=str, default=None, help="Excel sheet name (default: first sheet)")
    p.add_argument(
        "--date-cols",
        nargs="*",
        default=[],
        help="Column names to coerce to ISO dates (day-first parsing)",
    )
    p.add_argument("--email-col", type=str, default=None)
    p.add_argument("--salary-col", type=str, default=None)
    p.add_argument("--min-salary", type=float, default=None)
    p.add_argument(
        "--dedupe-cols",
        nargs="*",
        default=None,
        help="Columns defining duplicate rows to drop (first kept)",
    )

    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.cmd == "clean":
        run_clean(
            input_path=args.input,
            output_path=args.output,
            report_path=args.report,
            sheet=args.sheet,
            date_cols=args.date_cols,
            email_col=args.email_col,
            salary_col=args.salary_col,
            min_salary=args.min_salary,
            dedupe_cols=args.dedupe_cols,
        )
        return 0
    return 1
