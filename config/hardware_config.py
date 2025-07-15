import json
from pathlib import Path

class HardwareConfig:
    def __init__(self, config_path="config/hardware_config.json"):
        with open(config_path, encoding="utf-8") as f:
            self._config = json.load(f)

    @property
    def touch_pin(self):
        return self._config["touch"]

    @property
    def ir_pins(self):
        return self._config["ir"]

    @property
    def motor_pins(self):
        return self._config["motor"]

    @property
    def screen_pins(self):
        return self._config["screen"]

    @property
    def servo_config(self):
        return self._config["servo"]

    @property
    def sonar_config(self):
        return self._config["sonar"]

    @property
    def upgrade_command(self):
        return self._config.get("upgrade", {}).get("cmd", "")
