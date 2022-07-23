from pathlib import Path
from typing import Optional

from pydantic import PositiveInt
from apple_playlist_exporter.scraper import Scrapper
import logging

logging.basicConfig(
    format="%(levelname)s:%(name)s - %(message)s",
    level=logging.INFO,
)


def export():
    output_path = Path(__file__).parents[1].joinpath("output.csv")

    # example: https://music.apple.com/us/playlist/<username>/<playlist_id>
    username = "barbershop-jazz"
    playlist_id = "pl.u-EdAVzEquGelYd5"

    # number of musics to extract. None to infinity.
    limit: Optional[PositiveInt] = None

    scrapper = Scrapper(username, playlist_id)
    scrapper.export_to_csv(output_path, limit)


if __name__ == "__main__":
    export()
