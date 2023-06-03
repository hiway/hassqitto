import time
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
    # device.sleep(0.5)
    time.sleep(1)

    # TODO: Fix this
    # device.status("Hello, World!")
    # TODO: Fix this

except KeyboardInterrupt:
    # Stop the device when user presses Ctrl+C
    pass
finally:
    # Remove the device from Home Assistant
    device.destroy()
    device.stop()
