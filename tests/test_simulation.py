"""
Unit tests for the V2V simulation core logic.

Run with:
    python -m unittest discover -s tests
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation import Simulation, SimulationConfig
from vehicle import Vehicle


class TestDistance(unittest.TestCase):
    def test_distance_is_symmetric_and_absolute(self):
        a = Vehicle("A", position_m=10.0, speed_mps=0.0)
        b = Vehicle("B", position_m=150.0, speed_mps=0.0)
        self.assertEqual(Simulation.distance(a, b), 140.0)
        self.assertEqual(Simulation.distance(b, a), 140.0)


class TestRangeDetection(unittest.TestCase):
    def test_vehicles_starting_in_range_exchange_immediately(self):
        a = Vehicle("A", position_m=0.0, speed_mps=0.0)
        b = Vehicle("B", position_m=50.0, speed_mps=0.0)
        sim = Simulation([a, b], SimulationConfig(dt_s=1.0, duration_s=2.0,
                                                    comm_range_m=100.0))
        result = sim.run(verbose=False)
        self.assertTrue(all(result.in_range))
        self.assertGreater(len(result.messages), 0)

    def test_vehicles_out_of_range_never_exchange(self):
        a = Vehicle("A", position_m=0.0, speed_mps=0.0)
        b = Vehicle("B", position_m=500.0, speed_mps=0.0)
        sim = Simulation([a, b], SimulationConfig(dt_s=1.0, duration_s=2.0,
                                                    comm_range_m=100.0))
        result = sim.run(verbose=False)
        self.assertFalse(any(result.in_range))
        self.assertEqual(len(result.messages), 0)

    def test_entering_and_leaving_range_are_logged_once_each(self):
        # Vehicles start 300m apart, close to <100m, then separate again.
        a = Vehicle("A", position_m=0.0, speed_mps=20.0)
        b = Vehicle("B", position_m=300.0, speed_mps=-15.0)
        sim = Simulation([a, b], SimulationConfig(dt_s=1.0, duration_s=20.0,
                                                    comm_range_m=100.0))
        result = sim.run(verbose=False)
        entered = [e for e in result.events if "ENTERED" in e]
        left = [e for e in result.events if "LEFT" in e]
        self.assertEqual(len(entered), 1)
        self.assertEqual(len(left), 1)
        self.assertGreater(len(result.messages), 0)

    def test_raises_with_fewer_than_two_vehicles(self):
        with self.assertRaises(ValueError):
            Simulation([Vehicle("A", 0.0, 0.0)])


if __name__ == "__main__":
    unittest.main()
