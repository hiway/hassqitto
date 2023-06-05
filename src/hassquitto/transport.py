"""
Async MQTT Transport
"""
import asyncio
from inspect import isawaitable, iscoroutinefunction

from asgiref.sync import sync_to_async
from asyncgnostic import awaitable
from paho.mqtt import client as mqtt

from .logging import get_logger

logger = get_logger(__name__)


class MqttTransport:
    """
    Sync/Async MQTT Transport
    """

    def __init__(self, client_id: str) -> None:
        self._client = mqtt.Client(client_id=client_id)
        self.loop = None

    def ensure_loop(self) -> None:
        """
        Ensure that the transport has a loop
        """
        logger.debug("ensure_loop function called")
        if self.loop is None:
            self.loop = asyncio.get_event_loop()

    def on_connect(self, func) -> None:
        """
        Decorator for on_connect callback
        """
        logger.debug("on_connect function called with func: %s", func)

        def wrapper(client: mqtt.Client, userdata: None, flags: dict, rc: int) -> None:
            asyncio.run_coroutine_threadsafe(
                func(client, userdata, flags, rc), self.loop
            )

        if iscoroutinefunction(func) or isawaitable(func):
            self._client.on_connect = wrapper
            return wrapper
        else:
            self._client.on_connect = func
            return func

    def on_disconnect(self, func) -> None:
        """
        Decorator for on_disconnect callback
        """
        logger.debug("on_disconnect function called with func: %s", func)

        def wrapper(client: mqtt.Client, userdata: None, rc: int) -> None:
            asyncio.run_coroutine_threadsafe(func(client, userdata, rc), self.loop)

        if iscoroutinefunction(func) or isawaitable(func):
            self._client.on_disconnect = wrapper
            return wrapper
        else:
            self._client.on_disconnect = func
            return func

    def on_message(self, func) -> None:
        """
        Decorator for on_message callback
        """
        logger.debug("on_message function called with func: %s", func)

        def wrapper(client: mqtt.Client, userdata: None, msg: mqtt.MQTTMessage) -> None:
            asyncio.run_coroutine_threadsafe(func(client, userdata, msg), self.loop)

        if iscoroutinefunction(func) or isawaitable(func):
            self._client.on_message = wrapper
            return wrapper
        else:
            self._client.on_message = func
            return func

    def connect(self, host: str, port: int, username: str, password: str) -> None:
        """
        Connect to MQTT broker
        """
        logger.debug("connect function called with host: %s, port: %s", host, port)
        self._client.username_pw_set(username, password)
        self._client.connect(host, port)
        self._client.loop_start()

    @awaitable(connect)
    async def connect(self, host: str, port: int, username: str, password: str) -> None:
        """
        Connect to MQTT broker
        """
        logger.debug(
            "ASYNC connect function called with host: %s, port: %s", host, port
        )
        self.ensure_loop()
        await sync_to_async(self._client.username_pw_set)(username, password)
        await sync_to_async(self._client.connect)(host, port)
        await sync_to_async(self._client.loop_start)()

    def disconnect(self) -> None:
        """
        Disconnect from MQTT broker
        """
        logger.debug("disconnect function called")
        self._client.loop_stop()
        self._client.disconnect()

    @awaitable(disconnect)
    async def disconnect(self) -> None:
        """
        Disconnect from MQTT broker
        """
        logger.debug("ASYNC disconnect function called")
        self.ensure_loop()
        await sync_to_async(self._client.loop_stop)()
        await sync_to_async(self._client.disconnect)()

    def publish(
        self,
        topic: str,
        payload: str,
        qos: int = 0,
        retain: bool = False,
    ) -> None:
        """
        Publish message to MQTT broker
        """
        payload_preview = payload[:20] + "..." if len(payload) > 20 else payload
        logger.debug(
            "publish function called with \n\t\ttopic: %s, payload: '%s', qos: %s, retain: %s ",
            topic,
            payload_preview,
            qos,
            retain,
        )
        self._client.publish(topic, payload, qos, retain)

    @awaitable(publish)
    async def publish(
        self,
        topic: str,
        payload: str,
        qos: int = 0,
        retain: bool = False,
    ) -> None:
        """
        Publish message to MQTT broker
        """
        payload_preview = payload[:20] + "..." if len(payload) > 20 else payload
        logger.debug(
            "ASYNC publish function called with \n\t\ttopic: %s, payload: '%s', qos: %s, retain: %s ",
            topic,
            payload_preview,
            qos,
            retain,
        )
        self.ensure_loop()
        await sync_to_async(self._client.publish)(topic, payload, qos, retain)

    def subscribe(self, topic: str) -> None:
        """
        Subscribe to topic on MQTT broker
        """
        logger.debug("subscribe function called with topic: %s", topic)
        self._client.subscribe(topic)

    @awaitable(subscribe)
    async def subscribe(self, topic: str) -> None:
        """
        Subscribe to topic on MQTT broker
        """
        logger.debug("ASYNC subscribe function called with topic: %s", topic)
        self.ensure_loop()
        await sync_to_async(self._client.subscribe)(topic)

    def unsubscribe(self, topic: str) -> None:
        """
        Unsubscribe from topic on MQTT broker
        """
        logger.debug("unsubscribe function called with topic: %s", topic)
        self._client.unsubscribe(topic)

    @awaitable(unsubscribe)
    async def unsubscribe(self, topic: str) -> None:
        """
        Unsubscribe from topic on MQTT broker
        """
        logger.debug("ASYNC unsubscribe function called with topic: %s", topic)
        self.ensure_loop()
        await sync_to_async(self._client.unsubscribe)(topic)
