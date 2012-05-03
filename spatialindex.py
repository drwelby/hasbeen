import struct
import os

class Bin:
  def __init__(self):
    self.id = 1
    self.features = []
    
class Feature:
  def __init__(self):
    self.id = None
    self.xmin = None
    self.ymin = None
    self.xmax = None
    self.ymax = None
    
class SBN:
  def __init__(self, sbn=None):
    self.bins = []
    self.numFeat = 0
    self.sbnName = sbn
    self.load(self.sbnName)
    
  def load(self, sbnName=None):
    self.sbn = None
    self.fileCode = 9994
    self.unknownByte4 = -400
    self.unused1 = None
    self.unused2 = None
    self.unused3 = None
    self.unused4 = None
    self.fileLen = 0
    self.numRecords = 0
    self.xmin = None
    self.ymin = None
    self.xmax = None
    self.ymax = None 
    self.zmin = None
    self.zmax = None
    self.zmax = None
    self.mmin = None
    self.mmax = None 
    self.unknownByte96 = 0  
    if sbnName:
      try:
        self.sbn = open(sbnName, "rb")
      except IOError:
        raise Exception("Unable to open sbn file or sbn file not specified")     
      # Read sbn header
      self.fileCode = struct.unpack(">i", self.sbn.read(4))[0]    
      self.unknownByte4 = struct.unpack(">i", self.sbn.read(4))[0]
      self.unused1 = struct.unpack(">i", self.sbn.read(4))[0]
      self.unused2 = struct.unpack(">i", self.sbn.read(4))[0]
      self.unused3 = struct.unpack(">i", self.sbn.read(4))[0]
      self.unused4 = struct.unpack(">i", self.sbn.read(4))[0]
      self.fileLen = struct.unpack(">i", self.sbn.read(4))[0] * 2
      # NOTE: numRecords is records in shp/dbf file not # of bins!
      self.numRecords = struct.unpack(">i", self.sbn.read(4))[0]
      self.xmin = struct.unpack(">d", self.sbn.read(8))[0]
      self.ymin = struct.unpack(">d", self.sbn.read(8))[0]
      self.xmax = struct.unpack(">d", self.sbn.read(8))[0]
      self.ymax = struct.unpack(">d", self.sbn.read(8))[0]
      self.zmin = struct.unpack(">d", self.sbn.read(8))[0]
      self.zmax = struct.unpack(">d", self.sbn.read(8))[0]
      self.mmin = struct.unpack(">d", self.sbn.read(8))[0]
      self.mmax = struct.unpack(">d", self.sbn.read(8))[0]
      self.unknownByte96 = struct.unpack(">i", self.sbn.read(4))[0]    
      # Read BIN descriptors
      recNum = struct.unpack(">i", self.sbn.read(4))[0]
      recLen = struct.unpack(">i", self.sbn.read(4))[0] * 2    
      # Append a blank convienience bin as a placeholder for bin 1
      b = Bin()
      b.id = 1    
      self.bins.append(b)
      for i in range(recLen/8):
        b = Bin()
        b.id = struct.unpack(">i", self.sbn.read(4))[0]
        b.numFeat = struct.unpack(">i", self.sbn.read(4))[0]      
        self.bins.append(b)
      # Read Bin contents
      while self.sbn.tell() < self.fileLen:
        binId = struct.unpack(">i", self.sbn.read(4))[0]          
        recLen = struct.unpack(">i", self.sbn.read(4))[0] * 2
        
        for i in range(recLen/8):
          f = Feature()
          f.xmin = struct.unpack(">B",self.sbn.read(1))[0]
          f.ymin = struct.unpack(">B",self.sbn.read(1))[0]
          f.xmax = struct.unpack(">B",self.sbn.read(1))[0]
          f.ymax = struct.unpack(">B",self.sbn.read(1))[0]
          f.id = struct.unpack(">i", self.sbn.read(4))[0] 
          b = self.bin(binId)
          b.features.append(f)
          self.numFeat += 1                                                           
      self.sbn.close()

  def bin(self, bid):
    for b in self.bins:
      if b.id == bid:
        return b
        
  def save(self, sbnName=None):
    sbnName = sbnName or self.sbnName
    sbn = open(sbnName, "wb")
    sbxName = os.path.splitext(sbnName)[0] + ".sbx"
    sbx = open(sbxName, "wb")
    # Write headers
    sbn.write(struct.pack(">i", self.fileCode))
    sbx.write(struct.pack(">i", self.fileCode))
    sbn.write(struct.pack(">i", self.unknownByte4))
    sbx.write(struct.pack(">i", self.unknownByte4))
    sbn.write(struct.pack(">i", self.unused1))
    sbx.write(struct.pack(">i", self.unused1))
    sbn.write(struct.pack(">i", self.unused2))
    sbx.write(struct.pack(">i", self.unused2))
    sbn.write(struct.pack(">i", self.unused3))
    sbx.write(struct.pack(">i", self.unused3))
    sbn.write(struct.pack(">i", self.unused4))
    sbx.write(struct.pack(">i", self.unused4))
    
    # Calculate File Length fields    
    # first bin descriptors
    totalBinSize = len(self.bins[1:]) * 8
    # then bins with features
    usedBinSize = len([b for b in self.bins if b.id > 0]) * 8
    sbxSize = 100 + usedBinSize 
    sbnSize = 100 + totalBinSize + usedBinSize
    sbxSize //= 2
    sbnSize += self.numFeat * 8
    sbnSize //= 2
    sbn.write(struct.pack(">i", sbnSize))
    sbx.write(struct.pack(">i", sbxSize))
    sbn.write(struct.pack(">i", self.numRecords))
    sbx.write(struct.pack(">i", self.numRecords))
    sbn.write(struct.pack(">d", self.xmin))
    sbx.write(struct.pack(">d", self.xmin))
    sbn.write(struct.pack(">d", self.ymin))
    sbx.write(struct.pack(">d", self.ymin))
    sbn.write(struct.pack(">d", self.xmax))
    sbx.write(struct.pack(">d", self.xmax))
    sbn.write(struct.pack(">d", self.ymax))
    sbx.write(struct.pack(">d", self.ymax))
    sbn.write(struct.pack(">d", self.zmin))
    sbx.write(struct.pack(">d", self.zmin))
    sbn.write(struct.pack(">d", self.zmax))
    sbx.write(struct.pack(">d", self.zmax))
    sbn.write(struct.pack(">d", self.mmin))
    sbx.write(struct.pack(">d", self.mmin))
    sbn.write(struct.pack(">d", self.mmax))
    sbx.write(struct.pack(">d", self.mmax))    
    sbn.write(struct.pack(">i", self.unknownByte96))
    sbx.write(struct.pack(">i", self.unknownByte96))    
    # sbn and sbx records
    # first create bin descriptors record
    recLen = (len(self.bins[1:]) * 4)
    sbn.write(struct.pack(">i", 1))
    sbn.write(struct.pack(">i", recLen))
    sbx.write(struct.pack(">i", 100))
    sbx.write(struct.pack(">i", recLen + 2))
    for b in self.bins[1:]:
      sbn.write(struct.pack(">i", b.id))
      sbn.write(struct.pack(">i", len(b.features)))
    # write actual bins
    for b in self.bins[1:]:
      if b.id <= 0:
        continue
      sbx.write(struct.pack(">i", sbn.tell()))
      sbx.write(struct.pack(">i", (len(b.features) * 2)))
      sbn.write(struct.pack(">i", b.id))   
      sbn.write(struct.pack(">i", len(b.features) * 4))    
      for f in b.features:
        sbn.write(struct.pack(">B", f.xmin))
        sbn.write(struct.pack(">B", f.ymin))
        sbn.write(struct.pack(">B", f.xmax))
        sbn.write(struct.pack(">B", f.ymax))
        sbn.write(struct.pack(">i", f.id))     
    sbn.close()
    sbx.close()
    
      
          
    
    
    
    
        
      
