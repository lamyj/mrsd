import copy

import matplotlib.pyplot
import mrsd
import numpy

figure, plot = matplotlib.pyplot.subplots(tight_layout=True)
diagram = mrsd.Diagram(plot, ["RF", "$G_{RO}$", "Echoes"])

T2_star = 5
TE, TR = 4, 20
d_pulse, d_readout, d_ramp = 0.5, 1, 0.1
train_length = 10

pulse = diagram.hard_pulse("RF", d_pulse, 1, center=0)
diagram.add("RF", copy.copy(pulse).move(TR))
diagram.interval(0, TR, -1.5, "TR")

echo = diagram.echo("Echoes", d_readout, 1, center=TE)
readout = diagram.gradient("$G_{RO}$", d_readout, 1, d_ramp, center=echo.center)
diagram.add(
    "$G_{RO}$", readout.adapt(d_readout, -0.5, d_ramp, end=readout.begin))

figure.savefig("single_echo.png")

for echo in range(1, train_length):
    gradient_amplitude = (-1)**echo
    readout = diagram.gradient(
        "$G_{RO}$", d_readout, gradient_amplitude, ramp=d_ramp,
        begin=readout.end)
    
    elapsed = readout.center - TE
    echo_amplitude = numpy.exp(-elapsed/T2_star)
    diagram.echo("Echoes", d_readout, echo_amplitude, center=readout.center)

figure.savefig("multiecho.png")

xs = numpy.linspace(0, readout.end-TE, 100)
ys = numpy.exp(-xs/T2_star)
plot.plot(xs+TE, ys+diagram.y("Echoes"), color="C0", lw=1)
plot.text(TE+xs[len(xs)//2], 0.5, "$e^{-t/T_2^*}$", color="C0")

figure.savefig("final.png")
