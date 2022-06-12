import copy

import matplotlib.pyplot
import matplotlib.ticker
import numpy

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
    
    def sinc_pulse(self, channel, begin, end, amplitude, lobes=4, color="black"):
        center, span = 0.5*(begin+end), end-begin
        support = numpy.linspace(-1, 1, 100)
        
        y0 = self._channels[channel]
        sinc = numpy.sinc(2*lobes*support)
        taper = numpy.cos(numpy.pi/2*support)
        
        self.plot.plot(
            support*span/2+center, y0+amplitude*sinc*taper, color=color)
        
        self._update_time_range(begin, end)
        self._events[channel].append((begin, end))
    
    def hard_pulse(self, channel, begin, end, amplitude, color="black"):
        y = self._channels[channel]
        self.plot.plot(
            (begin, begin, end, end), (y, y+amplitude, y+amplitude, y),
            color=color)
        
        self._update_time_range(begin, end)
        self._events[channel].append((begin, end))
    
    def gradient(self, channel, begin, end, amplitude, color="black", alpha=0.2):
        y = self._channels[channel]
        shape = (begin, begin, end, end), (y, y+amplitude, y+amplitude, y)
        
        facecolor = list(matplotlib.colors.to_rgba(color))
        facecolor[3] *= alpha
        
        self.plot.fill(*shape, facecolor=facecolor, edgecolor=None)
        self.plot.plot(*shape, color=color)
        
        self._update_time_range(begin, end)
        self._events[channel].append((begin, end))
    
    def stepped_gradient(
            self, channel, begin, end, amplitude,
            direction=None, location="left", offset=0.1,
            color="black"):
        y0 = self._channels[channel]
        
        for y in [-amplitude, -amplitude/2, 0, amplitude/2, amplitude]:
            self.plot.plot(
                (begin, begin, end, end), (y0, y0+y, y0+y, y0), color=color)
        
        if direction is not None:
            arrowstyle = "<|-" if direction == +1 else "-|>"
            location = begin-offset if location == "left" else end+offset
            self.plot.annotate(
                "", (location, y0-amplitude), (location, y0+amplitude),
                arrowprops={"arrowstyle": arrowstyle, "color": color})
        
        self._update_time_range(begin, end)
        self._events[channel].append((begin, end))
    
    def echo(self, channel, begin, end, amplitude, color="black"):
        npoints = 26
        slope = numpy.linspace(0, 1, npoints)
        sign = -1+2*(numpy.arange(npoints)%2)
        ys = sign * numpy.exp(slope*4)
        # Make symmetrical
        ys = numpy.concatenate((ys, ys[-2::-1]))
        # Normalize amplitude and taper the ends
        ys *= amplitude/numpy.abs(ys).max()
        ys[0] = ys[-1] = 0
        
        y = self._channels[channel]
        xs = numpy.linspace(begin, end, 2*npoints-1)
        self.plot.plot(xs, y+ys, color=color)
        
        self._update_time_range(begin, end)
        self._events[channel].append((begin, end))
    
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
