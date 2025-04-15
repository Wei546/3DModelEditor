import vtk
import vedo
from vedo.applications import FreeHandCutPlotter
from vtk import vtkInteractorStyleTrackballCamera
from vedo import Plotter
from vedo import Mesh

class LassoInteractor(vtkInteractorStyleTrackballCamera):
    def __init__(self,poly_data,interactor,renderer):
        super().__init__()
        self.poly_data = poly_data
        self.interactor = interactor
        self.renderer = renderer

        self.plotter = Plotter(interactive=False, offscreen=True)
        self.plotter.renderers.append(renderer)
        self.plotter.renderer = renderer
        self.plotter.interactor = interactor
        print(f"[DEBUG] LassoInteractor: {id(poly_data)}")
        self.plotter.show(poly_data)
    def lasso_cut_vedo(self):
        vedo_mesh = Mesh(self.poly_data)
        self.plotter.show(vedo_mesh)
        self.cut_tool = FreeHandCutPlotter(vedo_mesh)
        self.cut_tool.add_hover_legend()
        self.cut_tool.start(axes=1, bg2='lightblue')
        self.cut_tool.close()