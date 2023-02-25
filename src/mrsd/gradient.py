import matplotlib.path

from .event import Event

class Gradient(Event):
    """ Gradient event, represented by a trapezoid.
        
        :param flat_top: duration of the gradient flat-top
        :param amplitude: amplitude of the gradient flat-top
        :param ramp,ramp_up,ramp_down: ramp durations of the gradient.
            Use `ramp` for symmetric gradients, and both `ramp_up` and
            `ramp_down` for asymmetric gradients
    """
    
    def __init__(self, flat_top, amplitude, ramp=0, **kwargs):
        kwargs.setdefault("ramp_up", ramp)
        kwargs.setdefault("ramp_down", ramp)
        
        self.flat_top = flat_top
        self.ramp_up = kwargs.pop("ramp_up")
        self.ramp_down = kwargs.pop("ramp_down")
        
        super().__init__(
            self.ramp_up+self.flat_top+self.ramp_down, amplitude, **kwargs)
    
    def adapt(
            self, flat_top, area_factor,
            ramp=0, ramp_up=None, ramp_down=None, **kwargs):
        """ Return a gradient with an area equal to a factor of the current
            gradient.
        """
        
        area = self.amplitude * (self.ramp_up/2 + self.flat_top + self.ramp_down/2)
        target_area = area * area_factor
        
        if ramp_up is None:
            ramp_up = ramp
        if ramp_down is None:
            ramp_down = ramp
        amplitude = target_area / (ramp_up/2 + flat_top + ramp_down/2)
        
        return Gradient(
            flat_top, amplitude, ramp_up=ramp_up, ramp_down=ramp_down, **kwargs)
    
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
