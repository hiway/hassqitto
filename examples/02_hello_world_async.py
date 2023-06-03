import asyncio
import logging
import signal
import hassquitto as hq

logging.getLogger("hassquitto").setLevel(logging.DEBUG)

# Create a new device with the name "Example Device"
device = hq.Device(name="Example Device")

# To see the device, open the following URL in browser:
#   homeassistant.local:8123/config/devices/dashboard


# Function to run when the device connects to the MQTT broker
@device.on_connect
async def device_connected():
    print("Device connected")

    # Update device status
    await device.status("Hello, World!")


async def main():
    # Run the device with MQTT username and password "example"
    # Default MQTT broker: homeassistant.local:1883
    await device.start(
        username="example",
        password="example",
    )

    await device.sleep(1)
    
    counter = 0
    try:
        while True:
            await device.status(f"Uptime: {str(counter)} seconds.")
            counter += 1
            await device.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        await device.destroy()
        await device.stop()


if __name__ == "__main__":
    asyncio.run(main())