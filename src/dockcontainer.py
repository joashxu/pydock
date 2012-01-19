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
   
    hresize_cursor = gtk.gdk.Cursor(gtk.gdk.SB_H_DOUBLE_ARROW)
    vresize_cursor = gtk.gdk.Cursor(gtk.gdk.SB_V_DOUBLE_ARROW)
    
    def __init__(self, frame):
        """
        
        Arguments:
        - `frame`:
        """

        ## Attribute
        #
        self.layout = None 
        self.needs_relayout = True
        
        self.current_handle_index = -1
        self.current_handle_group = None
        self.dragging = False
        self.drag_pos = -1
        self.drag_size = -1
        self.placeholderwindow = None        

        self.notebooks = []
        self.items = []

        ## Constructor
        #
        gtk.Container.__init__(self)

        self.props.events = gdk.BUTTON_PRESS_MASK | gdk.BUTTON_RELEASE_MASK | gdk.POINTER_MOTION_MASK | gdk.LEAVE_NOTIFY_MASK
        self.frame = frame        


    ## gtk.Widget override
    #
    
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
                colormap=self.get_colormap(),
                visual=self.get_visual(),
                event_mask=self.get_events() | gdk.EXPOSURE_MASK
                        | gdk.BUTTON1_MOTION_MASK 
                        | gdk.BUTTON_PRESS_MASK
                        | gdk.BUTTON_RELEASE_MASK)

        self.window.set_user_data(self)
        self.style.attach(self.window)
        self.style.set_background(self.window, gtk.STATE_NORMAL)

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

        if not self.layout:
            return

        rect.x, rect.y = 0, 0
        self.layout_widgets()
        self.layout.size = -1
        self.layout.size_allocate(rect)
    
    def do_unrealize(self):
        """
        """
        self.window.destroy()


    def do_expose_event(self, event):
        """
        
        Arguments:
        - `event`:
        """
        gtk.Container.do_expose_event(self, event)

        if self.layout:            
            self.layout.draw(event.area, 
                             self.current_handle_group,
                             self.current_handle_index)    

    def do_motion_notify_event(self, event):
        """
        
        Arguments:
        - `widget`:
        - `event`:
        """
        if self.dragging:
            new_pos = event.x if self.current_handle_group.type == DockGroupType.HORIZONTAL else event.y
            if new_pos != self.drag_pos:
                
                n_size = self.drag_size + (new_pos - self.drag_pos)
                self.current_handle_group.resize_item(self.current_handle_index, n_size)
                
                self.layout.draw_separators(self.allocation, 
                                            self.current_handle_group,
                                            self.current_handle_index,
                                            True)
                
                
        elif self.layout and self.placeholderwindow == None:
            grp, index = self.find_handle(self.layout, event.x, event.y)
            
            if grp and index != None:
                if self.current_handle_group != grp or self.current_handle_index != index:
                    if grp.type == DockGroupType.HORIZONTAL:
                        self.window.set_cursor(self.hresize_cursor)
                    else:                           
                        self.window.set_cursor(self.vresize_cursor)
                    
                    self.current_handle_group = grp
                    self.current_handle_index = index
                    
                    self.layout.draw_separators(self.allocation, 
                                                self.current_handle_group, 
                                                self.current_handle_index, 
                                                True)
            elif self.current_handle_group:
                self.reset_handle_highlight() 
    
    def do_leave_notify_event(self, event):
        if not self.dragging and event.mode != gtk.gdk.CROSSING_GRAB:
            self.reset_handle_highlight()    
    
    def do_button_press_event(self, ev):
        if self.current_handle_group:
            self.dragging = True
            self.drag_pos = ev.x if self.current_handle_group.type == DockGroupType.HORIZONTAL else ev.y
            
            obj = self.current_handle_group.visible_objects[self.current_handle_index]
            self.drag_size = obj.allocation.width if self.current_handle_group.type == DockGroupType.HORIZONTAL else obj.allocation.height        
    
    def do_button_release_event(self, ev):
        self.dragging = False
    
    def do_remove(self, ev):
        pass
    
    ## gtk.Container
    #
    def do_forall(self, include_internals, callback, callback_data):
        widgets = []
        
        for w in self.notebooks:
            widgets.append(w)
            
        for it in self.items:
            if it.has_widget and it.widget.parent == self:
                widgets.append(it.widget)
              
        for w in widgets:
            callback(w, callback_data)
    
    ## Separator handling
    #
    def reset_handle_highlight(self):        
        self.window.set_cursor(None)
        self.current_handle_group = None
        self.current_handle_index = -1
        
        if self.layout:
            self.layout.draw_separators(self.allocation, None, -1, True) 
    
    
    def find_handle(self, grp, x, y):
        found_grp, object_index = None, None

        if grp.allocation != None:
            x_x = grp.allocation.x
            y_y = grp.allocation.y
            x_right = grp.allocation.x + grp.allocation.width
            y_bottom = grp.allocation.height
        else:
            x_x, y_y = 0, 0
            x_right, y_bottom = 0, 0
        
        x_in_allocation = True if x_x <= x <= x_right else False
        y_in_allocation = True if y_y <= y <= y_bottom else False
        
        if grp.type != DockGroupType.TABBED and x_in_allocation and y_in_allocation:        
            for n, obj in enumerate(grp.visible_objects):
                if n < (len(grp.dock_objects) - 1):   
                    
                    if obj.allocation != None:                 
                        x_right = obj.allocation.x + obj.allocation.width
                        y_bottom = obj.allocation.height 
                    else:
                        x_right, y_bottom = 0, 0
                    
                    x_in_between = x_right < x < x_right + self.frame.total_handle_size
                    y_in_between = y_bottom < y < y_bottom + self.frame.total_handle_size
                    
                    if (grp.type == DockGroupType.HORIZONTAL and x_in_between) or\
                       (grp.type == DockGroupType.VERTICAL and y_in_between):    

                        found_grp, object_index = grp, n                              
                        return found_grp, object_index
                        
                if isinstance(obj, DockGroup):
                    return self.find_handle(obj, x, y)
                            
        return found_grp, object_index
        
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
        
    def relayout_widgets(self):
        """
        """
        self.needs_relayout = True
        self.queue_resize()
    
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

    def store_allocation(self):
        """
        """
        if self.layout:
            self.layout.store_allocation()
            
    ## Docking and Placeholder
    #
    def find_dock_group_item(self, id):
        """
        
        Arguments:
        - `id`:
        """
        if self.layout == None:
            return None
        else:
            return self.layout.find_dock_group_item(id)
    
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
            gitem.parent_group.replace_item (gitem, dummy_item);
            dock_delegate(item)
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
