import logging
import hassquitto as hq

logging.getLogger("hassquitto").setLevel(logging.DEBUG)

# Create a new device with the name "Example Device"
device = hq.Device(name="Example Device")

# To see the device, open the following URL in browser:
#   http://homeassistant.local:8123/config/devices/dashboard


@device.on_interval(1)
def on_interval():
    if device.status() is None:
        device.status("0")
        device.status_set_confirm()

    counter = int(device.status())
    counter += 1
    device.status(counter, retain=True)


try:
    # Defaults: host=homeassistant.local, port=1883
    device.connect(username="example", password="example")

    # Start scheduler
    device.start()

    for counter in range(10):
        device.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    # Remove the device from Home Assistant
    device.destroy()
    device.disconnect()
    device.stop()
