import copy

import matplotlib.pyplot
import numpy

import mrsd

TE, TR = 8, 20
readout_duration = 1
ramp = 0.2
epi_factor = 7

figure, plot = matplotlib.pyplot.subplots(tight_layout=True)
diagram = mrsd.Diagram(plot, ["RF", "$G_z$", "$G_y$", "$G_x$", "ADC"])

excitation, slice_selection = diagram.selective_pulse(
    "RF", "$G_z$", 1, center=0, ramp=ramp)
diagram.add(
    "$G_z$", slice_selection.adapt(1, -0.5, ramp, begin=slice_selection.end))

polarity = +1
center = epi_factor//2
begin, end = -center, epi_factor-center
for index in range(begin, end):
    t = index*(readout_duration+2*ramp)
    adc, echo, readout = diagram.readout(
        "ADC", "$G_x$", readout_duration, numpy.exp(-numpy.abs(t)/3), polarity,
        ramp, center=TE+t, adc_kwargs={"alpha": 0.5})
    
    if index == begin:
        diagram.gradient("$G_y$", readout_duration, -1, ramp, end=readout.begin)
    if index != end-1:
        diagram.gradient("$G_y$", ramp, +1, 0, begin=adc.end)
    
    polarity *= -1

diagram.add("RF", copy.copy(excitation).move(TR))
diagram.add("$G_z$", copy.copy(slice_selection).move(TR))

diagram.interval(0, TE, -1.5, "TE")
diagram.interval(0, TR, -2, "TR")

matplotlib.pyplot.show()
