import gtk
from gtk import gdk

from dockobject import DockObject
from dockitemstatus import DockItemStatus
from dockposition import DockPosition

class DockGroupItem(DockObject):
    """
    """

    def __init__(self, frame, item):
        """
        
        Arguments:
        - `frame`:
        - `item`:
        """

        DockObject.__init__(self, frame)

        self.frame = frame
        self.item = item

        self.visible_flag = item.visible
        self.autohide_size = -1
        self._status = DockItemStatus.DOCKABLE
        self.float_rect = None
        self.bar_doc_position = None
        
    @property
    def id(self):
        """Documentation"""
        
        return self.item.id

    def get_default_size(self):
        """Documentation"""
        return self.item.default_width, self.item.default_height

    def get_min_size(self):
        """Documentation"""
        width, height = self.size_request()

        return width, height

    def size_request(self):   
        return self.item.widget.size_request()

    def size_allocate(self, new_alloc):
        self.item.widget.size_allocate(new_alloc)
        DockObject.size_allocate(self, new_alloc)

    @property
    def expand(self):
        return self.item.expand

    def queue_resize(self):
        item.widget.queue_resize()

    def get_dock_target(self, item, px, py, rect=None):        
        
        if not rect:
            rect = self.allocation

        dock_delegate, out_rect = None, None
        is_point_in_rect = True if rect.x <= px <= rect.width and rect.y <= py <= rect.height else False
        if  item != self.item and self.item.visible and is_point_in_rect:
            xdock_margin = int((float(rect.width) * (1.0 - self.frame.ITEM_DOCK_CENTER_AREA)) / 2)
            ydock_margin = int((float(rect.height)* (1.0 - self.frame.ITEM_DOCK_CENTER_AREA)) / 2)

            pos = None

            if px <= rect.x + xdock_margin and self.parent_group.type != DockGroupType.HORIZONTAL:
                out_rect = gdk.Rectangle(rect.x, rect.y, xdock_margin, rect.height)
                pos = DockPosition.LEFT
            elif px >= rect.width - xdock_margin and self.parent_group.type != DockGroupType.HORIZONTAL:
                out_rect = gdk.Rectangle(rect.width - xdock_margin, rect.y, xdock_margin, rect.height)
                pos = DockPosition.RIGHT
            elif py <= rect.y + ydock_margin and self.parent_group.type != DockGroup.VERTICAL:
                out_rect = gdk.Rectangle(rect.x, rect.y, rect.width, ydock_margin)
                pos = DockPosition.TOP
            elif py >= rect.bottom - ydock_margin and self.parent_group.type != DockGroupType.VERTICAL:
                out_rect = gdk.Rectangle(rect.x, rect.y - ydock_margin, rect.width, ydock_margin)
                pos = DockPosition.BOTTOM
            else:
                out_rect = gdk.Rectangle(rect.x + xdock_margin,
                                         rect.y + ydock_margin,
                                         rect.width - xdock_margin*2,
                                         rect.height - ydock_margin*2)
                pos = DockPosition.CENTER

            def mini_function(dit):
                it = self.parent_group.add_object(dit, pos, self.id)
                it.set_visible(True)

                self.parent_group.focus_item(it)

            dock_delegate = mini_function
            
        return dock_delegate, out_rect

    def copy_from(self, ob):
        DockObject.copy_from(self, ob)

        self.item = ob.item
        self.visible_flag = ob.visible_flag
        self.float_rect = ob.float_rect

    @property
    def visible(self):
        return self.visible_flag and self.status == DockItemStatus.DOCKABLE

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if self._status == value:
            return

        old_value = self._status
        self._status = value

        if self._status == DockItemStatus.FLOATING:
            if self.float_rect:
                x, y = self.item.widget.translate_coordinates(self.item.widget.get_toplevel(), 0, 0)
                #win = self.frame.get_toplevel()

                #if win == None:              
                #    wx, wy = win.get_position()
                #    self.float_rect = gdk.Rectangle(wx + x,
                #                                    wy + y,
                #                                    self.allocation.width,
                #                                    self.allocation.height)
                self.item.set_float_mode(self.float_rect)
            elif self._status == DockItemStatus.AUTOHIDE:
                self.set_bar_doc_position()
                self.item.set_autohide_mode(self.bar_doc_position,
                                             self.get_autohide_size(self.bar_doc_position))
            else:
                self.item.reset_mode()

            if old_value == DockItemStatus.DOCKABLE or\
               self._status == DockItemStatus.DOCKABLE:
                   if self.parent_group != None:
                       self.parent_group.update_visible(self)

    def set_bar_doc_position(self):
        if self.allocation.width < self.allocation.height:
            mid = self.allocation.left + self.allocation.width / 2
            if mid > self.frame.allocation.left + self.frame.allocation.width / 2:
                self.bar_doc_position = gtk.POSITION_RIGHT
            else:
                self.bar_doc_position = gtk.POSITION_LEFT
        else:
            mid = self.allocation.top + self.allocation.height / 2
            if mid > self.frame.allocation.top + self.frame.allocation.height / 2:
                self.bar_doc_position = gtk.POSITION_BOTTOM
            else:
                self.bar_doc_position = gtk.POSITION_TYPE

    def set_visible(self, value):
        """
        
        Arguments:
        - `visible`:
        """
        
        if self.visible_flag != value:
            self.visible_flag = value
            if self.visible_flag:
                self.item.show_widget()
            else:
                self.item.hide_widget()

            if self.parent_group != None:
                self.parent_group.update_visible(self)

    def store_allocation(self):
        DockObject.store_allocation(self)

        if self.status == DockItemStatus.FLOATING:
            self.float_rect = self.item.floating_position
        elif self.status == DockItemStatus.AUTOHIDE:
            self.autohide_size = self.item.autohide_size

    def restore_allocation(self):
        DockObject.restore_allocation(self)
        self.item.update_visible_status()

        if self.status == DockItemStatus.FLOATING:
            self.item.set_float_mode(self.float_rect)
        elif self.status == DockItemStatus.AUTOHIDE:
            self.item.set_autohide_mode(self.bar_doc_position, self.get_autohide_size())
        else:
            self.item.reset_mode()

        if not self.visible_flag:
            self.item.hide_widget()

    def get_autohide_size(self, pos):
        if self.autohide_size != -1:
            return self.autohide_size

        if pos == gtk.POSITION_LEFT or pos == gtk.POSITION_RIGHT:
            return self.allocation.width
        else:
            return self.allocation.height

