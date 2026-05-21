import asyncio
import logging
from datetime import datetime, timezone

from backend.configs import app_config

from telethon import TelegramClient
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import Channel, InputChannel, InputNotifyPeer, InputPeerChannel, InputPeerNotifySettings


logger = logging.getLogger(__name__)


class TelegramConnection:
    def __init__(self, session: str, api_id: int, api_hash: str) -> None:
        self._client = TelegramClient(session, api_id, api_hash)
        self._task: asyncio.Task | None = None
        self._connected = asyncio.Event()


    @property
    def client(self) -> TelegramClient:
        return self._client


    def start(self) -> None:
        self._task = asyncio.create_task(self._connect(), name="telegram-connection")


    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            await asyncio.gather(self._task, return_exceptions=True)


    async def join_channel(self, url: str) -> None:
        try:
            await asyncio.wait_for(self._connected.wait(), timeout=30)
        except asyncio.TimeoutError:
            raise RuntimeError("Telegram is not connected")
        entity = await self._client.get_entity(url)
        if not isinstance(entity, Channel):
            raise ValueError(f"Not a channel: {url}")
        input_channel = InputChannel(entity.id, entity.access_hash or 0)
        input_peer = InputPeerChannel(entity.id, entity.access_hash or 0)

        await self._client(JoinChannelRequest(channel=input_channel))
        await self._client(UpdateNotifySettingsRequest(
            peer=InputNotifyPeer(input_peer),
            settings=InputPeerNotifySettings(mute_until=datetime(2038, 1, 19, tzinfo=timezone.utc)),
        ))
        logger.info("Joined and muted Telegram channel: %s", url)


    async def _connect(self) -> None:
        while True:
            try:
                async with self._client:
                    logger.info("Telegram connected")
                    self._connected.set()
                    await self._client.disconnected
                    logger.warning("Telegram connection lost, reconnecting in %ds", app_config.TG_BACKEND_RECONNECT_DELAY)
            except Exception:
                logger.exception("Telegram connection error, retrying in %ds", app_config.TG_BACKEND_RECONNECT_DELAY)
            finally:
                self._connected.clear()
            await asyncio.sleep(app_config.TG_BACKEND_RECONNECT_DELAY)
