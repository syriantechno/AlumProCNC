# model/occ_model.py
import os, tempfile
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.StlAPI import StlAPI_Writer
from core.dxf_loader import load_dxf_shape
import vtk
import tempfile
import os
from OCC.Core.StlAPI import StlAPI_Writer
from OCC.Core.BRep import BRep_Tool
from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
from OCC.Core.GeomAbs import GeomAbs_Line, GeomAbs_Circle

class OCCModel:
    def __init__(self):
        self.current_shape = None

    def make_box(self, x=50, y=50, z=30):
        self.current_shape = BRepPrimAPI_MakeBox(x, y, z).Shape()
        return self.current_shape

    def import_dxf(self, file_path):
        shape = load_dxf_shape(file_path)
        if shape:
            self.current_shape = shape
        return shape

    def shape_to_temp_stl(self, shape):
        """تحويل أي شكل إلى STL أو PolyData مؤقت للعرض"""
        if shape is None or shape.IsNull():
            print("❌ الشكل فارغ")
            return None

        # جرب حفظه STL أولاً (للأشكال الصلبة)
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".stl")
        tmp_path = tmp_file.name
        tmp_file.close()

        try:
            writer = StlAPI_Writer()
            if writer.Write(shape, tmp_path):
                if os.path.getsize(tmp_path) > 0:
                    print(f"[OCC] STL محفوظ ({os.path.getsize(tmp_path)} bytes): {tmp_path}")
                    return tmp_path
        except Exception:
            pass

        # لو STL فشل نحاول توليد Mesh من الحواف
        print("⚠️ STL فشل، توليد Mesh من خطوط DXF")

        points = vtk.vtkPoints()
        lines = vtk.vtkCellArray()

        te = TopologyExplorer(shape)
        point_id = 0

        for edge in te.edges():
            curve = BRepAdaptor_Curve(edge)
            first, last = curve.FirstParameter(), curve.LastParameter()
            num_pts = 30  # دقة الرسم

            for i in range(num_pts + 1):
                p = curve.Value(first + (last - first) * i / num_pts)
                points.InsertNextPoint(p.X(), p.Y(), p.Z())
                if i > 0:
                    line = vtk.vtkLine()
                    line.GetPointIds().SetId(0, point_id - 1)
                    line.GetPointIds().SetId(1, point_id)
                    lines.InsertNextCell(line)
                point_id += 1

        poly_data = vtk.vtkPolyData()
        poly_data.SetPoints(points)
        poly_data.SetLines(lines)

        # ✅ بدل الحفظ، نعيد الـ PolyData مباشرة
        print(f"[OCC] Mesh جاهز للعرض: {points.GetNumberOfPoints()} نقاط")
        return poly_data

