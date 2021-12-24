import matplotlib.pyplot
import numpy

import mrsd

# Define sequence parameters: echo time, train length, and durations of pulses,
# encoding, and readout.
TE = 8
train_length = 5
d_pulse, d_encoding, d_readout = 1, 1, 2

# Define time intervals
echoes = TE*numpy.arange(1, 1+train_length)
pulses = [mrsd.interval(x, d_pulse) for x in [0, *(echoes-TE/2)]]
encoding = pulses[0][1], pulses[0][1]+d_encoding
readouts = [mrsd.interval(x, d_readout) for x in echoes]

# Compute slice-selection and readout gradient pairs
G_slice = mrsd.gradient_pair(+1*d_pulse, -0.5, d_pulse, d_encoding)
G_readout = mrsd.gradient_pair(+1*d_readout, -0.5, d_readout, d_encoding)

# Create the underlying Matplotlib objects and the diagram
matplotlib.pyplot.rcParams["lines.linewidth"] = 1
figure, plot = matplotlib.pyplot.subplots()
diagram = mrsd.Diagram(
    plot, ["RF", "$G_{slice}$", "$G_{phase}$", "$G_{readout}$", "Signal"])

# Excitation pulse
diagram.sinc_pulse("RF", *pulses[0], 0.5)
diagram.gradient("$G_{slice}$", *pulses[0], G_slice[0])
diagram.idle(["$G_{phase}$", "$G_{readout}$", "Signal"], *pulses[0])

# Encoding: rewind slice-selection gradient, run phase gradient, prephase
# read-out gradient
diagram.gradient("$G_{slice}$", *encoding, G_slice[1])
diagram.stepped_gradient("$G_{phase}$", *encoding, 1)
diagram.gradient("$G_{readout}$", *encoding, G_readout[1])
diagram.idle(["RF", "Signal"], *encoding)

diagram.idle_all(encoding[1], pulses[1][0])

for i in range(train_length):
    diagram.sinc_pulse("RF", *pulses[i+1], 1)
    diagram.idle(
        ["$G_{slice}$", "$G_{phase}$", "$G_{readout}$", "Signal"], *pulses[i+1])
    
    diagram.idle_all(pulses[i+1][1], readouts[i][0])
    
    diagram.gradient("$G_{readout}$", *readouts[i], G_readout[0])
    diagram.echo("Signal", *readouts[i], numpy.exp(-i/2))
    diagram.idle(["RF", "$G_{slice}$", "$G_{phase}$", "Signal"], *readouts[i])
    
    if i != train_length-1:
        diagram.idle_all(readouts[i][1], pulses[i+2][0])

# Add annotations: flip angles and TE-related intervals
diagram.annotate("RF", pulses[0][1], r"90°", 1)
diagram.annotate("RF", pulses[1][1], r"180°", 1)
diagram.interval(0, TE/2, -1.5, "TE/2")
diagram.interval(0, TE, -2.5, "TE")
diagram.interval(TE, 2*TE, -2.5, "TE")

# Add effect of T2 relaxation
x = numpy.linspace(numpy.mean(echoes[0]), numpy.mean(echoes[-1]), 100)
y = numpy.exp(-numpy.linspace(0, train_length-1, 100)/2)
plot.plot(x, y, "C0")
plot.annotate(r"$\exp(-t/T_2)$", (numpy.mean(echoes[-2]), 0.5), color="C0")

figure.tight_layout()
matplotlib.pyplot.show()
