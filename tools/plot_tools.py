import numpy as np
import matplotlib.pyplot as plt
from typing import List, Union, Optional, Tuple, Iterable


def plot_signals(
    y: Union[np.ndarray, List[np.ndarray]],
    x: Optional[Union[np.ndarray, List[np.ndarray]]] = None,
    *,
    figsize: Tuple[float, float] = (10, 6),
    errors: Optional[
        Union[
            Tuple[Optional[np.ndarray], Optional[np.ndarray]],
            List[Tuple[Optional[np.ndarray], Optional[np.ndarray]]],
        ]
    ] = None,
    labels: Optional[Union[str, List[str]]] = None,
    colors: Optional[Union[str, List[str]]] = None,
    linestyles: Optional[Union[str, List[str]]] = None,
    limits: Optional[
        Tuple[Optional[Tuple[float, float]], Optional[Tuple[float, float]]]
    ] = None,
    log_scale: Optional[Tuple[bool, bool]] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    as_stem: Union[bool, List[bool]] = False,
    show_err: bool = False,
    legend_pos: Union[str, Tuple[float, float]] = "best",
    ncol: int = 1,
    save_name: Optional[str] = None,
) -> None:
    """
    Visualizes one or multiple 1D signals. Supports continuous plots,
    discrete (stem) plots, and errorbar visualizations.

    Parameters
    ----------
    - y : (N,) ndarray or List[(N,) ndarray]
        Amplitude values of the signal(s).
    - x : (N,) ndarray or List[(N,) ndarray], optional
        Time or index axis. If None, generated automatically as integer sequences.
    - figsize : Tuple[float, float], optional
        Figure size in inches (width, height). Defaults to (10, 6).
    - errors : Tuple or List[Tuple], optional
        Errors for X and Y axes. Format: (xerr, yerr).
        xerr/yerr can be arrays of the same length as y, or scalars.
    - labels : str or List[str], optional
        Labels for the legend. If a string is passed for multiple signals,
        it will only apply to the first one (or be wrapped in a list).
    - colors : str or List[str], optional
        Line/marker colors. Uses standard matplotlib property cycle if not set.
    - linestyles : str or List[str], optional
        Line styles (e.g., '-', '--', ':', '-.').
    - limits : Tuple[Optional[Tuple[float, float]], Optional[Tuple[float, float]]], optional
        Explicit axes limits in format ((x_min, x_max), (y_min, y_max)).
        Any tuple or element can be None for auto-scaling.
    - log_scale : Tuple[bool, bool], optional
        Tuple (log_x, log_y). If True, the respective axis uses a logarithmic scale.
    - title : str, optional
        Plot title.
    - xlabel : str, optional
        Label for the X-axis. Defaults to "Samples (n)" if x is not provided.
    - ylabel : str, optional
        Label for the Y-axis.
    - as_stem : bool or List[bool], optional
        If True, renders the signal as discrete samples (vertical lines with markers).
    - show_err : bool, optional
        Flag to activate error bar rendering. Requires `errors` parameter to be populated.
    - legend_pos : str or Tuple[float, float], optional
        Legend position. String (e.g., 'upper right') or relative coordinate tuple.
    - ncol : int, optional
        Number of columns in the legend.
    - save_name : str, optional
        File path to save the generated plot.

    Returns
    -------
    - None : None
        The function modifies the active matplotlib figure and returns nothing.

    Notes
    -----
    • *Algorithm workflow*
    1. Normalize input arrays and parameters into unified lists to handle single vs multiple signals.
    2. Prepare visual styles (colors, line types) dynamically based on the signal count.
    3. Render plot elements iteratively (priority: Errorbar -> Stem -> Standard Line).
    4. Apply axis formatting, grids, scales, and layout limits.
    """
    plt.close()  # Ensure cleanup of previous figures in interactive environments

    # --- Step 1: Input Data Normalization ---
    # Convert y to a list of arrays for unified processing
    y_list = [y] if isinstance(y, np.ndarray) and y.ndim == 1 else list(y)
    num_signals = len(y_list)

    # Generate integer indices if X-axis is not provided
    if x is None:
        x_list = [np.arange(len(sig)) for sig in y_list]  # shape: (N,) arrays in list
    else:
        x_list = [x] if isinstance(x, np.ndarray) and x.ndim == 1 else list(x)

    # Normalize the list of errors
    if errors is None:
        err_list = [(None, None)] * num_signals
    elif isinstance(errors, tuple):
        err_list = [errors] * num_signals
    else:
        err_list = list(errors)

    # --- Step 2: Visual Style Preparation ---
    # Obtain current color palette if colors are not explicitly defined
    if colors is None:
        if num_signals <= 10:
            # Standard property cycle
            style_colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        elif num_signals <= 20:
            # Extended qualitative palette
            style_colors = plt.get_cmap("tab20")(np.linspace(0, 1, num_signals))
        else:
            # Universal palette for a large number of lines (highly distinguishable)
            style_colors = plt.get_cmap("turbo")(np.linspace(0, 1, num_signals))
    else:
        style_colors = [colors] if isinstance(colors, str) else list(colors)

    style_lines = (
        ["-"]
        if linestyles is None
        else ([linestyles] if isinstance(linestyles, str) else list(linestyles))
    )

    # Generate legend labels
    if labels is None:
        final_labels = [f"Signal {i+1}" for i in range(num_signals)]
    else:
        final_labels = [labels] if isinstance(labels, str) else list(labels)

    # Broadcast as_stem flag across all signals if a single boolean is passed
    if isinstance(as_stem, bool):
        stem_flags = [as_stem] * num_signals
    else:
        stem_flags = list(as_stem)

    # --- Step 3: Canvas Initialization and Rendering ---
    fig, ax = plt.subplots(figsize=figsize)

    for i in range(num_signals):
        # Select current signal parameters with cyclical modulo fallback
        curr_x = x_list[0] if len(x_list) == 1 else x_list[i]
        curr_y = y_list[i]
        curr_err_y, curr_err_x = err_list[i % len(err_list)]

        color = style_colors[i % len(style_colors)]
        l_style = style_lines[i % len(style_lines)]
        current_as_stem = stem_flags[i % len(stem_flags)]

        # --- Step 3a: Plotting Logic ---
        # Priority: Errorbar -> Stem -> Standard Line Plot
        if show_err and (curr_err_x is not None or curr_err_y is not None):
            ax.errorbar(
                curr_x,
                curr_y,
                xerr=curr_err_x,
                yerr=curr_err_y,
                label=final_labels[i],
                color=color,
                linestyle=l_style,
                linewidth=1.8,
                capsize=3,
                capthick=1.2,
                elinewidth=1.0,
                alpha=0.9,
            )
        elif current_as_stem:
            markerline, stemlines, baseline = ax.stem(
                curr_x, curr_y, linefmt=color, basefmt=" ", label=final_labels[i]
            )
            plt.setp(markerline, marker="o", markersize=4, color=color)
            plt.setp(stemlines, linewidth=1.2, color=color, linestyle=l_style)
        else:
            ax.plot(
                curr_x,
                curr_y,
                label=final_labels[i],
                lw=1.8,
                color=color,
                linestyle=l_style,
            )

    # --- Step 4: Final Formatting and Plot Limits ---
    # Apply logarithmic scales if specified
    if log_scale:
        log_x, log_y = log_scale
        if log_x:
            ax.set_xscale("log")
        if log_y:
            ax.set_yscale("log")

    if limits:
        x_lim, y_lim = limits
        if x_lim is not None:
            ax.set_xlim(x_lim)
        if y_lim is not None:
            ax.set_ylim(y_lim)

    if title:
        ax.set_title(title, fontsize=12)

    ax.set_xlabel(xlabel if xlabel else ("Samples (n)" if x is None else ""))
    if ylabel:
        ax.set_ylabel(ylabel)

    # Configure grid: major lines solid gray, minor lines dotted
    ax.grid(True, which="major", color="gray", linestyle="-", alpha=0.4)
    ax.grid(True, which="minor", color="gray", linestyle=":", alpha=0.2)
    ax.minorticks_on()

    # Handle legend positioning dynamically
    if isinstance(legend_pos, tuple):
        ax.legend(
            loc="upper left",
            bbox_to_anchor=legend_pos,
            ncol=ncol,
            frameon=True,
            shadow=True,
            fontsize=9,
        )
    else:
        ax.legend(loc=legend_pos, ncol=ncol, frameon=True, shadow=True, fontsize=10)

    # Use bbox_inches='tight' to ensure external legends are not cut off during save
    if save_name:
        plt.savefig(save_name, bbox_inches="tight")

    plt.show()


def plot_dtft_analysis(
    nu_vec: np.ndarray,
    spectrums: Union[np.ndarray, List[np.ndarray]],
    *,
    labels: Optional[Union[str, List[str]]] = None,
    colors: Optional[Union[str, List[str]]] = None,
    linestyles: Optional[Union[str, List[str]]] = None,
    limits: Optional[
        Tuple[Optional[Tuple[float, float]], Optional[Tuple[float, float]]]
    ] = None,
    title: Optional[str] = None,
    plot_phase: bool = False,
    separate_axes: bool = False,
    as_stem: Union[bool, List[bool]] = False,
    use_db: bool = False,
    legend_pos: Union[str, Tuple[float, float]] = "best",
    ncol: int = 1,
    figsize: Optional[Tuple[float, float]] = None,
) -> None:
    """
    Visualizes the magnitude and phase spectrums of discrete-time signals.

    Parameters
    ----------
    - nu_vec : (N,) ndarray
        Vector of normalized frequencies (typically from -0.5 to 0.5 or 0 to 1).
    - spectrums : (N,) ndarray or List[(N,) ndarray]
        Complex spectrum values corresponding to the frequencies.
    - labels : str or List[str], optional
        Signal labels for the legend.
    - colors : str or List[str], optional
        Colors for lines or markers.
    - linestyles : str or List[str], optional
        Styles for the plot lines.
    - limits : Tuple[Optional[Tuple[float, float]], Optional[Tuple[float, float]]], optional
        Axes limits formatted as ((freq_min, freq_max), (amp_min, amp_max)).
        Note that Y-limits only apply to the magnitude plot.
    - title : str, optional
        Overall title for the figure.
    - plot_phase : bool, optional
        If True, creates an additional subplot/axis for the unwrapped phase spectrum.
    - separate_axes : bool, optional
        If True, renders each signal in its own distinct row of subplots.
    - as_stem : bool or List[bool], optional
        If True, visualizes the spectrum as discrete samples using a stem plot.
    - use_db : bool, optional
        Converts the magnitude to decibels using 20 * log10(|X|).
    - legend_pos : str or Tuple[float, float], optional
        Position of the legend, either as a location string or a coordinate tuple.
    - ncol : int, optional
        Number of columns for the legend layout. Defaults to 1.
    - figsize : Tuple[float, float], optional
        Figure dimensions. Defaults to automatic calculation based on subplot count.

    Returns
    -------
    - None : None
        Modifies and displays the active matplotlib figure.

    Notes
    -----
    • *Mathematical foundation*
    - Magnitude: |X(ν)|
    - Magnitude in dB: 20 * log10(|X(ν)|)
    - Phase: arg(X(ν)) (unwrapped to avoid 2π discontinuities)

    • *Algorithm workflow*
    1. Normalize complex spectrums into a unified list structure.
    2. Initialize visual parameters (colors, styles, labels).
    3. Calculate geometric layout for subplots depending on phase and separation flags.
    4. Compute magnitudes (linear or dB) and phase arrays.
    5. Render characteristics iteratively and apply axis limit configurations.
    """
    plt.close()

    # --- Step 1: Spectrums Normalization ---
    if isinstance(spectrums, np.ndarray):
        work_spectrums = (
            [spectrums] if spectrums.ndim == 1 else [row for row in spectrums]
        )  # shape of elements: (N,)
    else:
        work_spectrums = list(spectrums)

    num_signals = len(work_spectrums)
    stem_flags = [as_stem] * num_signals if isinstance(as_stem, bool) else list(as_stem)

    # --- Step 2: Style Initialization ---
    if colors is None:
        if num_signals <= 10:
            # Standard property cycle
            style_colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        elif num_signals <= 20:
            # Extended qualitative palette
            style_colors = plt.get_cmap("tab20")(np.linspace(0, 1, num_signals))
        else:
            # Universal palette for a large number of distinct lines
            style_colors = plt.get_cmap("turbo")(np.linspace(0, 1, num_signals))
    else:
        style_colors = [colors] if isinstance(colors, str) else list(colors)

    style_lines = (
        ["-"]
        if linestyles is None
        else ([linestyles] if isinstance(linestyles, str) else list(linestyles))
    )
    final_labels = (
        ([labels] if isinstance(labels, str) else list(labels))
        if labels
        else [f"Signal {i+1}" for i in range(num_signals)]
    )

    # --- Step 3: Layout Geometry Calculation ---
    # Require 2 rows per signal/group if phase plot is requested
    row_multiplier = 2 if plot_phase else 1
    nrows = num_signals * row_multiplier if separate_axes else row_multiplier

    if figsize is None:
        figsize = (10, 3.5 * nrows)

    fig, axes = plt.subplots(nrows, 1, figsize=figsize, sharex=True, squeeze=False)
    axes_f = axes.flatten()

    # --- Step 4: Characteristics Calculation and Rendering ---
    for i in range(num_signals):
        spec_val = work_spectrums[i]  # shape: (N,)
        lbl = final_labels[i % len(final_labels)]
        color = style_colors[i % len(style_colors)]
        l_style = style_lines[i % len(style_lines)]
        is_stem_mode = stem_flags[i % len(stem_flags)]

        # Determine target axes for the current signal
        ax_mag = axes_f[i * row_multiplier] if separate_axes else axes_f[0]

        # --- Step 4a: Magnitude Calculation ---
        magnitude = np.abs(spec_val)  # shape: (N,)
        if use_db:
            magnitude = 20 * np.log10(magnitude + 1e-12)  # shape: (N,)

        if is_stem_mode:
            markerline, stemlines, _ = ax_mag.stem(
                nu_vec, magnitude, linefmt=color, basefmt=" ", label=lbl
            )
            plt.setp(markerline, markersize=3, color=color)
            plt.setp(stemlines, linewidth=1.0, color=color, linestyle=l_style)
        else:
            ax_mag.plot(
                nu_vec, magnitude, label=lbl, color=color, linestyle=l_style, lw=1.8
            )

        # --- Step 4b: Phase Calculation and Rendering ---
        if plot_phase:
            ax_phase = axes_f[i * row_multiplier + 1] if separate_axes else axes_f[1]
            # Use unwrap to eliminate 2*pi phase jumps
            phase_vals = np.unwrap(np.angle(spec_val))  # shape: (N,)
            ax_phase.plot(
                nu_vec, phase_vals, label=lbl, color=color, linestyle=l_style, lw=1.5
            )

    # --- Step 5: Final Formatting and Limits Application ---
    for j, ax in enumerate(axes_f):
        if not ax.get_lines() and not ax.collections:
            continue

        ax.grid(True, which="both", linestyle="--", alpha=0.3)
        ax.minorticks_on()

        if isinstance(legend_pos, tuple):
            ax.legend(
                loc="upper left",
                bbox_to_anchor=legend_pos,
                ncol=ncol,
                frameon=True,
                shadow=True,
                fontsize=9,
            )
        else:
            ax.legend(loc=legend_pos, ncol=ncol, frameon=True, shadow=True, fontsize=9)

        # Determine if the current axis represents phase
        is_phase_ax = plot_phase and (
            j % row_multiplier != 0 if separate_axes else j % 2 != 0
        )

        if limits:
            x_lim, y_lim = limits
            if x_lim is not None:
                ax.set_xlim(x_lim)
            # Apply Y limits exclusively to the magnitude plot
            if y_lim is not None and not is_phase_ax:
                ax.set_ylim(y_lim)

        ax.set_ylabel(
            r"$\arg(X)$ [рад]"
            if is_phase_ax
            else (r"$|X|_{dB}$" if use_db else r"$|X|$")
        )

    if title:
        fig.suptitle(title, y=1.01)
    axes_f[-1].set_xlabel(r"Нормированная частота $\nu$")
    plt.tight_layout()
    plt.show()


def compute_dtft_analysis(
    signals: Union[np.ndarray, Iterable[np.ndarray]],
    *,
    labels: Optional[Union[str, List[str]]] = None,
    colors: Optional[Union[str, List[str]]] = None,
    linestyles: Optional[Union[str, List[str]]] = None,
    limits: Optional[
        Tuple[Optional[Tuple[float, float]], Optional[Tuple[float, float]]]
    ] = None,
    title: Optional[str] = None,
    dtft_points: int = 2048,
    plot_results: bool = False,
    plot_phase: bool = False,
    separate_axes: bool = False,
    should_shift: bool = True,
    use_db: bool = False,
    as_stem: Union[bool, List[bool]] = False,
    legend_pos: Union[str, Tuple[float, float]] = "best",
    ncol: int = 1,
    figsize: Optional[Tuple[float, float]] = None,
) -> Tuple[np.ndarray, Union[np.ndarray, List[np.ndarray]]]:
    """
    Computes the Discrete-Time Fourier Transform (DTFT) of one or multiple signals
    and optionally visualizes the results.

    Parameters
    ----------
    - signals : (M,) ndarray or Iterable[(M,) ndarray]
        Input time-domain signals.
    - labels : str or List[str], optional
        Signal labels for the visualization legend.
    - colors : str or List[str], optional
        Colors for plot lines or markers.
    - linestyles : str or List[str], optional
        Styles for the plot lines.
    - limits : Tuple[Optional[Tuple[float, float]], Optional[Tuple[float, float]]], optional
        Axes limits formatted as ((freq_min, freq_max), (amp_min, amp_max)).
    - title : str, optional
        Overall title for the figure.
    - dtft_points : int, optional
        Number of points N for the FFT computation. Defines the frequency resolution. Defaults to 2048.
    - plot_results : bool, optional
        Flag to automatically trigger the `plot_dtft_analysis` function. Defaults to False.
    - plot_phase : bool, optional
        If True, creates an additional subplot for the unwrapped phase spectrum (if plotted).
    - separate_axes : bool, optional
        If True, renders each signal in its own distinct row of subplots (if plotted).
    - should_shift : bool, optional
        If True, applies fftshift to center the zero frequency in the array/plot. Defaults to True.
    - use_db : bool, optional
        Converts the magnitude to decibels using 20 * log10(|X|) (if plotted).
    - as_stem : bool or List[bool], optional
        If True, visualizes the spectrum as discrete samples using a stem plot.
    - legend_pos : str or Tuple[float, float], optional
        Position of the legend, either as a location string or a coordinate tuple.
    - ncol : int, optional
        Number of columns for the legend layout. Defaults to 1.
    - figsize : Tuple[float, float], optional
        Figure dimensions for visualization.

    Returns
    -------
    - nu_vec : (dtft_points,) ndarray
        Vector of normalized frequencies.
    - spectrums : (dtft_points,) ndarray or List[(dtft_points,) ndarray]
        Computed complex spectrum values. Returns a single array if the input was a single array,
        otherwise returns a list of arrays.

    Notes
    -----
    • *Mathematical foundation*
    - The DTFT is approximated using an N-point Fast Fourier Transform (FFT):
      X(ν) ≈ ∑(n) x[n] * exp(-j * 2π * ν * n)
    - Zero-padding is automatically applied if the signal length is less than `dtft_points`.

    • *Algorithm workflow*
    1. Normalize input signals into a unified list structure.
    2. Generate the normalized frequency grid (optionally shifted to center 0).
    3. Compute the N-point FFT for each signal.
    4. Pass the calculated data to the visualizer if requested.
    """

    # --- Step 1: Input Data Normalization ---
    # Convert input to a unified list format for standardized iteration
    if isinstance(signals, np.ndarray) and signals.ndim == 1:
        work_signals = [signals]
        is_single_input = True
    else:
        work_signals = [np.atleast_1d(s) for s in signals]
        is_single_input = False

    # --- Step 2: Frequency Grid Generation ---
    nu_vec = np.fft.fftfreq(dtft_points)  # shape: (dtft_points,)
    if should_shift:
        nu_vec = np.fft.fftshift(nu_vec)  # shape: (dtft_points,)

    # --- Step 3: FFT Computation ---
    spectrums = []
    for sig in work_signals:
        # Compute N-point FFT (automatically applies zero-padding if len(sig) < dtft_points)
        spec = np.fft.fft(sig, n=dtft_points)  # shape: (dtft_points,)
        if should_shift:
            spec = np.fft.fftshift(spec)  # shape: (dtft_points,)
        spectrums.append(spec)

    # --- Step 4: Optional Visualization ---
    # Delegate rendering to the plotting function if the flag is active
    if plot_results:
        # Ensure plot_dtft_analysis is defined and imported in the scope
        plot_dtft_analysis(
            nu_vec=nu_vec,
            spectrums=spectrums,
            labels=labels,
            colors=colors,
            linestyles=linestyles,
            limits=limits,
            title=title,
            plot_phase=plot_phase,
            separate_axes=separate_axes,
            use_db=use_db,
            as_stem=as_stem,
            legend_pos=legend_pos,
            ncol=ncol,
            figsize=figsize,
        )

    return nu_vec, (spectrums[0] if is_single_input else spectrums)


def plot_phase_portrait(
    y1_data: Union[np.ndarray, List[np.ndarray]],
    y2_data: Union[np.ndarray, List[np.ndarray]],
    *,
    figsize: Tuple[int, int] = (8, 8),
    labels: Optional[Union[str, List[str]]] = None,
    colors: Optional[Union[str, List[str]]] = None,
    linestyles: Optional[Union[str, List[str]]] = None,
    limits: Optional[
        Tuple[Optional[Tuple[float, float]], Optional[Tuple[float, float]]]
    ] = None,
    log_scale: Optional[Tuple[bool, bool]] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    mark_start: bool = True,
    legend_pos: Union[str, Tuple[float, float]] = "best",
    ncol: int = 1,
    save_name: Optional[str] = None,
) -> None:
    """
    Plots a 2D phase portrait for one or multiple trajectories.

    Parameters
    ----------
    - y1_data : (K,) ndarray or List[(K,) ndarray]
        Data for the horizontal axis (e.g., coordinate or first state variable).
    - y2_data : (K,) ndarray or List[(K,) ndarray]
        Data for the vertical axis (e.g., momentum or second state variable).
    - figsize : Tuple[int, int], optional
        Figure dimensions in inches. Defaults to (8, 8).
    - labels : str or List[str], optional
        Labels for the legend.
    - colors : str or List[str], optional
        Colors for the trajectories.
    - linestyles : str or List[str], optional
        Line styles (e.g., '-', '--', ':').
    - limits : Tuple[Optional[Tuple[float, float]], Optional[Tuple[float, float]]], optional
        Axis limits in format ((xmin, xmax), (ymin, ymax)).
    - log_scale : Tuple[bool, bool], optional
        Toggle log scale for (x_axis, y_axis).
    - title : str, optional
        Plot title.
    - xlabel : str, optional
        Horizontal axis label. Defaults to "y₁".
    - ylabel : str, optional
        Vertical axis label. Defaults to "y₂".
    - mark_start : bool, optional
        If True, marks the initial point (y1[0], y2[0]) with a circle. Defaults to True.
    - legend_pos : str or Tuple[float, float], optional
        Position of the legend. Use a tuple (e.g., (1.02, 1)) to place it outside.
    - ncol : int, optional
        Number of columns in the legend. Defaults to 1.
    - save_name : str, optional
        Path to save the resulting figure.

    Returns
    -------
    - None : None
        The function modifies the active matplotlib figure and returns nothing.

    Notes
    -----
    • *Algorithm workflow*
    1. Normalize input data into lists of arrays for consistent iteration.
    2. Configure visual styles (colors, labels, markers).
    3. Loop through trajectories and plot curves on a single axis.
    4. Apply formatting (log scales, limits, grid) and export.
    """
    plt.close()

    # --- Step 1: Input Data Normalization ---
    # Convert single arrays to lists for uniform processing
    y1_list = (
        [y1_data]
        if isinstance(y1_data, np.ndarray) and y1_data.ndim == 1
        else list(y1_data)
    )
    y2_list = (
        [y2_data]
        if isinstance(y2_data, np.ndarray) and y2_data.ndim == 1
        else list(y2_data)
    )
    num_signals = len(y1_list)

    # --- Step 2: Style Preparation ---
    if colors is None:
        if num_signals <= 10:
            # Standard property cycle
            style_colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        elif num_signals <= 20:
            # Extended qualitative palette
            style_colors = plt.get_cmap("tab20")(np.linspace(0, 1, num_signals))
        else:
            # Universal palette for a large number of distinct lines
            # 'turbo' is a modern, highly distinguishable colormap
            style_colors = plt.get_cmap("turbo")(np.linspace(0, 1, num_signals))
    else:
        style_colors = [colors] if isinstance(colors, str) else list(colors)

    style_lines = (
        ["-"]
        if linestyles is None
        else ([linestyles] if isinstance(linestyles, str) else list(linestyles))
    )
    final_labels = (
        labels
        if isinstance(labels, list)
        else (
            [labels] * num_signals
            if labels
            else [f"Traj {i+1}" for i in range(num_signals)]
        )
    )

    # --- Step 3: Plotting Trajectories ---
    fig, ax = plt.subplots(figsize=figsize)

    for i in range(num_signals):
        curr_y1, curr_y2 = y1_list[i], y2_list[i]  # shape: (K,)
        color = style_colors[i % len(style_colors)]
        l_style = style_lines[i % len(style_lines)]

        # Plot phase curve
        ax.plot(
            curr_y1,
            curr_y2,
            label=final_labels[i],
            lw=1.8,
            color=color,
            linestyle=l_style,
            alpha=0.9,
        )

        # Mark initial state
        if mark_start and len(curr_y1) > 0:
            ax.plot(
                curr_y1[0],
                curr_y2[0],
                marker="o",
                markersize=6,
                color=color,
                markeredgecolor="black",
                linestyle="None",
            )  # shape: scalar

    # --- Step 4: Formatting & Scales ---
    if log_scale:
        if log_scale[0]:
            ax.set_xscale("log")
        if log_scale[1]:
            ax.set_yscale("log")

    if limits:
        x_lim, y_lim = limits
        if x_lim is not None:
            ax.set_xlim(x_lim)
        if y_lim is not None:
            ax.set_ylim(y_lim)

    if title:
        ax.set_title(title, fontsize=12)
    ax.set_xlabel(xlabel if xlabel else "y₁")
    ax.set_ylabel(ylabel if ylabel else "y₂")

    ax.grid(True, which="both", color="gray", linestyle="-", alpha=0.3)

    if isinstance(legend_pos, tuple):
        ax.legend(
            loc="upper left",
            bbox_to_anchor=legend_pos,
            ncol=ncol,
            frameon=True,
            shadow=True,
            fontsize=9,
        )
    else:
        ax.legend(loc=legend_pos, ncol=ncol, frameon=True, shadow=True)

    if save_name:
        plt.savefig(save_name, bbox_inches="tight")

    plt.show()


def plot_convergence(
    h_vec: Union[np.ndarray, List[float]],
    error_data: Union[np.ndarray, List[np.ndarray]],
    *,
    reference_orders: Optional[
        Union[int, float, List[Optional[Union[int, float]]]]
    ] = None,
    figsize: Tuple[int, int] = (10, 6),
    labels: Optional[Union[str, List[str]]] = None,
    colors: Optional[Union[str, List[str]]] = None,
    limits: Optional[
        Tuple[Optional[Tuple[float, float]], Optional[Tuple[float, float]]]
    ] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    legend_pos: Union[str, Tuple[float, float]] = "best",
    ncol: int = 1,
    save_name: Optional[str] = None,
) -> None:
    """
    Plots error convergence curves with individual reference slopes for each method.

    Parameters
    ----------
    - h_vec : (M,) ndarray or List[float]
        Vector of integration step sizes.
    - error_data : (M,) ndarray or List[(M,) ndarray]
        Global error values (e.g., ||y_true - y_num||) for one or more methods.
    - reference_orders : int, float, or List[Optional[Union[int, float]]], optional
        Theoretical convergence orders p. If a list is provided, each element
        corresponds to a method in `error_data`.
    - figsize : Tuple[int, int], optional
        Figure dimensions (width, height) in inches. Defaults to (10, 6).
    - labels : str or List[str], optional
        Legend labels for each numerical method.
    - colors : str or List[str], optional
        Custom color sequence for the plots.
    - limits : Tuple[Optional[Tuple[float, float]], Optional[Tuple[float, float]]], optional
        Manual axis limits in the format ((xmin, xmax), (ymin, ymax)).
    - title : str, optional
        Plot title.
    - xlabel : str, optional
        Label for the X-axis.
    - ylabel : str, optional
        Label for the Y-axis.
    - legend_pos : str or Tuple[float, float], optional
        Legend placement string or relative coordinate tuple. Defaults to "best".
    - ncol : int, optional
        Number of columns in the legend. Defaults to 1.
    - save_name : str, optional
        If provided, saves the figure to the specified file path.

    Returns
    -------
    - None : None
        The function modifies the active matplotlib figure and returns nothing.

    Notes
    -----
    • *Mathematical foundation*
    - Error model: E(h) ≈ C * hᵖ
    - Reference lines are anchored to the local minimum of each method to
      illustrate the slope in the asymptotic convergence region.

    • *Algorithm workflow*
    1. Normalize inputs into NumPy arrays and lists of signals.
    2. Iterate through each method to plot the experimental error data.
    3. Calculate a local constant C for each reference order and plot dashed lines.
    4. Configure log-log scales, grid, and legend.
    """
    plt.close()

    # --- Step 1: Data Normalization ---
    h_arr = np.asarray(h_vec, dtype=np.float64)  # shape: (M,)

    # Ensure error_data is a list of arrays for uniform iteration
    err_list = (
        [error_data]
        if isinstance(error_data, np.ndarray) and error_data.ndim == 1
        else list(error_data)
    )
    num_signals = len(err_list)

    # --- Step 2: Visual Style Setup ---
    if colors is None:
        if num_signals <= 10:
            # Standard property cycle
            style_colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        elif num_signals <= 20:
            # Extended qualitative palette
            style_colors = plt.get_cmap("tab20")(np.linspace(0, 1, num_signals))
        else:
            # Universal palette for a large number of distinct lines
            # 'turbo' is a modern, highly distinguishable colormap
            style_colors = plt.get_cmap("turbo")(np.linspace(0, 1, num_signals))
    else:
        style_colors = [colors] if isinstance(colors, str) else list(colors)

    if labels is None:
        final_labels = [f"Method {i+1}" for i in range(num_signals)]
    else:
        final_labels = labels if isinstance(labels, list) else [labels]

    # --- Step 3: Main Plotting (Log-Log) ---
    fig, ax = plt.subplots(figsize=figsize)

    for i in range(num_signals):
        color = style_colors[i % len(style_colors)]
        curr_errors = np.asarray(err_list[i])  # shape: (M,)

        # Plot experimental error points and lines
        ax.loglog(
            h_arr,
            curr_errors,
            label=final_labels[i],
            marker="o",
            markersize=5,
            lw=1.8,
            color=color,
        )

        # --- Step 4: Individual Reference Lines O(hᵖ) ---
        if reference_orders is not None:
            # Cast orders to list for indexed access
            orders = (
                [reference_orders]
                if isinstance(reference_orders, (int, float))
                else list(reference_orders)
            )

            # Check if an order is provided for the current method index
            if i < len(orders) and orders[i] is not None:
                p_order = orders[i]

                # Anchor to the local minimum to show slope in the most accurate region
                best_idx = np.argmin(curr_errors)  # shape: scalar
                base_h = h_arr[best_idx]  # shape: scalar
                base_err = curr_errors[best_idx]  # shape: scalar

                # Calculate normalization constant C = E / hᵖ
                c_const = base_err / (base_h**p_order)  # shape: scalar

                # Plot dashed reference line using the method's color
                # Theoretical line: y = C * hᵖ
                ax.loglog(
                    h_arr,
                    c_const * (h_arr**p_order),  # shape: (M,)
                    linestyle="--",
                    color=color,
                    lw=1.2,
                    alpha=0.6,
                    label=rf"Ref O(h^{p_order})",
                )

    # --- Step 5: Formatting & Grid ---
    if limits:
        x_lim, y_lim = limits
        if x_lim is not None:
            ax.set_xlim(x_lim)
        if y_lim is not None:
            ax.set_ylim(y_lim)

    ax.set_title(title if title else "Convergence Analysis (Global Error vs Step Size)")
    ax.set_xlabel(xlabel if xlabel else "Step size (h)")
    ax.set_ylabel(ylabel if ylabel else "Global Error ||y_true - y_num||")

    # Enable grid for both major and minor ticks (critical for log plots)
    ax.grid(True, which="both", linestyle="--", alpha=0.4)

    if isinstance(legend_pos, tuple):
        ax.legend(
            loc="upper left",
            bbox_to_anchor=legend_pos,
            ncol=ncol,
            frameon=True,
            shadow=True,
            fontsize=9,
        )
    else:
        ax.legend(loc=legend_pos, ncol=ncol, frameon=True, shadow=True, fontsize=9)

    if save_name:
        plt.savefig(save_name, bbox_inches="tight")

    plt.show()
