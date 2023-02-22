import matplotlib.path
import numpy

from .event import Event

class Echo(Event):
    """ Echo event, represented by an oscillating exponential.
    """
    
    def __init__(self, duration, amplitude=1, **kwargs):
        super().__init__(duration, amplitude, **kwargs)
    
    def get_path(self):
        npoints = 26
        slope = numpy.linspace(0, 1, npoints)
        sign = -1+2*(numpy.arange(npoints)%2)
        
        ys = sign * numpy.exp(slope*4)
        # Make symmetrical
        ys = numpy.concatenate((ys, ys[-2::-1]))
        # Normalize amplitude and taper the ends
        ys *= self.amplitude/numpy.abs(ys).max()
        ys[0] = ys[-1] = 0
        
        xs = numpy.linspace(self.begin, self.end, 2*npoints-1)
        
        return matplotlib.path.Path(numpy.transpose([xs, ys]))
    
    @property
    def _fields(self):
        return {x: getattr(self, x) for x in ["duration", "amplitude", "begin"]}
