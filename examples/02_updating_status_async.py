import asyncio
import logging
import hassquitto as hq

logging.getLogger("hassquitto").setLevel(logging.DEBUG)

# Create a new device with the name "Example Device"
device = hq.Device(name="Example Device")

# To see the device, open the following URL in browser:
#   http://homeassistant.local:8123/config/devices/dashboard


async def main():
    try:
        # Defaults: host=homeassistant.local, port=1883
        await device.connect(username="example", password="example")

        # Start scheduler
        await device.start()

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
