from queue import Queue
from typing import Optional


from sila2.server import MetadataDict

from ..generated.pumpcontrol import StopPump_Responses, StartPump_Responses, Pump_Responses, Suck_Responses, \
    SetAcceleration_Responses, SetVelocity_Responses, SetVoltage_Responses, GetStatus_Responses

from ..generated.pumpcontrol.pumpcontrol_base import PumpControlBase


from pd_pump.pump import Pump
from pd_pump.controller import ControllerPump
from serial import SerialException


class PumpControl(PumpControlBase):
    def __init__(self, parent_server):
        super().__init__(parent_server)

        self.__pump: Pump = parent_server.pump

        self.__controller: ControllerPump = self.__pump.controller
        self._status_queue = Queue()

    def GetStatus(self, *, metadata: MetadataDict) -> GetStatus_Responses:
        try:
            status = self.__controller.get_status()
            return GetStatus_Responses()
        except Exception as e:
            self._last_status = f"error: {str(e)}"
            self.update_PumpStatus(self._last_status, queue=self._status_queue)
            return GetStatus_Responses()

    def StartPump(self, Velocity: int, *, metadata: MetadataDict) -> StartPump_Responses:
        try:
            self.__controller.run_motor(Velocity)
            self._last_status = f"pump started on:{Velocity} steps/s"
            self.update_PumpStatus(self._last_status, queue=self._status_queue)
            return StartPump_Responses()
        except Exception as e:
            self._last_status = f"error: {str(e)}"
            self.update_PumpStatus(self._last_status, queue=self._status_queue)
            return StartPump_Responses()

    def StopPump(self, *, metadata: MetadataDict) -> StopPump_Responses:
        try:
            self.__controller.stop_motor()
            self._last_status = "pump idle"
            self.update_PumpStatus(self._last_status, queue=self._status_queue)
            return StopPump_Responses()

        except Exception as e:
            self._last_status = f"error: {str(e)}"
            self.update_PumpStatus(self._last_status, queue=self._status_queue)
            return StopPump_Responses()


    def SetVoltage(self, Voltage: int, *, metadata: MetadataDict) -> SetVoltage_Responses:
        try:
            self.__controller.set_voltage(Voltage)
            self._last_status = f"updated Voltage to: {Voltage}"
            self.update_PumpStatus(self._last_status, queue=self._status_queue)
            return SetVoltage_Responses()

        except Exception as e:
            self._last_status = f"error: {str(e)}"
            self.update_PumpStatus(self._last_status, queue=self._status_queue)
            return SetVoltage_Responses()

    def Pump(self, Amount: float, *, metadata: MetadataDict) -> Pump_Responses:
        try:
            self.__controller.pump_ml(Amount)
            self._last_status = f"pump pumping {Amount}: ml"
            self.update_PumpStatus(self._last_status, queue=self._status_queue)
            return Pump_Responses()

        except Exception as e:
            self._last_status = f"error: {str(e)}"
            self.update_PumpStatus(self._last_status, queue=self._status_queue)
            return Pump_Responses()

    def Suck(self, Amount: float, *, metadata: MetadataDict) -> Suck_Responses:
        try:
            self.__controller.suck_ml(Amount)
            self._last_status = f"pump sucking {Amount}: ml"
            self.update_PumpStatus(self._last_status, queue=self._status_queue)
            return Suck_Responses()

        except Exception as e:
            self._last_status = f"error: {str(e)}"
            self.update_PumpStatus(self._last_status, queue=self._status_queue)
            return Suck_Responses()

    def SetAcceleration(self, Acceleration: float, *, metadata: MetadataDict) -> SetAcceleration_Responses:
        try:
            self.__controller.set_acceleration(int(Acceleration))
            self._last_status = "updated Acceleration"
            self.update_PumpStatus(self._last_status, queue=self._status_queue)
            return SetAcceleration_Responses()

        except Exception as e:
            self._last_status = f"error: {str(e)}"
            self.update_PumpStatus(self._last_status, queue=self._status_queue)
            return SetAcceleration_Responses()

    def SetVelocity(self, Velocity: float, *, metadata: MetadataDict) -> SetVelocity_Responses:
        try:
            self.__controller.set_speed(int(Velocity))
            self._last_status = "updated Velocity"
            self.update_PumpStatus(self._last_status, queue=self._status_queue)
            return SetVelocity_Responses()

        except Exception as e:
            self._last_status = f"error: {str(e)}"
            self.update_PumpStatus(self._last_status, queue=self._status_queue)
            return SetVelocity_Responses()

    def PumpStatus_on_subscription(self, *, metadata: MetadataDict) -> Optional[Queue[str]]:
        return self._status_queue
