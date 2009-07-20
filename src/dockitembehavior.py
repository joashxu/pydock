class DockItemBehavior(object):
    """
    """

    NORMAL = 0
    NEVER_FLOATING = 1 
    NEVER_VERTICAL = 1 << 1
    NEVER_HORIZONTAL = 1 << 2
    CANT_CLOSE = 1 << 3
    CANT_AUTOHIDE = 1 << 4
    NO_GRIP = 1 << 5
    STICKY = 1 << 6

    # Must be the same with NO_GRIP
    LOCKED = 1 << 5    

    def __init__(self, ):
        """
        """
        raise Exception("No init")
        
