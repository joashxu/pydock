import gobject
import gtk
from gtk import gdk

from dockframetoplevel import DockFrameTopLevel

class AutoHideBox(DockFrameTopLevel):
    """
    """

    resize_cursor_w = gdk.Cursor(gdk.SB_H_DOUBLE_ARROW)
    resize_cursor_h = gdk.Cursor(gdk.SB_V_DOUBLE_ARROW)

    grip_size = 8

    def __init__(self, frame, item, pos, size):
        """
        
        Arguments:
        - `frame`:
        - `item`:
        - `pos`:
        - `size`:
        """
        self.frame = frame
        self.item = item
        self.position = pos
        self.target_size = size
        
        self.horiz = (pos == gtk.POS_LEFT) or (pos == gtk.POS_RIGHT)
        self.start_pos = (pos == gtk.POS_TOP) or (pos == gtk.POS_LEFT) 

        self.disposed = False
        self.inside_grip = False        
        self.animating = False
        self.resizing = False
        self.resize_pos = 0
        self.orig_size = 0
        self.orig_pos = 0
        self.target_pos = 0


        self.props.events = self.props.events | gdk.ENTER_NOTIFY_MASK | gdk.LEAVE_NOTIFY_MASK

        fr = None
        sep_box = gtk.EventBox()

        if horiz:
            fr = gtk.HBox()

            def delegate():
                sep_box.window.set_cursor(self.resize_cursor_w)

            sep_box.connect("realize", delegate)
            sep_box.props.width_request = self.grip_size
        else:
            fr = gtk.VBox()

            def delegate():
                sep_box.window.set_cursor(self.resize_cursor_h)

            sep_box.connect("realize", delegate)
            sep_box.props.height_request = self.grip_size

        sep_box.props.events = gdk.ALL_EVENT_MASK

        if pos == gtk.POS_LEFT or pos == gtk.POS_TOP:
            fr.pack_end(sep_box, False, False, 0)
        else:
            fr.pack_start(sep_box, False, False, 0)

        self.add(fr)
        self.show_all()

        self.scrollable = ScroballableContainer()
        self.scrollable.scroll_mode = False
        self.scrollable.show()
        self.scrollable.add(item.widget)
        item.widget.show()

        fr.pack_start(scrollable, True, True, 0)

        sep_box.connect("button-press-event", self.on_size_button_press)
        sep_box.connect("button-release-event", self.on_size_button_release)
        sep_box.connect("motion-notify-event", self.on_size_motion)
        sep_box.connect("expose-event", self.on_grip_expose)

        def enter_delegate():
            self.inside_grip = True
            sep_box.queue_draw()

        sep_box.connect("enter-notify-event", enter_delegate)

        def leave_delegate():
            self.inside_grip = False
            sep_box.queue_draw()

        sep_box.connect("leave-notify-event", leave_delegate)

        self.connect("hide", self.on_hidden)

    def animate_show(self):
        """
        """
        self.animating = True
        self.scrollable.scroll_mode = True
        self.scrollable.set_size(self.position, self.target_size)

        if position == gtk.POS_LEFT:
            self.props.width_request = 0
        elif position == gtk.POS_RIGHT:
            self.target_pos = self.x = self.x + self.props.width_request
            self.props.width_request = 0
        elif position == gtk.POS_TOP:
            self.props.height_request = 0
        elif position == gtk.POS_BOTTOM:
            self.target_pos = self.y = self.y + self.props.height_request
            self.props.height_request = 0

        gobject.timeout_add(10, self.run_animate_show)
    
     def animate_hide(self):
         """
         """
         self.animating = True
         self.scrollable.scroll_mode = True
         self.scrollable.set_size(self.position, self.target_size)

         gobject.timeout_add(10, self.run_animate_hide)

     def run_animate_show(self):
         """
         """
         if not self.animating:
             return False

         if self.position == gtk.POS_LEFT:
             self.props.width_request += 1 + (self.target_size - self.props.width_request) / 3
             if self.props.width_request < self.target_size:
                 return True
         elif self.position == gtk.POS_RIGHT:
             self.props.width_request += 1 + (self.target_size - self.props.width_request) / 3
             self.x = self.target_pos - self.props.width_request
             if self.props.width_request < self.target_size:
                 return True
         elif self.position == gtk.POS_TOP:
             self.props.height_request += 1 + (self.target_size - self.props.height_request) / 3
             if self.props.height_request < self.target_size:
                 return True
         elif self.position == gtk.POS_BOTTOM:
             self.props.height_request += 1 + (self.target_size - self.props.height_request) / 3
             self.y = self.target_pos - self.props.height_request
             if self.props.height_request < self.target_size:
                 return True

         self.scrollable.scroll_mode = False
         if self.horiz:
             self.props.width_request = self.target_size
         else:
             self.props.height_request = self.target_size

         self.animating = False
         
         return False
     
     def run_animate_hide(self):
         """
         """
         
         if not self.animating:
             return False

         if position == gtk.POS_LEFT:
             ns = self.props.width_request - 1 - self.props.width_request / 3
             if ns > 0:
                 self.props.width_request = ns
                 return True
         elif position == gtk.POS_RIGHT:
             ns = self.props.width_request - 1 - self.props.width_request / 3
             if ns > 0:
                 self.props.width_request = ns
                 self.x = self.target_pos - ns
                 return True
         elif position == gtk.POS_TOP:
             ns = self.props.height_request - 1 - self.props.height_request / 3
             if ns > 0:
                 self.props.height_request = ns
                 return True
         elif position == gtk.POS_BOTTOM:
             ns = self.props.height_request - 1 - self.props.height_request / 3
             if ns > 0:
                 self.props.height_request = ns
                 self.y = self.target_pos - ns
                 return True

         self.hide()
         self.animating = False

         return False

     def on_hide_event(self):
         """
         """
         self.animating = False
     
     
     @property
     def size(self):
         """
         """
         return self.props.width_request if horiz else self.props.height_request

     def on_size_button_press(self, ob, event):
         """
         
         Arguments:
         - `ob`:
         - `event`:
         """
         if event.button == 1 and not self.animating:
             if self.horiz:
                 self.resize_pos, n = self.get_toplevel().get_pointer()
                 self.orig_size = self.props.width_request

                 if not self.start_pos:
                     self.orig_pos = self.x + self.orig_size
             else:
                 n, self.resize_pos = self.get_toplevel().get_pointer()
                 self.orig_size = self.props.height_request
                 
                 if not self.start_pos:
                     self.orig_pos = self.y + self.orig_size

             self.resizing = True

     def on_size_button_release(self, ob, event):
         """
         
         Arguments:
         - `ob`:
         - `event`:
         """
         self.resizing = False

     def on_size_motion(self, ob, event):
         """
         
         Arguments:
         - `ob`:
         - `event`:
         """
         if self.resizing:
             if self.horiz:
                 new_pos, n = self.get_toplevel().get_pointer()
                 diff = new_pos - self.resize_pos if self.start_pos else self.resize_pos - new_pos
                 new_size = self.orig_size + diff

                 if new_size < self.get_child().props.width_request:
                     new_size = self.get_child().props.width_request:

                 if not self.start_pos:
                     self.x = self.orig_pos - new_size

                 self.props.width_request = new_size
             else:
                 n, new_pos = self.get_toplevel().get_pointer()
                 diff = new_pos - self.resize_pos if self.start_pos else self.resize_pos - new_pos
                 
                if new_size < self.get_child().props.height_request:
                    new_size = self.get_child().props.height_request

                if not self.start_pos:
                    self.y = self.orig_pos - new_size
                    
                self.props.height_request = new_size

             self.frame.queue_resize()

     def on_grip_expose(self, ob, event):
         """
         
         Arguments:
         - `ob`:
         - `event`:
         """
         handle_rect = ob.allocation
         handle_rect.x, handle_rect.y = 0, 0

         if self.position == gtk.POS_TOP:
             handle_rect.height -= 4
             handle_rect.y += 1
             
             gtk.Style.paint_hline(ob.window, gtk.STATE_NORMAL, event.area, ob, "", 0, ob.allocation.width, self.grip_size - 2)

         elif self.position == gtk.POS_BOTTOM:
             handle_rect.height -= 4
             handle_rect.y += 3

             gtk.Style.paint_hline(ob.window, gtk.STATE_NORMAL, event.area, ob, "", 0, ob.allocation.width, 0)

         elif self.position == gtk.POS_LEFT:
             handle_rect.width -= 4
             handle_rect.x += 1
             
             gtk.Style.paint_vline(ob.window, gtk.STATE_NORMAL, event.area, ob, "", 0, ob.allocation.height, self.grip_size - 2)

         elif self.position == gtk.POS_RIGHT:
             handle_rect.width -= 4
             handle_rect.x += 3

             gtk.Style.paint_vline(ob.window, gtk.STATE_NORMAL, event.area, ob, "", 0, ob.allocation.height, 0)

         orientation = gtk.ORIENTATION_VERTICAL if self.horiz else gtk.ORIENTATION_HORIZONTAL
         s = gtk.STATE_PREFLIGHT if self.inside_grip else gtk.STATE_NORMAL

         gtk.Style.paint_handle(ob.window, s, gtk.SHADOW_NONE, event.area, w, "paned", handle_rect.x, handle_rect.height, handle_rect.width, handle_rect.height, orientation)
         
     

class Scrollable(gtk.EventBox):
    """
    """

    def __init__(self ):
        """
        """

        gtk.EventBox.__init__(self)

        self._scroll_mode = False
        self.target_size = 0
        self.expand_pos = None

    @property
    def scroll_mode(self):
        """
        """
        return self._scroll_mode

    @scroll_mode.setter
    def scroll_mode(self, value):
        """
        
        Arguments:
        - `value`:
        """
        self._scroll_mode = value
        self.queue_resize()

    def set_size(self, expand_position, target_size):
        """
        
        Arguments:
        - `expand_position`:
        - `target_size`:
        """
        self.expand_pos = expand_position
        self.target_size = target_size

        self.queue_resize()

    def do_size_request(self, req):
        """
        
        Arguments:
        - `req`:
        """

        gtk.EventBox.do_size_request(self, req)

        if self.scroll_mode or self.get_child() == None:
            req.width, req.height = 0, 0
        else:
            req.width, req.height = self.get_child().get_size_request

    def do_size_allocate(self, alloc):
        """
        
        Arguments:
        - `alloc`:
        """
        
        if self.scroll_mode and self.get_child() != None:
            if self.expand_pos == gtk.POS_BOTTOM:
                alloc = gdk.Rectangle(alloc.x, alloc.y, alloc.width, self.target_size)
            elif self.expand_pos == gtk.POS_TOP:
                alloc = gdk.Rectangle(alloc.x, alloc.y - self.target_size + alloc.height, alloc.width, self.target_size)
            elif self.expand_pos == gtk.POS_RIGHT:
                alloc = gdk.Rectangle(alloc.x, alloc.y, self.target_size, alloc.height)
            elif self.expand_pos == gtk.POS_LEFT:
                alloc = gdk.Rectangle(alloc.x - self.target_size + alloc.width, alloc.y, self.target_size, alloc.height)


        gtk.EventBox.do_size_allocate(self, alloc)
    
