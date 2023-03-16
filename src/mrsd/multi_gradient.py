import matplotlib.path
import numpy

from .event import Event

class MultiGradient(Event):
    """ Multiple gradient events (e.g. phase encoding), represented by nested
        trapezoids.
        
        :param flat_top: duration of the gradient flat-top
        :param amplitude: maximum amplitude of the gradient flat-top
        :param ramp,ramp_up,ramp_down: ramp durations of the gradient.
            Use `ramp` for symmetric gradients, and both `ramp_up` and
            `ramp_down` for asymmetric gradients
        :param steps: number of steps drawn between the maximum and minimum
            amplitude
    """
    
    def __init__(self, flat_top, amplitude, ramp=0, steps=5, **kwargs):
        
        kwargs.setdefault("ramp_up", ramp)
        kwargs.setdefault("ramp_down", ramp)
        
        self.flat_top = flat_top
        self.ramp_up = kwargs.pop("ramp_up")
        self.ramp_down = kwargs.pop("ramp_down")
        
        self.steps = steps
        
        super().__init__(
            self.ramp_up+self.flat_top+self.ramp_down, amplitude, **kwargs)
        
    def get_path(self):
        amplitudes = numpy.linspace(-self.amplitude, self.amplitude, self.steps)
        
        paths = [
            matplotlib.path.Path([
                [self.begin, 0],
                [self.begin+self.ramp_up, amplitude],
                [self.begin+self.ramp_up+self.flat_top, amplitude],
                [self.end, 0]])
            for amplitude in [amplitudes[0], amplitudes[-1]]]
        
        # θ: angle at the top of the triangle forming the ramp of the gradient
        # sin θ = ramp / amplitude ⇒ θ = arcsin(ramp/amplitude)
        # at height h, the side is from h to amplitude-h ⇒ the base is
        # sin θ (amplitude - h)
        theta_up = numpy.arcsin(self.ramp_up / self.amplitude)
        theta_down = numpy.arcsin(self.ramp_down / self.amplitude)
        
        for amplitude in amplitudes[1:-1]:
            extra_up = numpy.sin(theta_up) * numpy.abs(amplitude)
            extra_down = numpy.sin(theta_down) * numpy.abs(amplitude)
            paths.append(matplotlib.path.Path([
                [self.begin+extra_up, amplitude],
                [self.end-extra_down, amplitude]]))
        
        return matplotlib.path.Path.make_compound_path(*paths)
    
    @property
    def _fields(self):
        return {
            x: getattr(self, x)
            for x in [
                "flat_top", "amplitude", "ramp_up", "ramp_down", "steps",
                "begin"]}
