import matplotlib.pyplot
import mrsd

figure, plot = matplotlib.pyplot.subplots(figsize=(4,4), tight_layout=True)
diagram = mrsd.Diagram(
    plot, ["RF", "$G_{slice}$", "$G_{phase}$", "$G_{readout}$", "Signal"])

figure.savefig("empty.png")

#########################
# Slice-selective pulse #
#########################

# Add events via classes

pulse = mrsd.RFPulse(2, 1, center=0)
slice_selection = mrsd.Gradient(pulse.duration, 0.5, center=pulse.center)

diagram.add("RF", pulse)
diagram.add("$G_{slice}$", slice_selection)

[x.remove() for x in (pulse, slice_selection)]

# Add events via individual Diagram functions

pulse = diagram.rf_pulse("RF", 2, 1, center=0)
slice_selection = diagram.gradient(
    "$G_{slice}$", pulse.duration, 0.5, center=pulse.center)

[x.remove() for x in (pulse, slice_selection)]

# Add events via convenience function

pulse, slice_selection = diagram.selective_pulse(
    "RF", "$G_{slice}$", 2, gradient_amplitude=0.5, ramp=0.1, center=0)

figure.savefig("pulse.png")

###########
# Readout #
###########

TE = 4
d_readout = 2

adc = mrsd.ADC(d_readout, center=TE, ec="0.5")
echo = mrsd.Echo(d_readout, 1, center=adc.center)
readout = mrsd.Gradient(d_readout, 1, ramp=0.1, center=adc.center)

diagram.add("Signal", adc)
diagram.add("Signal", echo)
diagram.add("$G_{readout}$", readout)

[x.remove() for x in (adc, echo, readout)]

adc = diagram.adc("Signal", d_readout, center=TE, ec="0.5")
echo = diagram.echo("Signal", d_readout, 1, center=adc.center)
readout = diagram.gradient(
    "$G_{readout}$", d_readout, 1, ramp=0.1, center=adc.center)

[x.remove() for x in (adc, echo, readout)]

adc, echo, readout = diagram.readout(
    "Signal", "$G_{readout}$", d_readout, ramp=0.1, center=TE,
    adc_kwargs={"ec": "0.5"})

figure.savefig("readout.png")

######################
# Encoding Gradients #
######################

d_encoding = 1

phase_encoding = mrsd.MultiGradient(d_encoding, 1, 0.1, end=readout.begin)
diagram.add("$G_{phase}$", phase_encoding)

phase_encoding.remove()

diagram.multi_gradient("$G_{phase}$", d_encoding, 1, 0.1, end=readout.begin)

readout_prephasing = readout.adapt(d_encoding, -0.5, 0.1, end=readout.begin)
diagram.add("$G_{readout}$", readout_prephasing)

diagram.add(
    "$G_{slice}$",
    slice_selection.adapt(d_encoding, -0.5, 0.1, end=readout.begin))

figure.savefig("encoding.png")

##########################
# Annotations and Copies #
##########################

TR = 10

diagram.interval(0, TE, -1.5, "TE")
diagram.interval(0, TR, -2.5, "TR")

diagram.annotate("RF", 0.2, 1, r"$\alpha$")
diagram.annotate("$G_{phase}$", phase_encoding.end, 0.5, r"$\uparrow$")

import copy

diagram.add("RF", copy.copy(pulse).move(TR))
diagram.add("$G_{slice}$", copy.copy(slice_selection).move(TR))
diagram.annotate("RF", TR+0.2, 1, r"$\alpha$")

figure.set_figwidth(6)
figure.savefig("flash.png")
