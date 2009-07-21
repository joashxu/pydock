import gtk
from gtk import gdk

from dockobject import DockObject
from dockgroupitem import DockGroupItem
from dockgrouptype import DockGroupType
from dockposition import DockPosition

class DockGroup(DockObject):
    """
    """
    
    class AllocStatus(object):
        """
        """
    
        NOT_SET = 0
        INVALID = 1
        RESTORE_PENDING = 2
        NEW_SIZE_REQUEST = 3
        VALID = 4

        def __init__(self):
            """
            """
            raise Exception("No init")
            
    def __init__(self, frame, type):
        """
        
        Arguments:
        - `frame`:
        - `type`:
        """
        DockObject.__init__(self, frame)

        self.type = type
        self.dock_objects = []
        self._visible_objects = []        
        self.alloc_status = self.AllocStatus.NOT_SET

        self.tab_strip = None
        self.tab_focus = None
        
        self.current_tab_page = -1
    
    def mark_for_relayout(self):
        """
        """
        if self.alloc_status == self.AllocStatus.VALID:
            self.alloc_status = self.AllocStatus.INVALID

    def add_object(self, obj):
        """
        
        Arguments:
        - `obj`:
        """
        obj.parent_group = self

        self.dock_objects.append(obj)
        self.reset_visible_groups()
    
    def add_item(self, obj, pos, rel_item_id):
        """
        
        Arguments:
        - `obj`:
        - `pos`:
        - `rel_item_id`:
        """
        
        npos = -1
        
        if rel_item_id:
            for n, it in enumerate(self.dock_objects):
                if it and it.id == rel_item_id:
                    npos = n

        if npos == -1:
            if pos == DockPosition.LEFT or pos == DockPosition.Top:
                npos = 0
            else:
                npos = len(self.dock_objects) - 1

        gitem = None

        if pos == DockPosition.LEFT or pos == DockPosition.RIGHT:
            if self.type != DockGroupType.HORIZONTAL:
                gitem = self.split(DockGroupType.Horizontal, pos == DockPosition.LEFT, obj, npos)
            else:
                gitem = self.insert_object(obj, npos, pos)
        elif pos == DockPosition.TOP or pos == DockPosition.BOTTOM:
            if self.type != DockGroupType.VERTICAL:
                gitem = self.split(DockGroupType.VERTICAL, pos == DockPosition.TOP, obj, npos)
            else:
                gitem = self.insert_object(obj, npos, pos)
        elif pos == DockPosition.CENTER_BEFORE or pos == DockPosition.CENTER:
            if self.type != DockGroupType.TABBED:
                gitem = self.split(DockGroupType.TABBED, pos == DockPosition.CENTER_BEFORE, obj, npos)
            else:
                if pos == DockPosition.CENTER:
                    npos += 1

                gitem = DockGroupItem(self.frame, obj)
                self.dock_objects.insert(npos, gitem)
                gitem.parent_group = self

        self.reset_visible_groups()

        return gitem


    def insert_object(self, obj, npos, pos):
        """
        
        Arguments:
        - `obj`:
        - `npos`:
        - `pos`:
        """
        if pos == DockPosition.BOTTOM or pos == DockPosition.RIGHT:
            npos += 1

        gitem = DockGroupItem(self.frame, obj)
        self.dock_objects.insert(npos, gitem)
        gitem.parent_group = self
        
        return gitem
    
    def split(self, new_type, add_first, obj, npos):
        """
        
        Arguments:
        - `new_type`:
        - `add_first`:
        - `obj`:
        - `npos`:
        """
        item = DockGroupItem(self.frame, obj)

        if npos == -1 or self.type == DockGroupType.TABBED:
            if self.parent_group != None and self.parent_group.type == new_type:
                i = self.parent_group.dock_objects.index(self)
                if add_first:
                    self.parent_group.dock_objects.insert(i, item)
                else:
                    self.parent_group.dock_objects.insert(i+1, item)

                item.parent_group = self.parent_group
                item.reset_default_size()
            else:
                grp = self.copy(self)
                self.dock_objects = []
                if add_first:
                    self.dock_objects.append(item)
                    self.dock_objects.append(grp)
                else:
                    self.dock_objects.append(grp)
                    self.dock_objects.append(item)

                item.parent_group = self
                item.reset_default_size()
                grp.parent_group = self
                grp.reset_default_size()
                self.type = type
        else:
            grp = DockGroup(self.frame, new_type)
            replaced = self.dock_objects[npos]

            if add_first:
                grp.add_object(item)
                grp.add_object(replaced)
            else:
                grp.add_object(replaced)
                grp.add_object(item)

            grp.copy_size_from(replaced)
            self.dock_objects[npos] = grp
            grp.parent_group = self
    
    def find_group_containing(self, id):
        """
        
        Arguments:
        - `id`:
        """
        it = self.find_dock_group_item(id)

        if it != None:
            return it.parent_group
        else:
            return None
    
    def find_dock_group_item(self, id):
        """
        
        Arguments:
        - `id`:
        """
        for ob in self.dock_objects:
            if ob != None and isinstance(ob, DockGroupItem) and ob.id == id:
                return ob
            
            if ob != None and isinstance(ob, self.__class__):
                it = ob.find_dock_group_item(id)
                if it != None:
                    return it
            
        return None

    def copy(self):
        """
        """
        grp = DockGroup(self.frame, self.type)
        grp.dock_objects = self.dock_objects[:]
        
        for obj in grp.dock_objects:
            obj_parent_group = grp

        grp.CopySizeFrom(self)

        return grp

    def get_object_index(self, obj):
        """
        
        Arguments:
        - `obj`:
        """
        for n, it in enumerate(self.dock_objects):
            if it == obj:
                return n

        return -1

    def remove_item_rec(self, item):
        """
        
        Arguments:
        - `item`:
        """
    
        for ob in self.dock_objects:
            if isintance(ob, DockGroup):
                if ob.remove_item_rec(item):
                    return True
            else:
                if ob != None and isinstance(ob, DockGroupItem) and ob.item == item:
                    self.remove(ob)
                    return True
    
        return False

    def Remove(self, obj):
        """
        
        Arguments:
        - `obj`:
        """
        self.dock_objects.remove(obj)
        self.reduce()
        
        obj.parent_group = None
        self._visible_objects = []

        if len(self.visible_objects) > 0:
            self.calc_new_sizes()
            self.mark_for_relayout()
        else:
            self.parent_group.update_visible(self)

    def reduce(self):
        """
        """
        if self.parent_group != None and len(self.dock_objects) == 1:
            obj = self.dock_objects[0]
            n = self.parent_group.get_object_index(self)
            self.parent_group.dock_objects[n] = obj
            obj.parent_group = self.parent_group
            obj.copy_size_from(self)
            self.dock_objects = []
            self.reset_visible_groups()
            self.parent_group.reset_visible_groups
    

    @property
    def visible_objects(self):
        """
        """
        if len(self._visible_objects) == 0:
            self._visible_objects = [obj for obj in self.dock_objects if hasattr(obj, 'visible') and obj.visible]            

        return self._visible_objects
            
    def reset_visible_groups(self):
        """
        """
        self._visible_objects = []
        self.mark_for_relayout()

    def update_visible(self, child):
        """
        
        Arguments:
        - `child`:
        """
        self._visible_objects = []

        self.calc_new_sizes()
        self.mark_for_relayout()

        vis_changed = len(self.visible_objects) == 1 if child.visible\
            else len(self.visible_objects) == 0

        if vis_changed and self.parent_group != None:
            self.parent_group.update_visible(self)

    def restore_allocation(self):
        """
        """
        DockObject.restore_allocation(self)

        alloc_status = self.AllocStatus.RESTORE_PENDING if self.size >= 0 else self.AllocStatus.NOT_SET

        for ob in self.dock_objects:
            ob.restore_allocation()
    
    def store_allocation(self):
        """
        """
        DockObject.store_allocation()
        for ob in self.dock_objects:
            ob.store_allocation

        if self.type == DockGroupType.TABBED and self.bound_tab_strip != None:
            self.current_tab_page = self.bound_tab_strip.current_tab

    @property
    def expand(self):
        """
        """
        for ob in self.dock_objects:
            if ob.expand:
                return True

        return False
    
    def size_allocate(self, new_alloc):
        """
        
        Arguments:
        - `new_alloc`:
        """
        old_alloc = self.allocation

        DockObject.size_allocate(self, new_alloc)

        if self.type == DockGroupType.TABBED:
            if self.bound_tab_strip != None:
                tabs_height = self.bound_tab_strip.size_request().height
                self.bound_tab_strip.size_allocate(
                    gdk.Rectangle(new_alloc.x,
                                  new_alloc.bottom - self.tabs_height,
                                  new_alloc.width,
                                  self.tabs_height))
            
            if self.alloc_status == self.AllocStatus.VALID and\
                    new_alloc == old_alloc:
                for ob in self.visible_objects:
                    ob.size_allocate(ob.allocation)

                return

            if len(self.visible_objects) > 1 and self.bound_tab_strip != None:
                tabs_height = self.bound_tab_strip.size_request().height
                new_alloc.height -= tabs_height
                self.bound_tab_strip.queue_draw()
            elif len(self.visible_objects) != 0:
                self.visible_objects[0].item.widget.show()
                

            self.alloc_status = self.AllocStatus.VALID
            for ob in self.visible_objects:
                ob.size = ob.pref_size = -1
                ob.size_allocate(new_alloc)

            return

        horiz = (self.type == DockGroupType.HORIZONTAL)
        pos = self.allocation.x if horiz else self.allocation.y

        if self.alloc_status == self.AllocStatus.VALID and new_alloc == old_alloc:
            if self.check_min_sizes():
                self.alloc_status = self.AllocStatus.new_size_request
            else:
                for ob in self.visible_objects:
                    ins = ob.alloc_size
                    if horiz:
                        rect = gdk.Rectangle(pos, self.allocation.x, ins, self.allocation.height)
                    else:
                        rect = gdk.Rectangle(self.allocation.x, pos, self.allocation.width, ins)
                    ob.size_allocate(rect)
                    pos += ins + self.frame.total_handle_size

                return

        real_size = self.get_real_size(self.visible_objects)

        if self.alloc_status == self.AllocStatus.NEW_SIZE_REQUEST:
            change = 0.0

            if horiz:
                change = float(new_alloc.width) / float(old_alloc.width)
            else:
                change = float(new_alloc.height) / float(old_alloc.height)

            tsize = 0
            rsize = 0

            for ob in self.visible_objects:
                tsize += ob.pref_size
                rsize += ob.size

            for ob in self.dock_objects:
                if ob.visible:
                    ob.size = ob.pref_size = (ob.pref_size / tsize) * float(real_size)
                else:
                    ob.size = ob.size * change
                    ob.pref_size = ob.pref_size * change

                ob.default_size = ob.default_size * change

            self.check_min_sizes()


        self.alloc_status = self.AllocStatus.VALID

        ts = 0
        
        for n, ob in enumerate(self.visible_objects):
            ins = int(ob.size)

            if n == len(self.visible_objects) - 1:
                ins = real_size - ts
            
            ts += ins

            if ins < 0:
                ins = 0

            ob.alloc_size = ins

            if horiz:
                ob.size_allocate(gdk.Rectangle(pos, self.allocation.y, ins, self.allocation.height))
            else:
                ob.size_allocate(gdk.Rectangle(self.allocation.x, pos, self.allocation.width, ins))

            pos += ins + self.frame.total_handle_size
    
    def get_real_size(self, objects):
        """
        
        Arguments:
        - `objects`:
        """
        
        real_size = 0

        if self.type == DockGroupType.HORIZONTAL:
            if self.allocation:
                real_size = self.allocation.width            
        else:
            if self.allocation:
                real_size = self.allocation.height

        if len(self.dock_objects) > 1:
            real_size -= (self.frame.total_handle_size * (len(self.dock_objects) - 1))

        return real_size
    
    def calc_new_sizes(self):
        """
        """
        
        real_size = self.get_real_size(self.visible_objects)

        has_expand_items = False
        no_expand_size = 0.0
        min_expand_size = 0.0
        default_expand_size = 0.0

        for n, ob in enumerate(self.visible_objects):
            if ob.expand:
                min_expand_size += ob.min_size
                default_expand_size += ob.default_size
                has_expand_items = True
            else:
                ob.size = ob.default_size
                no_expand_size += ob.default_size


        expand_size = real_size - no_expand_size
        for ob in self.visible_objects:
            if not has_expand_items:
                ob.size = (ob.default_size / no_expand_size) * real_size
            elif ob.expand:
                ob.size = (ob.default_size / default_expand_size) * expand_size

            ob.pref_size = ob.size

        self.check_min_sizes()

    def check_min_sizes(self):
        """
        """
        
        sizes_changed = False
        av_size, reg_size = 0, 0

        for ob in self.visible_objects:
            if ob.size < ob.min_size:
                reg_size += ob.min_size - ob.size
                ob.size = ob.min_size
                sizes_changed = True
            else:
                av_size += ob.size - ob.min_size


        if not sizes_changed:
            return False

        if reg_size > av_size:
            reg_size = av_size

        if av_size:    
            ratio = (av_size - reg_size) / av_size
            for ob in self.visible_objects:
                if ob.size <= ob.min_size:
                    continue

                avs = ob.size - ob.min_size
                ob.size = ob.min_size + avs * ratio
            
        return sizes_changed

    def size_request(self):
        """
        """
        get_max_w, get_max_h = True, True

        if self.type == DockGroupType.HORIZONTAL:
            get_max_w = False
        elif self.type == DockGroupType.VERTICAL:
            get_max_h = False

        width, height = 0, 0
        height = len(self.visible_objects) * self.frame.total_handle_size

        for ob in self.visible_objects:
            req_width, req_height = ob.size_request()
            if get_max_h:
                if req_height > height:
                    height = req_height
            else:
                height += req_height

            if get_max_w:
                if req_width > width:
                    width = req_width
            else:
                width += req_width

        if type == DockGroupType.TABBED and len(self.visible_objects) > 1 and self.bound_tab_strip != None:
            tabs = self.bound_tab_strip.size_request()
            heigt += tabs.height
            if width < tabs.width:
                width = tabs.width

        return width, height
    
    def update_notebook(self, ts):
        """
        
        Arguments:
        - `ts`:
        """
        old_page = None
        old_tab = -1

        if self.tab_focus != None:
            old_page = self.tab_focus.item.widget
            self.tab_focus = None
        elif self.bound_tab_strip != None:
            old_page = self.bound_tab_strip.current_page
            old_tab = self.bound_tab_strip.current_tab


        ts.clear()
    
        for ob in self.visible_objects:
            ts.add_tab(it.item.widget, it.item.icon, it.item.label)

        self.bound_tab_strip = ts

        if self.current_tab_page != -1 and self.current_tab_page < self.bound_tab_strip.tab_count:
            self.bound_tab_strip.current_tab = current_tab_page
            current_tab_page = -1
        elif old_page != None:
            self.bound_tab_strip.current_page = old_page

        if self.bound_tab_strip.current_tab == -1:
            if old_tab != -1:
                if old_tab < self.bound_tab_strip.tab_count:
                    self.bound_tab_strip.current_tab = old_tab
                else:
                    self.bound_tab_strip.current_tab = self.bound_tab_strip.tab_count - 1
            else:
                self.bound_tab_strip.current_tab = 0


    def present(self, it, give_focus):
        """
        
        Arguments:
        - `it`:
        - `give_focus`:
        """
        
        if self.type == DockGroupType.TABBED:
            for n, dit in enumerate(self.visible_objects):
                if dit.item == it:
                    self.current_tab_page = n
                    
                    if self.bound_tab_strip != None:
                        self.bound_tab_strip.current_page = it.widget
                    break

        if self.give_focus and it.visible:
            it.set_focus

    def is_selected_page(self, it):
        """
        
        Arguments:
        - `it`:
        """
        
        if self.type != DockGroupType.TABBED or\
                self.bound_tab_strip == None or\
                self.bound_tab_strip.current_tab == -1 or\
                self.visible_objects == None or\
                self.bound_tab_strip.current_tab >= len(self.visible_objects):

            return False

        dit = self.visible_objects[self.bound_tab_strip.current_tab]

        return dit.item == it
    
    def update_title(self, it):
        """
        
        Arguments:
        - `it`:
        """
        if it.visible and type == DockGroupType.TABBED and self.bound_tab_strip != None:
            self.bound_tab_strip.set_tab_label(it.widget, it.icon, it.label)

    def focus_item(self, it):
        """
        
        Arguments:
        - `it`:
        """
        self.tab_focus = it
    
    def reset_notebook(self):
        """
        """
        self.bound_tab_strip = None

    def layout_widgets(self):
        """
        """
        
        for ob in self.visible_objects:
            if isinstance(ob, DockGroupItem):
                if ob.item.widget.parent == None:
                    ob.item.widget.set_parent(self.frame.container)
                if ob.item.widget.props.visible and self.type != DockGroupType.TABBED:
                    ob.item.widget.show()
            else:
                ob.layout_widgets()
    
    def get_default_size(self):
        """
        """
        
        if self.type == DockGroupType.TABBED:
            width, height = -1, -1
            
            for ob in self.visible_objects:
                dw, dh = ob.get_default_size()
                if dw > width:
                    width = dw
                if dh > height:
                    height = dh
        elif self.type == DockGroupType.VERTICAL:
            width = -1
            height = (len(self.visible_objects) - 1 * self.frame.total_handle_size) if len(self.visible_objects) > 0 else 0

            for ob in self.visible_objects:
                dw, dh = ob.get_default_size()
                if dw > width:
                    width = dw
                    
                height += dh
        else:
            width = (len(self.visible_objects) - 1 * self.frame.total_handle_size) if len(self.visible_objects) > 0 else 0
            height = -1

            for ob in self.visible_objects:
                dw, dh = ob.get_default_size()
                if dh > height:
                    height = dh
                
                width += dw

        return width, height

    def get_min_size(self):
        """
        """
    
        if self.type == DockGroupType.TABBED:
            width, height = -1, -1
            for ob in self.visible_objects:
                dw, dh = ob.get_min_size()
                if dw > width:
                    width = dw
                if dh > height:
                    height = dh
        elif self.type == DockGroupType.VERTICAL:
            width = -1
            height = (len(self.visible_objects) - 1 * self.frame.total_handle_size) if len(self.visible_objects) > 0 else 0

            for ob in self.visible_objects:
                dw, dh = ob.get_min_size()
                if dw > width:
                    width = dw
                    
                height += dh
        else:
            width = (len(self.visible_objects) - 1 * self.frame.total_handle_size) if len(self.visible_objects) > 0 else 0
            height = -1

            for ob in self.visible_objects:
                dw, dh = ob.get_min_size()
                if dh > height:
                    height = dh
                
                width += dw

        return width, height
    
    def draw(self, exposed_area, current_handle_grp, current_handle_index):
        """
        
        Arguments:
        - `exposed_area`:
        - `current_handle_grp`:
        - `current_handle_index`:
        """
    
        if self.type != DockGroupType.TABBED:
            self.draw_separators(exposed_area, current_handle_grp, current_handle_index, False, False)
            for it in self.visible_objects:
                if isinstance(it, DockGroup):
                    it.draw(exposed_area, current_handle_grp, current_handle_index)


    def draw_separators(self, exposed_area, current_handle_grp, current_handle_index, invalidate_only, draw_children_sep=True):
        """
        
        Arguments:
        - `exposed_area`:
        - `current_handle_grp`:
        - `current_handle_index`:
        - `invalidate_only`:
        - `draw_children_sep`:
        """
        
        if self.type == DockGroupType.TABBED or len(self.visible_objects) == 0:
            return

        last = self.visible_objects[-1]
    
        horiz = type == DockGroupType.HORIZONTAL
        x, y = self.allocation.x, self.allocation.y

        hw = self.frame.handle_size if horiz else self.allocation.width
        hh = self.allocation.height if horiz else self.frame.handle_size

        orientation = gtk.ORIENTATION_VERTICAL if horiz else gtk.ORIENTATION_HORIZONTAL

        for n, ob in enumerate(self.visible_objects):
            if isinstance(ob, self.__class__) and draw_children_sep:
                ob.draw_separators(exposed_area, 
                                   current_handle_grp,
                                   current_handle_index,
                                   invalidate_only)

            if ob != last:
                if horiz:
                    x += ob.allocation.width + self.frame.handle_padding
                else:
                    y += ob.allocation.height + self.frame.handle_padding

                if invalidate_only:
                    self.frame.container.queue_draw_area(x, y, hw, hh)
                else:
                    state = None

                    if current_handle_grp == self and current_handle_index == n:
                        state = gtk.STATE_PRELIGHT
                    else:
                        state = gtk.STATE_NORMAL

                if horiz:
                    x += self.frame.handle_size + self.frame.handle_padding
                else:
                    y += self.frame.handle_size + self.frame.handle_padding

    def resize_item(self, index, new_size):
        """
        
        Arguments:
        - `index`:
        - `new_size`:
        """
    
        o1 = self.visible_objects[index]
        o2 = self.visible_objects[index + 1]

        dsize = new_size - o1.alloc_size
        
        if dsize < 0 and o1.alloc_size + dsize < o1.min_size:
            dsize = o1.min_size - o1.alloc_size
        elif dsize > 0 and (o2.alloc_size - dsize < o2.min_size):
            dsize = o2.alloc_size - o2.min_size

        size_diff = float(dsize)

        o1.alloc_size += dsize
        o2.alloc_size -= dsize
        
        o1.default_size += (o1.default_size * size_diff) / o1.size
        o1.size = o1.alloc_size
        o1.pref_size = o1.size

        o2.default_size -= (o2.default_size * size_diff) / o2.size
        o2.size = o2.alloc_size
        o2.pref_size = o2.size

        o1.queue_resize()
        o2.queue_resize()


    def queue_resize(self):
        """
        """
        for obj in self.visible_objects:
            obj.queue_resize()
    
    def get_object_size(self):
        """
        """
        total = 0.0

        for obj in self.visible_objects:
            total += obj.size

        return total

    def dock_target(self, item, n):
        """
        
        Arguments:
        - `item`:
        - `n`:
        """
        
        gitem = DockGroupItem(self.frame, item)
        self.dock_objects.insert(n, gitem)
        gitem.parent_group = self
        gitem.set_visible(True)
        self.reset_visible_groups()
        self.calc_new_sizes()

    def get_dock_target(self, item, px, py):
        """
        
        Arguments:
        - `item`:
        - `px`:
        - `py`:
        """
        
        dock_delegate, rect = None, None
        px_py_in_allocation = False

        if self.allocation.x <= px <= self.allocation.width and\
            self.allocation.y <= py <= self.allocation.height:
            px_py_in_allocation = True
             
        if not px_py_in_allocation or len(self.visible_objects) == 0:
            return dock_delegate, rect

        if self.type == DockGroupType.TABBED:
            return self.visible_objects.get_dock_target(item, px, py, self.allocation)
        elif self.type == DockGroupType.HORIZONTAL:
            if px >= self.allocation.width - self.frame.GROUP_DOCK_SEP_SIZE:
                
                def mini_function(it):
                    return self.dock_target(it, len(self.dock_objects))
                    
                dock_delegate = mini_function
            
                rect = gdk.Rectangle(self.allocation.width - self.frame.GROUP_DOCK_SEP_SIZE,
                                     self.allocation.y,
                                     self.frame.GROUP_DOCK_SEP_SIZE,
                                     self.allocation.height)
                
            elif px <= self.allocation.x + self.frame.GROUP_DOCK_SEP_SIZE:
                
                def mini_function(it):
                    return self.dock_target(it, 0)

                dock_delegate = mini_function
                
                rect = gdk.Rectangle(self.allocation.x,
                                     self.allocation.y,
                                     self.frame.GROUP_DOCK_SEP_SIZE,
                                     self.allocation.height)

            for n, ob in enumerate(self.visible_objects):
                if n < len(self.visible_objects) - 1 and\
                   px >= ob.allocation.width - self.frame.GROUP_DOCK_SEP_SIZE/2 and\
                   px <= ob.allocation.width + self.frame.GROUP_DOCK_SEP_SIZE/2:
                                       
                    dn = self.dock_objects.index(ob)
                    
                    def mini_function(it):
                        return self.dock_target(it, dn + 1)
                    
                    dock_delegate = mini_function

                    rect = gdk.Rectangle(ob.allocation.width - self.frame.GROUP_DOCK_SEP_SIZE/2,
                                         self.allocation.y,
                                         self.frame.GROUP_DOCK_SEP_SIZE, 
                                         self.allocation.height)

                else:
                    
                    dock_delegate, rect = ob.get_dock_target(item, px, py)

        elif self.type == DockGroupType.VERTICAL:
            if py >= self.allocation.bottom - self.frame.GROUP_DOCK_SEP_SIZE:
                
                def mini_function(it):
                    self.dock_target(it, len(self.dock_objects))

                rect = gdk.Rectangle(self.allocation.x,
                                     self.allocation.bottom - self.fram.GROUP_DOCK_SEP_SIZE,
                                     self.allocation.width,
                                     self.frame.GROUP_DOCK_SEP_SIZE)
            elif py <= self.allocation.height + self.frame.GROUP_DOCK_SEP_SIZE:
                
                def mini_function(it):
                    self.dock_target(it, 0)

                rect = gdk.Rectangle(self.allocation.x,
                                     self.allocation.height,
                                     self.allocation.width,
                                     self.frame.GROUP_DOCK_SEP_SIZE)

            
            for n, ob in enumerate(self.visible_objects):
                if n < len(self.visible_objects) - 1 and\
                   px >= ob.allocation.bottom - self.frame.GROUP_DOCK_SEP_SIZE/2 and\
                   py <= ob.allocation.bottom + self.frame.GROUP_DOCK_SEP_SIZE/2:
                    
                    dn = self.dock_objects.index(ob)

                    def mini_function(it):
                        self.dock_target(it, dn + 1)

                    rect = gdk.Rectangle(self.allocation.x,
                                         ob.allocation.bottom - self.frame.GROUP_DOCK_SEP_SIZE/2,
                                         self.allocation.width,
                                         self.frame.GROUP_DOCK_SEP_SIZE)
                else:
                    dock_delegate, rect = ob.get_dock_target(item, px, py)

        return dock_delegate, rect

    
    def replace_item(self, ob1, ob2):
        """
        
        Arguments:
        - `ob1`:
        - `ob2`:
        """
        i = self.dock_objects.index(ob1)

        self.dock_objects[i] = ob2

        ob2.parent_group = self
        ob2.reset_default_size()
        ob2.size = ob1.size
        ob2.default_size = ob1.default_size
        ob2.alloc_size = ob1.alloc_size

        self.reset_visible_groups()
    
    def copy_from(self, other):
        """
        
        Arguments:
        - `other`:
        """
        
        DockObject.copy_from(self, other)

        self.dock_objects = []

        for ob in other.dock_objects:
            cob = ob.clone()
            cob.parent_group = self
            self.dock_objects.append(cob)

        self.type = grp.type
        self.reset_visible_groups()
        self.bound_tab_strip = None
        self.tab_focus = None

    ## Dump
    #



    ## XML Read/Write
    #
