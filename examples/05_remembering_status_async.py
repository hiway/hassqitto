import asyncio
import logging
import hassquitto as hq

logging.getLogger("hassquitto").setLevel(logging.DEBUG)

# Create a new device with the name "Example Device"
device = hq.Device(name="Example Device")

# To see the device, open the following URL in browser:
#   http://homeassistant.local:8123/config/devices/dashboard


@device.on_interval(1)
async def on_interval():
    if await device.status() is None:
        await device.status("0")
        await device.status_set_confirm()

    counter = int(await device.status())
    counter += 1
    await device.status(counter, retain=True)


async def main():
    try:
        # Defaults: host=homeassistant.local, port=1883
        await device.connect(username="example", password="example")

        # Start scheduler
        await device.start()

        await device.sleep(10)
    except asyncio.CancelledError:
        pass
    finally:
        # Reset status
        # await device.status("", retain=True)

        # Remove the device from Home Assistant
        await device.destroy()
        await device.disconnect()
        await device.stop()


if __name__ == "__main__":
    asyncio.run(main())
