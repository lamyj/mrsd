import matplotlib.pyplot

import mrsd

# Define sequence parameters (arbitrary units): echo and repetition times,
# durations of pulses, encoding and readout
TE, TR = 4, 10
d_pulse, d_encoding, d_readout = 1, 1, 2

# Compute time intervals
pulses = [mrsd.interval(t, d_pulse) for t in [0, TR]]
readout = mrsd.interval(TE, d_readout)
encoding = readout[0]-d_encoding, readout[0]

# Compute slice-selection and readout gradient pairs
G_slice = mrsd.gradient_pair(+1*d_pulse, -0.5, d_pulse, d_encoding)
G_readout = mrsd.gradient_pair(+1*d_readout, -0.5, d_readout, d_encoding)

# Create the underlying Matplotlib objects and the diagram
figure, plot = matplotlib.pyplot.subplots()
diagram = mrsd.Diagram(
    plot, ["RF", "$G_{slice}$", "$G_{phase}$", "$G_{readout}$", "Signal"])

# Slice-selective pulse of the first TR
diagram.sinc_pulse("RF", *pulses[0], 1)
diagram.gradient("$G_{slice}$", *pulses[0], G_slice[0])
diagram.idle(["$G_{phase}$", "$G_{readout}$", "Signal"], *pulses[0])

# Dead time until the start of encoding
diagram.idle_all(pulses[0][1], encoding[0])

# Encoding: rewind slice-selection gradient, run phase gradient, prephase
# read-out gradient
diagram.gradient("$G_{slice}$", *encoding, G_slice[1])
diagram.stepped_gradient("$G_{phase}$", *encoding, 1)
diagram.gradient("$G_{readout}$", *encoding, G_readout[1])
diagram.idle(["RF", "Signal"], *encoding)

# Readout, centered on TE
diagram.gradient("$G_{readout}$", *readout, G_readout[0])
diagram.echo("Signal", *readout, +1)
diagram.idle(["RF", "$G_{slice}$", "$G_{phase}$"], *readout)

# Idle until end of TR
diagram.idle_all(readout[1], pulses[1][0])

# Start of next TR
diagram.sinc_pulse("RF", *pulses[1], 1)
diagram.gradient("$G_{slice}$", *pulses[1], G_slice[0])
diagram.idle(["$G_{phase}$", "$G_{readout}$", "Signal"], *pulses[1])

# Add annotations: flip angles and TE/TR intervals
diagram.annotate("RF", 0.2, r"$\alpha$", 1)
diagram.annotate("RF", TR+0.2, r"$\alpha$", 1)
diagram.interval(0, TE, -1.5, "TE")
diagram.interval(0, TR, -2.5, "TR")

matplotlib.pyplot.show()
