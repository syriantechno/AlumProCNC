# controller/main_controller.py

import os
import vtk
from model.occ_model import OCCModel
from PyQt5.QtWidgets import QFileDialog

class MainController:
    def __init__(self, viewer):
        self.model = OCCModel()
        self.viewer = viewer

    def import_dxf(self):
        """فتح ملف DXF وتحميله للعارض مع توليد إكسترود ثلاثي الأبعاد."""
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Open DXF File", "", "DXF Files (*.dxf)"
        )
        if not file_path:
            return

        print(f"📂 [DXF] جاري تحميل الملف: {file_path}")
        shape = self.model.import_dxf(file_path)
        if not shape:
            print("❌ فشل تحميل DXF")
            return

        # 🔹 تحويل الشكل إلى polydata أو STL مؤقت
        polydata_or_path = self.model.shape_to_temp_stl(shape)

        # ⚙️ في حال أرجعت الدالة مسار ملف STL (نصّي) وليس vtkPolyData
        if isinstance(polydata_or_path, str):
            print("🧩 [DXF] الشكل حُفظ كـ STL مؤقت، سيتم تحميله للعرض فقط.")
            self.viewer.display_stl(polydata_or_path, color=(0.5, 0.8, 1.0))
            return

        polydata = polydata_or_path
        print(
            f"🔹 [DXF] نقاط={polydata.GetNumberOfPoints()}, خطوط={polydata.GetNumberOfLines()}, أسطح={polydata.GetNumberOfPolys()}")

        # 🔹 توليد إكسترود من الشكل 2D بشكل آمن
        from tools.extrude_tool import ExtrudeTool
        solid = ExtrudeTool.create_extrude(polydata, depth=60.0, axis="Y")

        if solid and solid.GetNumberOfPoints() > 0:
            self.viewer.display_stl(solid, color=(0.35, 0.65, 0.95))
            print("🧱 [DXF→Extrude] تم إنشاء مجسم الإكسترود بنجاح ✅")
        else:
            print("⚠️ [DXF→Extrude] فشل إنشاء المجسم من DXF (الشكل فارغ أو غير صالح).")

        print(f"✅ DXF imported and processed: {file_path}")

    def create_box(self):
        shape = self.model.make_box(50, 50, 30)
        stl_path = self.model.shape_to_temp_stl(shape)
        if stl_path:
            try:
                self.viewer.display_stl(stl_path, color=(0.53, 0.81, 0.92))
            finally:
                # احذف الملف المؤقت بعد العرض
                try: os.remove(stl_path)
                except: pass
                print("✅ Box created, moving +20 on X")
                self.move_selected(20, 0, 0)

    def move_selected(self, dx=0, dy=0, dz=0):
        """تحريك العنصر المحدد (آمن بدون كراش)"""
        if not hasattr(self.viewer, "_last_actor") or self.viewer._last_actor is None:
            print("⚠️ لا يوجد كائن محدد للتحريك")
            return

        actor = self.viewer._last_actor

        try:
            # قراءة الـ matrix الحالي
            old_matrix = vtk.vtkMatrix4x4()
            actor.GetMatrix(old_matrix)

            # إنشاء matrix جديد بإزاحة
            new_matrix = vtk.vtkMatrix4x4()
            new_matrix.DeepCopy(old_matrix)
            new_matrix.SetElement(0, 3, old_matrix.GetElement(0, 3) + dx)
            new_matrix.SetElement(1, 3, old_matrix.GetElement(1, 3) + dy)
            new_matrix.SetElement(2, 3, old_matrix.GetElement(2, 3) + dz)

            # تطبيق الـ matrix الجديد بشكل آمن
            actor.PokeMatrix(new_matrix)

            # إعادة رسم المشهد
            self.viewer.render_window.Render()
            print(f"[MOVE] تم تحريك العنصر ({dx}, {dy}, {dz}) بدون كراش ✅")

        except Exception as e:
            print("🔥 خطأ أثناء التحريك:", e)

