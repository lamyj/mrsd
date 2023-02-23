import numpy

from .event import Event
from .adc import ADC
from .echo import Echo
from .gradient import Gradient
from .multi_gradient import MultiGradient
from .rf_pulse import RFPulse, box_envelope, gaussian_envelope, sinc_envelope

from .diagram import Diagram

def interval(center, span):
    return numpy.array([center-span/2, center+span/2])

def scale_amplitudes(*args):
    max_amplitude = numpy.max(numpy.abs([a for d,a in args]))
    scaling = 1/max_amplitude
    return [a * scaling for d,a in args]

def gradient_pair(moment, factor, duration_1, duration_2):
    return scale_amplitudes(
        (duration_1, moment/duration_1), (duration_2, factor*moment/duration_2))
