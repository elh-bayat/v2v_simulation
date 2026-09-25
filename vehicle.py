"""
vehicle.py
----------
Defines the Vehicle class used in the V2V communication simulation.

Each vehicle moves along a straight (1D) road at a constant speed and
direction, and can send/receive Basic-Safety-Message-style (BSM) packets
to/from other vehicles.
"""

from dataclasses import dataclass, field


@dataclass
class Message:
    """A simplified V2V "Basic Safety Message" (BSM)."""

    sender_id: str
    timestamp: float
    position_m: float
    speed_mps: float

    def __str__(self) -> str:
        return (
            f"BSM(from={self.sender_id}, t={self.timestamp:.1f}s, "
            f"pos={self.position_m:.1f}m, speed={self.speed_mps:.1f}m/s)"
        )


@dataclass
class Vehicle:
    """A single vehicle moving on a 1D road.

    Attributes:
        vehicle_id: Human-readable identifier (e.g. "A", "B").
        position_m: Current position along the road, in meters.
        speed_mps: Signed speed in meters/second. Positive moves the
            vehicle in the +x direction, negative in the -x direction.
        inbox: Messages received from other vehicles, in arrival order.
    """

    vehicle_id: str
    position_m: float
    speed_mps: float
    inbox: list = field(default_factory=list)

    def step(self, dt_s: float) -> None:
        """Advance the vehicle's position by one simulation timestep."""
        self.position_m += self.speed_mps * dt_s

    def build_message(self, timestamp: float) -> Message:
        """Create the BSM this vehicle would broadcast right now."""
        return Message(
            sender_id=self.vehicle_id,
            timestamp=timestamp,
            position_m=self.position_m,
            speed_mps=self.speed_mps,
        )

    def receive(self, message: Message) -> None:
        """Store an incoming message from another vehicle."""
        self.inbox.append(message)
