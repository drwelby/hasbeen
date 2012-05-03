import shapefile
from bextree import Tree
from mapper import mapshapefile

class HasBeen:
 
    def __init__(self,shpfile):

        # open the shapefile
        self.shp = shapefile.Reader(shpfile)
        # map the shapfile features to index space
        self.map = mapshapefile(self.shp)
        # build an empty tree of the right size
        self.tree = Tree(len(self.shp.shapes()))
        # insert the mapped features into the tree
        for feature in self.map:
            self.tree.insert(feature)
        # do the magic compaction algorithm
        self.tree.compactseamfeatures()
        #convert the tree structure to a flat array
        self.bins = self.tree.tobins()
