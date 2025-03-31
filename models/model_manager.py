import vtk

# 主要用來回傳polyData型別
class ModelSlot:
    def __init__(self, name, poly_data):
        self.name = name
        self.poly_data = poly_data
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


# 負責管理模型的類別，這個類別會把所有的模型都放在這裡面，並且可以選取目前正在編輯的模型
class ModelManager:
    def __init__(self):
        self.models = {}
        self.active_model_name = None

    # 這個函式會把傳進來的poly_data複製一份，然後放到models裡面，並且給它一個名字
    def add_model(self, name, poly_data, renderer=None):
        poly_data_copy = vtk.vtkPolyData()
        poly_data_copy.DeepCopy(poly_data)
        unique_name = self._make_unique_name(name)
        model_slot = ModelSlot(unique_name, poly_data_copy)
        self.models[unique_name] = model_slot
        print(f"[DEBUG] add_model: {name}, poly_data_copy id: {id(poly_data_copy)}")

        if renderer:
            renderer.AddActor(model_slot.actor)

        return unique_name

    def _make_unique_name(self, base_name):
        if base_name not in self.models:
            return base_name
        i = 1
        while f"{base_name}_{i}" in self.models:
            i += 1
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
