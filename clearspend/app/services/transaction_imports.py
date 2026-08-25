"""Deterministic parsing, normalization, and duplicate classification."""

import csv
import hashlib
import io
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.schemas.transaction_import import ImportMapping

MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_ROWS = 100_000
STAGING_BATCH_SIZE = 1_000
DATE_FORMATS = ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d/%m/%Y", "%Y/%m/%d")


def normalize_merchant(value: str) -> str:
    cleaned = re.sub(r"\s+", " ", value.strip())
    if not cleaned:
        raise ValueError("merchant is required")
    return cleaned[:200]


def parse_date(value: str):
    cleaned = value.strip()
    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, date_format).date()
        except ValueError:
            pass
    raise ValueError("date is not in a supported format")


def parse_amount(row: dict[str, str], mapping: ImportMapping) -> Decimal:
    value = row.get(mapping.amount, "") if mapping.amount else ""
    if not value and mapping.debit:
        value = row.get(mapping.debit, "")
    if not value and mapping.credit:
        value = row.get(mapping.credit, "")
    cleaned = value.strip().replace(",", "").replace("$", "")
    if cleaned.startswith("(") and cleaned.endswith(")"):
        cleaned = f"-{cleaned[1:-1]}"
    try:
        amount = abs(Decimal(cleaned)).quantize(Decimal("0.01"))
    except (InvalidOperation, AttributeError):
        raise ValueError("amount is not a valid number") from None
    if amount <= 0 or amount >= Decimal("10000000000"):
        raise ValueError("amount must be positive and fit the supported range")
    return amount


def fingerprint(transaction_date, amount: Decimal, merchant: str, currency: str) -> str:
    canonical = f"{transaction_date.isoformat()}|{amount:.2f}|{merchant.casefold()}|{currency}"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def read_csv(content: str) -> list[dict[str, str]]:
    if len(content.encode("utf-8")) > MAX_FILE_BYTES:
        raise ValueError("file exceeds the 5 MiB limit")
    try:
        reader = csv.DictReader(io.StringIO(content.lstrip("\ufeff")), strict=True)
        if not reader.fieldnames:
            raise ValueError("CSV header is required")
        rows = list(reader)
    except csv.Error as error:
        raise ValueError(f"malformed CSV: {error}") from error
    if not rows:
        raise ValueError("CSV must contain at least one data row")
    if len(rows) > MAX_ROWS:
        raise ValueError(f"file exceeds the {MAX_ROWS} row limit")
    return rows


def iter_csv(stream):
    """Yield rows from a text stream while enforcing the configured row limit."""
    try:
        reader = csv.DictReader(stream, strict=True)
        if not reader.fieldnames:
            raise ValueError("CSV header is required")
        found = False
        for count, row in enumerate(reader, start=1):
            found = True
            if count > MAX_ROWS:
                raise ValueError(f"file exceeds the {MAX_ROWS} row limit")
            yield row
        if not found:
            raise ValueError("CSV must contain at least one data row")
    except csv.Error as error:
        raise ValueError(f"malformed CSV: {error}") from error


def classify_rows(raw_rows: list[dict[str, str]], mapping: ImportMapping, owner_id: int, db: Session):
    return list(iter_classified_rows(iter(raw_rows), mapping, owner_id, db))


def iter_classified_rows(raw_rows, mapping: ImportMapping, owner_id: int, db: Session):
    required = [mapping.date, mapping.merchant]
    if not mapping.amount and not mapping.debit and not mapping.credit:
        raise ValueError("map amount or at least one debit/credit column")
    try:
        first_row = next(raw_rows)
    except StopIteration:
        raise ValueError("CSV must contain at least one data row") from None
    headers = set(first_row)
    missing = [column for column in required if column not in headers]
    amount_columns = [column for column in (mapping.amount, mapping.debit, mapping.credit) if column]
    if not any(column in headers for column in amount_columns):
        missing.append("amount/debit/credit")
    if missing:
        raise ValueError(f"mapped columns not found: {', '.join(missing)}")

    existing = {value for (value,) in db.query(Transaction.fingerprint).filter(Transaction.owner_id == owner_id, Transaction.fingerprint.is_not(None)).all()}
    existing_candidates = {(row.date, Decimal(row.amount)) for row in db.query(Transaction.date, Transaction.amount).filter(Transaction.owner_id == owner_id).all()}
    seen_candidates: set[tuple] = set()
    seen: set[str] = set()
    for row_number, raw in enumerate(_chain_first(first_row, raw_rows), start=2):
        result = {"row_number": row_number, "raw_values": dict(raw), "status": "new"}
        try:
            merchant_raw = raw.get(mapping.merchant, "")
            merchant = normalize_merchant(merchant_raw)
            transaction_date = parse_date(raw.get(mapping.date, ""))
            amount = parse_amount(raw, mapping)
            currency = (raw.get(mapping.currency, "USD") if mapping.currency else "USD").strip().upper() or "USD"
            if not re.fullmatch(r"[A-Z]{3}", currency):
                raise ValueError("currency must be a three-letter code")
            row_fingerprint = fingerprint(transaction_date, amount, merchant, currency)
            status = "exact_duplicate" if row_fingerprint in existing or row_fingerprint in seen else "new"
            if status == "new" and (transaction_date, amount) in (existing_candidates | seen_candidates):
                status = "possible_duplicate"
            seen.add(row_fingerprint)
            seen_candidates.add((transaction_date, amount))
            result.update(merchant_raw=merchant_raw, merchant=merchant, date=transaction_date, amount=amount, currency=currency, fingerprint=row_fingerprint, status=status)
        except ValueError as error:
            result.update(status="invalid", error_reason=str(error))
        yield result


def _chain_first(first, remainder):
    yield first
    yield from remainder
