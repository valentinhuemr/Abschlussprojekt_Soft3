import matplotlib.pyplot as plt
import matplotlib.animation as animation

def visualize_mechanism(positions_list, rods):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(-50, 50)
    ax.set_ylim(-50, 50)
    ax.set_aspect("equal")

    # Umlaufkreis hinzufügen
    circle = plt.Circle((-30, 0), 10, color='r', fill=False, linestyle="dashed")
    ax.add_patch(circle)

    points, = ax.plot([], [], 'ro', markersize=8)
    lines = []
    for _ in rods:
        line, = ax.plot([], [], 'k-', lw=2)
        lines.append(line)

    def update(frame):
        positions = positions_list[frame]
        x_vals, y_vals = zip(*[positions[j] for j in sorted(positions.keys())])
        points.set_data(x_vals, y_vals)

        for i, (joint1, joint2) in enumerate(rods):
            x1, y1 = positions[joint1]
            x2, y2 = positions[joint2]
            lines[i].set_data([x1, x2], [y1, y2])
        return [points] + lines

    ani = animation.FuncAnimation(fig, update, frames=len(positions_list), interval=50, blit=True)
    gif_path = "mechanism_animation.gif"
    ani.save(gif_path, writer='pillow', fps=15)
    plt.close(fig)
    return gif_path
