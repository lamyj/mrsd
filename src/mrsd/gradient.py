import matplotlib.path

from .event import Event

class Gradient(Event):
    """ Gradient event, represented by a trapezoid.
    """
    
    def __init__(self, flat_top, amplitude, ramp=0, **kwargs):
        kwargs.setdefault("ramp_up", ramp)
        kwargs.setdefault("ramp_down", ramp)
        
        self.flat_top = flat_top
        self.ramp_up = kwargs.pop("ramp_up")
        self.ramp_down = kwargs.pop("ramp_down")
        
        super().__init__(
            self.ramp_up+self.flat_top+self.ramp_down, amplitude, **kwargs)
    
    def get_path(self):
        return matplotlib.path.Path([
            [self.begin, 0],
            [self.begin+self.ramp_up, self.amplitude],
            [self.begin+self.ramp_up+self.flat_top, self.amplitude],
            [self.end, 0]
        ])
    
    @property
    def _fields(self):
        return {
            x: getattr(self, x)
            for x in ["flat_top", "amplitude", "ramp_up", "ramp_down", "begin"]}
