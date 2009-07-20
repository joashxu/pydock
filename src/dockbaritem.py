import gtk
from gtk import gdk

UINT32_MAX_VALUE = 2**32

class DockBarItem(gtk.EventBox):
    """
    """

    def __init__(self, bar, it, size):
        """
        
        Arguments:
        - `bar`:
        - `it`:
        - `size`:
        """
        self.bar = bar
        self.it = it
        self.size = size
        
        self.box = None
        self.autoshow_frame = None
        self.hidden_frame = None
        
        self.autoshow_timeout = UINT32_MAX_VALUE
        self.autohide_timeout = UINT32_MAX_VALUE
        self.size = None


        self.props.events = self.props.events | gdk.ENTER_NOTIFY_MASK | gdk.LEAVE_NOTIFY_MASK
        self.props.visible_window = False
        self.update_tab()

    def close(self):
        """
        """
        self.unschedule_autoshow()
        self.unschedule_autohide()
        self.auto_hide(False)
        self.bar.remove_item(self)
        self.destroy()

    def update_tab(self):
        """
        """
        if self.box != None:
            self.remove(self.box)
            self.box.destroy()

        if self.bar.orientation == gtk.ORIENTATION_HORIZONTAL:
            self.box = HBox()
        else:
            self.box = VBox()

        if it.icon:
            img = gtk.Image
            img.set_from_icon_name(it.icon, gtk.ICON_SIZE_MENU)
            self.box.pack_start(img, False, False, 0)

        if it.label:
            lab = gtk.Label(it.label)
            lab.props.use_markup = True
            if self.bar.orientation == gtk.ORIENTATION_VERTICAL:
                lab.props.angle = 270
            
            self.box.pack_start(lab, True, True, 0)

        self.box.show_all()
        self.box.props.border_widt = 3
        self.box.props.spacing = 2
        self.add(self.box)

    @property
    def dock_item(self):
        """
        """
        return self.it
    
    def do_hide(self):
        """
        """
        gtk.EventBox.do_hide(self)

        self.unschedule_autoshow()
        self.unschedule_autohide()

        self.autohide(False)


    def do_expose_event(self, event):
        """
        
        Arguments:
        - `event`:
        """
        self.paint_box(self.window, 
                       gtk.STATE_NORMAL,
                       gtk.SHADOW_OUT,
                       event.area,
                       self,
                       "",
                       self.allocation.x,
                       self.allocation.y,
                       self.allocation.width,
                       self.allocation.height)

        gtk.EventBox.do_expose_event(self)

    def present(self, give_focus):
        """
        
        Arguments:
        - `give_focus`:
        """
        self.autoshow()

        if give_focus:
            def delegate():
                self.it.set_focus()
                self.schedule_autohide(False)
                return False
            
            gobject.timeout_add(200, delegate)
    
    def autoshow(self):
        """
        """
        self.unschedule_autohide()

        if self.autoshow_frame == None:
            if self.hidden_frame != None:
                self.bar.frame.autohide(it, self.hidden_frame, False)

            self.autoshow_frame = self.bar.frame.autoshow(it, bar, size)
            self.autoshow_frame.connect("enter-notify-event", self.on_frame_enter)
            self.autoshow_frame.connect("leave-notify-event", self.on_frame_leave)
            self.autoshow_frame.connect("key-press-event", self.on_frame_keypress)

    def autohide(self, animate):
        """
        
        Arguments:
        - `animate`:
        """
        self.unschedule_autoshow()

        if self.autoshow == None:
            self.size = self.autoshow_frame.size
            self.hidden_frame = self.authoshow_frame

            def delegate():
                self.hidden_frame = None
            
            self.autoshow_frame.connect("hide", delegate)
            self.bar.frame.autohide(it, self.autoshow_frame, animate)

            self.autoshow_frame.disconnect_by_func(self.on_frame_enter)
            self.autoshow_frame.disconnect_by_func(self.on_frame_leave)
            self.autoshow_frame.disconnect_by_func(self.on_frame_keypress)
            
            self.autoshow_frame = None

    def schedule_autoshow(self):
        """
        """
        self.unschedule_autohide()

        if self.autoshow_timeout == UINT32_MAX_VALUE:
            def delegate():
                self.autoshow_timeout = UINT32_MAX_VALUE
                self.autoshow()
                return False

            self.autoshow_timeout = gobject.timeout_add(
                self.bar.frame.autoshow_delay,
                delegate)
    
    def schedule_autohide(self, cancel_autoshow, force=False):
        """
        
        Arguments:
        - `cancel_autoshow`:
        - `force`:
        """
        
        if self.cancel_autoshow():
            self.unschedule_autoshow()

        if force:
            it.widget.set_focus_child(None)

        if self.autohide_timeout == UINT32_MAX_VALUE:
            def delegate():
                if self.it.widget.get_focus_child != None:
                    return True

                self.autohide_timeout = UINT32_MAX_VALUE
                self.autohide(True)
                return False

            self.autohide_timeout = gobject.timeout_add(
                0 if force else self.bar.autohide_delay,
                delegate)

    def unschedule_autoshow(self):
        """
        """
        if self.autoshow_timeout != UINT32_MAX_VALUE:
            gobject.source_remove(self.autoshow_timeout)
            self.autoshow_timeout = UINT32_MAX_VALUE

    def unschedule_autohide(self):
        """
        """
        if self.autohide_timeout != UINT32_MAX_VALUE:
            gobject.source_remove(self.autohide_timeout)
            self.autohide_timeout = UINT32_MAX_VALUE

    def do_enter_notify_event(self, event):
        """
        
        Arguments:
        - `event`:
        """
        self.schedule_autoshow()
        self.modify_bg(gtk.STATE_NORMAL, self.bar.style.background[gtk.STATE_PREFLIGHT])

        return gtk.EventBox.do_enter_notify_event(self, event)

    def do_leave_notify_event(self, event):
        """
        
        Arguments:
        - `event`:
        """
        
        self.schedule_autohide(True)
        self.modify_bg(gtk.STATE_NORMAL, self.bar.style.background[gtk.STATE_NORMAL])

        return gtk.EventBox.do_leave_notify_event(self, event)
    
    def on_frame_enter(self, s, event):
        """
        
        Arguments:
        - `s`:
        - `event`:
        """
        self.autoshow()
    
    def on_frame_keypress(self, s, event):
        """
        
        Arguments:
        - `s`:
        - `event`:
        """
        keyname = gtk.gdk.keyval_name(event.keyval)

        if keyname == "Escape":
            self.schedule_autohide(True, True)

    def on_frame_leave(self, s, event):
        """
        
        Arguments:
        - `s`:
        - `event`:
        """
        if event.detail != gtk.gdk.NOTIFY_INFERIOR:
            self.schedule_autohide(True)

    def do_button_press_event(self, event):
        """
        
        Arguments:
        - `event`:
        """
        if event.button == 1:
            self.autoshow()
        elif event.button == 3:
            self.it.show_dock_popup_menu(event.time)
        return gtk.EventBox.do_button_press_event(self, event)
    
    
    


    
