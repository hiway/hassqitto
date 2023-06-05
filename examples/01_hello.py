import asyncio
import logging
import hassquitto as hq


logging.getLogger("hassquitto").setLevel(logging.DEBUG)

# Create a new device with the name "Example Device"
device = hq.Device(name="Example Device")

# To see the device, open the following URL in browser:
#   http://homeassistant.local:8123/config/devices/dashboard


try:
    # Defaults: host=homeassistant.local, port=1883
    device.connect(username="example", password="example")

    # Start scheduler
    device.start()

    # Set device status
    print("Setting status...")
    device.status("Hello, World!")

    # Wait for 10 seconds
    device.sleep(10)
except asyncio.CancelledError:
    pass
finally:
    # Remove the device from Home Assistant
    # After 10 seconds or if Ctrl+C is pressed
    device.destroy()
    device.disconnect()
    device.stop()
