import gtk
import gobject

from gtk import gdk
from dockgroup import DockGroup
from dockgrouptype import DockGroupType
from dockitembehavior import DockItemBehavior
from placeholderwindow import PlaceHolderWindow
from dockitemstatus import DockItemStatus
from dockgroupitem import DockGroupItem
from dockitem import DockItem

class DockContainer(gtk.Container):
    """
    """
    __gsignals__ = { 'expose-event' : 'override' }

    def __init__(self, frame):
        """
        
        Arguments:
        - `frame`:
        """

        gtk.Container.__init__(self)

        self.frame = frame
        
        self.props.events = gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.LEAVE_NOTIFY_MASK        

        self.layout = None 
        self.needs_relayout = True
        
        self.current_handle_index = -1
        self.current_handle_group = None
        self.dragging = False
        self.drag_pos = -1
        self.drag_size = -1
        self.placeholderwindow = None

        self.hresize_cursor = gtk.gdk.Cursor(gtk.gdk.SB_H_DOUBLE_ARROW)
        self.vresize_cursor = gtk.gdk.Cursor(gtk.gdk.SB_V_DOUBLE_ARROW)

        self.notebooks = []
        self.items = []

    def do_size_request(self, requisition):
        """
        
        Arguments:
        - `requisition`:
        """
        
        if self.layout:
           self.layout_widgets()
           requisition.width, requisition.height = self.layout.size_request()

    def do_size_allocate(self, rect):
        """
        
        Arguments:
        - `allocation`:
        """
        gtk.Container.do_size_allocate(self, rect)

        print "satu"
        if not self.layout:
            return

        print "dua"
        rect.x, rect.y = 0, 0
        self.layout_widgets()
        self.layout.size = -1
        self.layout.size_allocate(rect)
    
    def do_realize(self):
        """
        """
        
        self.set_flags(self.flags() | gtk.REALIZED)

        self.window = gdk.Window(
                self.get_parent_window(),
                width=self.allocation.width,
                height=self.allocation.height,
                window_type=gdk.WINDOW_CHILD,
                wclass=gdk.INPUT_OUTPUT,
                
                event_mask=self.get_events() | gdk.EXPOSURE_MASK
                        | gdk.BUTTON1_MOTION_MASK | gdk.BUTTON_PRESS_MASK
                        | gtk.gdk.POINTER_MOTION_MASK
                        | gtk.gdk.POINTER_MOTION_HINT_MASK)

        # Associate the gdk.Window with ourselves, Gtk+ needs a reference
        # between the widget and the gdk window
        self.window.set_user_data(self)

        # Attach the style to the gdk.Window, a style contains colors and
        # GC contextes used for drawing
        self.style.attach(self.window)

        # The default color of the background should be what
        # the style (theme engine) tells us.
        self.style.set_background(self.window, gtk.STATE_NORMAL)
        self.window.move_resize(*self.allocation)
        
        # self.style is a gtk.Style object, self.style.fg_gc is
        # an array or graphic contexts used for drawing the forground
        # colours
        #self.gc = self.style.fg_gc[gtk.STATE_NORMAL]

        self.connect("motion_notify_event", 
                     self.motion_notify_event)


    def do_unrealize(self):
        """
        """
        self.window.destroy()


    def do_expose_event(self, event):
        """
        
        Arguments:
        - `event`:
        """
        print "exposed"
        gtk.Container.do_expose_event(self, event)

        if self.layout:
            self.layout.draw(event, 
                             self.current_handle_group,
                             self.current_handle_index)    

    def layout_widgets(self):
        """
        """
        if not self.needs_relayout:
            return

        self.needs_relayout = False

        tabbed_group = []
        self.get_tabbed_groups(self.layout, tabbed_group)
        
        for index, item in enumerate(tabbed_group):
            ts = None

            if index < len(self.notebooks):
                ts = self.notebooks[index]
            else:
                ts = TabStrip()
                ts.show()
                self.notebooks.append(ts)
                ts.parent = self

            item.update_notebook(ts)
            

        for index in range(len(self.notebooks)-1, len(tabbed_group)-1, -1):
            ts = self.notebooks[index]

            ts.clear()
            ts.unparent()
            ts.destroy()
            self.notebooks.remove_at(index)

        self.layout.layout_widgets()

    def get_tabbed_groups(self, dock_group, tabbed_group):
        """
        
        Arguments:
        - `dock_group`:
        - `tabbed_group`:
        """
        
        if dock_group.type == DockGroupType.TABBED:
            if len(dock_group.visible_objects) > 1:
                tabbed_group.append(dock_group)
            else:
                dock_group.reset_notebook()
        else:
            dock_group.reset_notebook()
            for dock_object in dock_group.dock_objects:
                if isinstance(dock_object, DockGroup):
                    self.get_tabbed_groups(dock_object, tabbed_group)

    def store_allocation(self):
        """
        """
        if self.layout:
            self.layout.store_allocation()
    

    def motion_notify_event(self, widget, event):
        """
        
        Arguments:
        - `widget`:
        - `event`:
        """
        pass
    
    ## Layout
    #
    def load_layout(self, dl):
        """
        
        Arguments:
        - `dl`:
        """
        sickyOnTop = []

        for it in self.items:
            if (it.behavior & DockItemBehavior.STICKY) != 0:
                gitem = self.find_dock_group_item(it.id)
                if gitem and gitem.parent_group.is_selected_page(it):
                    sickyOnTop.append(it)

        if self.layout:
            self.layout.store_allocation()

        self.layout = dl
        self.layout.restore_allocation()

        for it in self.items:
            if (it.behavior & DockItemBehavior.STICKY) != 0:
                it.visible = it.sticky_visible
            if self.layout.find_dock_group_item(it.id) == None:
                it.hide_widget()

        self.relayout_widgets()

        for it in sickyOnTop:
            it.Present(False)
                    

    def find_dock_group_item(self, id):
        """
        
        Arguments:
        - `id`:
        """
        if self.layout == None:
            return None
        else:
            return self.layout.find_dock_group_item(id)
        
    def relayout_widgets(self):
        """
        """
        self.needs_relayout = True
        self.queue_resize()
    
    def do_forall(self, include_internals, callback, callback_data):
        widgets = []
        for w in self.notebooks:
            widgets.append(w)
        for it in self.items:
            if it.has_widget and it.widget.parent == self:
                widgets.append(it.widget)
        for w in widgets:
            callback(w, callback_data)        
        
    def show_placeholder(self):
        self.placeholderwindow = PlaceHolderWindow(self.frame)
        
    def update_placeholder(self, item, width, height, allow_docking):
        if self.placeholderwindow == None:
            return False
        
        px, py = self.get_pointer()
        self.placeholderwindow.allow_docking = allow_docking
        
        dock_delegate, rect = self.layout.get_dock_target(item, px, py)
        
        if allow_docking and dock_delegate and rect:
            ox, oy = self.window.get_origin()
            
            self.placeholderwindow.relocate(ox + rect.x, 
                                            oy + rect.y,
                                            rect.width,
                                            rect.height,
                                            True)
            self.placeholderwindow.show()
            return True
        else:
            ox, oy = self.window.get_origin()
            
            self.placeholderwindow.relocate(ox + px - width/2,
                                            oy + py - 18,
                                            width,
                                            height,
                                            False)
            self.placeholderwindow.show()
            
        return False
    
    def dock_in_placeholder(self, item):
        if self.placeholderwindow == None or not self.placeholderwindow.props.visible:
            return
        
        item.status = DockItemStatus.DOCKABLE
        
        px, py = self.get_pointer()
        
        dock_delegate, rect = self.layout.get_dock_target(item, px, py)
        if self.placeholderwindow.allow_docking and dock_delegate and rect:
            dummy_item = DockGroupItem(self.frame, DockItem(self.frame, "__dummy"))
            gitem = self.layout.find_dock_group_item(item.id)
            dock_delegate(item)
            if dummy_item.parent_group:
                dummy_item.parent_group.remove(dummy_item)
            self.relayout_widgets()
        else:            
            gi = self.find_dock_group_item(item.id)
            px, py = self.placeholderwindow.get_position()
            pw, ph = self.placeholderwindow.get_size()
            gi.float_rect = gdk.Rectangle(px, py, pw, ph)
            item.status = DockItemStatus.FLOATING        
    
    def hide_placeholder(self):
        if self.placeholderwindow != None:
            self.placeholderwindow.destroy()
            self.placeholderwindow = None
            
        
    
gobject.type_register(DockContainer) 
