import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from hassquitto.transport import AsyncMQTT


@pytest.fixture
async def mqtt():
    mqtt = AsyncMQTT(client_id="test")
    mqtt._client.username_pw_set = MagicMock()
    mqtt._client.connect = MagicMock()
    mqtt._client.disconnect = MagicMock()
    mqtt._client.loop_start = MagicMock()
    mqtt._client.publish = MagicMock()
    mqtt._client.subscribe = MagicMock()
    mqtt._client.unsubscribe = MagicMock()
    mqtt._client.loop_stop = MagicMock()
    mqtt.loop = asyncio.get_event_loop()
    yield mqtt


async def test_publish(mqtt):
    topic = "test/topic"
    payload = "test payload"
    await mqtt.publish(topic, payload)
    mqtt._client.publish.assert_called_once_with(topic, payload)


async def test_subscribe(mqtt):
    topic = "test/topic"
    await mqtt.subscribe(topic)
    mqtt._client.subscribe.assert_called_once_with(topic)


async def test_unsubscribe(mqtt):
    topic = "test/topic"
    await mqtt.unsubscribe(topic)
    mqtt._client.unsubscribe.assert_called_once_with(topic)


async def test_on_connect(mqtt):
    coro = AsyncMock()
    wrapped = mqtt.on_connect(coro)

    rc = 0
    flags = {"test_flag": True}
    wrapped(None, None, flags, rc)

    coro.assert_called_once_with(None, None, flags, rc)


async def test_on_disconnect(mqtt):
    coro = AsyncMock()
    mqtt.on_disconnect(coro)
    wrapped = mqtt.on_disconnect(coro)

    rc = 0
    wrapped(None, None, rc)

    coro.assert_called_once_with(None, None, rc)


async def test_on_message(mqtt):
    coro = AsyncMock()
    mqtt.on_message(coro)
    wrapped = mqtt.on_message(coro)

    msg = MagicMock()
    wrapped(None, None, msg)

    coro.assert_called_once_with(None, None, msg)


async def test_connect(mqtt):
    await mqtt.connect("localhost", 1883, "username", "password")
    mqtt._client.username_pw_set.assert_called_once_with("username", "password")
    mqtt._client.connect.assert_called_once_with("localhost", 1883)
    mqtt._client.loop_start.assert_called_once()


async def test_disconnect(mqtt):
    await mqtt.disconnect()
    mqtt._client.loop_stop.assert_called_once()
    mqtt._client.disconnect.assert_called_once()


async def test_ensure_loop(mqtt):
    mqtt.loop = None
    mqtt.ensure_loop()
    assert mqtt.loop is not None


def test_sync_connect(mqtt):
    mqtt.sync_connect("localhost", 1883, "username", "password")
    mqtt._client.username_pw_set.assert_called_once_with("username", "password")
    mqtt._client.connect.assert_called_once_with("localhost", 1883)
    mqtt._client.loop_start.assert_called_once()


def test_sync_disconnect(mqtt):
    mqtt.sync_disconnect()
    mqtt._client.loop_stop.assert_called_once()
    mqtt._client.disconnect.assert_called_once()
