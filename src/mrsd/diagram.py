import copy

import matplotlib.pyplot
import matplotlib.ticker
import numpy

from .adc import ADC
from .echo import Echo
from .gradient import Gradient
from .multi_gradient import MultiGradient
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
        
        # Minimum and maximum time at which an event was specified
        self._t_min = numpy.inf
        self._t_max = -numpy.inf
        # Begin and end time of each event, per channel
        self._events = {x: [] for x in channels}
        
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
    
    def add(self, channel, event):
        """ Add an event to the specified channel.
        """
        
        event.offset[1] += self._channels[channel]
        self.plot.add_patch(event)
    
    def idle(self, channel_or_channels, begin, end, **kwargs):
        if isinstance(channel_or_channels, str):
            channel = channel_or_channels
            y = self._channels[channel]
            args = {"color": "black"}
            args.update(kwargs)
            self.plot.plot((begin, end), (y, y), **args)
            
            self._update_time_range(begin, end)
            self._events[channel].append((begin, end))
        else:
            for channel in channel_or_channels:
                self.idle(channel, begin, end, **kwargs)
    
    def idle_all(self, begin, end, **kwargs):
        for channel in self._channels:
            self.idle(channel, begin, end, **kwargs)
    
    # def sinc_pulse(self, channel, begin, end, amplitude, lobes=4, color="black"):
    #     center, span = 0.5*(begin+end), end-begin
    #     support = numpy.linspace(-1, 1, 100)
    #     
    #     y0 = self._channels[channel]
    #     sinc = numpy.sinc(2*lobes*support)
    #     taper = numpy.cos(numpy.pi/2*support)
    #     
    #     self.plot.plot(
    #         support*span/2+center, y0+amplitude*sinc*taper, color=color)
    #     
    #     self._update_time_range(begin, end)
    #     self._events[channel].append((begin, end))
    # 
    # def hard_pulse(self, channel, begin, end, amplitude, color="black"):
    #     y = self._channels[channel]
    #     self.plot.plot(
    #         (begin, begin, end, end), (y, y+amplitude, y+amplitude, y),
    #         color=color)
    #     
    #     self._update_time_range(begin, end)
    #     self._events[channel].append((begin, end))
    
    def adc(self, channel, *args, **kwargs):
        event = ADC(*args, **kwargs)
        self.add(channel, event)
        return event
    
    def echo(self, channel, *args, **kwargs):
        event = Echo(*args, **kwargs)
        self.add(channel, event)
        return event
    
    def gradient(self, channel, *args, **kwargs):
        event = Gradient(*args, **kwargs)
        self.add(channel, event)
        return event
    
    def multi_gradient(self, channel, *args, **kwargs):
        event = MultiGradient(*args, **kwargs)
        self.add(channel, event)
        return event
    
    def rf_pulse(self, channel, *args, **kwargs):
        event = RFPulse(*args, **kwargs)
        self.add(channel, event)
        return event
    
    def hard_pulse(self, channel, *args, **kwargs):
        event = RFPulse(*args, envelope="box", **kwargs)
        self.add(channel, event)
        return event
    
    def sinc_pulse(self, channel, *args, **kwargs):
        kwargs.update({"envelope": "sinc"})
        event = RFPulse(*args, **kwargs)
        self.add(channel, event)
        return event
    
    def annotate(self, channel, x, label, y, color="black"):
        y0 = self._channels[channel]
        self.plot.annotate(label, (x, y0+y), color=color)
    
    def interval(self, begin, end, y, label, color="black"):
        self._marker(begin, y, color=color)
        self._marker(end, y, color=color)
        
        self.plot.annotate(
            "", (begin, y), (end, y),
            arrowprops={"arrowstyle":"<|-|>", "color": color})
        self.plot.text(
            (begin+end)/2, y, label, color=color,
            horizontalalignment="center", verticalalignment="bottom")
    
    def auto_idle(self):
        events_copy = copy.deepcopy(self._events)
        for channel, events in events_copy.items():
            for index, event in enumerate(events):
                if index == 0:
                    self.idle(channel, self._t_min, event[0])
                elif events[index-1][1] != event[0]:
                    self.idle(channel, events[index-1][1], event[0])
                if index == len(events)-1:
                    self.idle(channel, event[1], self._t_max)
        self._events = events_copy
    
    def _marker(self, x, min_y, color="black"):
        max_y = (
            len(self._channels)
            *(self._channel_height+self._channel_gap)-self._channel_height/2)
        self.plot.plot([x, x], [min_y, max_y], "-", lw=0.3, color=color)
    
    def _update_time_range(self, begin, end):
        self._t_min = min(self._t_min, begin)
        self._t_max = max(self._t_max, end)
