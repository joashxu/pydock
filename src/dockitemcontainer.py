import gtk
from gtk import gdk

from dockitembehavior import DockItemBehavior
from dockitemstatus import DockItemStatus

class DockItemContainer(gtk.VBox):

    pix_close = gdk.pixbuf_new_from_file("stock-close-12.png")
    pix_autohide = gdk.pixbuf_new_from_file("stock-auto-hide.png")
    pix_dock = gdk.pixbuf_new_from_file("stock-dock.png")

    def __init__(self, frame=None, item=None):
        gtk.VBox.__init__(self)

        self.title = None
        self.btn_close = None
        self.btn_dock = None
        self.txt = ""
        self.header = None
        self.header_alignment = None
        self.widget = None
        self.frame = frame
        self.item = item
        self.border_frame = None
        self.allow_placeholder_docking = False
        self.pointer_hover = False
        self.tips = gtk.Tooltips()

        self.fleur_cursor = gdk.Cursor(gtk.gdk.FLEUR)
        self.hand_cursor = gdk.Cursor(gtk.gdk.HAND2)        

        self.props.resize_mode = gtk.RESIZE_QUEUE
        self.props.spacing = 0

        self.title = gtk.Label()
        self.title.props.xalign = 0
        self.title.props.xpad = 3
        self.title.props.use_markup = True

        self.btn_dock = gtk.Button()
        self.btn_dock.props.image = gtk.Image()
        self.btn_dock.props.image.set_from_pixbuf(self.pix_dock)
        self.btn_dock.props.relief = gtk.RELIEF_NONE
        self.btn_dock.props.can_focus = False
        self.btn_dock.set_size_request(17, 17)
        self.btn_dock.connect("clicked", self.on_click_btn_dock)

        self.btn_close = gtk.Button()
        self.btn_close.props.image = gtk.Image()
        self.btn_close.props.image.set_from_pixbuf(self.pix_close)
        self.btn_close.props.relief = gtk.RELIEF_NONE
        self.btn_close.props.can_focus = False
        self.btn_close.set_size_request(17, 17)
        self.btn_close.connect("clicked", self.on_click_btn_close)

        self.tips.set_tip(self.btn_close, "Hide", "")

        box = gtk.HBox(False, 0)
        box.pack_start(self.title, True, True, 0)
        box.pack_end(self.btn_close, False, False, 0)
        box.pack_end(self.btn_dock, False, False, 0)

        self.header_align = gtk.Alignment(0.0, 0.0, 1.0, 1.0)
        self.header_align.props.top_padding = 1
        self.header_align.props.bottom_padding = 1
        self.header_align.props.right_padding = 1
        self.header_align.props.left_padding = 1
        self.header_align.add(box)

        self.header = gtk.EventBox()
        self.header.props.events = self.header.props.events | gdk.KEY_PRESS_MASK | gdk.KEY_RELEASE_MASK
        self.header.connect("button-press-event", self.header_button_press)
        self.header.connect("button-release-event", self.header_button_release)
        self.header.connect("motion-notify-event", self.header_motion)
        self.header.connect("key-press-event", self.header_key_press)
        self.header.connect("key-release-event", self.header_key_release)
        self.header.add(self.header_align)
        self.header.connect("expose-event", self.header_expose)

        def realize_function(wdg):
            self.header.window.set_cursor(self.hand_cursor)

        self.header.connect("realize", realize_function)

        for w in [self.header, self.btn_dock, self.btn_close]:
            w.connect("enter-notify-event", self.header_enter_notify)
            w.connect("leave-notify-event", self.header_leave_notify)

        self.pack_start(self.header, False, False, 0)
        self.show_all()
        self.update_behavior()        

    def on_click_btn_close(self, widget):
        self.item.visible = False

    def on_click_btn_dock(self, widget):

        if self.item.status == DockItemStatus.AUTOHIDE or\
           self.item.status == DockItemStatus.FLOATING:
            self.item.status = DockItemStatus.DOCKABLE
        else:
            self.item.status = DockItemStatus.AUTOHIDE

    def update_content(self):
        if self.widget != None:
            self.widget.parent.remove(self.widget)
        self.widget = self.item.content

        if self.item.draw_frame:
            if self.border_frame == None:
                self.border_frame = gtk.Frame()
                self.border_frame.props.shadow_type = gtk.SHADOW_IN
                self.border_frame.show()
                self.pack_start(self.border_frame, True, True, 0)

            if self.widget != None:
                self.border_frame.add(self.widget)
                self.widget.show()
        elif self.widget != None:
            if self.border_frame != None:
                self.remove(self.border_frame)
                self.border_frame = None
            self.pack_start(self.widget, True, True, 0)
            self.widget.show()

    def update_behavior(self):
        self.btn_close.props.visible = (self.item.behavior & DockItemBehavior.CANT_CLOSE) == 0
        self.header.props.visible = (self.item.behavior & DockItemBehavior.LOCKED) == 0
        self.btn_dock.props.visible = (self.item.behavior & DockItemBehavior.CANT_AUTOHIDE) == 0

        if self.item.status == DockItemStatus.AUTOHIDE or\
           self.item.status == DockItemStatus.FLOATING:
            self.btn_dock.props.image = gtk.Image()
            self.btn_dock.props.image.set_from_pixbuf(self.pix_dock)                
            self.tips.set_tip(self.btn_dock, "Dock", "")
        else:
            self.btn_dock.props.image = gtk.Image()
            self.btn_dock.props.image.set_from_pixbuf(self.pix_autohide)
            self.tips.set_tip(self.btn_dock, "Auto Hide", "")

    def header_button_press(self, ob, event):
        if event.button == 1:
            self.frame.show_placeholder()
            self.header.window.set_cursor(self.fleur_cursor)
            self.frame.get_toplevel().connect("key-press-event", self.header_key_press)
            self.frame.get_toplevel().connect("key-release-event", self.header_key_release)
            self.allow_placeholder_docking = True
        elif event.button == 3:
            self.item.show_dock_popupmenu(args.event.time)

    def header_button_release(self, ob, event):
        if event.button == 1:
            self.frame.dock_in_placeholder(self.item)
            self.frame.hide_placeholder()
            if self.header.window != None:
                self.header.window.set_cursor(self.hand_cursor)

            self.frame.get_toplevel().disconnect_by_func(self.header_key_press)
            self.frame.get_toplevel().disconnect_by_func(self.header_key_release)

    def header_motion(self, ob, args):
        self.frame.update_placeholder(self.item, 
                                      self.allocation.width, 
                                      self.allocation.height, 
                                      self.allow_placeholder_docking)

    def header_key_press(self, ob, event):
        if event.state & gdk.CONTROL_MASK:
            self.allow_placeholder = False            
            self.frame.update_placeholder(self.item, 
                                          self.allocation.width, 
                                          self.allocation.heightFalse)

        keyname = gtk.gdk.keyval_name(event.keyval)

        if keyname == "Escape":
            self.frame.hide_placeholder()
            self.frame.get_toplevel().connect("key-press-event", self.header_key_press)
            self.frame.get_toplevel().connect("key-release-event", self.header_key_release)
            self.window.get_display().pointer_ungrab(0)

    def header_key_release(self, ob, event):
        if event.state & gdk.CONTROL_MASK:
            self.allow_placeholder_docking = True
            self.frame.update_placeholder(self.item, 
                                          self.allocation.width, 
                                          self.allocation.height,
                                          True)

    def header_expose(self, ob, event):
        rect = gdk.Rectangle(0, 0, self.header.allocation.width - 1, self.header.allocation.height)
        gc = self.frame.style.mid_gc[gtk.STATE_ACTIVE]\
                if self.pointer_hover else self.frame.style.mid_gc[gtk.STATE_NORMAL]

        self.header.window.draw_rectangle(gc, True, rect.x, rect.y, rect.width, rect.height)
        self.header.window.draw_rectangle(self.frame.style.dark_gc[gtk.STATE_NORMAL], 
                                          False, 
                                          rect.x,
                                          rect.y,
                                          rect.width,
                                          rect.height)
        
        for child in self.header.get_children():
            self.header.propagate_expose(child, event)
            
    def header_leave_notify(self, ob, event):
        self.pointer_hover = False
        self.header.queue_draw()
        
    def header_enter_notify(self, ob, event):
        self.pointer_hover = True
        self.header.queue_draw()
        
    @property
    def label(self):
        return self.txt
    
    @label.setter
    def label(self, value):
        self.title.set_markup("<small>%s</small>" % value)
        self.txt = value










        
