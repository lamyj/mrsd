import matplotlib.path
import numpy

from .event import Event

class RFPulse(Event):
    """ RF pulse event, represented by a cardinal sine.
    """
    
    # TODO: envelope (box, sinc, gaussian)
    
    def __init__(self, duration, amplitude, **kwargs):
        self.lobes = 3
        super().__init__(duration, amplitude, **kwargs)
        
    def get_path(self):
        center, span = 0.5*(self.begin+self.end), self.end-self.begin
        support = numpy.linspace(-1, 1, 100)
        xs = support*span/2+center
        
        sinc = numpy.sinc(2*self.lobes*support)
        taper = numpy.cos(numpy.pi/2*support)
        ys = self.amplitude*sinc*taper
        
        return matplotlib.path.Path(numpy.transpose([xs, ys]))
    
    @property
    def _fields(self):
        return {x: getattr(self, x) for x in ["duration", "amplitude", "begin"]}
