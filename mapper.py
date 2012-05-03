import shapefile
from spatialindex import SBN, Bin, Feature
from math import floor, ceil

def mapshapefile(sf):
    # map features in a shapefile to index space
    shapes = sf.shapes()
    features = []
    for index, shape in enumerate(shapes):
        ft = mapfeature(index,shape,sf)
        features.append(ft)
    return features


def mapfeature(index,shape,sf):
    # map individual features, returns Features
    sf_xrange = sf.bbox[2]-sf.bbox[0]
    sf_yrange = sf.bbox[3]-sf.bbox[1]

    ft = Feature()
    ft.id = index + 1
    if sf.shapeType == 1:
        (ptx,pty) = shape.points[0]
        sh_bbox = (ptx, pty, ptx, pty)
    else:
        sh_bbox = shape.bbox

    ft_xmin = ((sh_bbox[0]-sf.bbox[0])/sf_xrange*255.0)
    # not sure why this rounding is needed, but it is
    mod_xmin = (ft_xmin%1 - .005)%1 + int(ft_xmin)
    ft.xmin = int(floor(mod_xmin))
    if ft.xmin < 0 : ft.xmin = 0
     
    ft_ymin = ((sh_bbox[1]-sf.bbox[1])/sf_yrange*255.0)
    mod_ymin = (ft_ymin%1 - .005)%1 + int(ft_ymin)
    ft.ymin = int(floor(mod_ymin))
    if ft.ymin < 0 : ft.ymin = 0

    ft_xmax = ((sh_bbox[2]-sf.bbox[0])/sf_xrange*255.0)
    mod_xmax = (ft_xmax%1 + .005)%1 + int(ft_xmax)
    ft.xmax = int(ceil(mod_xmax))
    if ft.xmax > 255: ft.xmax = 255

    ft_ymax = ((sh_bbox[3]-sf.bbox[1])/sf_yrange*255.0)
    mod_ymax = (ft_ymax%1 + .005)%1 + int(ft_ymax)
    ft.ymax = int(ceil(mod_ymax))
    if ft.ymax > 255: ft.ymax = 255

    return ft

if __name__ == "__main__":
    file = "../cities/132"
    s = shapefile.Reader(file)
    sf = mapshapefile(s)
    sbn = SBN(file + ".sbn")
    for id, bin in enumerate(sbn.bins):
        for f in bin.features:
            m = sf[f.id-1]
            if (f.xmin,f.xmax,f.ymin,f.ymax) != (m.xmin,m.xmax,m.ymin,m.ymax):
                print "Bin %s (%s)" % (id, bin.id)  
                print " SBN Feature %s (%s,%s,%s,%s)" % (f.id, f.xmin, f.ymin, f.xmax, f.ymax)
                print " Mapper Feature %s (%s,%s,%s,%s)\n" %(m.id, m.xmin, m.ymin, m.xmax, m.ymax) 
