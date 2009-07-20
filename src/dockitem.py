import gtk
from gtk import gdk

from dockitemcontainer import DockItemContainer
from dockitembehavior import DockItemBehavior

class DockItem(object):
    """
    """

    def __init__(self, frame, id, widget=None):
        """
        
        Arguments:
        - `frame`:
        - `id`:
        """
        self.frame = frame
        self.id = id

        self._widget = None
        self._content = None
        self.default_visible = True
        self.default_location = ""
        self.default_width = -1
        self.default_height = -1
        self._label = ""
        self.icon = ""
        self.expand = False
        self.draw_frame = True
        self._behavior = DockItemBehavior.NORMAL
        self.floating_window = None
        self.dockbar_item = None
        self.last_visible_status = False
        self.last_content_visible_status = False
        self.getting_content = False
        self.is_position_marker = False
        self.sticky_visible = False
        
        self.visible_changed = None
        self.content_visible_changed = None     
        self.content_required = None

        if widget:
            self.content = widget

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label = value
        if self.widget != None:
            self.widget.label = value
        self.frame.update_title(self)
        if self.floating_window != None:
            self.floating_window.set_title(self.get_window_title())

    @property
    def visible(self):
        return self.frame.get_visible(self)

    @visible.setter
    def visible(self, value):
        self.sticky_visible = value;
        self.frame.set_visible(self, value);
        self.update_visible_status();

    @property
    def status(self):
        return self.frame.get_status(self)

    @status.setter
    def status(self, value):
        return self.frame.set_status(self, value)

    @property
    def widget(self):
        if self._widget == None:
            self._widget = DockItemContainer(self.frame, self)
            self._widget.label = self.label
            if self.content_required != None:
                self.getting_content = True
                self.content_required(self, None)

            self._widget.update_content()
            self._widget.connect("show", self.update_content_visible_status)
            self._widget.connect("hide", self.update_content_visible_status)
            self._widget.connect("parent-set", self.update_content_visible_status)

        return self._widget
    
    @property
    def content(self):
        return self._content
    
    @content.setter
    def content(self, value):
        self._content = value
        if not self.getting_content and self._widget != None:
            self.widget.update_content

    @property
    def has_widget(self):
        return self._widget != None

    @property
    def behavior(self):
        return self._behavior

    @behavior.setter
    def behavior(self, value):
        self._behavior = value
        if self.widget != None:
            self.widget.update_behavior()

    def present(self, give_focus):
        if self.dockbar_item != None:
            self.dockbar_item.present(give_focus)
        else:
            self.frame.present(self, give_focus)

    @property
    def content_visible(self):
        if self._widget == None:
            return False

        return self.widget.parent != None and self.widget.props.visible

    def set_focus(self):
        self.widget.child_focus(gtk.DIR_TAB_FORWARD)

        win = self.widget.get_toplevel()
        if win == None:
            return

        if win.get_focus() != None:
            c = win.get_focus().get_parent()
            if len(c.get_children()) == 0:
                win.set_focus(c)

    def update_visible_status(self):
        vis = self.frame.get_visible(self)
        if vis != self.last_visible_status:
            self.last_visible_status = vis
            if self.visible_changed != None:
                self.visible_changed(self, None)
        self.update_content_visible_status()

    def update_content_visible_status(self, ob=None, event=None):
        vis = self.content_visible
        if vis != self.last_content_visible_status:
            self.last_content_visible_status = vis
            if self.content_visible_changed != None:
                self.content_visible_changed(self, None)

    def show_widget(self):
        """
        """
        if self.floating_window != None:
            self.floating_window.show()

        if self.dockbar_item != None:
            self.dockbar_item.show()

        self.widget.show()

    def hide_widget(self):
        """
        """
        if self.floating_window != None:
            self.floating_window.hide()
        elif self.dockbar_item != None:
            self.dockbar_item.hide()
        elif self.widget != None:
            self.widget.hide()

    def set_float_mode(self, rect):
        self.reset_bar_undock_mode()

        if self.floating_window == None:
            if self.widget.get_parent() != None:
                self.widget.unparent()

            self.floating_window = gtk.Window()
            self.floating_window.set_title(self.get_window_title())
            self.floating_window.props.transient_for = self.frame.get_toplevel()
            self.floating_window.props.type_hint = gtk.gdk.WINDOW_TYPE_HINT_UTILITY
            self.floating_window.add(self.widget)

            def mini_function(o, a):
                if self.behavior == DockItemBehavior.CANT_CLOSE:
                    self.status = DockItemStatus.Dockable
                else:
                    self.visible = False

            self.floating_window.connect("delete-event", mini_function)
            self.floating_window.move(rect.x, rect.y)
            self.floating_window.resize(rect.width, rect.height)
            self.floating_window.show()
            self.widget.update_behavior()
            self.widget.show()

    def reset_float_mode(self):
        if self.floating_window != None:
            self.floating_window.remove(self.widget)
            self.floating_window.destroy()
            self.floating_window = None

            self.widget.update_behavior()

    @property
    def floating_position(self):
        if self.floating_window != None:
            x, y = self.floating_window.get_position()
            w, h = self.floating_window.get_size()

            return gdk.Rectangle(x, y, w, h)
        else:
            return gdk.Rectangle()

    def reset_mode(self):
        self.reset_float_mode()
        self.reset_bar_undock_mode()

    def set_autohide_mode(self, pos, size):
        self.reset_mode()
        if self.widget != None:
            self.widget.unparent()

        self.dockbar_item = self.frame.bar_dock(pos, self, size)
        if self.widget != None:
            self.widget.update_behavior()

    def reset_bar_undock_mode(self):
        if self.dockbar_item != None:
            self.dockbar_item.close()
            self.dockbar_item = None
            if self.widget != None:
                self.widget.update_behavior()

    @property
    def autohide_size(self):
        if self.dockbar_item != None:
            return dockbar_item.size
        else:
            return -1

    def get_window_title(self):
        return self.label

    def show_dock_popup_menu(self, time):
        menu = gtk.Menu()

        if (self.behavior & DockItemBehavior.CANT_CLOSE) == 0:
            mitem = gtk.MenuItem("Hide")
            def activated_delegate(wdg, evt):
                self.visible = False

            mitem.connect("activated", activated_delegated)

        citem = gtk.CheckMenuItem("Dockable")
        citem.props.active = self.status = DockItemStatus.DockItemStatus.DOCKABLE
        citem.props.draw_as_radio = True

        def toggled_delegate(wdg, evt):
            self.status = DockItemStatus.FLOATING
                
        citem.connect("toggled", toggled_delegate)
        menu.append(citem)

        if (self.behavior & DockItemBehavior.NEVER_FLOATING) == 0:
            citem = CheckMenuItem("Floating")
            citem.props.active = self.status = DockItemStatus.FLOATING
            citem.props.draw_as_radio = True

            def toggled_delegate(wdg, evt):
                self.status = DockItemStatus.FLOATING

            citem.connect("toggled", toggled_delegate)            
            menu.append(citem)

        if (self.behavior & DockItemBehavior.CANT_AUTOHIDE) == 0:
            citem = CheckMenuItem("Auto Hide")
            citem.props.active = self.status = DockItemStatus.AUTOHIDE
            citem.props.draw_as_ratio = True

            def toggled_delegate(wdg, evt):
                self.status = DockItemStatus.FLOATING

            citem.connect("toggled", toggled_delegate)
            menu.append(citem)

        menu.show_all()
        menu.popup(None, None, None, 3, time)




    

    
        
    
    
    
                
                
