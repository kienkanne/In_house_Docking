from chimera import runCommand, openModels
import WriteDMS
import _surface
import sys

# load structure
runCommand("open 8hqg_charged_noH.mol2")

# generate molecular surface
runCommand("surface")

# get generated surface model
surfs = openModels.list(modelTypes=[_surface.SurfaceModel])

surf = surfs[0]

# write DMS
WriteDMS.writeDMS(surf, "rec.dms")

runCommand("stop")