import asyncio
import logging
import hassquitto as hq

logging.getLogger("hassquitto").setLevel(logging.DEBUG)

# Create a new device with the name "Example Device"
device = hq.Device(name="Example Device")

# To see the device, open the following URL in browser:
#   homeassistant.local:8123/config/devices/dashboard


async def main():
    try:
        # Run the device with MQTT username and password "example"
        # Default MQTT broker: homeassistant.local:1883
        await device.start(
            username="example",
            password="example",
        )

        counter = 0
        while True:
            await device.status(f"Running {str(counter)}")
            await device.sleep(3)
            counter += 1

    except asyncio.CancelledError:
        pass
    finally:
        # Remove the device from Home Assistant
        await device.destroy()
        await device.stop()


asyncio.run(main())
