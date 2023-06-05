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

        # Set device status
        print("Setting status...")
        await device.status("Hello, World!")

        # Wait for 10 seconds
        await device.sleep(10)
    except asyncio.CancelledError:
        pass
    finally:
        # Remove the device from Home Assistant
        # After 10 seconds or if Ctrl+C is pressed
        await device.destroy()
        await device.disconnect()
        await device.stop()


if __name__ == "__main__":
    asyncio.run(main())
