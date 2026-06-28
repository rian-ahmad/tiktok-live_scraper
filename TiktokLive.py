import asyncio
import json
from TikTokLive import TikTokLiveClient
from TikTokLive.client.logger import LogLevel
from TikTokLive.events import ConnectEvent, CommentEvent, LikeEvent, SocialEvent, RoomUserSeqEvent
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

with open(os.getenv("CONFIG_FILE"), "r") as file:
    config = json.load(file)

target = os.getenv("TARGET")
viewer_file = os.getenv("VIEWERS_FILE")
komentar_file = os.getenv("KOMENTAR_FILE")
like_file = os.getenv("LIKE_FILE")
share_file = os.getenv("SHARE_FILE")

if os.path.exists(viewer_file):
    with open(viewer_file, 'r', encoding='utf-8') as f:
        try:
            viewer_list = json.load(f)
        except json.JSONDecodeError:
            viewer_list = []
else:
    viewer_list = []

if os.path.exists(komentar_file):
    with open(komentar_file, 'r', encoding='utf-8') as f:
        try:
            komentar_list = json.load(f)
        except json.JSONDecodeError:
            komentar_list = []
else:
    komentar_list = []


if os.path.exists(like_file):
    with open(like_file, 'r', encoding='utf-8') as f:
        try:
            like_list = json.load(f)
        except json.JSONDecodeError:
            like_list = []
else:
    like_list = []


if os.path.exists(share_file):
    with open(share_file, 'r', encoding='utf-8') as f:
        try:
            share_list = json.load(f)
        except json.JSONDecodeError:
            share_list = []
else:
    share_list = []


def save(data, file):
    """
    Menyimpan data ke dalam file JSON.

    Args:
        data: Data yang akan disimpan.
        file (str): Path ke file JSON.
    """
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, default=str)


client: TikTokLiveClient = TikTokLiveClient(
    unique_id=target
)


@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    client.logger.info(f"Connected to @{event.unique_id}!")
    await asyncio.sleep(config["DURATION"])
    for end in range(10):
        time = 10 - end
        print(f'Client will disconnect in {time}')
    await client.disconnect()

    save(komentar_list, komentar_file)
    save(like_list, like_file)
    save(share_list, share_file)
    save(viewer_list, viewer_file)


@client.on(RoomUserSeqEvent)
async def on_viewer_update(event: RoomUserSeqEvent) -> None:
    client.logger.info(f"\n[{datetime.now()}] Total viewers: {event.total_user}")
    viewer_list.append({
        'datetime': datetime.now(),
        'viewers': event.total_user 
    })


@client.on(LikeEvent)
async def on_like(event: LikeEvent) -> None:
    client.logger.info(f"\n[{datetime.now()}] Total Likes: {event.total}")
    like_list.append({
        'datetime': datetime.now(),
        'like': event.total
    })


@client.on(CommentEvent)
async def on_comment(event: CommentEvent) -> None:
    client.logger.info(f"\n[{datetime.now()}] {event.user.nick_name}: {event.comment}")
    komentar_list.append({
        'datetime': datetime.now(),
        'nickname': event.user.nick_name,
        'komentar': event.comment
    })


@client.on(SocialEvent)
async def on_share(event: SocialEvent) -> None:
    client.logger.info(f"\n[{datetime.now()}] Total Shares: {event.share_count}")
    share_list.append({
        'datetime': datetime.now(),
        'share': event.share_count
    })


async def check_loop(client):
    # while True:
    while not await client.is_live():
        client.logger.info(f'{datetime.now()} -> {target} is currently not live')
        await asyncio.sleep(config["DELAY"])

    client.logger.info(f'{datetime.now()} -> {target} is live!')
    await client.connect()


if __name__ == '__main__':
    client.logger.setLevel(LogLevel.INFO.value)

    try:
        asyncio.run(check_loop(client))
    except Exception:
        save(viewer_list, viewer_file)
        save(komentar_list, komentar_file)
        save(like_list, like_file)
        save(share_list, share_file)
