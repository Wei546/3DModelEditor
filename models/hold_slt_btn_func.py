import vtk
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleRubberBand3D
class HoldSltbtnFunc(vtkInteractorStyleRubberBand3D):
    def __init__(self,renderer,interactor):
        self.renderer = renderer
        self.interactor = interactor
        self.AddObserver("LeftButtonPressEvent", self.OnLeftButtonPress)
        return
    def OnLeftButtonPress(self):
        print("left button press")