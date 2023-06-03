import asyncio
import logging
import hassquitto as hq

logging.getLogger("hassquitto").setLevel(logging.DEBUG)

# Create a new device with the name "Example Device"
device = hq.Device(name="Example Device")

# To see the device, open the following URL in browser:
#   homeassistant.local:8123/config/devices/dashboard


async def main():
    # Run the device with MQTT username and password "example"
    # Default MQTT broker: homeassistant.local:1883
    try:
        await device.start(
            username="example",
            password="example",
        )

        # Update device status
        await device.status("Hello, World!")

        # Wait for 30 seconds
        await device.sleep(30)
    except asyncio.CancelledError:
        pass
    finally:
        # Remove the device from Home Assistant
        # After 30 seconds or if Ctrl+C is pressed
        await device.destroy()
        await device.stop()


if __name__ == "__main__":
    asyncio.run(main())
