import copy

import matplotlib.pyplot
import matplotlib.ticker
import numpy

from .adc import ADC
from .echo import Echo
from .gradient import Gradient
from .multi_gradient import MultiGradient
from . import rf_pulse
from .rf_pulse import RFPulse

class Diagram(object):
    def __init__(self, plot, channels):
        self._channel_height = 2
        self._channel_gap = 0.2
        
        self.plot = plot
        self.plot.spines[:].set_visible(False)
        
        self._channels = { 
            x: i*(self._channel_height+self._channel_gap)
            for i, x in enumerate(channels[::-1]) }
        
        self.plot.xaxis.set_major_locator(matplotlib.ticker.NullLocator())
        self.plot.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
        
        self.plot.yaxis.set_major_locator(
            matplotlib.ticker.FixedLocator(sorted(self._channels.values())))
        self.plot.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())
        def channel_formatter(x, pos):
            distances = [numpy.abs(x-value) for value in self._channels.values()]
            return list(self._channels.keys())[numpy.argmin(distances)]
        self.plot.yaxis.set_major_formatter(channel_formatter)
        self.plot.yaxis.set_tick_params(length=0, width=0)
        
        self._background_line_style = {"color": "0.9", "lw": 1, "zorder": -1}
        
        for y in self._channels.values():
            self.plot.axhline(y, **self._background_line_style)
    
    def add(self, channel, event):
        """ Add an event to the specified channel.
        """
        
        event.offset[1] += self._channels[channel]
        self.plot.add_patch(event)
    
    def adc(self, channel, *args, **kwargs):
        """ Add an ADC event to the specified channel.
        """
        
        event = ADC(*args, **kwargs)
        self.add(channel, event)
        return event
    
    def echo(self, channel, *args, **kwargs):
        """ Add an echo event to the specified channel.
        """
        
        event = Echo(*args, **kwargs)
        self.add(channel, event)
        return event
    
    def gradient(self, channel, *args, **kwargs):
        """ Add a gradient event to the specified channel.
        """
        
        event = Gradient(*args, **kwargs)
        self.add(channel, event)
        return event
    
    def multi_gradient(self, channel, *args, **kwargs):
        """ Add a multi-gradient event to the specified channel.
        """
        
        event = MultiGradient(*args, **kwargs)
        self.add(channel, event)
        return event
    
    def rf_pulse(self, channel, *args, **kwargs):
        """ Add an RF pulse event to the specified channel.
        """
        
        event = RFPulse(*args, **kwargs)
        self.add(channel, event)
        return event
    
    def gaussian_pulse(self, channel, *args, **kwargs):
        """ Add a hard RF pulse event to the specified channel.
        """
        
        kwargs["envelope"] = rf_pulse.gaussian_envelope
        event = RFPulse(*args, **kwargs)
        self.add(channel, event)
        return event
    
    def hard_pulse(self, channel, *args, **kwargs):
        """ Add a hard RF pulse event to the specified channel.
        """
        
        kwargs["envelope"] = rf_pulse.box_envelope
        event = RFPulse(*args, **kwargs)
        self.add(channel, event)
        return event
    
    def sinc_pulse(self, channel, *args, **kwargs):
        """ Add a sinc RF pulse event to the specified channel.
        """
        
        kwargs["envelope"] = rf_pulse.sinc_envelope
        event = RFPulse(*args, **kwargs)
        self.add(channel, event)
        return event
    
    def annotate(self, channel, x, y, text, **kwargs):
        """ Add an annotation to the diagram
        """
        
        self.plot.text(x, self._channels[channel]+y, text, **kwargs)
    
    def interval(self, begin, end, y, label, color="k"):
        self.plot.set(ylim=min(y, self.plot.get_ylim()[0]))
        
        self.plot.annotate(
            "", (begin, y), (end, y),
            arrowprops={
                "arrowstyle":"<|-|>", "shrinkA": 0, "shrinkB": 0,
                **self._background_line_style})
        self.plot.text(
            (begin+end)/2, y, label,
            color=color, bbox={"fc": "white", "ec": "none"},
            horizontalalignment="center", verticalalignment="center")
        
        self.plot.vlines(
            [begin, end],
            y, self._channel_height/2+max(self._channels.values()),
            **self._background_line_style)
