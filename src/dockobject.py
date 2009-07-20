import copy

from gtk import gdk

from dockgrouptype import DockGroupType

class DockObject(object):
    """
    """

    def __init__(self, frame):
        """
        
        Arguments:
        - `frame`:
        """
        
        self.frame = frame
        self.rect = None
        
        self.size = -1
        self.alloc_size = -1

        self.default_hor_size = -1
        self.default_ver_size = -1
        self.pref_size = 0

        self.ax = -1
        self.ay = -1

        #self.visible = None

        self._parent_group = None

    @property
    def default_size(self):
        """
        """
        if self.default_hor_size < 0:
            self.init_default_size()

        if self.parent_group:
            if self.parent_group.type == DockGroupType.HORIZONTAL:
                return self.default_hor_size
            elif self.parent_group.type == DockGroupType.VERTICAL:
                return self.default_ver_size

        return 0
    
    @default_size.setter
    def default_size(self, value):
        """
        
        Arguments:
        - `value`:
        """
        if self.parent_group:
            if self.parent_group.type == DockGroupType.HORIZONTAL:
                self.default_hor_size = value
            elif self.parent_group.type == DockGroupType.VERTICAL:
                self.default_ver_size = value
        
    @property
    def parent_group(self):
        """
        """
        return self._parent_group

    @parent_group.setter
    def parent_group(self, value):
        """
        
        Arguments:
        - `value`:
        """
        self._parent_group = value
        if self.size < 0:
            self.size = self.pref_size = self.default_size

    @property
    def has_allocated_size(self):
        """
        """
        return (not self.alloc_size == -1)
    
    @property
    def min_size(self):
        """
        """
        w, h = self.get_min_size()

        if self.parent_group:
            if self.parent_group.type == DockGroupType.HORIZONTAL:
                return w
            elif self.parent_group.type == DockGroupType.VERTICAL:
                return h

        return w

        
    @property
    def allocation(self):
        """
        """
        return self.rect

    @allocation.setter
    def allocation(self, value):
        """
        
        Arguments:
        - `value`:
        """
        self.rect = value
    
    def reset_default_size(self):
        """
        """
        self.default_hor_size = -1
        self.default_ver_size = -1
    
    def init_default_size(self):
        """
        """
        
        width, height = self.get_default_size()

        if width == -1:
            width = self.frame.default_item_width
        if height == -1:
            height = self.frame.default_item_height

        self.default_hor_size = width
        self.default_ver_size = height

    def get_default_size(self):
        """
        """
        return -1, -1

    def get_min_size(self):
        """
        """
        return 0, 0
    
    ## Allocation
    #
    def size_allocate(self, rect):
        """
        
        Arguments:
        - `rect`:
        """
        self.rect = rect

    def store_allocation(self):
        """
        """
        if self.visible:
            if not self.parent_group or\
               self.parent_group.type == DockGroupType.HORIZONTAL:
                self.size = self.pref_size = int(self.rect.width)
            elif self.parent_group.type == DockGroupType.VERTICAL:
                self.size = self.pref_size = int(self.rect.height)

            self.ax = self.allocation.x
            self.ay = self.allocation.y
            

    def restore_allocation(self):
        """
        """
        
        if self.parent_group != None:
            x = 0 if self.ax == -1 else self.ax
            y = 0 if self.ay == -1 else self.ay
            
            if self.parent_group.type == DockGroupType.HORIZONTAL:
                self.rect = gdk.Rectangle(x, 
                                          y,
                                          int(self.size),
                                          self.parent_group.allocation.height)
            elif self.parent_group.type == DockGroupType.VERTICAL:
                self.rect = gdk.Rectangle(x,
                                          y,
                                          self.parent_group.allocation.width,
                                          int(self.size))


    ## XML Read/Write
    #

    ## Copy
    #
    def copy_size_from(self, obj):
        """
        
        Arguments:
        - `obj`:
        """
        self.size = obj.size
        self.alloc_size = obj.alloc_size
        self.default_hor_size = obj.default_hor_size
        self.default_ver_size = obj.default_ver_size
        self.pref_size = obj.pref_size
    
    def copy_from(self, obj):
        """
        
        Arguments:
        - `obj`:
        """
        pass

    def clone(self):
        """
        """
        return copy.copy(self)
    
    
    ## Abstract 
    #
    

    


