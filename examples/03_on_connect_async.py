import asyncio
import logging
import hassquitto as hq

logging.getLogger("hassquitto").setLevel(logging.DEBUG)

# Create a new device with the name "Example Device"
device = hq.Device(name="Example Device")

# To see the device, open the following URL in browser:
#   http://homeassistant.local:8123/config/devices/dashboard


# Function to run when the device connects to the MQTT broker
@device.on_connect
async def device_connected():
    print("Device connected")

    # Update device status
    await device.status("Hello, World!")


async def main():
    try:
        # Defaults: host=homeassistant.local, port=1883
        await device.connect(username="example", password="example")

        # Start scheduler
        await device.start()

        # Wait for 10 seconds
        await device.sleep(10)
    except asyncio.CancelledError:
        pass
    finally:
        await device.destroy()
        await device.stop()


if __name__ == "__main__":
    asyncio.run(main())
