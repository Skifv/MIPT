"""
# ------------------------------------------------------------------
# Visualization Helper Module
# ------------------------------------------------------------------
"""
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Optional

@dataclass
class PlotParams:
    """
    Container for plot style parameters.
    
    Parameters
    ----------
    - linestyle (str): Line style (e.g., '-', '--').
    - color (str): Color code.
    - linewidth (float): Line width.
    - marker (Optional[str]): Marker type.
    - markersize (float): Marker size.
    - label (str): Legend label.
    - alpha (float): Transparency.
    """
    linestyle:  str = "-"
    color:      str = "k"
    linewidth:  float = 1.5
    marker:     Optional[str] = None
    markersize: float = 4.0
    label:      str = ""
    alpha:      float = 1.0

class Plotter:
    """
    Class for creating publication-quality plots.

    Methods
    -------
    - add_plot: Adds a line plot.
    - add_scatter: Adds a scatter plot.
    - finalize_and_show: Configures grid, legend, and displays/saves the plot.
    """

    def __init__(self, title: str = None, xlabel: str = None, ylabel: str = None, figsize: tuple = (10, 6)):
        self.fig, self.ax = plt.subplots(figsize=figsize)
        if title:
            self.ax.set_title(title, fontsize=16, pad=15)
        if xlabel:
            self.ax.set_xlabel(xlabel, fontsize=14, labelpad=10)
        if ylabel:
            self.ax.set_ylabel(ylabel, fontsize=14, labelpad=10)

    def add_plot(self, x: np.ndarray, y: np.ndarray, params: PlotParams):
        """
        Add a line plot.

        Parameters
        ----------
        - x (np.ndarray): X coordinates.
        - y (np.ndarray): Y coordinates.
        - params (PlotParams): Styling parameters.
        """
        self.ax.plot(
            x, y,
            linestyle   = params.linestyle,
            color       = params.color,
            linewidth   = params.linewidth,
            label       = params.label,
            marker      = params.marker,
            markersize  = params.markersize,
            alpha       = params.alpha
        )

    def add_scatter(self, x: np.ndarray, y: np.ndarray, params: PlotParams):
        """
        Add a scatter plot.

        Parameters
        ----------
        - x (np.ndarray): X coordinates.
        - y (np.ndarray): Y coordinates.
        - params (PlotParams): Styling parameters.
        """
        # Use star marker if not specified, and ensure it's visible but not huge
        marker = params.marker if params.marker else '*'
        
        self.ax.scatter(
            x, y,
            color       = params.color,
            label       = params.label,
            s           = params.markersize**2 * 5, # Adjusted scaling for star markers
            marker      = marker,
            zorder      = 5
        )

    def finalize_and_show(self, save_path: Optional[str] = None):
        """
        Apply formatting and show/save.

        Parameters
        ----------
        - save_path (Optional[str]): Path to save the figure (e.g., 'plot.pdf').
        """
        self.ax.minorticks_on()
        self.ax.grid(True, which='major', linestyle='-', alpha=0.5)
        self.ax.grid(True, which='minor', linestyle=':', alpha=0.2)
        
        if self.ax.get_legend_handles_labels()[0]:
            self.ax.legend(fontsize=12, loc='best', frameon=True, fancybox=True, framealpha=0.9)
            
        self.ax.tick_params(axis='both', which='major', labelsize=12)
        self.fig.tight_layout()

        if save_path:
            self.fig.savefig(save_path, dpi=300)
            print(f"Plot saved to: {save_path}")

        plt.show()
