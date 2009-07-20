import gtk

from dockframe import DockFrame 
from dockbar import DockBar

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

        print "add-item"
        item = df.add_item("Document")
        
        btn = gtk.Button("hello")
        btn.show()
        
        print "add-content"
        item.content = btn
        item.visible = True
        item.label = "Test"
        
        right = df.add_item( "right" )
        right.default_location = "Document/Right"
        right.default_visible = True
        right.visible = True
        right.label = "Derecha"
        right.draw_frame = True;
        lbl = gtk.Label("HAIYAAA!!!")
        lbl.show()
        
        right.content = lbl 
        right.icon = "gtk-close"
            
        print "create-layout"
        df.create_layout("test", True)

        df.current_layout = "test"
        
        self.window.add(df)      
        
        print "show-all"
        self.window.show_all()       
        
        
        #self.print_content(self.window)
            
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
