import vtk

# 主要用來儲存模型的類別，這個類別會把模型的資料放在這裡面，並且可以更新模型的資料
class ModelSlot:
    def __init__(self, name, poly_data, file_path = None):
        # 這裡的name是模型的名稱
        self.name = name
        # 這裡的poly_data是模型的資料
        self.poly_data = poly_data
        # 這裡的file_path是模型的路徑
        self.file_path = file_path
        # 為了方便統一管理在renderer裡面顯示
        self.actor = self._create_actor(poly_data)
        self.visible = True
        self.metadata = {}

    def _create_actor(self, poly_data):
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        return actor

    def update_poly_data(self, new_poly_data):
        self.poly_data = new_poly_data
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(new_poly_data)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        self.actor = actor
    def cover_old_poly_data(self, new_poly_data):
        # 將新的poly_data覆蓋到舊的poly_data上，這樣就不會影響到原本的poly_data了
        self.poly_data.DeepCopy(new_poly_data)
        # 更新actor的資料
        self.actor.GetMapper().SetInputData(self.poly_data)




# 負責管理模型的類別，這個類別會把所有的模型都放在這裡面，並且可以選取目前正在編輯的模型
class ModelManager:
    def __init__(self):
        self.models = {}
        self.active_model_name = None

    # 這個函式會把傳進來的poly_data複製一份，然後放到models裡面，並且給它一個名字
    def add_model(self, name, poly_data,file_path = None, renderer=None):
        # 避免後續trim影響到個別模型
        poly_data_copy = vtk.vtkPolyData()
        # 這裡的DeepCopy會把poly_data的資料複製到poly_data_copy裡面
        poly_data_copy.DeepCopy(poly_data)
        # 避免匯入同名的模型
        unique_name = self._make_unique_name(name)
        # 確保字典的鍵名是唯一的，也就是說不會有重複的模型名稱
        model_slot = ModelSlot(unique_name, poly_data_copy,file_path)
        self.models[unique_name] = model_slot
        print(f"[DEBUG] add_model: {name}, poly_data_copy id: {id(poly_data_copy)}")
        # 確保模型不會馬上被renderer
        if renderer:
            renderer.AddActor(model_slot.actor)

        return unique_name
    # 如果QListWidget的檔名一樣的話，會自動加上_1、_2、_3...等字串；設定private，是因為不要在其他類別誤用
    def _make_unique_name(self, base_name):
        # 如果沒有同名的模型，就直接回傳
        if base_name not in self.models:
            return base_name
        # 如果有同名的模型，就加上_1、_2、_3...等字串
        # 例如：這裡的base_name重複會是model_1.stl
        i = 1
        while f"{base_name}_{i}" in self.models:
            i += 1
        # 回傳加上_1、_2、_3...等字串的檔名
        return f"{base_name}_{i}"

    def get_model(self, name):
        return self.models.get(name)

    def set_active_model(self, name):
        if name in self.models:
            self.active_model_name = name

    def get_active_model(self):
        if self.active_model_name:
            return self.models[self.active_model_name]
        return None

    def get_all_models(self):
        return self.models
    def get_all_model_names(self):
        return list(self.models.keys())
