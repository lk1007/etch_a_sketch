import image_to_drawing as img
from rich.progress import Progress
black = 20
import math
import cv2
import numpy as np
usebar = False
progress = None
progress = Progress()
import threading
from counter import Counter
class Node:
    pos = 0,0
    bkptr = None
    e = False
    edge = False
    external =False
    jumppoint = None
    def __init__(self, x,y):
        self.pos = x,y
        
    def dist(self, destination):
        calculated_distance = math.dist(self.pos, destination.pos)
        if destination == self.jumppoint or destination.jumppoint == self:
            return calculated_distance / 100000
        if calculated_distance - math.sqrt(2) < 0.001:
            return calculated_distance / 100000
        else:
            return calculated_distance
    def cost(self, destination):
        y1,x1 = self.pos
        y2, x2 = destination.pos
        
        if x1 == x2 and y1 - y2 == 1:
            return 1.0/100000.0
        elif (y1 == y2 and abs(x1 - x2)) == 1 or abs(y1-y2) == 1 and x1 == x2:
            return 1
        else:
            return self.dist(destination)

    def __str__(self):
        a = ", E" if (self.e) else ""
        return "NODE: " + str(self.pos) + a

    def __repr__(self) :
        return "<N: " + str(self.pos)  +  ">"


def to_nodes(arr):
    if usebar:
        task0 = progress.add_task("Converting " + str(len(arr[0])) + " x " + str(len(arr)) + " image...", total = len(arr))
    coords = {}
    i = 0
    coords[(0,0)] = Node(0,0)
    while i < len(arr):
        if usebar:
            progress.update(task0, advance = 1)
        j = 0
        while j < len(arr[i]):
            landlocked = False
            isolated = False
            try:
                if arr[i + 1][j] <= black and arr[i - 1][j] <= black and arr[i][j + 1] <= black and arr[i][j - 1] <= black and arr[i + 1][j + 1] <= black and arr[i + 1][j -1] <= black and arr[i - 1][j- 1] <= black and arr[i - 1][j + 1] <= black:
                    landlocked = True
                if arr[i + 1][j] >= black and arr[i - 1][j] >= black and arr[i][j + 1] >= black and arr[i][j - 1] >= black and arr[i + 1][j + 1] >= black and arr[i + 1][j -1] >= black and arr[i - 1][j- 1] >= black and arr[i - 1][j + 1] >= black:
                    isolated = True
            except:
                pass
            if arr[i][j] <= black and (not landlocked and not isolated) :
                newnode = Node(i,j)
                coords[(i,j)] = newnode
            j = j + 1
        i = i + 1
    
    return coords
def travel(nodelist):
    dist = 0.0
    prev = nodelist[0]
    for node in nodelist[1:]:
        dist = dist + prev.cost(node)
        prev = node
    return dist

def min_dist(distance_dict, unex = False):
    
    if len(distance_dict) == 0:
        return None
    min_key = None
    min_dist = None
    min_path = None
    for node in distance_dict:
        dist = distance_dict[node][1]
        if  (min_dist is None or dist < min_dist) and ((not unex) or (not node.e)) :
            min_key = node
            min_dist = dist
            min_path = distance_dict[node][0]
    #asert len(min_path) > 0, "Bad path!"
    return min_key, min_path

def extend_path(path_entry, node, updatepath = True):
    newlist = []
    path, dist = path_entry
    for n in path:
        if updatepath:
            newlist.append(n)
    if updatepath:
        newlist.append(node)
        last = path[-1]
    else:
        newlist = [node]
        last = path_entry[0][0]
    return (newlist, dist + last.dist(node))

def adjacent_nodes (node_dict, node, directly = True, unex = False, lastnode = None):

    x,y = node.pos
    v = []
    c = 0
    h = False
    
    priority = [(x + 1, y), (x - 1, y)]
    next_in_direction = None
    if lastnode is not None:
        fx, fy = lastnode.pos
        dx, dy = (x - fx, y - fy)
        dxr, dyr = 0,0
        if dx != 0:
            dxr = dx//abs(dx)
        if dy != 0:
            dyr = dy//abs(dy)
        if dx == 0 and abs(dyr) == 1:
            next_in_direction = (x, y + dyr)
        elif abs(dxr) == 1 and dy == 0:
            next_in_direction = (x + dxr, y)
        elif abs(dxr) == 1 and abs(dyr) == 1:
            next_in_direction = (x + dxr, y + dyr)
    if next_in_direction is not None:
        pos =[next_in_direction, (x, y - 1), (x + 1, y), (x - 1, y), (x, y + 1)
            ,(x + 1, y + 1), (x - 1, y - 1),
            (x - 1, y + 1), (x + 1, y - 1)
        ]
    else:
         pos =[(x, y - 1), (x + 1, y), (x - 1, y), (x, y + 1)
            ,(x + 1, y + 1), (x - 1, y - 1),
            (x - 1, y + 1), (x + 1, y - 1)
        ]
    for p in pos:
        if p in node_dict:
            if p not in v:
                c = c + 1
            n = node_dict[p]
            if (not unex) or (not n.e):
                v.append(n)
            if p in priority or p == next_in_direction:
                h = True
    
    node.edge = c <= 5
    node.external = not c == 8
    if h or directly:
        return v
    else:
        outer = []
        lp = (x - 1, y)
        notfound = True
        while (lp in node_dict) and notfound:
            n = node_dict[lp]
            if not n.e:
                outer.append(n)
                notfound = False
            x,y = lp
            lp = (x - 1, y)
        rp = (x + 1, y)
        notfound = True
        while (rp in node_dict) and notfound:
            n = node_dict[rp]
            if not n.e:
                outer.append(node_dict[rp])
                notfound = False
            x,y = rp
            rp = (x + 1, y)
       
        for h in outer:
            h.jumppoint = node
       
        else:
            outer.extend(v)
            return outer

def get_new(node_dict, node, r = 1, shortcut = False):
    x1,y1 = node.pos
    newdict = {}
    unex = False
    while not unex and r < len(node_dict) ** 2:
        coords = []
        curr = (r,0)
        for i in range(r + 1):
            x2, y2 = curr
            coords.extend([
                (x1 + x2, y1 + y2),
                (x1 - x2, y1 - y2),
                (x1 - x2, y1 + y2),
                (x1 + x2, y1 - y2)
            ])
            curr = (x2 - 1, y2 + 1)
        for c in coords:
            if c in node_dict and c not in newdict:
                v = node_dict[c]
                if not v.e:
                    unex = True
                    newdict[c] = v 
                elif shortcut:
                    newdict[c] = v
        r = r + 1

    return newdict
def get_edges(node_dict, node, strict = False):
    edges = {}
    start = node

    while not (start.external and ((not strict) or start.edge)):
        x,y = start.pos
        try:
            start = node_dict[(x+1, y)]
        except KeyError:
            break

    stack = [start]

    while len(stack) > 0:
        curr = stack.pop()
        if curr.external and ((not strict) or curr.edge) and curr.pos not in edges:
            edges[curr.pos] = curr
            stack.extend(adjacent_nodes(node_dict, curr))
    return edges

def shortest_path(node_dict, start, end = None):
    if usebar:
        if end is None:
            task2 = progress.add_task("Computing " + str(len(node_dict)) + " nodes...", total = len(node_dict))
        else:
            task2 = progress.add_task("Finding node from " + str(len(node_dict)) +" nodes...", total = len(node_dict))

    for n in node_dict.values():
        n.in_frontier = False
        n.in_settled = False

    frontier_count = 1
    distances={}
    distances[start] = ([start], 0.0)
    current = start

    while (current is not None and frontier_count > 0):
        current.in_frontier = False  
        frontier_count = frontier_count - 1
        if usebar:
            progress.update(task2, advance = 1)
        current.in_settled = True
        
        if end is not None and current.pos == end.pos:
            if usebar:
                progress.remove_task(task2)
            return distances[current]
        adj = adjacent_nodes (node_dict, current, directly = True, unex = False)
        if all(n.in_settled or len(adj) < 8 for n in adj):
            sub = node_dict.values()
        else:
            sub = adj

        if all(n.in_settled for n in adj):
            sub = node_dict.values()
        else:
            sub = adj
        sub = node_dict.values()
  
        for node in sub:
            if not node.in_settled and not node.in_frontier:
                distances[node] = extend_path(distances[current],node)
                node.in_frontier = True
                frontier_count = frontier_count + 1
            elif (not node.in_settled) and ((extend_path(distances[current],node))[1] < (distances[node])[1]):
                distances[node] = extend_path(distances[current],node)
                
        ret = min_dist({k: v for k, v in distances.items() if k.in_frontier})
        
        if ret is not None:
            current, _ = ret
    if usebar:
        progress.remove_task(task2)
    
    return distances

    
def explore(node_dict, precision_factor = 1000, counter = None):

    if usebar:
        task1 = progress.add_task("Tracing " + str(len(node_dict)) + " nodes...", total=len(node_dict), )
    for node in node_dict.values():
        node.e = False
        node.f = False
    if counter is not None:
        counter.add(len(node_dict))
    current = node_dict[(0,0)]
    current.f = True
    path = []
    distances = {}
    distances[current] = ([current], 0)
    explored_count = 0
    last = current
    while explored_count < len(node_dict):
        cluster = {}
        while current is not None:
            path.append([current])
            explored_count = explored_count + 1
            if counter is not None:
                counter.inc()
                #prit(counter.count, counter.total)
            if usebar:
                progress.update(task1, advance = 1, description = "Tracing {}/{} nodes...".format(explored_count, len(node_dict)))
            before = last
            #prit("C: ",current, ", E: ", explored_count, ", T: ", len(node_dict))
            last = current
            #asert not current.e, "Current already explored!"
            #asert current.f, "Not part of frontier set!"
            current.e = True
            current.f = False
            cluster[current.pos] = current
            
            for node in adjacent_nodes(node_dict, current, directly = False):
                if not node.f and not node.e:
                    distances[node] = extend_path(distances[current],node, updatepath = False)
                    node.f = True
                elif (not node.e) and ((extend_path(distances[current],node, updatepath = False))[1] < (distances[node])[1]):
                    distances[node] = extend_path(distances[current],node, updatepath = False)
            nextnode = None

            adj = adjacent_nodes(node_dict, current, directly= False, unex = True, lastnode = before)
            if len(adj) == 0:
                nextnode = current
                if usebar:
                    backtracking = progress.add_task("Backtracking...", total =None)
                while nextnode is not None and len(adjacent_nodes(node_dict, nextnode, directly = True, unex = True)) == 0:
                    nextnode = nextnode.bkptr

                if nextnode is not None:
                    nextnode = adjacent_nodes(node_dict,nextnode, directly = True, unex = True)[0]

                    nearby = get_edges(node_dict, current, strict = False)

                    nearby[current.pos] = current
                    nearby[nextnode.pos] = nextnode
                    p, _ = shortest_path(nearby, current, nextnode)
                    # if travel(p) > 10:
                    #     prit(p)
                    if len(p) > 2:
                        path.append(p[1:(len(p)-1)])
                if usebar:
                    progress.remove_task(backtracking)
            else:
                nextnode = adj[0]

            if nextnode is not None:
                nextnode.bkptr = current
                
            current = nextnode
        #all adjacent nodes explored, closest unadjacent node will be visited
        if explored_count < len(node_dict):
            d = {}
            radiate_new = get_new(node_dict, last, shortcut = True)
            if len(radiate_new) > precision_factor:
                radiate_new = get_new(node_dict, last, shortcut= True)

            edges = get_edges(node_dict, last, strict = False)
            if len(edges) > precision_factor:
                edges = get_edges(node_dict, last, strict = True)
            if len(edges) > 3 * precision_factor:
                edges = {last.pos : last}
       
            radiate_new.update(edges)
            
            calc = shortest_path(radiate_new, last)
            #asert(len(calc) >= len(radiate_new)), "Len calc: " + str(len(calc)) + ", Len radiate new: " + str(len(radiate_new))
            for node in radiate_new.values():
                if not node.e:
                    d[node] = calc[node] 

            
            nextnode, p = min_dist(d, unex = True)
            distances[nextnode] = extend_path(distances[last], nextnode, updatepath = False)#frompath
            subpath = p[1 :len(p)-1] # len -1
            if len(subpath) != 0:
                path.append(subpath)
            nextnode.jumppoint = last
            current = nextnode
            
    seq = []
    arr = np.array([])
  
    for p in path:
        for n in p:
            seq.append(n.pos)
    arr = np.array(seq)
    dxy = np.diff(arr, axis = 0)
    inst = []
    i = -1
    while i < (len(dxy)-1):
        i = i + 1
        el = dxy[i]
        c = dxy[i]
        while (i < len(dxy)- 1) and np.array_equal(el, dxy[i + 1]) :
            c = c + dxy[i + 1]
            i = i + 1
        inst.append(c)
    if counter is not None:
        counter.reset()
    return np.array(inst)



def path(name, fname, s, precision_factor = 100000000000000, brightness = 200, counter = None):
    with progress: 
        if usebar:
            getimg = progress.add_task("Converting image...", total = None)
        _, testarr = img.drawing_img(fname, brightness, (320,240))
        testarr = cv2.resize(
            testarr, s, interpolation=cv2.INTER_LINEAR)
        if usebar:
            progress.remove_task(getimg)
        nl = to_nodes(testarr)
        e = explore(nl, precision_factor=precision_factor, counter=counter)
        if usebar:
            writefile = progress.add_task("Writing sequence of {}...".format(len(e)), total = len(e))
        with open(name + ".txt", 'w') as f:
            for n in e:
                #asert len(n) ==2, "Something went horribly wrong!"
                f.write(str(n[0]) + "," + str(n[1]))
                f.write("\n")
                if usebar:
                    progress.update(writefile, advance = 1)



class PathMaker():
    def __init__(self, dest, img, dim = (320,240),precision_factor = 200000):
        self.dest = dest
        self.img = img
        self.dim = dim
        self.pf = precision_factor
        self.processes = {}
        self.files = {}
        self.counter = Counter()


    def pathmaker(self, brightness):
        def f():
            path(self.dest + str(brightness), self.img, self.dim, precision_factor=self.pf, brightness=brightness, counter=self.counter)
        return f

    def brightness_maker(self, brightnesses):
        ts = {}
        for brightness in brightnesses:
            f = self.pathmaker(brightness)
            fname = self.dest + str(brightness)
            self.files[brightness] = fname + ".txt"
            ts[brightness] = (threading.Thread(target=f))
        self.processes = ts
    
    def start(self):
        for t in self.processes.values():
            t.start()
