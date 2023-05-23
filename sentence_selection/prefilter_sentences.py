"""Here we do a little bit of prefiltering on the sentences
remove:
    - found in a table...
    - ...

Optionally apply some user supplied regexes to remove sentences that match those regexes.
"""
import polars as pl


def prefilter_sentences(df, regexes=None):
    """
    Use a regex to remove sentences that are found in tables, figures or supplementary material

    Optionally apply some user supplied regexes to remove sentences that match those regexes.
    """
    filtered_df = (
        df.lazy()
        .filter(
            pl.col("sentence")
            .str.contains("image|figure|table|supplementary material")
            .is_not()
        )
        .collect()
    )

    if regexes:
        for regex in regexes:
            filtered_df = (
                filtered_df.lazy()
                .filter(pl.col("sentence").str.contains(regex).is_not())
                .collect()
            )

    return filtered_df
