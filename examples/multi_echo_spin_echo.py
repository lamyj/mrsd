""" Draw the sequence diagram of a multi-echo gradient echo sequence, with
    bipolar readout gradients.
"""

import copy

import matplotlib.pyplot
import mrsd
import numpy

# Define the tissue and sequence parameters (arbitrary units): T2,
# echo and repetition times, durations of ramp, pulses, encoding and readout,
# length of the echo train
T2 = 10
TE, TR = 10, 40
d_pulse, d_encoding, d_readout, d_ramp = 1, 3, 1, 0.1
train_length = 10

# Create the underlying Matplotlib objects and the diagram
figure, plot = matplotlib.pyplot.subplots(tight_layout=True, figsize=(10,5))
diagram = mrsd.Diagram(plot, ["RF", "$G_z$", "$G_y$", "$G_x$", "Echoes"])

# Add the excitation RF pulse, show the beginning of the next repetition
excitation, excitation_selection = diagram.selective_pulse(
    "RF", "$G_z$", d_pulse, 0.5, 0.5, ramp=d_ramp, center=0)
diagram.annotate("RF", excitation.center+0.2, 1, "90°")
diagram.add("RF", copy.copy(excitation).move(TR))
diagram.add("$G_z$", copy.copy(excitation_selection).move(TR))
diagram.annotate("RF", excitation.center+0.2+TR, 1, "90°")
diagram.interval(0, TR, -2, "TR")

# Add the refocalization RF pulse
refocalization, _ = diagram.selective_pulse(
    "RF", "$G_z$", d_pulse, 1, 0.5, ramp=d_ramp, center=TE/2)
diagram.annotate("RF", refocalization.center+0.2, 1, "180°")
diagram.interval(0, TE/2, -1, "TE/2")

# Add the first echo
echo = diagram.echo("Echoes", d_readout, 1, center=TE)
readout = diagram.gradient("$G_x$", d_readout, 1, d_ramp, center=echo.center)
diagram.interval(0, TE, -1.5, "TE")

# Add the encoding gradients
diagram.add(
    "$G_z$", excitation_selection.adapt(
        d_encoding, -0.5, d_ramp, begin=excitation_selection.end))
diagram.multi_gradient(
    "$G_y$", d_encoding, 0.5, d_ramp, begin=excitation_selection.end)
diagram.add(
    "$G_x$", readout.adapt(
        d_encoding, -0.5, d_ramp, begin=excitation_selection.end))

# Add the other echoes in the train
for echo in range(1, train_length):
    refocalization_selection = diagram.gradient(
        "$G_z$", d_pulse, 0.5, d_ramp, begin=readout.end)
    refocalization = diagram.sinc_pulse(
        "RF", d_pulse, 1, center=refocalization_selection.center)
    diagram.annotate(
        "RF", refocalization.center+0.2, 1, "180°", fontsize=8, color="0.5")
    
    readout = diagram.gradient(
        "$G_x$", d_readout, 1, d_ramp, begin=refocalization_selection.end)
    
    elapsed = readout.center - TE
    echo_amplitude = numpy.exp(-elapsed/T2)
    diagram.echo("Echoes", d_readout, echo_amplitude, center=readout.center)

# Add the T2 decay curve
xs = numpy.linspace(0, readout.end-TE, 100)
ys = numpy.exp(-xs/T2)
plot.plot(xs+TE, ys+diagram.y("Echoes"), color="C0", lw=1)
plot.text(TE+xs[len(xs)//2], 0.5, "$e^{-t/T_2}$", color="C0")

matplotlib.pyplot.show()
