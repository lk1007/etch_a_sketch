import preprocessing.image_to_drawing as img
from rich.progress import Progress

black = 20
import math
import cv2
import numpy as np
usebar = True
progress = None
progress = Progress()
import threading
import multiprocessing

from gui.counter import Counter

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

    if updatepath:
        for n in path:
            newlist.append(n)
        
        newlist.append(node)
        last = path[-1]
    else:
        newlist = [node]
        last = path_entry[0][0]
    return (newlist, dist + last.dist(node))

def shortest_path(node_dict, start, end = None, any_f = False):

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

        current.in_settled = True
        
        if any_f:
            if current.f and not current.e:
                return distances[current]
        elif end is not None and current == end:
            return distances[current]

        adj = adjacent_nodes (node_dict, current, unseg_only=False, unex_sp_only = True)
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
                distances[node] = extend_path(distances[current],node, updatepath=True)
                node.in_frontier = True
                frontier_count = frontier_count + 1
            elif (not node.in_settled) and ((extend_path(distances[current],node))[1] < (distances[node])[1]):
                distances[node] = extend_path(distances[current],node)
                
        ret = min_dist({k: v for k, v in distances.items() if k.in_frontier})
        
        if ret is not None:
            current, _ = ret
    #raise Exception("This path unused.")
    return None

def travel(nodelist):
    dist = 0.0
    prev = nodelist[0]
    for node in nodelist[1:]:
        dist = dist + prev.cost(node)
        prev = node
    return dist

def adjacent_nodes (node_dict, node, lastnode = None, unseg_only = True, unex_only = False, unex_sp_only = False, f_only = False):
    x,y = node.pos
    v = []
    c = 0
    
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
            if (not unseg_only or (not n.segmented and not n.to_segment)) and (not unex_only or not n.e) and (not unex_sp_only or not n.in_settled) and (not f_only or n.f):
                v.append(n)
                n.to_segment = True
    
    node.edge = c <= 5
    node.external = not c == 8

    return v


class Node:
    def __init__(self, x,y):
        self.pos = x,y
        self.bkptr = None
        self.e = False
        self.f = False
        self.edge = False
        self.external = False
        self.jumppoint = None
        self.to_segment = False
        self.segmented = False
        self.color = -1
        
    def dist(self, destination):
        calculated_distance = math.dist(self.pos, destination.pos)
        if destination == self.jumppoint or destination.jumppoint == self:
            return calculated_distance / 100000
        elif calculated_distance - math.sqrt(2) < 0.001:
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

#Convert an image array into continuous segments, 
#also return a dictionary mapping pixels of the image
#to nodes.
def to_segments(arr):
    nodes = {}
    i = 0
    nodes[(0,0)] = Node(0,0)
    
    while i < len(arr):
        j = 0
        while j < len(arr[i]):
            landlocked = False
            try:
                if arr[i + 1][j] <= black and arr[i - 1][j] <= black and arr[i][j + 1] <= black and arr[i][j - 1] <= black and arr[i + 1][j + 1] <= black and arr[i + 1][j -1] <= black and arr[i - 1][j- 1] <= black and arr[i - 1][j + 1] <= black:
                    landlocked = True
            except IndexError:
                pass

            if arr[i][j] <= black and not landlocked:
                newnode = Node(i,j)
                nodes[(i,j)] = newnode
            j = j + 1
        i = i + 1

    #Now coords maps coordinates to nodes. Now scan in a raster and segment
    # clusters of the path. 
    segmented_count = 0
    current = None
    last = None
    segments = []
    all_nodes = list(nodes.values())
    k = 0
    color = 0
    while segmented_count < len(nodes):
        #Get next unsegmented node.
        current = None
        k = 0
        while k < len(all_nodes) and current is None:
            n = all_nodes[k]
            if not n.segmented:
                current = n
            k += 1

        cluster = {}
        clusterfrontier = []
        if current is not None:
            clusterfrontier = [current]

        while len(clusterfrontier) > 0:
            current = clusterfrontier.pop(0)
            cluster[current.pos] = current

            segmented_count += 1

            last = current
            current.segmented = True
            #Get a node list: nodes not yet added to cluster.
            adj = adjacent_nodes(nodes, current, last)
            adj.extend(clusterfrontier)
            clusterfrontier = adj
        
        #Register the cluster. Also, color in the cluster for later.
        segments.append(cluster)
        for n in cluster.values():
            n.color = color
        color += 1

    return segments, nodes

def trace_segment(segment):

    #segment, counter = args
    #Initialize variables    
    path = []
    segment_size = len(segment)
    if segment_size == 0:
        return path

    for node in segment.values():
        node.e = False
        node.f = False
    current = list(segment.values())[0]

    last = None
    distances = {}
    distances[current] = ([current], 0)

    #continue until path goes through all nodes.
    while segment_size > 0 :
        #Add on to new path.
        path.append(current)
        segment_size -= 1

        last = current

        #Add to explored, remove from frontier.
        current.e = True
        current.f = False

        #Get adj and go to next adj. Repeat. As you go, update the distances dictionary.
        #If not in frontier set, calculate distance and store.
        #If in frontier set, calculate distance and store IF a shorter distance is found,
        # and not in explore set. 
        for node in adjacent_nodes(segment, current, last, unseg_only = False, unex_only=True):
            if not node.f and not node.e:
                distances[node] = extend_path(distances[current], node, updatepath = True)
                node.f = True
            elif (not node.e) and (node.f) and ((extend_path(distances[current],node, updatepath = True))[1] < (distances[node])[1]):
                distances[node] = extend_path(distances[current],node, updatepath = True)

        #Get adjacencies not explored and in frontier.
        adj = adjacent_nodes(segment, current, last, unseg_only=False, unex_only = True, f_only = True)

        #If nothing adjacent, go to closest frontier node.
        if len(adj) == 0:
            #Shortest path to new frontier.
            path_to_next = []
            result = shortest_path(segment, current, any_f = True)
            if result is not None:
                path_to_next, d = result
            #Append path, exlude start and end.
            if len(path_to_next) > 2:
                path.extend((path_to_next[1:(len(path_to_next)-1)]))
                
                segment_size -= len(path_to_next) - 2
            
                #Next node at the end of the path.

                path_to_current, nd = distances[current]
                current = path_to_next[-1]
                path_to_current.extend(path_to_current[1:])
            

                #todo: add new node's distance entry.
                distances[current] = (path_to_current , d + nd) 
            else:
                current = None
        #If something adjacent, go there.
        elif len(adj) > 0:
            current = adj[0]
            # print("Error:", segment_size, len(segment))
            # raise Exception("Huh? Maybe at the last node?")
    return path

def trace_segments(segments, counter = None):
    paths = []
    if counter is not None:
        counter.add(len(segments))
    if usebar:
        task = progress.add_task(f"Tracing {len(segments)} segments...", total = len(segments))
    with multiprocessing.Pool() as pool:
        for path in pool.imap_unordered(trace_segment, segments):
            counter.inc()
            paths.append(path)
            if usebar:
                progress.update(task, advance = 1)
    if usebar:
        progress.remove_task(task)
    return paths

#Given a node, find closest untraced node.
def radiate_new(points, current_color, nodes):
    itineraries = []
    for point in points:
        x,y = point.pos
        
        r = 1
        found = False
        while not found:
            coords = []
            curr = (r, 0)
            for i in range(r + 1):
                x2, y2 = curr
                coords.extend([
                    (x + x2, y + y2),
                    (x - x2, y - y2),
                    (x - x2, y + y2),
                    (x + x2, y - y2)
                ])
                curr = (x2 - 1, y2 + 1)

            for c in coords:
                if c in nodes and nodes[c].color == current_color:
                    itineraries.append((nodes[c], point))
                    found = True
            r += 1
    #Now itineraries has tuples (start, destination).
    #Return the smallest cost tuple.
    shortest_iternary = itineraries[0]
    shortest_cost = shortest_iternary[0].dist(shortest_iternary[1])
    for itinerary in itineraries:
        cost = shortest_iternary[0].dist(shortest_iternary[1])
        if cost < shortest_cost:
            shortest_iternary = itinerary 
            shortest_cost = cost
    return shortest_iternary

def connect(paths, nodes, node_segments, min_segment = 16, counter = None):

    #Connects the paths in arbitrary order.
    #Makes a bad result. 
    paths_considered = []
    path = []
    colors = [] #colors that have been taken to account.

    #Add each available color to list of colors.

    for p in paths:
        if len(p) >= min_segment or (p[0].pos[0] == 0 and p[0].pos[1] == 0):
            #Add path to be considered.
            paths_considered.append(p)
        else:
            print(p)
            colors.append(p[0].color)
    
    #Now connect the filtered path. 
    # for p in paths_considered:
    #     path.extend(p)
    current = paths_considered[0]
    
    if counter is not None:
        counter.reset()
        counter.add(len(paths_considered))

    while len(paths_considered) > 0:
        print(len(paths_considered))
        paths_considered.remove(current)
        path.extend(current)
        current_color = current[0].color
        colors.append(current_color)

        if len(paths_considered) > 0:
            #Find which starter node is closest to the current color.
            
            #For the rest of the segments in the list 
            # whose color hasn't been added to the list, calculate nearest
            # current-color node to it.
            points = []
            for p in paths_considered:
                if p[0].color not in colors:
                    points.append(p[0])
            starting_point, next_node = radiate_new(points, current_color, nodes)
            print("Calculating shortest path.")

            #get relevant subsection of node dictionary.
            node_segment = {}
            for segment in node_segments:
                if(list(segment.values())[0].color == current_color):
                    node_segment = segment

            #shortest path: end of current path -> starting point.
            p = shortest_path(node_segment, p[-1], end=starting_point)
            
            #add in that path
            if len(p) > 2:
                path.extend(p[1:-1])
            
            #Update current
            for path in paths_considered:
                if path[0] == next_node:
                    current = path

        if counter is not None:
            counter.inc()

    #Generate the machine instructions.
    seq = [(0,0)]
    arr = np.array([])
  
    for n in path:
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

    return np.array(inst)

    # raise Exception("Unimplemented")

def path(name, fname, s, precision_factor = 100000000000000, brightness = 200, counter = None):
    with progress: 
        if usebar:
            getimg = progress.add_task("Converting image...", total = None)
        _, testarr = img.drawing_img(fname, brightness, (320,240))
        testarr = cv2.resize(
            testarr, s, interpolation=cv2.INTER_LINEAR)
        if usebar:
            progress.remove_task(getimg)
        sl, nodes = to_segments(testarr)
        paths = trace_segments(sl, counter = counter)
        e = connect(paths, nodes, node_segments = sl, counter=counter)
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
