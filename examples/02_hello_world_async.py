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


async def stop(loop):
    # Remove the device from Home Assistant
    await device.destroy()
    await device.stop()

    # Gather all pending tasks
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    # Cancel all pending tasks
    for task in tasks:
        task.cancel()

    # Wait for all pending tasks to be cancelled
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


async def main():
    # Run the device with MQTT username and password "example"
    # Default MQTT broker: homeassistant.local:1883
    await device.run(
        username="example",
        password="example",
    )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(stop(loop)))
    loop.run_until_complete(main())
