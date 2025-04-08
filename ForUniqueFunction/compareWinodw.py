import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
import vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class DualSTLViewer(QWidget):
    def __init__(self, stl_path1, stl_path2):
        super(DualSTLViewer, self).__init__()

        # Qt layout setup
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        layout = QVBoxLayout()
        layout.addWidget(self.vtk_widget)
        self.setLayout(layout)

        # 建立 renderer
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.1, 0.1, 0.1)

        # 載入第一個 STL 模型（紅色）
        actor1 = self.load_stl_model(stl_path1, color=(1, 1, 1), position=(8, 0, 0))
        self.renderer.AddActor(actor1)

        # 載入第二個 STL 模型（綠色，位移到右邊一點）
        actor2 = self.load_stl_model(stl_path2, color=(1, 1, 1), position=(5, 0, 0))
        self.renderer.AddActor(actor2)

        # 綁定 renderer 到視窗
        render_window = self.vtk_widget.GetRenderWindow()
        render_window.AddRenderer(self.renderer)

        # 初始化互動
        self.interactor = render_window.GetInteractor()
        self.interactor.Initialize()
        self.renderer.ResetCamera()
        self.interactor.Start()

    def load_stl_model(self, file_path, color=(1, 1, 1), position=(0, 0, 0)):
        reader = vtk.vtkSTLReader()
        reader.SetFileName(file_path)
        reader.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        actor.SetPosition(*position)
        return actor

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # STL 模型路徑（請改成你自己的檔案）
    path1 = "resources/my_pipeline_inlay/smooth_subdivision_ai_data0078down_smooth.stl"
    path2 = "resources/test_stitch/inlay_complete_merge_0078.stl"

    window = DualSTLViewer(path1, path2)
    window.setWindowTitle("Dual STL Viewer - Qt + VTK")
    window.resize(1000, 800)
    window.show()

    sys.exit(app.exec_())
