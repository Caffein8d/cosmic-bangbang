#!/usr/bin/env python3
"""
normalize_timesheets.py

Prototype processor for messy timesheet inputs.

Usage:
  - Place input files (CSV or .xlsx) into ./uploads/
  - Run: ./scripts/normalize_timesheets.py
  - Outputs are written to ./outputs/{input_basename}_by_day.csv and ./outputs/{input_basename}_by_day.xlsx

Defaults (per user):
  - Timezone: America/Chicago (US Central)
  - No rounding
  - No automatic break deductions (breaks are included in raw data)
  - Output is grouped "by day": each output row is a date + employee + total_hours

Assumptions & heuristics (prototype):
  - Detects likely employee id/name column by common header names (id, emp, employee, name)
  - Detects timestamp column by common header names (time, timestamp, ts, punched, datetime)
  - Detects optional "type" column (in/out, clock-in/clock-out). If not present, assumes punches alternate in, out, in, out...
  - Pairs in->out chronologically; if out < in, treats out as next day (overnight shift)
  - Attributes each paired duration to the calendar date of the IN timestamp (group-by-day uses that date in America/Chicago timezone)
  - Unpaired IN without a following OUT are ignored but reported in the log

This is a pragmatic, testable script — we'll iterate after you provide a real sample.
"""

import os
import sys
import glob
import math
from datetime import datetime, timedelta
import pandas as pd
import pytz
from dateutil import parser

UPLOAD_DIR = os.path.join(os.getcwd(), 'uploads')
OUTPUT_DIR = os.path.join(os.getcwd(), 'outputs')
TZ = pytz.timezone('America/Chicago')  # US Central

COMMON_EMP_COLS = ['employee_id', 'employeeid', 'emp_id', 'empid', 'id', 'employee', 'name', 'staff']
COMMON_TIME_COLS = ['timestamp', 'time', 'datetime', 'ts', 'punch_time', 'punched', 'clock']
COMMON_TYPE_COLS = ['type', 'event', 'direction', 'inout', 'action']

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def find_first_column(df, candidates):
    lowered = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand in lowered:
            return lowered[cand]
    # fuzzy: look for substring
    for col in df.columns:
        l = col.lower()
        for cand in candidates:
            if cand in l:
                return col
    return None


def parse_dt(x):
    if pd.isna(x):
        return None
    # if numeric, try Excel serial
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        try:
            # Excel serial date (1900 system)
            base = datetime(1899, 12, 30)
            return base + timedelta(days=float(x))
        except Exception:
            return None
    if isinstance(x, datetime):
        return x
    s = str(x).strip()
    if not s:
        return None
    # try pandas first for some speed
    try:
        return pd.to_datetime(s, utc=False)
    except Exception:
        pass
    try:
        return parser.parse(s)
    except Exception:
        return None


def load_file(path):
    ext = path.lower().rsplit('.', 1)[-1]
    if ext in ('xls', 'xlsx'):
        return pd.read_excel(path, dtype=object)
    else:
        # try common separators
        try:
            return pd.read_csv(path, dtype=object)
        except Exception:
            return pd.read_csv(path, sep=';', dtype=object)


def process_df(df, input_name):
    # Normalize column names
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    emp_col = find_first_column(df, COMMON_EMP_COLS)
    time_col = find_first_column(df, COMMON_TIME_COLS)
    type_col = find_first_column(df, COMMON_TYPE_COLS)

    if time_col is None:
        raise RuntimeError('No timestamp column found in input; columns: ' + ','.join(df.columns))

    if emp_col is None:
        # fallback: try to create synthetic employee column by grouping all rows into one 'unknown'
        print('WARN: No employee column detected — using synthetic "UNKNOWN" grouping')
        df['_EMPLOYEE_SYNTH'] = 'UNKNOWN'
        emp_col = '_EMPLOYEE_SYNTH'

    # parse timestamps
    timestamps = []
    for v in df[time_col]:
        dt = parse_dt(v)
        if dt is None:
            timestamps.append(pd.NaT)
        else:
            # localize naive to TZ if naive
            if dt.tzinfo is None:
                try:
                    dt = TZ.localize(dt)
                except Exception:
                    dt = dt.replace(tzinfo=TZ)
            else:
                dt = dt.astimezone(TZ)
            timestamps.append(dt)
    df['_PARSED_TS'] = pd.to_datetime(timestamps)

    # drop rows without parsed timestamp
    missing_ts = df['_PARSED_TS'].isna().sum()
    if missing_ts:
        print(f'WARN: {missing_ts} rows had unparseable timestamps and will be skipped')
    df = df[df['_PARSED_TS'].notna()].copy()

    # normalize type
    if type_col:
        df['_TYPE'] = df[type_col].astype(str).str.lower().str.strip()
    else:
        df['_TYPE'] = None

    # employee key
    df['_EMP'] = df[emp_col].astype(str).str.strip()

    results = []
    problem_rows = []

    # iterate per employee
    for emp, group in df.groupby('_EMP'):
        g = group.sort_values('_PARSED_TS')
        times = list(g['_PARSED_TS'])
        types = list(g['_TYPE'])
        rows = list(g.index)

        # build pairs
        i = 0
        pairs = []
        if all(t is None for t in types):
            # assume alternating in/out starting with IN
            while i + 1 < len(times):
                t_in = times[i]
                t_out = times[i+1]
                pairs.append((t_in, t_out, rows[i], rows[i+1]))
                i += 2
            if i < len(times):
                problem_rows.append((emp, 'unpaired', times[i]))
        else:
            # try to group by explicit IN/OUT markers
            pending_in = None
            pending_in_row = None
            for t, typ, ridx in zip(times, types, rows):
                if typ is None or typ == '':
                    # ambiguous — if we have pending_in, treat as OUT; else treat as IN
                    if pending_in is None:
                        pending_in = t
                        pending_in_row = ridx
                    else:
                        pairs.append((pending_in, t, pending_in_row, ridx))
                        pending_in = None
                        pending_in_row = None
                else:
                    lt = typ
                    if 'in' in lt or 'start' in lt or 'clock in' in lt or 'on' in lt:
                        if pending_in is not None:
                            # consecutive INs; treat previous as unmatched
                            problem_rows.append((emp, 'unmatched_in', pending_in))
                        pending_in = t
                        pending_in_row = ridx
                    elif 'out' in lt or 'stop' in lt or 'end' in lt or 'clock out' in lt or 'off' in lt:
                        if pending_in is None:
                            # unmatched OUT — skip
                            problem_rows.append((emp, 'unmatched_out', t))
                        else:
                            pairs.append((pending_in, t, pending_in_row, ridx))
                            pending_in = None
                            pending_in_row = None
                    else:
                        # fallback alternating
                        if pending_in is None:
                            pending_in = t
                            pending_in_row = ridx
                        else:
                            pairs.append((pending_in, t, pending_in_row, ridx))
                            pending_in = None
                            pending_in_row = None
            if pending_in is not None:
                problem_rows.append((emp, 'unpaired', pending_in))

        # compute durations and attribute by date of IN
        per_day = {}
        for tin, tout, rin, rout in pairs:
            if tout < tin:
                # assume overnight, add 1 day
                tout = tout + timedelta(days=1)
            dur = (tout - tin).total_seconds() / 3600.0
            if math.isnan(dur) or dur < 0:
                problem_rows.append((emp, 'negative_duration', tin, tout))
                continue
            day = tin.astimezone(TZ).date()
            per_day.setdefault(day, 0.0)
            per_day[day] += dur

        for day, hrs in per_day.items():
            results.append({'date': day.isoformat(), 'employee': emp, 'hours': round(hrs, 4), 'pairs': len(pairs)})

    out_df = pd.DataFrame(results)
    if out_df.empty:
        print('No paired records found in', input_name)
    else:
        # sort by date then employee
        out_df = out_df.sort_values(['date', 'employee'])
    return out_df, problem_rows


def process_file(path):
    print('Processing', path)
    try:
        df = load_file(path)
    except Exception as e:
        print('ERROR loading', path, e)
        return
    out_df, problems = process_df(df, os.path.basename(path))
    base = os.path.basename(path)
    name = os.path.splitext(base)[0]
    csv_path = os.path.join(OUTPUT_DIR, f"{name}_by_day.csv")
    xlsx_path = os.path.join(OUTPUT_DIR, f"{name}_by_day.xlsx")
    out_df.to_csv(csv_path, index=False)
    wrote_xlsx = False
    try:
        out_df.to_excel(xlsx_path, index=False, engine='openpyxl')
        wrote_xlsx = True
    except Exception:
        wrote_xlsx = False
    if wrote_xlsx:
        print('WROTE', csv_path, 'and', xlsx_path)
    else:
        print('WROTE', csv_path)
        print('WARNING: could not write Excel file (openpyxl may be missing)')
    if problems:
        print('Problems / warnings encountered:')
        for p in problems[:50]:
            print('  ', p)
    else:
        print('No problems detected')


if __name__ == '__main__':
    # If a filename provided, process only that file; otherwise process all uploads
    files = []
    if len(sys.argv) > 1:
        files = [sys.argv[1]]
    else:
        for ext in ('*.csv', '*.xls', '*.xlsx'):
            files.extend(glob.glob(os.path.join(UPLOAD_DIR, ext)))
    if not files:
        print('No input files found in uploads/. Place CSV or XLSX files there and re-run.')
        sys.exit(0)
    for f in files:
        process_file(f)
