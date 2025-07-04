from queue import Queue
from typing import Optional


from sila2.server import MetadataDict

from ..generated.pumpcontrol import InitPump_Responses, StopPump_Responses,\
     StartPump_Responses, Pump_Responses, Suck_Responses, Direction_Responses

from ..generated.pumpcontrol.pumpcontrol_base import PumpControlBase


from pd_pump.pump import Pump
from pd_pump.controller import ControllerPump
from serial import SerialException


class PumpControl(PumpControlBase):
    def __init__(self, parent_server):
        super().__init__(parent_server)

        self.__pump: Pump = parent_server.pump

        self.__controller: ControllerPump = None
        self.direction = "forwards"
        self._status_queue = Queue()
        self._last_status = "not initialized"



    """
    Not needed, handeld by Server
    """
    def InitPump(self, ComPort: str, *, metadata: MetadataDict) -> InitPump_Responses:
        try:
            self.__pump = Pump(ComPort)
            self.__controller = self.__pump.controller
            self.pump_initialized = True

            self._last_status = "pump initialized"
            self.update_PumpStatus(self._last_status, queue = self._status_queue)
            return InitPump_Responses()

        except SerialException as e:
            self._last_status = f"error: {str(e)}"
            self.update_PumpStatus(self._last_status, queue=self._status_queue)
            return InitPump_Responses()

    def StartPump(self, Start: bool, *, metadata: MetadataDict) -> StartPump_Responses:
        if not self.pump_initialized:
            return StartPump_Responses()

        if not Start:
            self._last_status = "pump idle"
            self.update_PumpStatus(self._last_status, queue=self._status_queue)

        if self.direction == "forward":
            print("start pump forwards")
            self._last_status = "pump running forwards"
            self.update_PumpStatus(self._last_status, queue=self._status_queue)

        elif self.direction == "backwards":
            self._last_status = "pump running backwards"
            self.update_PumpStatus(self._last_status, queue=self._status_queue)
            print("start pump backwards")

        return StartPump_Responses()

    def StopPump(self, Stop: bool, *, metadata: MetadataDict) -> StopPump_Responses:
        if not Stop or not self.pump_initialized:
            return StopPump_Responses()

        print("Stop Pump")
        self._last_status = "pump idle"
        self.update_PumpStatus(self._last_status, queue=self._status_queue)
        return StopPump_Responses()

    def Pump(self, Amount: float, *, metadata: MetadataDict) -> Pump_Responses:
        if not self.pump_initialized:
            return Pump_Responses()

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
        if not self.pump_initialized:
            return Suck_Responses()

        try:
            self.__controller.suck_ml(Amount)
            self._last_status = f"pump sucking {Amount}: ml"
            self.update_PumpStatus(self._last_status, queue=self._status_queue)
            return Suck_Responses()

        except Exception as e:
            self._last_status = f"error: {str(e)}"
            self.update_PumpStatus(self._last_status, queue=self._status_queue)
            return Suck_Responses()

    def Direction(self, Direction: bool, *, metadata: MetadataDict) -> Direction_Responses:
        if not self.pump_initialized:
            return Direction_Responses()

        if Direction:
            self.direction = "forwards"

        else:
            self.direction = "backwards"

        return Direction_Responses()

    def PumpStatus_on_subscription(self, *, metadata: MetadataDict) -> Optional[Queue[str]]:
        return self._status_queue
