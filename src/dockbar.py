import gtk
import gobject

from dockbaritem import DockBarItem

class DockBar(gtk.EventBox):
    """
    """

    def __init__(self, frame, position):
        """
        
        Arguments:
        - `frame`:
        - `position`:
        """

        gtk.EventBox.__init__(self)

        self.frame = frame
        self.position = position
        
        if gtk.Orientation == gtk.ORIENTATION_HORIZONTAL:
            self.box = gtk.HBox()
        else:
            self.box = gtk.VBox()

        alg = gtk.Alignment(0, 0, 0, 0)

        if self.position == gtk.POS_TOP:
            alg.props.bottom_padding = 2
        elif self.position == gtk.POS_BOTTOM:
            alg.props.top_padding = 2
        elif self.position == gtk.POS_LEFT:
            alg.props.right_padding = 2
        elif self.position == gtk.POS_RIGHT:
            alg.props.left_padding = 2

        self.box.props.spacing = 3
        alg.add( self.box )

        self.add( alg )
        self.show_all()
        
    @property
    def orientation(self):
        """
        """
        if (self.position == gtk.POS_LEFT) or (self.position == gtk.POS_RIGHT):
            return gtk.ORIENTATION_VERTICAL
        else:
            return gtk.ORIENTATION_HORIZONTAL
        pass
    
        
    def add_item(self, item, size):
        """
        
        Arguments:
        - `item`:
        - `size`:
        """
        self.it = DockBarItem(self, item, size)        
        self.box.pack_start(self.it, False, False, 0)

        self.it.show_all()

        return self.it

    def remove_item(self, item):
        """
        
        Arguments:
        - `item`:
        """
        self.box.remove(item)

    def update_title(self, item):
        """
        
        Arguments:
        - `item`:
        """
        for it in box.get_children():
            if it.dock_item == item :
                it.update_tab()
                break
