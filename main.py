"""
main.py
-------
Entry point for the V2V communication simulation.

Scenario: two vehicles approach each other on a straight road, come within
100 m of each other (entering communication range), exchange Basic Safety
Messages while in range, then separate again as they pass.

Run with:
    python main.py
"""

from simulation import Simulation, SimulationConfig
from vehicle import Vehicle
from visualize import plot_results

OUTPUT_PLOT_PATH = "v2v_simulation_result.png"


def build_scenario() -> Simulation:
    """Two vehicles on a 300 m road, driving toward each other and passing."""
    vehicle_a = Vehicle(vehicle_id="A", position_m=0.0, speed_mps=20.0)
    vehicle_b = Vehicle(vehicle_id="B", position_m=300.0, speed_mps=-15.0)
    config = SimulationConfig(dt_s=1.0, duration_s=20.0, comm_range_m=100.0)
    return Simulation([vehicle_a, vehicle_b], config)


def main() -> None:
    sim = build_scenario()

    print("Starting V2V simulation")
    print(f"  Vehicle A: start=0m,   speed=+20 m/s")
    print(f"  Vehicle B: start=300m, speed=-15 m/s")
    print(f"  Communication range: {sim.config.comm_range_m:.0f} m")
    print(f"  Duration: {sim.config.duration_s:.0f} s, dt={sim.config.dt_s:.0f} s")
    print("-" * 60)

    result = sim.run(verbose=True)

    print("-" * 60)
    print(f"Simulation finished: {len(result.messages)} messages exchanged "
          f"over {len(result.events)} range-transition events.")

    plot_results(result, sim.config.comm_range_m, OUTPUT_PLOT_PATH)
    print(f"Plot saved to {OUTPUT_PLOT_PATH}")


if __name__ == "__main__":
    main()
