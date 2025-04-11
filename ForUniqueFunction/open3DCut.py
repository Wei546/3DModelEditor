import vtk

# Step 1: 讀入 STL 模型
reader = vtk.vtkSTLReader()
reader.SetFileName("resources/0075/ai_data0075down_smooth.stl")  # 替換成你的 STL 路徑
reader.Update()

# Step 2: 將模型加入 mapper 和 actor
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(reader.GetOutputPort())

actor = vtk.vtkActor()
actor.SetMapper(mapper)

# Step 3: 設定 renderer 與 render window
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)

renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)

# Step 4: 設定 interactor 與 Polygon 選取互動模式
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(renderWindow)

style = vtk.vtkInteractorStyleDrawPolygon()
interactor.SetInteractorStyle(style)

# Step 5: 設定 AreaPicker（Polygon 的選取邏輯）
picker = vtk.vtkAreaPicker()
interactor.SetPicker(picker)

def onSelectionComplete(caller, event):
    frustum = picker.GetFrustum()  # 取得多邊形框選區域對應的視錐體
    extract = vtk.vtkExtractGeometry()
    extract.SetInputData(reader.GetOutput())
    extract.SetImplicitFunction(frustum)
    extract.Update()

    selected = extract.GetOutput()

    selected_mapper = vtk.vtkPolyDataMapper()
    selected_mapper.SetInputData(selected)

    selected_actor = vtk.vtkActor()
    selected_actor.SetMapper(selected_mapper)
    selected_actor.GetProperty().SetColor(1, 0, 0)  # 紅色顯示被選取的區域

    renderer.AddActor(selected_actor)
    renderWindow.Render()

# 綁定互動結束時的 callback
picker.AddObserver("EndPickEvent", onSelectionComplete)

# 啟動視窗
renderWindow.Render()
interactor.Start()
