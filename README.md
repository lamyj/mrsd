# mrsd: a toolkit to generate MR sequence diagrams

*mrsd* is a Python toolkit to generate MR sequence diagrams, as shown below for the basic [FLASH](https://onlinelibrary.wiley.com/doi/10.1002/mrm.1910030217) sequence.

![FLASH sequence diagram generated with mrsd](flash.png)

*mrsd* is based on [Matplotlib](https://matplotlib.org/) and additionally requires [numpy](https://numpy.org/). The code which generated the previous diagram is available in the *examples* direction, and an excerpt is shown below.

```python
figure, plot = matplotlib.pyplot.subplots()
diagram = mrsd.Diagram(
    plot, ["RF", "$G_{slice}$", "$G_{phase}$", "$G_{readout}$", "Signal"])

# Slice-selective pulse of the first TR
diagram.sinc_pulse("RF", 0, RF_duration, 1)
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
diagram.readout("Signal", *readout, +1)
diagram.idle(["RF", "$G_{slice}$", "$G_{phase}$"], *readout)

# Idle until end of TR
diagram.idle_all(readout[1], RF[1][0])

# Start of next TR
diagram.sinc_pulse("RF", TR, RF_duration, 1)
diagram.gradient("$G_{slice}$", *RF[1], selection)
diagram.idle(["$G_{phase}$", "$G_{readout}$", "Signal"], *RF[1])
diagram.idle_all(TR+RF_duration/2, TR+RF_duration)

# Add annotations: flip angles and TE/TR intervals
diagram.annotate("RF", 0.2, r"$\alpha$", 1)
diagram.annotate("RF", TR+0.2, r"$\alpha$", 1)
diagram.interval(0, TE, -1.5, "TE", 10)
diagram.interval(0, TR, -2.5, "TR", 10)
```
