import logging
import hassquitto as hq

logging.getLogger("hassquitto").setLevel(logging.DEBUG)

# Create a new device with the name "Example Device"
device = hq.Device(name="Example Device")

# To see the device, open the following URL in browser:
#   http://homeassistant.local:8123/config/devices/dashboard


device.manufacturer = "Example Manufacturer"
device.model = "Example Model"
device.hw_version = "v1.0"
device.sw_version = "v2.0"
device.configuration_url = "http://example.com/configuration"
device.suggested_area = "Test"


try:
    # Defaults: host=homeassistant.local, port=1883
    device.connect(username="example", password="example")
    device.status("Check Device Info")

    # Start scheduler
    device.start()

    device.sleep(10)
except KeyboardInterrupt:
    pass
finally:
    # Remove the device from Home Assistant
    device.destroy()
    device.disconnect()
    device.stop()
