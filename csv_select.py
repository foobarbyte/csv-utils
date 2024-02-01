#!/usr/bin/env python3
"""Output rows from a csv, where row[i] == key.

csv_select.py --help  # commandline documentation
"""
from pathlib import Path
from typing import Union as U
import argparse
import csv
import sys


class StdIn:
    def open(self, mode: str = "r"):
        if mode == "r":
            return sys.stdin
        raise ValueError(f"Unsupported mode {mode}")


class StdOut:
    def open(self, mode: str):
        if mode == "w":
            return sys.stdout
        raise ValueError(f"Unsupported mode {mode}")


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'csv', metavar='csv', type=get_input_path,
        help='csv file to select row from, - will read from stdin. Each matching row is output immediately after being read in.'
    )
    parser.add_argument('key', type=str, help='unique identifier for row')
    parser.add_argument(
        '--index-col', type=int, default=0,  # no -i, ambiguous with input
        help='column to check for key in (defaults to the first column, column 0)',
        )
    parser.add_argument(
        '-o', '--output-file', type=get_output_path, default=StdOut(),
        help='file to write matching rows to, - will write to stdout (defaults to stdout)',
    )
    return parser


def get_input_path(name: str) -> U[Path, StdIn]:
    if name == "-":
        return StdIn()
    return Path(name)


def get_output_path(name: str) -> U[Path, StdOut]:
    if name == "-":
        return StdOut()
    return Path(name)


def main() -> None:
    args = get_parser().parse_args()
    with args.csv.open() as f:
        for row in csv.reader(f):
            if row[args.index_col] == args.key:
                with args.output_file.open("w") as output:
                    csv.writer(output).writerow(row)


if __name__ == "__main__":
    main()
