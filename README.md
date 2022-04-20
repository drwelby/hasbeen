### FYI this is reaaallly old



HASBEEN
==========

Tools to create ESRI's .sbn spatial indexing format

Background
------------

In October 2011 Joel Lawhead figured out [how to decode ESRI's SBN spatial indexing format](http://geospatialpython.com/2011/10/your-chance-to-make-gis-history.html). He didn't recognize the indexing algorithm, so in the best Open Source spirit he released his code and some sample data with the challenge to figure out what was going on.

I took his data and started trying to visualize it differently, looking for patterns that might give away the algorithm. First I noticed [Z-shaped curves](http://flic.kr/p/atrEim), which suggest quadtrees, or a z-order curve. I then noticed that the many of features were actually on seams between possible divisions of the space, and by tracking them it became clear that the spatial index was a binary division. The index space (a 256 x 256 grid) initally split in half horizontally. Then each rectangular half would split vertical into two squares, and so on. 

To further test how the algorithm worked, I created a series of incremental shapefiles that would add one feature to the previous one. I then wrote some scripts that would track how the index tree grew and also tracked features as they were sorted in the tree. Tracking through thousands of shapefiles, I noticed is that no matter the shapefiles, the size of the tree [jumped at fixed feature counts](http://flic.kr/p/cnSSTC). Looking at the numbers, it became clear that the size of tree was designed to keep an average of 8 features or less per node. By tracking individual nodes, I also noticed that a node would fill up until it had 8 features in it, and after that it would send the feature down to its child nodes.

With thousands of test shapefiles to work with, I also tested the algorithm that maps the features to index space and found that it does some interesting rounding. At this point it seems like we had the algorithm figured out. But in some of the test shapefiles some features would be sorted one level lower than the ESRI algorithm places them. After checking the individual features, we couldn't find any reason why the features did not sort all the way to the bin that should contain them. And there didn't seem to be any obvious explanation why.

After looking at many shapefiles with errors, something popped out. If you look at a bin, you'd usually see something like this:

    BIN 12 : 5, 67, 122, 156

Where the numbers are the Feature ID's of the features in that bin. They are almost always in ascending order. But in the cases where features were sorting too low, I'd see:

    BIN 15: 13, 23, 77, 145, 20, 92

Where features 20 and 92 were two features that should not be in this node, but actually in its child nodes. Being out of order, it seemed like they had been sorted down, then pulled back up. Looking at a lot of shapefiles with the pattern revealed another level to the algorithm: after sorting all the features into the tree, another process would check nodes to see if their grandchildren were empty - if they were, then it would pull its child features back up. Once this was implemented in the code I was able to correctly reproduce the ESRI SBN sorting in my test shapefiles.

There was only one problem - the test shapefiles were randomly generated and spatially very uniformly distributed. Testing against real world data, like the world cities shapefile, still showed some features that were sorted further into the tree than the ESRI algorithm. I have some ideas why, but haven't cracked this final step. 

About The Code
--------------

hasbeen.py gives you the spatial index tree and a way to add features to it, and get the whole tree as a flat array. It does not write the SBN files. SBN read/write is provided by Joel Lawhead's spatialindex.py, of which I include an older version for reading SBNs for testing. Joel is integrating hasbeen into spatialindex.

Also
----------

Since the division is binary, it looks like you can do the sorting quickly with a little [bit twiddling](https://gist.github.com/drwelby/5977601).
