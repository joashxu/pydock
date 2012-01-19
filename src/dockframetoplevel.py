import gtk

class DockFrameTopLevel(gtk.EventBox):
    """
    """

    def __init__(self):
        """
        """
        self._x = 0
        self._y = 0

        gtk.EventBox.__init__(self)


    @property
    def x(self):
        """
        """
        return self._x
    
    @x.setter
    def x(self, value):
        """
        
        Arguments:
        - `value`:
        """
        self._x = value
        if self.parent != None:
            self.parent.queue_resize()


    @property
    def y(self):
        """
        """
        return self._y

    @y.setter
    def y(self, value):
        """
        
        Arguments:
        - `value`:
        """
        self._y = value
        if self.parent != None:
            self.parent.queue_resize()
    
    
    

