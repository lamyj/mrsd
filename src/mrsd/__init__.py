import numpy

from .diagram import Diagram

def interval(center, span):
    return center-span/2, center+span/2

def scale_amplitudes(*args):
    max_amplitude = numpy.max(numpy.abs([a for d,a in args]))
    scaling = 1/max_amplitude
    return [a * scaling for d,a in args]

def gradient_pair(moment, factor, duration_1, duration_2):
    return scale_amplitudes(
        (duration_1, moment/duration_1), (duration_2, factor*moment/duration_2))
