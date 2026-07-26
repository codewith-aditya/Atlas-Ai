import json
import os
import requests

# IoT / Home Automation Module
# Currently simulates devices. Can be extended for real APIs (Philips Hue, Wipro, etc.)

DEVICES_FILE = "materials/iot_devices.json"

class IoTModule:
    def __init__(self):
        self.devices_file = DEVICES_FILE
        self.devices = self.load_devices()

    def load_devices(self):
        if os.path.exists(self.devices_file):
            try:
                with open(self.devices_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Default devices (Simulation)
        return {
            "bedroom light": {"state": "off", "brightness": 100, "color": "white"},
            "kitchen fan": {"state": "off", "speed": 0},
            "living room ac": {"state": "off", "temp": 24}
        }

    def save_devices(self):
        os.makedirs(os.path.dirname(self.devices_file), exist_ok=True)
        with open(self.devices_file, 'w') as f:
            json.dump(self.devices, f, indent=2)

    def control_device(self, device_name, action, value=None):
        """ Control a device """
        device_name = device_name.lower()
        if device_name not in self.devices:
            return f"Device '{device_name}' not found."

        device = self.devices[device_name]
        
        if action == "turn on":
            device["state"] = "on"
            msg = f"Turned on {device_name}."
        elif action == "turn off":
            device["state"] = "off"
            msg = f"Turned off {device_name}."
        elif action == "set brightness":
            device["brightness"] = value
            msg = f"Set {device_name} brightness to {value}%."
        elif action == "set color":
            device["color"] = value
            msg = f"Changed {device_name} color to {value}."
            
        self.save_devices()
        return msg

    def get_status(self):
        status = "Home Device Status:\n"
        for name, data in self.devices.items():
            state_icon = "🟢" if data["state"] == "on" else "🔴"
            status += f"{state_icon} {name.title()}: {data['state'].upper()}\n"
        return status

# Global Instance
_iot_module = None

def get_iot_module():
    global _iot_module
    if _iot_module is None:
        _iot_module = IoTModule()
    return _iot_module

def control_home_device(command):
    iot = get_iot_module()
    
    # Simple NLP parsing
    command = command.lower()
    
    if "status" in command:
        return iot.get_status()
        
    for device in iot.devices:
        if device in command:
            if "turn on" in command or "switch on" in command:
                return iot.control_device(device, "turn on")
            elif "turn off" in command or "switch off" in command:
                return iot.control_device(device, "turn off")
            elif "brightness" in command:
                # Extract number
                import re
                nums = re.findall(r'\d+', command)
                if nums:
                    return iot.control_device(device, "set brightness", int(nums[0]))
            elif "color" in command:
                colors = ["red", "blue", "green", "white", "yellow"]
                for c in colors:
                    if c in command:
                        return iot.control_device(device, "set color", c)
            
    return "Could not understand device command."
