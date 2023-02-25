import matplotlib.path
import numpy

from .event import Event

def box_envelope(pulse):
    return (
        [pulse.begin, pulse.begin, pulse.end, pulse.end],
        [0, pulse.amplitude, pulse.amplitude, 0])

def gaussian_envelope(pulse):
    support = numpy.linspace(-1, +1, pulse.points)
    xs = support/(support[-1]-support[0])*(pulse.end-pulse.begin)+pulse.center
    
    ys = pulse.amplitude * numpy.exp(-support**2 / (2*pulse.sd**2))
    
    return xs, ys

def sinc_envelope(pulse):
    support = numpy.linspace(-pulse.lobes, +pulse.lobes, pulse.points)
    xs = support/(support[-1]-support[0])*(pulse.end-pulse.begin)+pulse.center
    
    envelope = (
        sinc if pulse.apodization is None
        else globals()[f"{pulse.apodization}_sinc"])
    ys = pulse.amplitude*envelope(pulse.lobes)(support)
    
    return xs, ys

class RFPulse(Event):
    """ RF pulse event, represented by a user-defined envelope
        
        :param duration: duration of the pulse
        :param amplitude: maximum amplitude
        :param envelope: sinc_envelope (default), box_envelope, or
            gaussian_envelope
        :param lobes: number of lobes on each side of a sinc envelope (defaults
            to 3)
        :param apodization: apodization of a sinc envelope (None (default),
            "hann", or "hamming")
        :param sd: standard deviation of a Gaussian envelope (defaults to 0.3)
        :param points: number of points used to draw the envelope (defaults to
            101)
    """
    
    def __init__(self, duration, amplitude, envelope=sinc_envelope, **kwargs):
        self.envelope = envelope
        self.sd = kwargs.pop("sd", 0.3)
        self.lobes = kwargs.pop("lobes", 3)
        self.apodization = kwargs.pop("apodization", None)
        self.points = kwargs.pop("points", 101)
        super().__init__(duration, amplitude, **kwargs)
        
    def get_path(self):
        xs, ys = self.envelope(self)
        return matplotlib.path.Path(numpy.transpose([xs, ys]))
    
    @property
    def _fields(self):
        return {
            x: getattr(self, x) for x in [
                "duration", "amplitude", "begin", "center", "end",
                "envelope", "lobes", "apodization", "points"]}

def apodized_sinc(N, alpha):
    return lambda t: ((1-alpha) + alpha*numpy.cos(numpy.pi*t/N)) * numpy.sinc(t)

sinc = lambda N: apodized_sinc(N, 0)
hann_sinc = lambda N: apodized_sinc(N, 0.5)
hamming_sinc = lambda N: apodized_sinc(N, 25./46.)
