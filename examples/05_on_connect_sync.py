import logging
import hassquitto as hq

logging.getLogger("hassquitto").setLevel(logging.DEBUG)

# Create a new device with the name "Example Device"
device = hq.Device(name="Example Device")

# To see the device, open the following URL in browser:
#   homeassistant.local:8123/config/devices/dashboard


# Function to run when the device connects to the MQTT broker
@device.on_connect
def device_connected():
    print("Device connected")

    # Update device status
    device.status("Hello, World!")


try:
    # Run the device with MQTT username and password "example"
    # Default MQTT broker: homeassistant.local:1883
    device.run(
        username="example",
        password="example",
    )
except KeyboardInterrupt:
    pass
finally:
    # Remove the device from Home Assistant
    device.destroy()
    device.stop()
