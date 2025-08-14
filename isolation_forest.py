import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from sklearn.ensemble import IsolationForest
import matplotlib.animation as animation


class SensorNetworkMonitor:
    """
    Modular system for simulation, analysis and visualization of a sensor network.
    """

    def __init__(
        self, num_sensors=50, area_size=100, window_size=20, anomaly_ratio=0.05, seed=42
    ):
        """
        Initialize the sensor network with configurable parameters.
        """
        self.num_sensors = num_sensors
        self.area_size = area_size
        self.window_size = window_size
        self.anomaly_ratio = anomaly_ratio
        self.seed = seed
        self.positions = {}
        self.graph = nx.Graph()
        self.data_history = []
        self._init_rng()
        self._generate_network()

    def _init_rng(self):
        """
        Set up the random number generator for reproducibility.
        """
        np.random.seed(self.seed)

    def _generate_positions(self):
        """
        Generate random spatial coordinates for the sensors.
        """
        return {
            i: (
                np.random.uniform(0, self.area_size),
                np.random.uniform(0, self.area_size),
            )
            for i in range(self.num_sensors)
        }

    def _generate_network(self):
        """
        Build the connected graph of sensors based on distance.
        """
        self.positions = self._generate_positions()
        self.graph.clear()
        for i in range(self.num_sensors):
            self.graph.add_node(i, pos=self.positions[i])
        for i in range(self.num_sensors):
            for j in range(i + 1, self.num_sensors):
                dist = np.linalg.norm(
                    np.array(self.positions[i]) - np.array(self.positions[j])
                )
                if dist < self.area_size * 0.2:
                    self.graph.add_edge(i, j)

    def generate_sensor_data(self, timestep):
        """
        Simulate sensor readings at a given time step.
        """
        data = []
        for _ in range(self.num_sensors):
            base = 20 + 5 * np.sin(2 * np.pi * timestep / 1440)
            noise = np.random.normal(0, 0.5)
            if np.random.rand() < self.anomaly_ratio:
                reading = base + noise + np.random.normal(15, 5)
            else:
                reading = base + noise
            data.append(reading)
        return np.array(data)

    def detect_anomalies(self):
        """
        Apply Isolation Forest to identify anomalous sensors.
        """
        matrix = np.stack(self.data_history, axis=1)
        features = np.mean(matrix, axis=1).reshape(-1, 1)
        model = IsolationForest(
            contamination=self.anomaly_ratio, random_state=self.seed
        )
        preds = model.fit_predict(features)
        return ["red" if p == -1 else "green" for p in preds]

    def update_history(self, data):
        """
        Update the temporal window of recent data.
        """
        self.data_history.append(data)
        if len(self.data_history) > self.window_size:
            self.data_history.pop(0)

    def run_visualization(self, frames=200, interval=200):
        """
        Launch real-time animation of the network with visual indication of anomalies.
        """
        fig, ax = plt.subplots()
        scatter = ax.scatter([], [], c=[], cmap="coolwarm", vmin=15, vmax=45, s=100)
        ax.set_xlim(0, self.area_size)
        ax.set_ylim(0, self.area_size)
        ax.set_title("Sensor network monitoring - Anomaly detection")

        def update(frame):
            data = self.generate_sensor_data(frame)
            self.update_history(data)
            if len(self.data_history) < self.window_size:
                return (scatter,)
            colors = self.detect_anomalies()
            coords = np.array([self.positions[i] for i in range(self.num_sensors)])
            scatter.set_offsets(coords)
            scatter.set_color(colors)
            return (scatter,)

        # Keep reference to animation to avoid garbage collection
        self.ani = animation.FuncAnimation(
            fig, update, frames=frames, interval=interval, blit=True
        )
        plt.show()


# System execution with initial pre-loading
if __name__ == "__main__":
    monitor = SensorNetworkMonitor()

    # Fill the window buffer before animation
    for t in range(monitor.window_size):
        data = monitor.generate_sensor_data(t)
        monitor.update_history(data)

    monitor.run_visualization()
