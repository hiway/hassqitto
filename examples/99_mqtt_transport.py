import asyncio
import json
from hassquitto.transport import AsyncMQTT

transport = AsyncMQTT()


@transport.on_connect
async def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")


@transport.on_message
async def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")


async def main():
    await transport.connect(
        host="homeassistant.local",
        port=1883,
        username="example",
        password="example",
    )
    await transport.subscribe("homeassistant/switch/transport_test/command")

    message = json.dumps(
        {
            "name": "Transport Test",
            "availability_topic": "homeassistant/switch/transport_test/availability",
            "payload_available": "online",
            "payload_not_available": "offline",
            "state_topic": "homeassistant/switch/transport_test/state",
            "command_topic": "homeassistant/switch/transport_test/command",
            "object_id": "transport_test",
            "unique_id": "transport_test",
            "device": {
                "identifiers": ["transport_test"],
                "manufacturer": "Hassquitto",
                "model": "MQTT Transport",
            },
        }
    )
    await transport.publish("homeassistant/switch/transport_test/config", message)

    await asyncio.sleep(1)
    await transport.publish(
        "homeassistant/switch/transport_test/availability", "online"
    )

    for i in range(3):
        await asyncio.sleep(3)
        await transport.publish("homeassistant/switch/transport_test/state", "ON")
        await asyncio.sleep(3)
        await transport.publish("homeassistant/switch/transport_test/state", "OFF")

    await asyncio.sleep(1)
    await transport.publish(
        "homeassistant/switch/transport_test/availability", "offline"
    )

    await asyncio.sleep(1)
    await transport.publish("homeassistant/switch/transport_test/config", "")


if __name__ == "__main__":
    asyncio.run(main())
