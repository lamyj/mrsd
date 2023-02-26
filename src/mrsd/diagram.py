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
    """ MR sequence diagram
        
        :param plot: an instance of matplotlib axes (plot, subplot, etc.)
        :param channels: sequence of channels names in the plot, from top to
            bottom
    """
    
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
        self.plot.autoscale_view()
    
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
    
    def readout(
            self, adc_channel, gradient_channel, duration,
            echo_amplitude=1, gradient_amplitude=1,
            ramp=0, ramp_up=None, ramp_down=None, 
            begin=None, end=None, center=None,
            adc_kwargs=None, echo_kwargs=None, gradient_kwargs=None):
        """ Add a readout block (echo, ADC and gradient)
            
            :param adc_channel: channel of the echo and ADC
            :param gradient_channel: channel of the gradient
            :param duration: duration of the echo, ADC, and gradient flat-top
            :param echo_amplitude: amplitude of the echo
            :param gradient_amplitude: amplitude of the gradient flat-top
            :param ramp,ramp_up,ramp_down: ramp durations of the gradient.
                Use `ramp` for symmetric gradients, and both `ramp_up` and
                `ramp_down` for asymmetric gradients
            :param begin,end,center: time of the begin, end, or center of the
                echo/ADC. Only one must be specified.
            :param adc_kwargs: extra parameters for the ADC event (e.g. style)
            :param echo_kwargs: extra parameters for the echo event (e.g. style)
            :param gradient_kwargs: extra parameters for the gradient event
                (e.g. style)
        """
        
        adc = self.adc(
            adc_channel, duration, begin=begin, end=end, center=center,
            **(adc_kwargs or {}))
        echo = self.echo(
            adc_channel, adc.duration, echo_amplitude, center=adc.center,
            **(echo_kwargs or {}))
        gradient = self.gradient(
            gradient_channel, adc.duration, gradient_amplitude,
            ramp_up=ramp_up if ramp_up is not None else ramp,
            ramp_down=ramp_down if ramp_down is not None else ramp,
            center=adc.center, **(gradient_kwargs or {}))
        
        return adc, echo, gradient
    
    def selective_pulse(
            self, pulse_channel, gradient_channel, duration,
            pulse_amplitude=1, gradient_amplitude=1,
            envelope=None, ramp=0, ramp_up=None, ramp_down=None, 
            begin=None, end=None, center=None,
            pulse_kwargs=None, gradient_kwargs=None):
        """ Add a selective pulse block (pulse and gradient)
            
            :param pulse_channel: channel of the RF pulse
            :param gradient_channel: channel of the gradient
            :param duration: duration of the pulse and gradient flat-top
            :param pulse_amplitude: amplitude of the RF pulse
            :param gradient_amplitude: amplitude of the gradient flat-top
            :param envelope: envelope of the pulse (default to sinc)
            :param ramp,ramp_up,ramp_down: ramp durations of the gradient.
                Use `ramp` for symmetric gradients, and both `ramp_up` and
                `ramp_down` for asymmetric gradients
            :param begin,end,center: time of the begin, end, or center of the
                echo/ADC. Only one must be specified.
            :param pulse_kwargs: extra parameters for the pulse event (e.g.
                style)
            :param gradient_kwargs: extra parameters for the gradient event
                (e.g. style)
        """
        
        pulse = self.rf_pulse(
            pulse_channel, duration, pulse_amplitude,
            envelope or rf_pulse.sinc_envelope,
            begin=begin, end=end, center=center,
            **(pulse_kwargs or {}))
        gradient = self.gradient(
            gradient_channel, pulse.duration, gradient_amplitude,
            ramp_up=ramp_up if ramp_up is not None else ramp,
            ramp_down=ramp_down if ramp_down is not None else ramp,
            center=pulse.center, **(gradient_kwargs or {}))
        
        return pulse, gradient
    
    def annotate(self, channel, x, y, text, **kwargs):
        """ Add an annotation
            
            :param channel: channel to which the annotation is added
            :param x: time of the annotation
            :param y: relative position of the annotation in the channel
            :param text: text of the annotation
            :param kwargs: extra parameters passed to matplotlib.axes.Axes.text
        """
        
        self.plot.text(x, self._channels[channel]+y, text, **kwargs)
    
    def interval(self, begin, end, y, label, color="k"):
        """ Add a time interval annotation
            
            :param begin,end: begin and end time of the interval
            :param y: vertical position of the annotation
            :param label: label of the annotation
            :param color: color of the annotation label
        """
        
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
    
    def y(self, channel):
        """ Return the y coordinate of the center of a channnel.
        """
        
        return self._channels[channel]
