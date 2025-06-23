from python_graphql_client import GraphqlClient # type: ignore
import urllib.request
import os
from dotenv import load_dotenv
import pathlib
import logging
load_dotenv()

logger = logging.getLogger(__name__)

# Retrieve your access token from whereever you saved it before.
access_token = os.getenv("PODCHASER_DEV_KEY")

# Prepare our query.
query = """
query {
    podcasts {
        data {
            title,
            description
        }
    }
}
"""

# Add our access token in the Authorization header.
headers = {
    'Authorization': f'Bearer {access_token}'
}

# Execute the GraphQL call.
response = GraphqlClient(endpoint="https://api.podchaser.com/graphql", headers=headers).execute(query=query)

# Print out the first podcast's title.
print(response['data']['podcasts']['data'][0]['title'])

class DownloadResult:
    def __init__(self, data: bytes, content_type: str):
        self.data = data
        self.content_type = content_type


def download_podcast_file(url: str) -> DownloadResult:
    req = urllib.request.Request(
        url,
        data=None,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
        },
    )
    with urllib.request.urlopen(req) as response:
        return DownloadResult(
            data=response.read(),
            content_type=response.headers["content-type"],
        )


def sizeof_fmt(num: float, suffix: str = "B") -> str:
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def store_original_audio(
    url: str, destination: pathlib.Path, overwrite: bool = False
) -> None:
    if destination.exists():
        if overwrite:
            logger.info(
                f"Audio file exists at {destination} but overwrite option is specified."
            )
        else:
            logger.info(f"Audio file exists at {destination}, skipping download.")
            return

    podcast_download_result = download_podcast_file(url=url)
    humanized_bytes_str = sizeof_fmt(num=len(podcast_download_result.data))
    logger.info(f"Downloaded {humanized_bytes_str} episode from URL.")
    with open(destination, "wb") as f:
        f.write(podcast_download_result.data)
    logger.info(f"Stored audio episode at {destination}.")