import logging
import hassquitto as hq

logging.getLogger("hassquitto").setLevel(logging.DEBUG)

# Create a new device with the name "Example Device"
device = hq.Device(name="Example Device")

# To see the device, open the following URL in browser:
#   http://homeassistant.local:8123/config/devices/dashboard

try:
    # Run the device with MQTT username and password "example"
    # Default MQTT broker: homeassistant.local:1883
    device.start(
        username="example",
        password="example",
    )

    # Update device status
    device.status("Hello, World!")

    # Wait for 30 seconds
    device.sleep(30)
except KeyboardInterrupt:
    pass
finally:
    # Remove the device from Home Assistant
    # After 30 seconds or if Ctrl+C is pressed
    device.destroy()
    device.stop()
