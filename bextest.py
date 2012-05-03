# Bextest.py tests binning algoritms against an existing .sbn file
#
import shapefile
from hasbeen import HasBeen
from bextree import Tree
from mapper import mapshapefile
from spatialindex import SBN
import sys

if len(sys.argv) > 1:
    shpfile =  sys.argv[1]
else:
    print "Usage: bextest.py [shapefile]"
    print "Bins the features in a shapefile and compares it to an existing sbn"
    sys.exit()


h = HasBeen(shpfile)

# open up the existing sbn to compare against
sbn = SBN(shpfile + ".sbn")

# compare the generated sbn versus ESRI's
for id, bin in enumerate(sbn.bins):
    if id ==0 : continue
    a = len(bin.features) == len(h.bins[id].features)
    if not a: 
        print "Bin %s -" % id,
        print "E: %s, L:%s" % (len(bin.features), len(h.bins[id].features))
        if len(bin.features) > 0:
            tb = bin.features
        else:
            tb = h.bins[id].features
        xmin = 255
        ymin = 255
        xmax = 0
        ymax = 0
        for f in tb:
            print "%s," % f.id,
            xmin = min(xmin,f.xmin)
            ymin = min(ymin,f.ymin)
            xmax = max(xmax,f.xmax)
            ymax = max(ymax,f.ymax)
        print "\n f_bbox %s-%s,%s-%s" % (xmin,xmax,ymin,ymax)
        node = t.nodes[id]
        print " node %s-%s,%s-%s/%s\n" % (node.xmin,node.xmax,node.ymin,node.ymax,node.splitcoord)



