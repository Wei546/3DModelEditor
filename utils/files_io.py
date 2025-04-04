import vtk
def get_writer_by_extension(file_path):
        """Return the appropriate writer based on file extension."""
        extension = file_path.split('.')[-1].lower()
        writers = {
            'vtp': vtk.vtkXMLPolyDataWriter,
            'obj': vtk.vtkOBJWriter,
            'ply': vtk.vtkPLYWriter,
            'stl': vtk.vtkSTLWriter
        }
        if extension not in writers:
            raise ValueError("不支援的檔案格式.")
        return writers[extension]()
# 讀取不同格式的模型
def read_model(file_path):
    # 取得副檔名
    extension = file_path.split('.')[-1].lower()
    readers = {
        'vtp': vtk.vtkXMLPolyDataReader,
        'obj': vtk.vtkOBJReader,
        'ply': vtk.vtkPLYReader,
        'stl': vtk.vtkSTLReader
    }
    if extension not in readers:
        raise ValueError("不支援的檔案格式.")
    reader = readers[extension]()
    reader.SetFileName(file_path)
    reader.Update()
    # 這裡的GetOutput()會回傳vtkPolyData物件
    return reader.GetOutput()