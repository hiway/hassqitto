import hassquitto as hq
import logging

# Enable logging
logging.getLogger("hassquitto").setLevel(logging.DEBUG)


# Define the device.
class Device(hq.Device):
    pass


# Instantiate the device.
device = Device(name="Example Device")

# Set device properties.
device.hw_version = "1.0"
device.sw_version = "1.2.3"
device.manufacturer = "Example Manufacturer"
device.model = "Example Model"
device.suggested_area = "Example Area"


# To see the device in Home Assistant, open the following URL:
# http://homeassistant.local:8123/config/devices/dashboard
# look for "Example Device" and click on the name.

try:
    # Connect to MQTT.
    device.connect(
        host="homeassistant.local",
        port=1883,  # MQTT port.
        username="example",  # MQTT username.
        password="example",  # MQTT password.
    )
    # Set device availability.
    device.set_available()
    device.set_online()

    # Loop forever.
    device.run()

except KeyboardInterrupt:
    # Wait for Ctrl+C.
    pass

finally:
    # Remove the example device from Home Assistant.
    device.destroy_discovery()

    # Disconnect from MQTT.
    device.disconnect()
