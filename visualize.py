"""
visualize.py
-------------
Renders the simulation results as a two-panel static plot:
  1. Vehicle trajectories (position vs. time)
  2. Inter-vehicle distance vs. time, with the 100 m communication
     threshold and the periods spent in range highlighted.

Colors follow a validated categorical palette (blue / orange for the two
vehicles) so the two series stay distinguishable for colorblind viewers,
with direct legend labels rather than relying on color alone.
"""

import matplotlib.pyplot as plt

# --- palette (validated categorical + chrome tokens) ---
SURFACE = "#fcfcfb"
INK_PRIMARY = "#0b0b0b"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
SERIES_A = "#2a78d6"   # blue
SERIES_B = "#eb6834"   # orange
IN_RANGE_FILL = "#1baf7a"  # aqua, used at low alpha as a state band


def plot_results(result, comm_range_m: float, out_path: str) -> None:
    """Save a two-panel PNG summarizing the simulation to ``out_path``."""
    fig, (ax_traj, ax_dist) = plt.subplots(
        2, 1, figsize=(9, 7), sharex=True, facecolor=SURFACE
    )

    # --- Panel 1: trajectories ---
    ax_traj.set_facecolor(SURFACE)
    vehicle_ids = list(result.positions_m.keys())
    colors = [SERIES_A, SERIES_B]
    for vid, color in zip(vehicle_ids, colors):
        ax_traj.plot(
            result.time_s, result.positions_m[vid],
            color=color, linewidth=2, label=f"Vehicle {vid}",
        )
    ax_traj.set_ylabel("Position (m)", color=INK_PRIMARY)
    ax_traj.set_title("Vehicle trajectories", color=INK_PRIMARY, loc="left")
    ax_traj.legend(frameon=False, labelcolor=INK_PRIMARY)
    _style_axes(ax_traj)

    # --- Panel 2: distance + range threshold ---
    ax_dist.set_facecolor(SURFACE)

    # Shade the periods the vehicles spent in communication range.
    in_range_started = None
    for i, in_range in enumerate(result.in_range):
        t = result.time_s[i]
        if in_range and in_range_started is None:
            in_range_started = t
        elif not in_range and in_range_started is not None:
            ax_dist.axvspan(in_range_started, t, color=IN_RANGE_FILL, alpha=0.15,
                             label="_nolegend_")
            in_range_started = None
    if in_range_started is not None:
        ax_dist.axvspan(in_range_started, result.time_s[-1],
                         color=IN_RANGE_FILL, alpha=0.15, label="_nolegend_")

    ax_dist.plot(result.time_s, result.distance_m, color=SERIES_A, linewidth=2,
                 label="Distance between vehicles")
    ax_dist.axhline(comm_range_m, color=INK_MUTED, linewidth=1.5, linestyle="--",
                     label=f"{comm_range_m:.0f} m communication threshold")

    ax_dist.set_xlabel("Time (s)", color=INK_PRIMARY)
    ax_dist.set_ylabel("Distance (m)", color=INK_PRIMARY)
    ax_dist.set_title("Inter-vehicle distance and communication range",
                       color=INK_PRIMARY, loc="left")
    ax_dist.legend(frameon=False, labelcolor=INK_PRIMARY, loc="upper right")
    _style_axes(ax_dist)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def _style_axes(ax) -> None:
    """Apply recessive gridlines/spines consistent with the rest of the plot."""
    ax.grid(True, color=GRIDLINE, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRIDLINE)
    ax.tick_params(colors=INK_MUTED)
