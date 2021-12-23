import numpy

from .diagram import Diagram

def scale_amplitudes(*args):
    max_amplitude = numpy.max(numpy.abs([a for d,a in args]))
    scaling = 1/max_amplitude
    return [a * scaling for d,a in args]
