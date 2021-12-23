import matplotlib.collections
import matplotlib.patches
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
    
    def idle(self, channel_or_channels, begin, end):
        if isinstance(channel_or_channels, str):
            y = self._channels[channel_or_channels]
            self.plot.plot((begin, end), (y, y), color="black")
        else:
            for channel in channel_or_channels:
                self.idle(channel, begin, end)
    
    def idle_all(self, begin, end):
        for channel in self._channels:
            self.idle(channel, begin, end)
    
    def sinc_pulse(self, channel, center, duration, amplitude):
        xs = numpy.linspace(center-duration/2, center+duration/2, 100)
        
        y = self._channels[channel]
        ys = y+amplitude*numpy.sinc(4*(xs-center)/duration)
        self.plot.plot(xs, ys, color="black")
    
    def hard_pulse(self, channel, center, duration, amplitude):
        y = self._channels[channel]
        begin, end = center-duration/2, center+duration/2
        self.plot.plot(
            (begin, begin, end, end), (y, y+amplitude, y+amplitude, y),
            color="black")
    
    def gradient(self, channel, begin, end, amplitude):
        y = self._channels[channel]
        self.plot.plot(
            (begin, begin, end, end), (y, y+amplitude, y+amplitude, y),
            color="black")
        self.plot.add_patch(
            matplotlib.patches.Rectangle(
                (begin, y), end-begin, amplitude, color=(0, 0, 0, 0.2)))
    
    def stepped_gradient(self, channel, begin, end, amplitude):
        y0 = self._channels[channel]
        
        for y in [-amplitude, -amplitude/2, 0, amplitude/2, amplitude]:
            self.plot.plot(
                (begin, begin, end, end), (y0, y0+y, y0+y, y0), color="black")
    
    def readout(self, channel, begin, end, amplitude):
        center = (begin+end)/2
        duration = end-begin
        
        npoints = 50
        wedge = numpy.concatenate(
            (numpy.linspace(0, 1, npoints//2), numpy.linspace(1, 0, npoints//2)))
        sign = -1+2*(numpy.arange(npoints)%2)
        ys = sign * numpy.exp(wedge*4)
        ys *= amplitude/numpy.abs(ys).max()
        ys[0] = ys[-1] = 0
        
        y = self._channels[channel]
        xs = numpy.linspace(begin, end, npoints)
        self.plot.plot(xs, y+ys, color="black")
    
    def interval(self, begin, end, y, label, mutation_scale=20):
        self._marker(begin, y)
        self._marker(end, y)
        arrow = matplotlib.patches.FancyArrowPatch(
            (begin, y), (end, y), arrowstyle="<|-|>",
            mutation_scale=mutation_scale, color="black")
        self.plot.add_patch(arrow)
        self.plot.text(
            (begin+end)/2, y, label, horizontalalignment="center",
            verticalalignment="bottom")
    
    def _marker(self, x, min_y):
        max_y = (
            len(self._channels)
            *(self._channel_height+self._channel_gap)-self._channel_height/2)
        self.plot.plot([x, x], [min_y, max_y], "-", lw=0.3, color="black")
