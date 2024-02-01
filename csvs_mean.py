#!/usr/bin/env python3
"""Output a csv where output[i][j] = mean(csv[i][j] for csv in input_csvs)

csvs_mean.py --help  # commandline documentation
"""
from pathlib import Path
from typing import Union as U, List
import argparse
import csv
import statistics
import sys


#######
# cli #
#######

class StdOut:
    def open(self, mode: str):
        if mode == "w":
            return sys.stdout
        raise ValueError(f"Unsupported mode {mode}")


def get_path(name: str) -> U[Path, StdOut]:
    if name == "-":
        return StdOut()
    return Path(name)


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'csvs', metavar='csv', type=Path, nargs='+', help='csv files to take the mean of',
    )
    parser.add_argument(
        '--freeze-rows', type=int, default=0,
        help='number of csv rows to treat as frozen headers, excluded from mean (default 0)',
    )
    parser.add_argument(
        '--freeze-cols', type=int, default=0,
        help='number of csv columns to treat as frozen prefix, excluded from mean (default 0)',
    )
    parser.add_argument(
        '-o', '--output-file', type=get_path, default=StdOut(),
        help='file to output result to, defaults to stdout',
    )
    return parser


#######
# csv #
#######

Row = List[U[str, float]]
Rows = List[Row]


class SimpleDataCSV:
    def __init__(self, rows: Rows, *, freeze_rows: int = 0, freeze_cols: int = 0):
        self.rows = rows
        self.freeze_rows = freeze_rows
        self.freeze_cols = freeze_cols

    @property
    def data(self) -> List[List[float]]:
        rows = self.rows[self.freeze_rows :]
        freeze_cols = self.freeze_cols
        return [
            [float(val) for val in row[freeze_cols :]]
            for row in rows
        ]

    @property
    def headers(self) -> Rows:
        return [list(row) for row in self.rows[: self.freeze_rows]]

    def data_prefix(self, data_row: int) -> Row:
        return list(self.rows[data_row + self.freeze_rows][: self.freeze_cols])

    @classmethod
    def mean(cls, csv_: 'SimpleDataCSV', *csvs: 'SimpleDataCSV') -> 'SimpleDataCSV':
        return cls(
            [
                *csv_.headers,
                *[
                    csv_.data_prefix(row_idx) + [
                        statistics.mean(
                            [val, *(c.data[row_idx][col_idx] for c in csvs)]
                        )
                        for col_idx, val in enumerate(row_data)
                    ]
                    for row_idx, row_data in enumerate(csv_.data)
                ]
            ],
            freeze_rows=csv_.freeze_rows,
            freeze_cols=csv_.freeze_cols,
        )

    def save(self, path: U[Path, StdOut]) -> None:
        with path.open("w") as f:
            writer = csv.writer(f)
            writer.writerows(self.rows)


########
# main #
########

def main():
    parser = get_parser()
    args = parser.parse_args()
    csvs = []
    for path in args.csvs:
        with path.open() as f:
            csv_ = SimpleDataCSV(
                list(csv.reader(f)),
                freeze_rows=args.freeze_rows,
                freeze_cols=args.freeze_cols,
            )
            csvs.append(csv_)
    assert csvs
    means_csv = SimpleDataCSV.mean(*csvs)  # pylint: disable=no-value-for-parameter
    means_csv.save(args.output_file)


if __name__ == "__main__":
    main()
