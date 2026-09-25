# V2V Communication Simulation

A basic Vehicle-to-Vehicle (V2V) communication simulator: two vehicles move
along a straight road and exchange Basic-Safety-Message (BSM) style packets
whenever they are within 100 m of each other.

## Structure

- `vehicle.py` — `Vehicle` and `Message` data model
- `simulation.py` — time-stepped simulation engine (movement, range
  detection, message exchange, event/history logging)
- `visualize.py` — renders trajectory + distance/range plots
- `main.py` — runs the default scenario end-to-end
- `tests/test_simulation.py` — unit tests for distance and range logic

## Run it

```bash
pip install -r requirements.txt
python main.py
```

This prints range-transition events and message exchanges to the console
and writes `v2v_simulation_result.png`.

## Test it

```bash
python -m unittest discover -s tests
```

## Scenario

Vehicle A starts at 0 m moving at +20 m/s; Vehicle B starts at 300 m moving
at -15 m/s. They approach, come within the 100 m communication range,
exchange messages every second while in range, then separate again as they
pass — all parameters are adjustable in `main.py`.
