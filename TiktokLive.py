import asyncio
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from TikTokLive import TikTokLiveClient
from TikTokLive.client.logger import LogLevel
from TikTokLive.events import ConnectEvent, CommentEvent, LikeEvent, SocialEvent, RoomUserSeqEvent

class TikTokLiveScraper:
    def __init__(self, target=None, duration=None, delay=None):
        """
        Inisialisasi TikTokLiveScraper dengan kontrol state running.
        """
        load_dotenv()
        
        config_file = os.getenv("CONFIG_FILE", "config.json")
        if os.path.exists(config_file):
            with open(config_file, "r") as file:
                self.config = json.load(file)
        else:
            self.config = {"DURATION": 60, "DELAY": 60}
        
        self.target = target or os.getenv("TARGET")
        self.duration = duration or self.config.get("DURATION", 60)
        self.delay = delay or self.config.get("DELAY", 60)
        
        if not self.target:
            raise ValueError("Target username (unique_id) harus ditentukan.")
        
        self.viewer_file = os.getenv("VIEWERS_FILE", "viewers.json")
        self.komentar_file = os.getenv("KOMENTAR_FILE", "komentar.json")
        self.like_file = os.getenv("LIKE_FILE", "like.json")
        self.share_file = os.getenv("SHARE_FILE", "share.json")
        
        self.viewer_list = self._load_json(self.viewer_file)
        self.komentar_list = self._load_json(self.komentar_file)
        self.like_list = self._load_json(self.like_file)
        self.share_list = self._load_json(self.share_file)
        
        self.client = TikTokLiveClient(unique_id=self.target)
        
        self.is_running = False
        self.loop = None
        
        self._register_events()

    def _load_json(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def save(self, data, file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4, default=str)

    def save_all_data(self):
        """Menyimpan seluruh state list ke file JSON."""
        self.save(self.komentar_list, self.komentar_file)
        self.save(self.like_list, self.like_file)
        self.save(self.share_list, self.share_file)
        self.save(self.viewer_list, self.viewer_file)

    def _register_events(self):
        @self.client.on(ConnectEvent)
        async def on_connect(event: ConnectEvent):
            self.client.logger.info(f"Connected to @{event.unique_id}!")
            
            for _ in range(int(self.duration)):
                if not self.is_running:
                    break
                await asyncio.sleep(1)
            
            if self.is_running and self.client.connected:
                for end in range(10):
                    if not self.is_running:
                        break
                    time = 10 - end
                    print(f'Client will disconnect in {time}')
                    await asyncio.sleep(1)
                
                if self.client.connected:
                    await self.client.disconnect()
            
            self.save_all_data()

        @self.client.on(RoomUserSeqEvent)
        async def on_viewer_update(event: RoomUserSeqEvent) -> None:
            self.client.logger.info(f"\n[{datetime.now()}] Total viewers: {event.total_user}")
            self.viewer_list.append({'datetime': datetime.now(), 'viewers': event.total_user})

        @self.client.on(LikeEvent)
        async def on_like(event: LikeEvent) -> None:
            self.client.logger.info(f"\n[{datetime.now()}] Total Likes: {event.total}")
            self.like_list.append({'datetime': datetime.now(), 'like': event.total})

        @self.client.on(CommentEvent)
        async def on_comment(event: CommentEvent) -> None:
            self.client.logger.info(f"\n[{datetime.now()}] {event.user.nick_name}: {event.comment}")
            self.komentar_list.append({
                'datetime': datetime.now(),
                'nickname': event.user.nick_name,
                'komentar': event.comment
            })

        @self.client.on(SocialEvent)
        async def on_share(event: SocialEvent) -> None:
            self.client.logger.info(f"\n[{datetime.now()}] Total Shares: {event.share_count}")
            self.share_list.append({'datetime': datetime.now(), 'share': event.share_count})

    async def check_loop(self):
        """Loop pengecekan status Live dengan interupsi stop yang responsif."""
        while self.is_running:
            if await self.client.is_live():
                self.client.logger.info(f'{datetime.now()} -> {self.target} is live!')
                await self.client.connect()
                break
            
            self.client.logger.info(f'{datetime.now()} -> {self.target} is currently not live')
            
            # Mengganti blocking sleep lama dengan perulangan 1 detik
            for _ in range(int(self.delay)):
                if not self.is_running:
                    break
                await asyncio.sleep(1)

    def start(self):
        """Menjalankan scraper dan menginisialisasi event loop baru."""
        self.client.logger.setLevel(LogLevel.INFO.value)
        self.is_running = True
        
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            self.loop.run_until_complete(self.check_loop())
        except Exception as e:
            self.client.logger.error(f"Error encountered: {e}")
        finally:
            self.save_all_data()
            self.loop.close()

    def stop(self):
        """Menghentikan proses scraping dari thread eksternal."""
        self.is_running = False
        self.client.logger.info("Menghentikan scraper...")
        
        if self.loop and self.loop.is_running():
            if self.client.connected:
                asyncio.run_coroutine_threadsafe(self.client.disconnect(), self.loop)
        
        self.save_all_data()

if __name__ == '__main__':
    scraper = TikTokLiveScraper()
    try:
        scraper.start()
    except KeyboardInterrupt:
        scraper.stop()