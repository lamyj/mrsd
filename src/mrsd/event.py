import matplotlib.patches
import matplotlib.transforms
import numpy

class Event(matplotlib.patches.Patch):
    """ Abstract sequence event
        
        :param duration: total duration.
        :param amplitude: normalized amplitude between -1 and +1.
        :param begin,end,center: time of the begin, end, or center of the
            event. Only one must be specified.
        :param offset: horizontal and vertical offset to position the event.
        :param kwargs: passed to matplotlib.patches.Patch
    """
    
    def __init__(
            self, duration, amplitude,
            begin=None, end=None, center=None, offset=None,
            **kwargs):
        self.duration = duration
        self.amplitude = amplitude
        
        if begin is not None:
            self.begin = begin
        elif center is not None:
            self.begin = center - self.duration/2
        elif end is not None:
            self.begin = end - self.duration
        else:
            raise Exception("Missing time")
        
        self.center = self.begin + self.duration/2
        self.end = self.begin + self.duration
        
        self.offset = numpy.array(offset if offset is not None else [0., 0.])
        
        if "color" not in kwargs:
            if"edgecolor" not in kwargs and "ec" not in kwargs:
                kwargs.setdefault("edgecolor", "black")
            if "facecolor" not in kwargs and "fc" not in kwargs:
                kwargs.setdefault("facecolor", "none")
        if "linewidth" not in kwargs and "lw" not in kwargs:
            kwargs.setdefault("linewidth", 1)
        
        super().__init__(**kwargs)
    
    def move(self, offset):
        """ Move on the time axis, return the object
        """
        
        self.begin += offset
        self.center += offset
        self.end += offset
        return self
    
    def __copy__(self):
        new_object = self.__class__(**self._fields)
        inspector = matplotlib.artist.ArtistInspector(self)
        setters = inspector.get_setters()
        for name, value in inspector.properties().items():
            if name == "transform" or name not in setters:
                continue
            
            getattr(new_object, f"set_{name}")(value)
        
        return new_object
    
    def get_patch_transform(self):
        """ Inherited from parent class.
        """
        
        return matplotlib.transforms.Affine2D().translate(*self.offset)
