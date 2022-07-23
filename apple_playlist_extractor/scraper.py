from pathlib import Path
from typing import List, Generator, Optional
from urllib import parse
import json
from pydantic import PositiveInt, validate_arguments
import requests
from bs4 import BeautifulSoup, ResultSet
from apple_playlist_extractor.dto import Song
import csv
import logging

logger = logging.getLogger(__name__)


class Scrapper:
    __origin = "https://music.apple.com"
    __tracks_url = "https://amp-api.music.apple.com/v1/catalog/us/playlists"

    def __init__(self, username: str, playlist_id: str) -> None:
        self.__playlist_id = playlist_id
        self.__username = username
        self.__token = self.__get_media_token(username, playlist_id)

    @validate_arguments
    def get_songs(self, limit: Optional[PositiveInt] = None) -> Generator[Song, None, None]:
        logger.info(f"Extracting playlist: {self.__username}/{self.__playlist_id}")
        counter = 0
        params = {
            "l": "en-us",
            "platform": "web",
            "include[songs]": "artists,composers",
            "fields[artists]": "name,url",
            "offset": 0,
        }
        headers = {
            "authorization": f"Bearer {self.__token}",
            "origin": self.__origin,
        }
        while True:
            url = f"{self.__tracks_url}/{self.__playlist_id}/tracks"
            response = requests.get(url, params, headers=headers)
            response.raise_for_status()
            response_json = response.json()
            items_list = response_json["data"]
            for item in items_list:
                if counter == limit:
                    break
                song = Song.parse_obj(item["attributes"])
                counter += 1
                yield song

            if "next" not in response_json or counter == limit:
                break

            offset = dict(parse.parse_qsl(parse.urlsplit(response_json["next"]).query)).get("offset", None)
            if offset is None:
                break

            params["offset"] = offset

        logger.info(f"{counter} songs extracted!")

    @validate_arguments
    def export_to_csv(self, filepath: Path, limit: Optional[PositiveInt] = None) -> None:
        if filepath.name.rsplit(".", 1)[1].lower() != "csv":
            raise ValueError("The file extension must be a .csv")
        if not filepath.exists():
            filepath.parent.mkdir(parents=True, exist_ok=True)

        field_names = list(Song.schema(by_alias=False)["properties"].keys())
        with filepath.open("w", encoding="utf-8", newline="") as fp:
            writter = csv.DictWriter(fp, fieldnames=field_names, delimiter=";")
            writter.writeheader()
            for i, song in enumerate(self.get_songs(limit)):
                logger.info(f"#{i+1} song extracted: [{song.albumName}]{song.artistName} - {song.name}")
                writter.writerow(song.dict())

    def __get_media_token(self, username: str, playlist_id: str) -> str:
        url = f"{self.__origin}/us/playlist/{username}/{playlist_id}"
        response = requests.get(url)
        response.raise_for_status()
        self.soup = BeautifulSoup(response.text, "html.parser")
        media = self.soup.find("meta", dict(name="desktop-music-app/config/environment"))
        return json.loads(parse.unquote(media["content"]))["MEDIA_API"]["token"]
