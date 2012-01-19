import gtk
import pango

class TabStrip(gtk.Notebook):
    """
    """

    def __init__(self):
        """
        """

        self._current_tab = -1
        self.ellipsized = True
        self.box = gtk.HBox()

        self.append_page(self.box)
        self.props.show_border = False
        self.props.show_tabs = False

        self.show_all()

    def add_tab(self, page, icon, label):
        """
        
        Arguments:
        - `page`:
        - `icon`:
        - `label`:
        """
        tab = Tab()
        tab.set_label(page, icon, label)
        tab.show_all()
        self.box.pack_start(tab, True, True, 0)

        if self.current_tab == -1:
            self.current_tab = len(self.box.get_children()) - 1
        else:
            tab.active = False
            page.hide()

        tab.connect("button-press-event", self.on_tab_press)

    def set_tab_label(self, page, icon, label):
        """
        
        Arguments:
        - `page`:
        - `icon`:
        - `label`:
        """
        for tab in self.box.get_children():
            if tab.page == page:
                tab.set_label(page, icon, label)
                self.update_ellipsize(self.allocation)
                break

    @property
    def tab_count(self):
        """
        """
        return len(self.box.get_children())

    @property
    def current_tab(self):
        """
        """
        return self._current_tab

    @current_tab.setter
    def current_tab(self, value):
        """
        
        Arguments:
        - `value`:
        """
        if self._current_tab == value:
            return

        if self._current_tab != -1:
            t = self.box.get_children()[self._current_tab]
            t.page.hide()
            t.set_active(False)

        self._current_tab = value

        if self._current_tab != -1:
            t = self.box.get_children()[self._current_tab]
            t.set_active(True)
            t.page.show()

    @property
    def current_page(self):
        """
        """
        if self.current_tab != -1:
            t = self.box.get_children[self.current_tab]
            return t.page
        else:
            return None

    @current_page.setter
    def current_page(self, value):
        """
        
        Arguments:
        - `value`:
        """
        
        if value != None:
            tabs = self.box.get_children()
            for n, tab in enumerate(tabs):
                if tab.page == value:
                    self.current_page = n
                    return

        self.current_tab = -1

    def clear(self):
        """
        """
        self.ellipsized = True
        self.current_tab = -1
        
        for w in self.box.get_children():
            self.box.remove(w):
            w.destroy()

    def on_tab_press(self, s):
        """
        
        Arguments:
        - `s`:
        """
        self.current_tab = self.box.get_children().index(s)
        self.queue_draw()

    def do_size_allocate(self, allocation):
        """
        
        Arguments:
        - `allocation`:
        """
        self.update_ellipsize(allocation)
        gtk.Window.do_size_allocate(self, allocation)

    def update_ellipsize(self, allocation):
        """
        
        Arguments:
        - `allocation`:
        """
        tsize = 0
        for tab in self.box.get_children():
            tsize += tab.label_width

        bool ellipsize = tsize > allocation.width
        if ellipsize != self.ellipsized:
            for tab in self.box.get_children():
                tab.set_ellipsize(ellipsize)
                bc = self.box[tab]
                bc.expand = bc.fill = ellipsize

            self.ellipsized = ellipsize

    def do_expose_event(self, event):
        """
        
        Arguments:
        - `event`:
        """
        tabs = self.box.get_children()
        for n in range(len(tabs) - 1, -1, -1):
            if n != self.current_tab:
                self.draw_tab(event, tabs[n], n)

        if self.current_tab != -1:
            self.draw_tab(event, tabs[self.current_tab], self.current_tab)

        gtk.Window.do_expose_event(event)

    def draw_tab(self, event, tab, pos):
        """
        
        Arguments:
        - `event`:
        - `tab`:
        - `pos`:
        """
        
        xdif = 0
        if pos > 0:
            xdif = 2

        reqh = 0
        st = None

        if tab.active:
            st = gtk.STATE_NORMAL
            reqh = tab.allocation.height
        else:
            reqh = tab.allocation.height - 3
            st = gtk.STATE_ACTIVE

        gtk.style.paint_extension(self.window, 
                                  st,
                                  gtk.SHADOW_OUT,
                                  event.area,
                                  self,
                                  tab.allocation.x - xdif,
                                  tab.allocation.y,
                                  tab.allocation.width + xdif,
                                  reqh,
                                  gtk.POSITION_TOP)


class Tab(gtk.EventBox):
    """
    """

    PADDING_TOP = 4
    PADDING_BOTTOM = 6
    PADDING_TOP_ACTIVE = 5
    PADDING_BOTTOM_ACTIVE = 8
    PADDING_HORIZONTAL = 7
    

    def __init__(self, ):
        """
        """
        

        self._active = False
        self.page = None
        self.label_widget = None
        self.label_width = 0
        self.visible_window = False
    
    def set_label(self, page, icon, label):
        """
        
        Arguments:
        - `page`:
        - `icon`:
        - `label`:
        """
        old_model = pango.ELLIPSIZE_END
        
        self.page = page
        if self.child != None:
            if self.label_widget != None:
                old_model = self.label_widget.ellipsize
            oc = self.child
            self.remove(oc)
            oc.destroy()

        box = HBox()
        box.props.spacing = 2

        if icon:
            img = gtk.Image()
            img.set_from_icon_name(icon, gtk.ICON_SIZE_MENU)
            self.box.pack_start(img, False, False, 0)

        if label:
            self.label_widget = gtk.Label(label)
            self.label_widget.props.use_markup = True
            self.box.pack_start(self.label_widget, True, True, 0)
        else:
            self.label_widget = None


        self.add(box)

        self.show_all()
        self.label_width, temp = self.size_request()

        if self.label_widget != None:
            self.label_widget.ellipsize = old_model

    def set_ellipsize(self, ellipsize):
        """
        
        Arguments:
        - `ellipsize`:
        """
        if self.label_widget != None:
            if ellipsize:
                self.label_widget.ellipsize = pango.ELLIPSIZE_END
            else:
                self.label_widget.ellipsize = pango.ELLIPSIZE_NONE

    @property
    def active(self):
        """
        """
        return self._active

    @active.setter
    def active(self, value):
        """
        
        Arguments:
        - `value`:
        """
        self._active = value
        self.queue_resize()
        self.queue_draw()

    def do_size_request(self, req):
        """
        
        Arguments:
        - `req`:
        """
        req.width, req.height = self.get_child().size_request()
        req.width += self.PADDING_HORIZONTAL * 2
        
        if self.active:
            req.height += self.PADDING_TOP_ACTIVE + self.PADDING_BOTTON_ACTIVE
        else:
            req.height += self.PADDING_TOP + PADDING_BOTTOM

    def do_size_allocate(self, rect):
        """
        
        Arguments:
        - `rect`:
        """
        gtk.EventBox.do_size_allocate(rect)

        rect.x += self.PADDING_HORIZONTAL
        rect.width -= self.PADDING_HORIZONTAL * 2

        if active:
            rect.y += self.PADDING_TOP_ACTIVE
            rect.height = self.get_child().size_request().height
        else:
            rect.y += self.PADDING_TOP
            rect.height = self.get_child().size_request().height

        self.get_child().do_size_allocate(rect)
    
    
    
    

    
        
    

    
    
            
    
    

    
    
    
    

    
    
    
    
    
        
        
