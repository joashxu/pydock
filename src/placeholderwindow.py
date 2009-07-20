import gtk
import gobject
from gtk import gdk


class PlaceHolderWindow(gtk.Window):
    """
    """
    __gsignals__ = { 'expose-event' : 'override' }

    def __init__(self, frame):
        """
        
        Arguments:
        - `frame`:
        """
        
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)

        self.props.decorated = False
        self.props.transient_for = frame.get_toplevel()
        self.props.type_hint = gdk.WINDOW_TYPE_HINT_UTILITY

        self.realize()
        self.redgc = gdk.GC(self.window)
        self.redgc.set_rgb_fg_color(frame.style.bg[gtk.STATE_SELECTED])

        self.rx, self.ry, self.rw, self.rh = 0, 0, 0, 0
        self.anim = 0
        self.allow_docking = True
    
    def create_shape(self, width, height):
        """
        
        Arguments:
        - `width`:
        - `height`:
        """

        black = gdk.Color(0, 0, 0)
        black.pixel = 1

        white = gdk.Color(255, 255, 255)
        white.pixel = 0

        pm = gdk.Pixmap(self.window, width, height, 1)
        gc = gdk.GC(pm)

        gc.set_background(white)
        gc.set_foreground(white)
        pm.draw_rectangle(gc, True, 0, 0, width, height)
        
        gc.set_foreground(black)
        pm.draw_rectangle(gc, False, 0, 0, width - 1, height - 1)
        pm.draw_rectangle(gc, False, 1, 1, width - 3, height - 3)

        self.shape_combine_mask(pm, 0, 0)


    def do_size_allocate(self, allocation):
        """
        
        Arguments:
        - `allocation`:
        """                
        gtk.Window.do_size_allocate(self, allocation)

        self.create_shape(allocation.width, allocation.height)
        


    def do_expose_event(self, args):
        """
        
        Arguments:
        - `args`:
        """        
        w, h = self.get_size()
        
        self.window.draw_rectangle(self.redgc, False, 0, 0, w - 1, h - 1)
        self.window.draw_rectangle(self.redgc, False, 1, 1, w - 3, h - 3)        
   
    def relocate(self, x, y, w, h, animate):
        """
        
        Arguments:
        - `x`:
        - `y`:
        - `w`:
        - `h`:
        - `animate`:
        """
        
        if x != self.rx or y != self.ry or w != self.rw or h != self.rh:
            self.move(x, y)
            self.resize(w, h)

            self.rx, self.ry, self.rw, self.rh = x, y, w, h

            if self.anim != 0:
                gobject.source_remove(self.anim)
                self.anim = 0
                
            if animate and w < 150 and h < 150:
                sa = 7
                self.move( self.rx - sa, self.ry - sa )
                self.resize(self.rw + sa*2, self.rh + sa*2)
                anim = gobject.timeout_add(10, self.run_animation)
    
    def run_animation(self):
        """
        """
        
        cw, ch = self.get_size()
        cx, cy = self.get_position()

        if cx != self.rx:
            cx += 1
            cy += 1
            
            ch -= 2
            cw -= 2

            self.move(cx, cy)
            self.resize(cw, ch)

            return True

        self.anim = 0
        return False
    

