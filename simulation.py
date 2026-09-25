"""
simulation.py
--------------
Core simulation engine for the V2V communication scenario.

At every timestep, each vehicle's position is advanced, and every pair of
vehicles is checked for range: if the distance between them is within
``comm_range_m`` (100 m by default), they exchange a Basic-Safety-Message
(BSM). Range entry/exit events and every exchanged message are logged, and
the full time history is recorded so it can be plotted afterwards.
"""

from dataclasses import dataclass, field
from itertools import combinations
from typing import Dict, List, Tuple

from vehicle import Message, Vehicle

DEFAULT_COMM_RANGE_M = 100.0


@dataclass
class SimulationConfig:
    """Parameters controlling how the simulation is run."""

    dt_s: float = 1.0          # simulation timestep, in seconds
    duration_s: float = 30.0   # total simulated time, in seconds
    comm_range_m: float = DEFAULT_COMM_RANGE_M


@dataclass
class SimulationResult:
    """Everything recorded while the simulation ran."""

    time_s: List[float] = field(default_factory=list)
    positions_m: Dict[str, List[float]] = field(default_factory=dict)
    distance_m: List[float] = field(default_factory=list)
    in_range: List[bool] = field(default_factory=list)
    messages: List[Message] = field(default_factory=list)
    events: List[str] = field(default_factory=list)


class Simulation:
    """Runs a time-stepped V2V communication simulation for N vehicles.

    Only pairwise range checks are implemented (sufficient for the 2-vehicle
    scenario this project targets), but the engine works for any number of
    vehicles supplied in ``vehicles``.
    """

    def __init__(self, vehicles: List[Vehicle], config: SimulationConfig = None):
        if len(vehicles) < 2:
            raise ValueError("Simulation needs at least two vehicles.")
        self.vehicles = vehicles
        self.config = config or SimulationConfig()
        # Tracks whether each vehicle pair was in range on the previous step,
        # so we can detect and log "entered range" / "left range" transitions.
        self._pair_was_in_range: Dict[Tuple[str, str], bool] = {
            (a.vehicle_id, b.vehicle_id): False
            for a, b in combinations(self.vehicles, 2)
        }

    @staticmethod
    def distance(a: Vehicle, b: Vehicle) -> float:
        """Euclidean distance between two vehicles (1D road -> absolute diff)."""
        return abs(a.position_m - b.position_m)

    def _exchange_messages(self, a: Vehicle, b: Vehicle, t: float,
                            result: SimulationResult) -> None:
        """Have two in-range vehicles broadcast BSMs to each other."""
        msg_a = a.build_message(t)
        msg_b = b.build_message(t)
        b.receive(msg_a)
        a.receive(msg_b)
        result.messages.append(msg_a)
        result.messages.append(msg_b)

    def run(self, verbose: bool = True) -> SimulationResult:
        """Run the simulation from t=0 to t=duration_s and return the results."""
        result = SimulationResult()
        for v in self.vehicles:
            result.positions_m[v.vehicle_id] = []

        n_steps = int(round(self.config.duration_s / self.config.dt_s)) + 1
        for step in range(n_steps):
            t = step * self.config.dt_s

            # Record current positions before advancing.
            for v in self.vehicles:
                result.positions_m[v.vehicle_id].append(v.position_m)

            # Only meaningful for the 2-vehicle case, but generalizes to
            # every pair if more vehicles are added later.
            for a, b in combinations(self.vehicles, 2):
                d = self.distance(a, b)
                currently_in_range = d <= self.config.comm_range_m
                pair_key = (a.vehicle_id, b.vehicle_id)
                was_in_range = self._pair_was_in_range[pair_key]

                if len(self.vehicles) == 2:
                    result.distance_m.append(d)
                    result.in_range.append(currently_in_range)

                if currently_in_range and not was_in_range:
                    event = (f"t={t:5.1f}s  {a.vehicle_id}<->{b.vehicle_id} "
                             f"ENTERED range (distance={d:.1f}m)")
                    result.events.append(event)
                    if verbose:
                        print(event)
                elif was_in_range and not currently_in_range:
                    event = (f"t={t:5.1f}s  {a.vehicle_id}<->{b.vehicle_id} "
                             f"LEFT range (distance={d:.1f}m)")
                    result.events.append(event)
                    if verbose:
                        print(event)

                if currently_in_range:
                    self._exchange_messages(a, b, t, result)
                    if verbose:
                        print(f"  t={t:5.1f}s  message exchange "
                              f"({a.vehicle_id}<->{b.vehicle_id}, distance={d:.1f}m)")

                self._pair_was_in_range[pair_key] = currently_in_range

            result.time_s.append(t)

            # Advance vehicles for the next step (skip after the last sample).
            if step < n_steps - 1:
                for v in self.vehicles:
                    v.step(self.config.dt_s)

        return result
