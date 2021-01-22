import uuid

from datetime import datetime
from uuid import UUID

# TODO: Decide whether to put them into one class or let them be two separate ones with the same properties


class BuySignal:
    def __init__(self, price: float, time: datetime, ) -> None:
        self.signal_id: UUID = uuid.uuid4()
        self.price: float = price
        self.time: datetime = time
        self.accepted: bool = False


class SellSignal:
    def __init__(self, signal_id: UUID, price: float, time: datetime) -> None:
        self.signal_id: UUID = signal_id  # Same id as the corresponding buy signal
        self.price: float = price
        self.time: datetime = time
        self.accepted: bool = False
