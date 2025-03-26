import vtk
from vtk import vtkInteractorStyleTrackballCamera
from models.interaction_styles.point_interactor import PointInteractor
from models.interaction_styles.lasso_interactor import LassoInteractor
from models.interaction_styles.box_interactor import BoxInteractor
from models.visible_select_func import VisibleSlt

class HighlightInteractorStyle(vtkInteractorStyleTrackballCamera):
    def __init__(self, poly_data_1,poly_data_2, renderer,interactor):
        super().__init__()
        # 互動器參數
        self.interactor = interactor
        # 初始化輸入資料
        self.poly_data_1 = poly_data_1
        self.poly_data_2 = poly_data_2
        # 渲染視窗
        self.renderer = renderer
        # 矩形鍵盤快捷鍵、按鈕選取開關
        self.boxSltMode = False 
        # 點鍵盤快捷鍵、按鈕選取開關
        self.pointSltMode = False
        # 套索鍵盤快捷鍵、按鈕選取開關
        self.lassoSltMode = False
         # 穿透按鈕開關
        self.throughBtnMode = False
        # 拼接按鈕開關
        self.stitchingBtnMode = False

        self.mapper = vtk.vtkPolyDataMapper()
        self.actor = vtk.vtkActor()
        # 鍵盤按下監聽器
        self.AddObserver("LeftButtonPressEvent", self.onLeftButtonDown)
        self.AddObserver("LeftButtonReleaseEvent", self.onLeftButtonUp)
        self.AddObserver("RightButtonPressEvent", self.onRightButtonDown)
        self.AddObserver("RightButtonReleaseEvent", self.onRightButtonUp)
        self.AddObserver("MouseWheelForwardEvent", self.onMouseWheelForward)
        self.AddObserver("MouseWheelBackwardEvent", self.onMouseWheelBackward)
        self.AddObserver("MiddleButtonDownEvent", self.onMiddleButtonDown)
        self.AddObserver("MiddleButtonUpEvent", self.onMiddleButtonUp)
        self.AddObserver("KeyPressEvent", self.modeSltKeyPress)

       
    

    def enable_box_mode(self):
        self.boxSltMode = True
        self.pointSltMode = False
        self.lassoSltMode = False
        self.box_func = BoxInteractor(self.poly_data_1,self.interactor,self.renderer)
    def unable_box_mode(self):
        self.boxSltMode = False
        self.box_func = None
    def enable_point_mode(self):
        self.pointSltMode = True
        self.boxSltMode = False
        self.lassoSltMode = False
        self.point_func = PointInteractor(self.poly_data_1,self.interactor,self.renderer)
    def unable_point_mode(self):
        self.pointSltMode = False
        self.point_func = None
    def enable_lasso_mode(self):
        self.lassoSltMode = True
        self.boxSltMode = False
        self.pointSltMode = False
        self.lasso_func = LassoInteractor(self.poly_data_1,self.interactor,self.renderer)
    def unable_lasso_mode(self):
        self.lassoSltMode = False
        self.lasso_func = None

    # 選取在視窗上可見的範圍功能狀態
    def enable_through_mode(self):
        self.throughBtnMode = True
        self.box_func = BoxInteractor(self.poly_data_1,self.interactor,self.renderer)
    def unable_through_mode(self):
        self.throughBtnMode = False
        print("Through button is off")
        self.box_func = None
    # 拼接功能狀態
    def enable_stitching_mode(self):
        self.through_func = VisibleSlt(self.renderer,self.interactor)
        self.through_func.process_stitching()

    # 鍵盤按下監聽器
    def modeSltKeyPress(self, obj, event):
        self.key = self.GetInteractor().GetKeySym()
        if self.key in ["c", "C"]:
            if self.boxSltMode:
                self.unable_box_mode()
            else:
                self.enable_box_mode()
        # 點選取模式
        elif self.key in ["p", "P"]:
            if self.pointSltMode:
                self.unable_point_mode()
            else:
                self.enable_point_mode()
        # 套索選取模式
        elif self.key in ["l", "L"]:
            if self.lassoSltMode:
                self.unable_lasso_mode()
            else:
                self.enable_lasso_mode()
        # 矩形刪除範圍，滿足按下delete鍵且矩形選取模式為True
        elif self.key == "Delete" and self.boxSltMode:
            # 移除選取範圍
            self.removeCells(self.poly_data_1,self.box_func.selection_frustum)
            # 清除所有矩形的視覺化資料
            self.box_func.unRenderAllSelectors()
        # 點刪除範圍，滿足按下delete鍵且點選取模式為True
        elif self.key == "Delete" and self.pointSltMode:
            # 移除選取範圍
            self.removeCells(self.poly_data_1,self.point_func.loop)
            # 清除所有點的視覺化資料、最短路徑資料等
            self.point_func.unRenderAllSelectors()
        # 套索刪除範圍，滿足按下delete鍵且套索選取模式為True
        elif self.key == "Delete" and self.lassoSltMode:
            # 移除選取範圍
            self.removeCells(self.poly_data_1,self.lasso_func.loop)
            # 清除所有套索的視覺化資料、最短路徑資料等
            self.lasso_func.unRenderAllSelectors()
        # 封閉點選取範圍，滿足按下enter鍵
        elif self.key == "Return":
            # enter後閉合點選範圍
            self.point_func.closeArea()
        # 點選取undo，滿足按下z鍵且點選取模式為True
        elif (self.key == "z" or self.key == "Z") and self.pointSltMode:
            # 點選取undo
            self.point_func.undo(self.renderer,self.GetInteractor())
        # 點選取redo，滿足按下y鍵且點選取模式為True
        elif (self.key == "y" or self.key == "Y") and self.pointSltMode:
            # 點選取redo
            self.point_func.redo(self.renderer,self.GetInteractor())
        # 套索選取undo，滿足按下z鍵且套索選取模式為True
        elif (self.key == "z" or self.key=="Z") and self.lassoSltMode:
            # 套索選取undo
            self.lasso_func.undo(self.renderer,self.GetInteractor())
        # 套索選取redo，滿足按下y鍵且套索選取模式為True
        elif (self.key == "y" or self.key == "Y") and self.lassoSltMode:
            # 套索選取redo
            self.lasso_func.redo(self.renderer,self.GetInteractor())
    # 移除選取範圍，第一個參數接收輸入模型，第二個參數接收
    def removeCells(self,poly_data,selection_frustum):
        # 檢查輸入的剪裁資料，型別有無符合vtk.vtkImplicitFunction；如果沒有會報錯，如缺少參數等
        if not isinstance(selection_frustum, vtk.vtkImplicitFunction):
            return
        # 初始化剪裁器
        clipper = vtk.vtkClipPolyData()
        # 要剪裁的目標放入輸入的3D模型
        clipper.SetInputData(poly_data)
        # 剪裁的函數是選取範圍 
        clipper.SetClipFunction(selection_frustum)
        # 剪裁的方向是選取範圍的內部
        clipper.GenerateClippedOutputOff()
        # 更新剪裁器
        clipper.Update()
        # 取得剪裁後的資料
        new_poly_data = clipper.GetOutput()
        # 如果剪裁後的資料沒有任何cell，代表沒有選取到任何東西，不做事
        if new_poly_data.GetNumberOfCells() == 0:
            return
        # 複製剪裁後的資料給輸入的3D模型
        self.poly_data_1.DeepCopy(new_poly_data)
        # 移除所有視覺化資料
        self.renderer.RemoveActor(self.actor)
        # 更新視覺化資料
        self.mapper.SetInputData(poly_data)
        # 更新渲染器、互動器
        self.GetInteractor().GetRenderWindow().Render()
    def onRightButtonDown(self, obj, event):
        super().OnRightButtonDown()
    def onRightButtonUp(self, obj, event):
        super().OnRightButtonUp()
    def onLeftButtonDown(self, obj, event):   
        if self.boxSltMode and not self.pointSltMode and not self.lassoSltMode and not self.throughBtnMode:
            print(f"box in all mode.")
            self.box_func.onLeftButtonPress(obj,event)
        elif self.boxSltMode and not self.pointSltMode and not self.lassoSltMode and self.throughBtnMode:
            print(f"box  in visible  mode.")
            print(f"{self.throughBtnMode}")
            self.box_func.onLeftButtonPress(obj,event)
            
        elif self.pointSltMode and not self.boxSltMode and not self.lassoSltMode:
            self.point_func.onLeftButtonDown(obj,event)
        elif self.lassoSltMode and not self.boxSltMode and not self.pointSltMode:
            self.lasso_func.onLeftButtonDown(obj,event)
        else:
            super().OnLeftButtonDown()
    def onLeftButtonUp(self, obj, event):
        if self.boxSltMode and not self.pointSltMode and not self.lassoSltMode and not self.throughBtnMode:
            self.box_func.onLeftButtonUp(obj,event)
            select_area = self.box_func.boxSelectArea()
            self.box_func.show_all_area(select_area)
        elif self.boxSltMode and not self.pointSltMode and not self.lassoSltMode and self.throughBtnMode:
            print(f"This is in-visible view")
            self.box_func.onLeftButtonUp(obj,event)
            self.box_func.show_on_visible()
        else:
            super().OnLeftButtonUp()

    def onMouseWheelForward(self, obj, event):
        super().OnMouseWheelForward()
    def onMouseWheelBackward(self, obj, event):
        super().OnMouseWheelBackward()
    def onMiddleButtonDown(self, obj, event):
        super().OnMiddleButtonDown()
    def onMiddleButtonUp(self, obj, event):
        super().OnMiddleButtonUp()
        


    