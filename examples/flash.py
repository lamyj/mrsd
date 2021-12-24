import matplotlib.pyplot

import mrsd

# Define sequence parameters (arbitraty units)
TE = 4
TR = 10
RF_duration = 1
encoding_duration = 1
readout_duration = 2

# Compute time intervals
RF = [(t-RF_duration/2, t+RF_duration/2) for t in [0, TR]]
readout = TE-readout_duration/2, TE+readout_duration/2
encoding = readout[0]-encoding_duration, readout[0]

# Compute normalized gradient areas
selection, rewind = mrsd.scale_amplitudes(
    (RF_duration/2, 1),
    (encoding_duration, -1 * RF_duration/2/encoding_duration))
prephasing, dephasing = mrsd.scale_amplitudes(
    (encoding_duration, -1),
    (readout_duration/2, +1 * encoding_duration/(readout_duration/2)))

# Create the underlying Matplotlib objects and the diagram
figure, plot = matplotlib.pyplot.subplots()
diagram = mrsd.Diagram(
    plot, ["RF", "$G_{slice}$", "$G_{phase}$", "$G_{readout}$", "Signal"])

# Slice-selective pulse of the first TR
diagram.sinc_pulse("RF", *RF[0], 1)
diagram.gradient("$G_{slice}$", *RF[0], selection)
diagram.idle(["$G_{phase}$", "$G_{readout}$", "Signal"], *RF[0])

# Dead time until the start of encoding
diagram.idle_all(RF[0][1], encoding[0])

# Encoding: rewind slice-selection gradient, run phase gradient, prephase
# read-out gradient
diagram.gradient("$G_{slice}$", *encoding, rewind)
diagram.stepped_gradient("$G_{phase}$", *encoding, 1)
diagram.gradient("$G_{readout}$", *encoding, prephasing)
diagram.idle(["RF", "Signal"], *encoding)

# Readout, centered on TE
diagram.gradient("$G_{readout}$", *readout, dephasing)
diagram.echo("Signal", *readout, +1)
diagram.idle(["RF", "$G_{slice}$", "$G_{phase}$"], *readout)

# Idle until end of TR
diagram.idle_all(readout[1], RF[1][0])

# Start of next TR
diagram.sinc_pulse("RF", *RF[1], 1)
diagram.gradient("$G_{slice}$", *RF[1], selection)
diagram.idle(["$G_{phase}$", "$G_{readout}$", "Signal"], *RF[1])
diagram.idle_all(TR+RF_duration/2, TR+RF_duration)

# Add annotations: flip angles and TE/TR intervals
diagram.annotate("RF", 0.2, r"$\alpha$", 1)
diagram.annotate("RF", TR+0.2, r"$\alpha$", 1)
diagram.interval(0, TE, -1.5, "TE")
diagram.interval(0, TR, -2.5, "TR")

matplotlib.pyplot.show()
