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
    
    def idle(self, channel_or_channels, begin, end, **kwargs):
        if isinstance(channel_or_channels, str):
            y = self._channels[channel_or_channels]
            args = {"color": "black"}
            args.update(kwargs)
            self.plot.plot((begin, end), (y, y), **args)
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
    
    def hard_pulse(self, channel, begin, end, amplitude, color="black"):
        y = self._channels[channel]
        self.plot.plot(
            (begin, begin, end, end), (y, y+amplitude, y+amplitude, y),
            color=color)
    
    def gradient(self, channel, begin, end, amplitude, color="black", alpha=0.2):
        y = self._channels[channel]
        shape = (begin, begin, end, end), (y, y+amplitude, y+amplitude, y)
        
        facecolor = list(matplotlib.colors.to_rgba(color))
        facecolor[3] *= alpha
        
        self.plot.fill(*shape, facecolor=facecolor, edgecolor=None)
        self.plot.plot(*shape, color=color)
    
    def stepped_gradient(self, channel, begin, end, amplitude, color="black"):
        y0 = self._channels[channel]
        
        for y in [-amplitude, -amplitude/2, 0, amplitude/2, amplitude]:
            self.plot.plot(
                (begin, begin, end, end), (y0, y0+y, y0+y, y0), color=color)
    
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
    
    def _marker(self, x, min_y, color="black"):
        max_y = (
            len(self._channels)
            *(self._channel_height+self._channel_gap)-self._channel_height/2)
        self.plot.plot([x, x], [min_y, max_y], "-", lw=0.3, color=color)
