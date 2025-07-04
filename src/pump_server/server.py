from typing import Optional
from uuid import UUID

from sila2.server import SilaServer

from .feature_implementations.pump_controll_impl import PumpControl
from .generated.pumpcontrol import PumpControlFeature
from pd_pump.pump import Pump

class Server(SilaServer):
    def __init__(self, config, pump: Pump, server_uuid: Optional[UUID] = None):
        super().__init__(
            server_name="Pump SiLA2 Server",
            server_type="PumpController",
            server_version="0.1",
            server_description="A SiLA2 Server for controlling a pump based on PDStepper",
            server_vendor_url="https://github.com/Tiagomey",
            server_uuid=server_uuid,
        )

        self.config = config
        self.pump = pump

        self.pump_control = PumpControl(self)
        self.set_feature_implementation(PumpControlFeature, self.pump_control)
