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
    
    def sinc_pulse(self, channel, begin, end, amplitude, lobes=4):
        center, span = 0.5*(begin+end), end-begin
        support = numpy.linspace(-1, 1, 100)
        
        y0 = self._channels[channel]
        sinc = numpy.sinc(2*lobes*support)
        taper = numpy.cos(numpy.pi/2*support)
        
        self.plot.plot(
            support*span/2+center, y0+amplitude*sinc*taper, color="black")
    
    def hard_pulse(self, channel, begin, end, amplitude):
        y = self._channels[channel]
        self.plot.plot(
            (begin, begin, end, end), (y, y+amplitude, y+amplitude, y),
            color="black")
    
    def gradient(self, channel, begin, end, amplitude):
        y = self._channels[channel]
        shape = (begin, begin, end, end), (y, y+amplitude, y+amplitude, y)
        self.plot.fill(*shape, facecolor=(0, 0, 0, 0.2), edgecolor=None)
        self.plot.plot(*shape, color="black")
    
    def stepped_gradient(self, channel, begin, end, amplitude):
        y0 = self._channels[channel]
        
        for y in [-amplitude, -amplitude/2, 0, amplitude/2, amplitude]:
            self.plot.plot(
                (begin, begin, end, end), (y0, y0+y, y0+y, y0), color="black")
    
    def echo(self, channel, begin, end, amplitude):
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
        self.plot.plot(xs, y+ys, color="black")
    
    def annotate(self, channel, x, label, y):
        y0 = self._channels[channel]
        self.plot.annotate(label, (x, y0+y))
    
    def interval(self, begin, end, y, label):
        self._marker(begin, y)
        self._marker(end, y)
        
        self.plot.annotate(
            "", (begin, y), (end, y), arrowprops={"arrowstyle":"<|-|>"})
        self.plot.text(
            (begin+end)/2, y, label, horizontalalignment="center",
            verticalalignment="bottom")
    
    def _marker(self, x, min_y):
        max_y = (
            len(self._channels)
            *(self._channel_height+self._channel_gap)-self._channel_height/2)
        self.plot.plot([x, x], [min_y, max_y], "-", lw=0.3, color="black")
