# hassquitto

Home-Assistant MQTT Device Framework


Example:

```python
import hassquitto as hq

device = hq.Device(name="Example Device")


@device.on_connect
async def device_connected():
    await device.status("Hello, World!")


try:
    device.run(
        username="example",
        password="example",
    )
except KeyboardInterrupt:
    pass
finally:
    device.destroy()
    device.stop()
```
