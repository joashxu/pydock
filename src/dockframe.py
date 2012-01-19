import gtk
import gobject

from dockbar import DockBar
from dockcontainer import DockContainer
from dockitem import DockItem
from docklayout import DockLayout
from dockgroupitem import DockGroupItem
from dockitemstatus import DockItemStatus
from dockposition import DockPosition
from autohidebox import AutoHideBox

from utils.datastructures import SortedDict

class DockFrame(gtk.HBox):
    """
    """
    __gsignals__ = { 'size-allocate' : 'override' }
    
    ITEM_DOCK_CENTER_AREA = 0.4
    GROUP_DOCK_SEP_SIZE = 40

    def __init__(self):
        """
        """

        gtk.HBox.__init__(self)

        # Properties
        self.default_item_height = 130
        self.default_item_width  = 130

        self.autohide_delay = 500
        self.autoshow_delay = 500

        self.handle_size = 8
        self.handle_padding = 1

        self.layouts = SortedDict()        
        self.top_levels = []
        self._current_layout = ""
        
        # Setting up the dock bar
        self.dockbar_top = DockBar(self, gtk.POS_TOP)
        self.dockbar_bottom = DockBar(self, gtk.POS_BOTTOM)
        self.dockbar_left = DockBar(self, gtk.POS_LEFT)
        self.dockbar_right = DockBar(self, gtk.POS_RIGHT)

        # Setting up the container
        self.container = DockContainer(self)

        hbox = gtk.HBox()
        hbox.pack_start(self.dockbar_left, False, False, 0)
        hbox.pack_start(self.container, True, True, 0)
        hbox.pack_start(self.dockbar_right, False, False, 0)
        
        self.main_box = gtk.VBox()
        self.main_box.pack_start(self.dockbar_top, False, False, 0)
        self.main_box.pack_start(hbox, True, True, 0)
        self.main_box.pack_start(self.dockbar_bottom, False, False, 0)

        self.add(self.main_box)

        self.main_box.show_all()
    

    @property
    def total_handle_size(self):
        """
        """
        return self.handle_size + self.handle_padding*2 

    
    def add_item(self, id):
        """
        
        Arguments:
        - `id`:
        """        
        for item in self.container.items:            
            if item.id == id:
                if item.is_position_marker:
                    item.is_position_marker = False
                    return item

                raise Exception("Item with Id %d already exist" % id)
            break
    
        new_item = DockItem(self, id) 
        self.container.items.append(new_item)
        
        return new_item

    def remove_item(self, item):
        """
        
        Arguments:
        - `item`:
        """
        
        if self.container.layout:
            container.layout.remove_item_rec(item)

        for group in self.layouts.values:
            group.remote_item_rec(item)
        
        self.container.items.remove(item)
    

    def get_item(self, id):
        """
        
        Arguments:
        - `id`:
        """
        for item in self.container.items:
            if item.id == id:
                if not item.is_position_marker:
                    return item
                else:
                    return None

        return None

    def get_items(self):
        """
        """
        return (x for x in self.container.items)          
    
    ## Layout
    #
    
    def load_layout(self, layout_name):
        """
        
        Arguments:
        - `layout_name`:
        """
        dock_layout = DockLayout(self)
        dock_layout = self.layouts.get(layout_name, None)

        if dock_layout:          
            self.container.load_layout(dock_layout)
            return True
    
        return False
    
    def create_layout(self, name, copy_current=False):
        """
        
        Arguments:
        - `name`:
        - `copy_current`:
        """
        dock_layout = DockLayout(self)
        if self.container.layout == None or not copy_current:
            dock_layout = self.get_default_layout()
        else:
            self.container.store_allocation()
            dock_layout = self.container.layout.clone()

        dock_layout.name = name
        self.layouts[name] = dock_layout

    def has_layout(self, id):
        """
        
        Arguments:
        - `id`:
        """
        
        return self.layouts.has_key(id)

    def save_layouts(self, file):
        """
        
        Arguments:
        - `file`:
        """
        pass

    def load_layouts(self, file):
        """
        
        Arguments:
        - `file`:
        """
        pass

    def get_default_layout(self):
        """
        """
    
        group = DockLayout(self)

        todock = []
        
        for item in self.container.items:
            if not item.default_location:
                dgt = DockGroupItem(self, item)
                dgt.set_visible(item.default_visible)
                group.add_object(dgt)
            else:
                todock.append(item)

        last_count = 0

        while last_count != len(todock):
            last_count = len(todock)
            i = 0
            while i < len(todock):
                it = todock[i]                
                if self.add_default_item(group, it) != None:
                    todock.remove(it)
                    i -= 1
                i += 1
    
        
        for item in todock:
            dgt = DockGroupItem(self, item)
            dgt.set_visible(False)
            group.add_object(dgt)
        
        return group

    @property
    def current_layout(self):
        """
        """
        return self._current_layout
    
    @current_layout.setter
    def current_layout(self, value):
        """
        
        Arguments:
        - `value`:
        """
        if hasattr(self, '_current_layout') and self._current_layout == value:
            return
        
        if self.load_layout(value):
            self._current_layout = value
    
    def update_title(self, item):
        """
        
        Arguments:
        - `item`:
        """
        
        gitem = self.container.find_dock_group_item(item.id)

        if gitem == None:
            return

        gitem.parent_group.update_title(item)
        self.dockbar_top.update_title(item)
        self.dockbar_bottom.update_title(item)
        self.dockbar_left.update_title(item)
        self.dockbar_right.update_title(item)
    
    def present(self, item, give_focus):
        """
        
        Arguments:
        - `item`:
        - `give_focus`:
        """
        
        gitem = self.container.find_dock_group_item(item.id)
        
        if gitem == None:
            return False
    
        return gitem.parent_group.present(item, give_focus)
    
    def get_visible(self, item):
        gitem = self.container.find_dock_group_item(item.id)
        if gitem == None:
            return False
        return gitem.visible_flag   
    
    def set_visible(self, item, visible):
        """
        
        Arguments:
        - `item`:
        - `visible`:
        """
        
        if self.container.layout == None:
            return

        gitem = self.container.find_dock_group_item(item.id)

        if gitem == None:
            if visible:
                if item.default_location:
                    gitem = self.add_default_item(container.layout, item)
                    
                if gitem == None:
                    gitem = DockGroupItem(self, item)
                    self.container.layout.add_object(gitem)
            else:
                return

        gitem.set_visible(visible)
        self.container.relayout_widgets()
    
    def get_status(self, item):
        """
        
        Arguments:
        - `item`:
        """
        
        gitem = self.container.find_dock_group_item(item.id)

        if gitem == None:
            return DockItemStatus.DOCKABLE

        return gitem.status
        
    def set_status(self, item, status):
        """
        
        Arguments:
        - `item`:
        - `status`:
        """
        
        gitem = self.container.find_dock_group_item(item.id)

        if gitem == None:
            return

        gitem.store_allocation()
        gitem.status = status
        
        self.container.relayout_widgets()
    
    
    def add_default_item(self, group, item):
        """
        
        Arguments:
        - `group`:
        - `item`:
        """
        positions = item.default_location.split(';')
        for pos in positions:
            try:
                idx = pos.index('/')
            except ValueError:
                continue
            
            id = pos[:idx].strip()
            g = group.find_group_containing(id)

            if g != None:
                try:
                    position_str = pos[idx + 1:].strip()
                    
                    if position_str == 'Left':
                        dpos = DockPosition.LEFT
                    elif position_str == 'Right':
                        dpos = DockPosition.RIGHT
                    elif position_str == 'Top':
                        dpos = DockPosition.TOP
                    elif position_str == 'Bottom':
                        dpos = DockPosition.BOTTOM
                    elif position_str == 'Center':
                        dpos = DockPosition.CENTER
                    elif position_str == 'CenterBefore':
                        dpos = DockPosition.CENTER_BEFORE
                        
                except Exception, e:
                    continue
                                
                dgt = g.add_item(item, dpos, id)
                dgt.set_visible(item.default_visible)

                return dgt

        return None

    def add_top_level(self, w, x, y):
        """
        
        Arguments:
        - `w`:
        - `x`:
        - `y`:
        """
        w.set_parent(self)
        w.x = x
        w.y = y

        self.top_levels.append(w)
    
    def remove_top_level(self, w):
        """
        
        Arguments:
        - `w`:
        """
        
        w.unparent()
        self.top_levels.remove(w)
        self.queue_resize()
    

    def show_placeholder(self):
        """
        """
        self.container.show_placeholder()

    def dock_in_placeholder(self, item):
        """
        
        Arguments:
        - `item`:
        """
        self.container.dock_in_placeholder(item)

    def hide_placeholder(self):
        """
        """
        self.container.hide_placeholder()
    
    def update_placeholder(self, item, width, height, allow_docking):
        """
        
        Arguments:
        - `item`:
        - `size`:
        - `allow_docking`:
        """
        self.container.update_placeholder(item, width, height, allow_docking)
    
    
    def bar_dock(self, pos, item, size):
        """
        
        Arguments:
        - `pos`:
        - `item`:
        - `size`:
        """
        if pos == gtk.POS_TOP:
            return self.dockbar_top.add_item(item, size)
        elif pos == gtk.POS_BOTTOM:
            return self.dockbar_bottom.add_item(item, size)
        elif pos == gtk.POS_LEFT:
            return self.dockbar_left.add_item(item, size)
        elif pos == gtk.POS_RIGHT:
            return self.dockbar_right.add_item(item, size)
        else:
            raise Exception("InvalidOperationException")
        
    
    def autoshow(self, item, bar, size):
        """
        
        Arguments:
        - `item`:
        - `bar`:
        - `size`:
        """
        aframe = AutoHideBox(self, item, bar.position, size)

        x, y = 0, 0
        if bar == self.dockbar_left or bar == self.dockbar_right:
            aframe.props.height_request = self.allocation.height -\
                self.dockbar_top.props.height_request -\
                self.dockbar_bottom.props.height_request

            aframe.props.width_request = size
            y = self.dockbar_top.props.height_request
            if bar == self.dockbar_left:
                x = bar.allocation.width
            else:
                x = self.allocation.width - bar.size_request()[0] - size
        else:
            aframe.props.width_request = self.allocation.width -\
                self.dockbar_left.props.width_request -\
                self.dockbar_right.props.width_request

            aframe.props.height_request = size
            if bar == self.dockbar_top:
                y = bar.allocation.height
            else:
                y = self.allocation.height - bar.allocation.height - size
        
        self.add_top_level(aframe, x, y)
        aframe.animate_show()
        return aframe

    def autohide(self, item, widget, animate):
        """
        
        Arguments:
        - `item`:
        - `widget`:
        - `animate`:
        """
        if animate:
            def frame_autohide_delegate(event):
                if widget:
                    self.autohide(item, widget, False)
                    
            widget.connect("hide", frame_autohide_delegate)
            widget.animate_hide()
        else:
            parent = item.widget.parent
            parent.remove(item.widget)
            self.remove_top_level(widget)
            widget.destroy()    
    
    def do_size_allocate(self, allocation):
        """
        
        Arguments:
        - `allocation`:
        """
        gtk.HBox.do_size_allocate(self, allocation)
        for tl in self.top_levels:
            width, height = tl.size_request()
            tl.size_allocate(gtk.gdk.Rectangle(allocation.x + tl.x,
                                               allocation.y + tl.y,
                                               width,
                                               height))
   
