"""
This script just orchestrates the execution of an SQL query against the given DB and saves the result to a JSON file.



The SQL query should return a table with the following columns:
- job_id
- result_id
- pmcid
- sentence

The result of the query will be available as a polars dataframe, and saved to JSON when running this as a script.

"""

import click
import polars as pl


def pull_data_from_db(conn_str, query):
    """
    Just executes the pull using connextorx in the background. Should be directly writable to JSON, or useable as a dataframe.
    """

    df = pl.read_database(query, conn_str, protocol="binary")
    if df.schema["sentence"] != pl.List:
        print(
            "Sentence column is not a list, assuming we need to do string manipulation"
        )
        ## Implies the df is not grouped by job_id
        df = df.with_columns(pl.col("sentence").str.split("$$$"))

        df = (
            df.groupby(["primary_id"])
            .agg(
                [
                    pl.col("*").exclude(["sentence", "job_id"]),
                    pl.col("sentence").explode(),
                    pl.col("job_id").unique(),
                ]
            )
            .filter(pl.col("result_id").arr.lengths() > 1)
        )

    return df  # .sort(by="job_id")


@click.command()
@click.option("--conn_str", envvar="PGDATABASE", type=str)
@click.option("--query", type=click.Path(exists=True))
@click.option("--output_file", type=click.Path())
def main(conn_str, query, output_file):
    df = pull_data_from_db(conn_str, query)
    df.write_json(output_file)
