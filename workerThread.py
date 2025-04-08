from PyQt5.QtCore import QThread, pyqtSignal

class StitchingWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, defect_path, repair_path, thickness=0):
        super().__init__()
        self.defect_path = defect_path
        self.repair_path = repair_path
        self.thickness = thickness
        self.result = None

    def run(self):
        from models.stitch_slt_btn_model import MeshProcessor
        processor = MeshProcessor(self.defect_path, self.repair_path)
        self.result = processor.process_complete_workflow(thickness=self.thickness)
        print(f"In worker thread: {self.result}")
        self.finished.emit(self.result)
        
