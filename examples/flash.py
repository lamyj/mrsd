""" Draw the sequence diagram of the FLASH sequence. Adapted from "FLASH
    imaging. Rapid NMR imaging using low flip-angle pulses", Haase et al.,
    Journal of Magnetic Resonance, 67(2), pp. 258-266, 1986.
"""

import copy

import matplotlib.pyplot
import mrsd

# Define sequence parameters (arbitrary units): echo and repetition times,
# durations of ramp, pulses, encoding and readout
TE, TR = 4, 10
d_ramp, d_pulse, d_encoding, d_readout = 0.1, 1, 1, 2

# Create the underlying Matplotlib objects and the diagram
figure, plot = matplotlib.pyplot.subplots(tight_layout=True)
diagram = mrsd.Diagram(
    plot, ["RF", "$G_{slice}$", "$G_{phase}$", "$G_{readout}$", "Signal"])

# Slice-selective pulse of the first TR
excitation, slice_selection = diagram.selective_pulse(
    "RF", "$G_{slice}$", d_pulse, ramp=d_ramp, center=0)

# Readout, centered on TE
adc, echo, readout = diagram.readout(
    "Signal", "$G_{readout}$", d_readout, ramp=d_ramp, center=TE,
    adc_kwargs={"ec": "0.5"})

# Encoding: rewind slice-selection gradient, run phase gradient, prephase
# read-out gradient
diagram.add(
    "$G_{slice}$",
    slice_selection.adapt(d_encoding, -0.5, d_ramp, end=readout.begin))
diagram.multi_gradient(
    "$G_{phase}$", d_encoding, 1, d_ramp, end=readout.begin)
diagram.add(
    "$G_{readout}$", readout.adapt(d_encoding, -0.5, d_ramp, end=readout.begin))

# Start of next TR
diagram.add("RF", copy.copy(excitation).move(TR))
diagram.add("$G_{slice}$", copy.copy(slice_selection).move(TR))

# Add annotations: flip angles and TE/TR intervals
diagram.annotate("RF", 0.2, 1, r"$\alpha$")
diagram.annotate("RF", TR+0.2, 1, r"$\alpha$")
diagram.interval(0, TE, -1.5, "TE")
diagram.interval(0, TR, -2.5, "TR")

matplotlib.pyplot.show()
