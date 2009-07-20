from gtk import gdk

from dockgroup import DockGroup
from dockgrouptype import DockGroupType

class DockLayout(DockGroup):
    """
    """

    def __init__(self, frame):
        """
        
        Arguments:
        - `frame`:
        """

        DockGroup.__init__(self, frame, DockGroupType.HORIZONTAL)
        
        self.layout_width = 1024
        self.layout_height = 768
        
    def size_allocate(self, rect):
        """
        
        Arguments:
        - `rect`:
        """

        self.size = rect.width
        DockGroup.size_allocate(self, rect)

        
    def store_allocation(self):
        """
        """
        
        DockGroup.store_allocation(self)
        self.layout_width = self.allocation.width
        self.layout_height = self.allocation.height

    def restore_allocation(self):
        """
        """
        
        self.allocation = gdk.Rectangle(0, 
                                        0, 
                                        self.layout_width,
                                        self.layout_height)

        DockGroup.restore_allocation(self)
    
