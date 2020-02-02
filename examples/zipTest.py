import tempfile as tmp
import ssop_config
import os
from zipfile import ZipFile, ZIP_DEFLATED

s = "abc.sol"
us = unicode(s)
print("abc in s: " + str('abc' in s))
print("abc in ustr: " + str("abc" in us))
print("uabc in ustr: " + str(u"abc" in s))

zipFilePath = "/home/vladimirv/python_work/pyomo-everest/ssop/.tmp/testSsop-1-results.zip"
with ZipFile(zipFilePath, 'r') as z:
    fileNames = z.namelist()
    infoList =z.infolist()
    print("fileNames: " , fileNames)
    print("infoList : ", infoList)
    for finfo in infoList:
        if '.sol' in finfo.filename:
            finfo.filename = os.path.basename(finfo.filename)
            z.extract(finfo, ssop_config.SSOP_DEFAULT_WORKING_DIR)
            # z.extract(fn, ssop_config.SSOP_DEFAULT_WORKING_DIR + "/" + os.path.basename(fn))

quit()

print(ssop_config.SSOP_RESOURCES["vvvolhome"])
print(os.path.join(os.path.dirname(__file__)))

path = "/home/user/some/ m_ore/f.opt"
pathSplitted = path.split("/")
print pathSplitted
print pathSplitted[len(pathSplitted) - 1]
quit()

files = ["f1", "f2", "f3"]
print "".join(files[i] + " " for i in range(len(files)))

quit()

tdir = tmp.mkdtemp()

print str(tdir)

for k in ssop_config.SSOP_RESOURCES.keys():
    print(ssop_config.SSOP_RESOURCES[k])
print("======================")
print(ssop_config.SSOP_RESOURCES.values())
