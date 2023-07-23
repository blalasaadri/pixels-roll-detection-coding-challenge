#!/usr/bin/env python3

import click
import csv
import os
from determine_state import *


@click.command()
@click.argument("infile")
@click.option(
    "--output",
    prompt="Output CSV",
    default="out.csv",
    help="The CSV output file to which to write the determined roll states",
)
def start(infile: str, output: str):
    """Read the CSV input from INFILE and try to calculate the roll state of each entry."""
    click.echo(
        "Reading from {} and writing to {}...".format(infile, output), color=True
    )
    with open(infile, newline="", mode="r") as input_file, open(
        output, mode="w"
    ) as output_file:
        # Prepare the output file
        output_file.write("millis,x,y,z,state,predicted" + os.linesep)
        # Read from the input file
        reader = csv.reader(input_file, delimiter=",")
        next(reader)  # skip the headers
        for row in reader:
            predictedState = updateState(
                int(row[0]), (float(row[1]), float(row[2]), float(row[3]))
            )
            click.echo(
                "Predicted state: {}; actual state: {}".format(predictedState, row[4])
            )
            output_file.write(
                "{},{},{},{},{},{}{}".format(
                    row[0], row[1], row[2], row[3], row[4], predictedState, os.linesep
                )
            )


if __name__ == "__main__":
    start()
