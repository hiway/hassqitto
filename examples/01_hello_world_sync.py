import logging
import hassquitto as hq

logging.getLogger("hassquitto").setLevel(logging.DEBUG)

# Create a new device with the name "Example Device"
device = hq.Device(name="Example Device")

# To see the device, open the following URL in browser:
#   homeassistant.local:8123/config/devices/dashboard

try:
    # Run the device with MQTT username and password "example"
    # Default MQTT broker: homeassistant.local:1883
    device.start(
        username="example",
        password="example",
    )

    # Update device status
    device.status("Hello, World!")
except KeyboardInterrupt:
    pass
finally:
    # Remove the device from Home Assistant
    device.destroy()
    device.stop()
