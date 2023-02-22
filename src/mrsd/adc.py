import matplotlib.path

from .event import Event

class ADC(Event):
    """ ADC/readout event, represented by a rectangle of amplitude 1.
    """
    
    def __init__(self, duration, **kwargs):
        super().__init__(duration, 1, **kwargs)
    
    def get_path(self):
        return matplotlib.path.Path([
            [self.begin, 0],
            [self.begin, self.amplitude],
            [self.begin+self.duration, self.amplitude],
            [self.begin+self.duration, 0]])
    
    @property
    def _fields(self):
        return {x: getattr(self, x) for x in ["duration", "begin"]}
