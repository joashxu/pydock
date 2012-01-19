import gtk

from dockframe import DockFrame 
from dockbar import DockBar

from dockitembehavior import DockItemBehavior
from dockitemstatus import DockItemStatus

class App(object):
    """
    """

    def __init__(self, ):
        """
        """
        self.window = gtk.Window()
        self.window.set_size_request(800, 600)
        self.window.connect(
            "delete-event",
            lambda w, e: gtk.main_quit())

        df = DockFrame()
        df.default_item_height = 100
        df.default_item_width = 100
        df.props.homogeneous = False
    
        item = df.add_item("Document")
        
        btn = gtk.Button("hello")
        btn.show()
        
        item.content = gtk.TextView()
        item.visible = True
        item.label = "Test"
        item.expand = True
        item.behavior = DockItemBehavior.LOCKED
                
        right = df.add_item( "right" )
        right.default_location = "Document/Right"
        right.default_visible = True
        right.visible = True
        right.behavior = DockItemBehavior.CANT_CLOSE | DockItemBehavior.NEVER_FLOATING
        right.label = "Right window"
        right.draw_frame = True
        right.content = gtk.Label("Content")
        right.icon = "gtk-close";
        
        rb = df.add_item( "right_left" )
        rb.default_location = "right/Left"
        rb.default_visible = True
        rb.visible = True
        rb.label = "List"
        rb.draw_frame = True
        rb.content = gtk.TreeView()
        rb.icon = "gtk-new";
        
        btm = df.add_item( "bottom" )
        btm.default_location = "Document/Bottom"
        btm.default_visible = True
        btm.visible = True
        btm.label = "Bottom list"
        btm.draw_frame = True
        btm.content = gtk.TreeView()
        btm.icon = "gtk-new";
        
        df.create_layout("test", True)

        df.current_layout = "test"
        
        self.window.add(df)                      
        self.window.show_all()    
        
        right.status = DockItemStatus.AUTOHIDE
            
    def print_content(self, widget):
        if hasattr(widget, 'get_children'):
            for item in widget.get_children():
                print item 
                print item.props.visible
                print item.size_request()
                self.print_content(item)
        else:
            print widget
            
        

    def main(self, ):
        """
        """
        gtk.main()
    


if __name__ == '__main__':
    a = App()
    a.main()
