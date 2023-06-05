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

    counter = 0
    while True:
        device.status(f"Running {str(counter)}")
        device.sleep(1)
        counter += 1

except KeyboardInterrupt:
    pass
finally:
    # Remove the device from Home Assistant
    device.destroy()
    device.disconnect()
    device.stop()
