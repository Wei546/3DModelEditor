import vedo
from vedo.applications import FreeHandCutPlotter

vedo.settings.use_parallel_projection = True  # to avoid perspective artifacts

msh = vedo.Volume(vedo.dataurl+'embryo.tif').isosurface().color('gold', 0.25) # Mesh

plt = FreeHandCutPlotter(msh)
plt.add_hover_legend()
#plt.init(some_list_of_initial_pts) #optional!
plt.start(axes=1, bg2='lightblue').close()