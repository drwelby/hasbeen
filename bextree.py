# Binary EXpanding TREE
# (for those not familiar with ESRI trivia)
# The spatial index tree behind the SBN file format


from spatialindex import Bin, Feature
from math import log, ceil

class Node:
    id = None
    tree = None
    split = None # "x" or "y" based on axis of cutting coord
    righttop = None # child node, either right or top
    parent = None # parent node
    leftbottom = None # child node, either left or bottom
    sibling = None # sibling node
    splitcoord = 0
    features = []
    holdfeatures = []
    seamcompacted = True # should this node compact its seam features
    full = False
    maxcount = 0

    def __init__(self, id):
        self.id = id
        self.count = 0
        self.features = []
        self.seamcompacted = True
        self.holdfeatures = []
        self.full = False
        self.sibling = None

    def __repr__(self):
        return 'Node %s: (%s-%s,%s-%s)/%s' % (self.id, self.xmin, self.xmax, self.ymin, self.ymax, self.splitcoord)

    def addsplitcoord(self):
        if self.split == "x":
            mid = int((self.xmin + self.xmax) / 2.0) + 1
        else:
            mid = int((self.ymin + self.ymax) / 2.0) + 1
        self.splitcoord = mid - mid%2


    def addchildren(self):
        #first child node
        rt = self.tree.nodes[self.id*2]
        rt.tree = self.tree
        if self.split == "x":
            rt.xmin = int(self.splitcoord) + 1
            rt.xmax = self.xmax
            rt.ymin = self.ymin
            rt.ymax = self.ymax
            rt.split = "y"
            rt.addsplitcoord()
        else:
            rt.xmin = self.xmin
            rt.xmax = self.xmax
            rt.ymin = int(self.splitcoord) + 1
            rt.ymax = self.ymax
            rt.split = "x"
            rt.addsplitcoord()
        rt.parent = self
        self.righttop = rt
        #second child node
        lb = self.tree.nodes[self.id * 2 + 1]
        lb.tree = self.tree
        if self.split == "x":
            lb.xmax = int(self.splitcoord)
            lb.xmin = self.xmin
            lb.ymin = self.ymin
            lb.ymax = self.ymax
            lb.split = "y"
            lb.addsplitcoord()
        else:
            lb.xmin = self.xmin
            lb.xmax = self.xmax
            lb.ymax = int(self.splitcoord)
            lb.ymin = self.ymin
            lb.split = "x"
            lb.addsplitcoord()
        lb.parent = self
        self.leftbottom = lb
        lb.sibling = rt
        rt.sibling = lb

    def grow(self):
        #recursively grow the tree
        if self.id >= self.tree.firstleafid:
            return
        self.addchildren()
        self.righttop.grow()
        self.leftbottom.grow()

    def insert(self,feature):
        # if this is leaf, just take the feature
        if self.id >= self.tree.firstleafid:
            self.features.append(feature)
            return
        # it takes 8 features to split a node
        # so we'll hold 8 features first
        if self.id > 1:
            if not self.full:
                if len(self.holdfeatures) < 8 :
                    self.holdfeatures.append(feature)
                    return
                if len(self.holdfeatures) == 8 :
                    self.full = True
                    self.holdfeatures.append(feature)
                    for f in self.holdfeatures:
                        self.insert(f)
                    return
        # The node is split so we can sort features
        if self.split == "x":
            (min,max) = (feature.xmin, feature.xmax)
            (smin,smax) = (feature.ymin, feature.ymax)
        else:
            (min,max) = (feature.ymin, feature.ymax)
            (smin,smax) = (feature.xmin, feature.xmax)
        # Grab features on the seam we can't split
        if min <= self.splitcoord and max > self.splitcoord:
            self.features.append(feature)
            return
        else:
            self.passfeature(feature)

    def passfeature(self, feature):
        # pass the feature to a child node
        if self.split == "x":
            (min,max) = (feature.xmin, feature.xmax)
        else:
            (min,max) = (feature.ymin, feature.ymax)
        if min  < self.splitcoord:
            self.leftbottom.insert(feature)
        else:
            self.righttop.insert(feature)

    def allfeatures(self):
        # return all the features in the node
        if self.id >= self.tree.firstleafid:
            return self.features
        if self.id == 1:
            return self.features
        if len(self.holdfeatures) <= 8:
            return self.holdfeatures
        else: 
            return self.features 

    def siblingfeaturecount(self):
        # return the number of features of a node and its sibling
        return len(self.allfeatures()) + len(self.sibling.allfeatures())

class Tree:
    
    nodes = []
    levels = 0
    firstleafid = 0
    root = None

    def __init__(self, featurecount):
        self.nodes = []
        self.levels = int(log(((featurecount -1 )/8.0 + 1),2) + 1)
        if self.levels < 2 :
            self.levels = 2
        if self.levels > 15: 
            self.levels = 15
        self.firstleafid = 2**(self.levels-1)
        for i in xrange(2**self.levels):
            n = Node(i)
            self.nodes.append(n)

        self.root = self.nodes[1]
        self.root.id = 1
        self.root.tree = self
        self.root.split = "x"
        self.root.xmin = 0
        self.root.ymin = 0
        self.root.xmax = 255
        self.root.ymax = 255
        self.root.addsplitcoord()
        self.root.grow()

    def insert(self,feature):
        #insert a feature into the tree
        self.root.insert(feature)

    def tobins(self):
        #convert a tree structure to a SpatialIndex bin array
        bins = []
        b = Bin()
        bins.append(b)
        for node in self.nodes[1:]:
            b = Bin()
            b.features = node.allfeatures()
            bins.append(b)
        return bins

    def featuresinlevel(self, level):
        # return the number of features in a level
        start = int(2**(level-1))
        end = int((2 * start) - 1)
        featurecount = 0
        for node in self.nodes[start:end+1]:
            featurecount += len(node.features)
        return featurecount


    def compactseamfeatures(self):
        # the mystery algorithm - compaction? optimization? obfuscation?
        if self.levels < 4:
            return
        if self.levels > 4:
            self.compactseamfeatures2()
            return
        #for node in self.nodes[1:self.firstleafid/4]:
        start = self.firstleafid/2 - 1
        end = start/8
        if start < 3: start = 3 
        if end < 1 : end = 1
        for node in self.nodes[start:end:-1]:
            #if len(node.features) > 0:
            #    continue
            id = node.id
            children = self.nodes[id*2:id*2+2]
            for child in children:
                cid = child.id
                grandchildren = self.nodes[cid*2:cid*2 + 2]
                gccount = 0
                for gcnode in grandchildren:
                    gccount += len(gcnode.allfeatures())
                #print "Node %s has %s GC" % (id,gccount)
                if gccount == 0:
                    #print "Slurping %s features from node %s" % (len(child.allfeatures()),child.id)
                    #node.features.extend(child.features)
                    if len(child.allfeatures()) < 4: # this is weird but it works
                        node.features.extend(child.allfeatures())
                        child.features = []
                        child.holdfeatures = []

    def compactseamfeatures2(self):
        # another run at the mystery algorithm

        #for node in self.nodes[1:self.firstleafid/4]:
        start = self.firstleafid/2 - 1
        end = start/8
        if start < 3: start = 3 
        if end < 1: end =1 
        for node in self.nodes[start:end:-1]:
            #if len(node.features) > 0 and self.levels < 6:
            #    continue
            id = node.id
            children = self.nodes[id*2:id*2+2]
            grandchildren = self.nodes[id*4:id*4+4]
            gccount = 0
            for gcnode in grandchildren:
                gccount += len(gcnode.allfeatures())
            #print "Node %s has %s GC" % (id,gccount)
            if gccount == 0:
                for cnode in children:
                    if len(cnode.allfeatures()) + len(node.features) > 8:
                        continue
                    #print "Slurping %s features from node %s" % (len(cnode.features),cnode.id)
                    node.features.extend(cnode.allfeatures())
                    #node.features.extend(cnode.features)
                    cnode.features = []
                    cnode.holdfeatures = []
        # compact unsplit nodes see cities/248
        return
        for node in self.nodes[start:end:-1]:
            level = ceil(log(node.id,2))  
            id = node.id
            children = self.nodes[id*2+1:id*2-1:-1]
            empty = False
            childrenfeatures = 0
            for child in children:
                #if not child.full:
                #    held = True
                cid = child.id
                childrenfeatures += len(child.features)
                grandchildren = self.nodes[cid*2:cid*2 + 2]
                for gcnode in grandchildren:
                    if len(gcnode.features) == 0:
                        empty = True
                #print "Node %s childless: %s" % (cid,empty)
            print empty, childrenfeatures
            if empty and childrenfeatures > 0: 
                #node.features.extend(child.features)
                for child in children:
                    if child.siblingfeaturecount() < 4 and child.siblingfeaturecount() > 0 :
                        continue
                    #if self.featuresinlevel(level) >= 8:
                    #    return
                    #print "Slurping %s features from node %s" % (len(child.allfeatures()),child.id)
                    node.features.extend(child.allfeatures())
                    #node.full = True
                    child.features = []
                    child.holdfeatures = []
                return


                    
if __name__ == "__main__":

    t = Tree(4)

    for i in range(8):
        f = Feature()
        f.xmin = 120
        f.xmax = 130
        f.ymin = 120
        f.ymax = 130

        t.insert(f)

    f = Feature()
    f.xmin = 130
    f.xmax = 140
    f.ymin = 130
    f.ymax = 140

    t.insert(f)

    for node in t.nodes[1:]:
        hfl = len(node.holdfeatures)
        nfl = len(node.nodefeatures)
        print "%s: %s %s" % (node.id, nfl, hfl)

