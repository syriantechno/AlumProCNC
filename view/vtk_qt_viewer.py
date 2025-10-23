from PyQt5.QtWidgets import QFrame, QVBoxLayout, QToolBar, QAction
import vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class VTKQtViewer(QFrame):
    """عارض VTK احترافي داخل Qt — مع شبكة ومحاور وأزرار كاميرا."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        # 🔹 شريط أدوات الكاميرا
        self.toolbar = QToolBar("Camera Tools", self)
        self.toolbar.setIconSize(parent.iconSize() if parent else None)
        self.layout().addWidget(self.toolbar)

        # 🔹 واجهة VTK داخل Qt
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        self.layout().addWidget(self.vtk_widget)

        # 🔹 الإعدادات الأساسية
        self.renderer = vtk.vtkRenderer()
        self.render_window = self.vtk_widget.GetRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        self.interactor = self.render_window.GetInteractor()
        self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.interactor.Initialize()

        # 🔹 إعداد المشهد
        self.renderer.SetBackground(0.12, 0.12, 0.13)
        self._add_orientation_widget()
        self._add_axes()
        self._add_grid()
        self._add_measurement_grid()  # شبكة القياسات بالأرقام ✅

        # 🔹 متغيرات داخلية
        self._last_actor = None

        # 🔹 أزرار التحكم بالكاميرا
        self._add_camera_actions()
        self.enable_picking()

        # 🎥 ضبط الكاميرا تلقائيًا عند التشغيل
        self.reset_camera_smooth()

        print("[Viewer] VTK-Qt viewer (Pro) initialized ✅")

    # -------------------------------------------------------------
    # ✅ الأدوات البصرية الأساسية
    # -------------------------------------------------------------
    def _add_orientation_widget(self):
        axes = vtk.vtkAxesActor()
        widget = vtk.vtkOrientationMarkerWidget()
        widget.SetOrientationMarker(axes)
        widget.SetViewport(0.0, 0.0, 0.18, 0.18)
        widget.SetInteractor(self.interactor)
        widget.EnabledOn()
        widget.InteractiveOn()
        self._axes_widget = widget

    def _add_axes(self):
        """محاور رفيعة وأنيقة (أسلوب Fusion-style)."""
        axes = vtk.vtkAxesActor()

        # 🔹 تقليل الطول العام للمحاور
        axes.SetTotalLength(40, 40, 40)

        # 🔹 نوع العمود (cylinder) بسماكة خفيفة جدًا
        axes.SetShaftTypeToCylinder()
        axes.SetCylinderRadius(0.005)  # السماكة الأصلية كانت 0.02

        # 🔹 ضبط حجم الأسهم (رؤوس المحاور)
        axes.SetConeRadius(0.04)
        axes.SetConeResolution(20)
        axes.SetNormalizedShaftLength(0.9, 0.9, 0.9)
        axes.SetNormalizedTipLength(0.1, 0.1, 0.1)

        # 🔹 ألوان المحاور (أحمر/أخضر/أزرق خافتة)
        axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetColor(0.95, 0.4, 0.4)
        axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetColor(0.4, 0.95, 0.4)
        axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetColor(0.4, 0.6, 1.0)

        # 🔹 إخفاء النصوص الكبيرة (اختياري)
        for axis in [
            axes.GetXAxisCaptionActor2D(),
            axes.GetYAxisCaptionActor2D(),
            axes.GetZAxisCaptionActor2D(),
        ]:
            prop = axis.GetCaptionTextProperty()
            prop.SetFontSize(12)
            prop.BoldOff()
            prop.ItalicOff()
            prop.ShadowOff()

        self.renderer.AddActor(axes)
        self.axes_actor = axes
        print("🧭 [Axes] Slim Fusion-style axes added ✅")

    def _add_grid(self, size=200, spacing=10):
        """شبكة XY رمادية شفافة."""
        grid = vtk.vtkAppendPolyData()
        for i in range(-size, size + 1, spacing):
            # خطوط X
            pts_x = vtk.vtkPoints()
            lines_x = vtk.vtkCellArray()
            pts_x.InsertNextPoint(-size, i, 0)
            pts_x.InsertNextPoint(size, i, 0)
            line_x = vtk.vtkLine()
            line_x.GetPointIds().SetId(0, 0)
            line_x.GetPointIds().SetId(1, 1)
            lines_x.InsertNextCell(line_x)
            pd_x = vtk.vtkPolyData()
            pd_x.SetPoints(pts_x)
            pd_x.SetLines(lines_x)
            grid.AddInputData(pd_x)

            # خطوط Y
            pts_y = vtk.vtkPoints()
            lines_y = vtk.vtkCellArray()
            pts_y.InsertNextPoint(i, -size, 0)
            pts_y.InsertNextPoint(i, size, 0)
            line_y = vtk.vtkLine()
            line_y.GetPointIds().SetId(0, 0)
            line_y.GetPointIds().SetId(1, 1)
            lines_y.InsertNextCell(line_y)
            pd_y = vtk.vtkPolyData()
            pd_y.SetPoints(pts_y)
            pd_y.SetLines(lines_y)
            grid.AddInputData(pd_y)

        grid.Update()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(grid.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.5, 0.5, 0.5)
        actor.GetProperty().SetOpacity(0.25)
        self.renderer.AddActor(actor)
        self.grid_actor = actor

    def _add_measurement_grid(self):
        """إضافة شبكة القياسات بالأرقام (مثل الصورة)."""
        cube_axes = vtk.vtkCubeAxesActor()
        cube_axes.SetCamera(self.renderer.GetActiveCamera())
        cube_axes.SetBounds(-200, 200, -200, 200, 0, 0)

        cube_axes.SetFlyModeToStaticEdges()
        cube_axes.SetGridLineLocation(vtk.vtkCubeAxesActor.VTK_GRID_LINES_FURTHEST)
        cube_axes.DrawXGridlinesOn()
        cube_axes.DrawYGridlinesOn()
        cube_axes.DrawZGridlinesOff()

        # الألوان والخطوط
        for i in range(3):
            cube_axes.GetTitleTextProperty(i).SetColor(0.8, 0.8, 0.8)
            cube_axes.GetLabelTextProperty(i).SetColor(0.8, 0.8, 0.8)

        cube_axes.GetXAxesLinesProperty().SetColor(0.4, 0.4, 0.4)
        cube_axes.GetYAxesLinesProperty().SetColor(0.4, 0.4, 0.4)
        cube_axes.GetXAxesGridlinesProperty().SetColor(0.25, 0.25, 0.25)
        cube_axes.GetYAxesGridlinesProperty().SetColor(0.25, 0.25, 0.25)
        cube_axes.SetLabelOffset(10)
        cube_axes.SetTitleOffset(20)

        self.renderer.AddActor(cube_axes)
        self.cube_axes = cube_axes
        print("📏 [Grid] Measurement grid added ✅")

    # -------------------------------------------------------------
    # ✅ أدوات الكاميرا
    # -------------------------------------------------------------
    def _add_camera_actions(self):
        def add_action(text, func):
            act = QAction(text, self)
            act.triggered.connect(func)
            self.toolbar.addAction(act)

        add_action("Isometric", self.view_isometric)
        add_action("Top", self.view_top)
        add_action("Front", self.view_front)
        add_action("Right", self.view_right)
        add_action("Reset", self.reset_view)

    def view_isometric(self):
        self.renderer.GetActiveCamera().Azimuth(45)
        self.renderer.GetActiveCamera().Elevation(30)
        self.renderer.ResetCamera()
        self.render_window.Render()

    def view_top(self):
        cam = self.renderer.GetActiveCamera()
        cam.SetPosition(0, 0, 1)
        cam.SetFocalPoint(0, 0, 0)
        cam.SetViewUp(0, 1, 0)
        self.renderer.ResetCamera()
        self.render_window.Render()

    def view_front(self):
        cam = self.renderer.GetActiveCamera()
        cam.SetPosition(0, -1, 0)
        cam.SetFocalPoint(0, 0, 0)
        cam.SetViewUp(0, 0, 1)
        self.renderer.ResetCamera()
        self.render_window.Render()

    def view_right(self):
        cam = self.renderer.GetActiveCamera()
        cam.SetPosition(1, 0, 0)
        cam.SetFocalPoint(0, 0, 0)
        cam.SetViewUp(0, 0, 1)
        self.renderer.ResetCamera()
        self.render_window.Render()

    def reset_view(self):
        """FitAll-style — إعادة ضبط الكاميرا لتظهر كامل المشهد بدون تغيير الاتجاه"""
        self.renderer.ResetCamera()
        self.renderer.ResetCameraClippingRange()
        self.render_window.Render()

    # -------------------------------------------------------------
    # ✅ الكاميرا الذكية
    # -------------------------------------------------------------
    def reset_camera_smooth(self):
        try:
            cam = self.renderer.GetActiveCamera()
            cam.SetPosition(300, -300, 200)
            cam.SetFocalPoint(0, 0, 0)
            cam.SetViewUp(0, 0, 1)
            self.renderer.ResetCameraClippingRange()
            self.renderer.ResetCamera()
            self.render_window.Render()
            print("🎥 [Camera] Auto-reset to Fusion-style view ✅")
        except Exception as e:
            print("⚠️ [Camera] reset failed:", e)

    # -------------------------------------------------------------
    # ✅ نظام التحديد Selection
    # -------------------------------------------------------------
    def enable_picking(self):
        self.picker = vtk.vtkPropPicker()
        self.interactor.AddObserver("LeftButtonPressEvent", self._on_left_click)
        print("[Picker] Enabled ✅")

    def _on_left_click(self, obj, event):
        click_pos = self.interactor.GetEventPosition()
        self.picker.Pick(click_pos[0], click_pos[1], 0, self.renderer)
        actor = self.picker.GetActor()
        if actor:
            print(f"[SELECT] Actor selected: {actor}")
            self._highlight_actor(actor)
            if hasattr(self, "on_object_selected"):
                self.on_object_selected(actor)
        else:
            print("[SELECT] لا يوجد كائن تحت المؤشر")

    def _highlight_actor(self, actor):
        if self._last_actor:
            self._last_actor.GetProperty().SetEdgeVisibility(False)
        self._last_actor = actor
        actor.GetProperty().SetEdgeColor(1, 1, 0)
        actor.GetProperty().EdgeVisibilityOn()
        self.render_window.Render()

    # -------------------------------------------------------------
    # ✅ عرض STL أو Mesh
    # -------------------------------------------------------------
    def display_stl(self, data, color=(0.4, 0.7, 1.0)):
        import os

        if isinstance(data, str):
            if not os.path.exists(data):
                print(f"❌ الملف غير موجود: {data}")
                return
            reader = vtk.vtkSTLReader()
            reader.SetFileName(data)
            reader.Update()
            polydata = reader.GetOutput()
        else:
            polydata = data

        if not polydata or polydata.GetNumberOfPoints() == 0:
            print("⚠️ STL فارغ أو فشل التوليد.")
            return

        print(f"[OCC] Mesh جاهز للعرض: {polydata.GetNumberOfPoints()} نقاط")

        # 🔹 تعديل موضع الشكل بحيث الركن الأدنى هو (0,0,0)
        bounds = [0]*6
        polydata.GetBounds(bounds)
        dx, dy, dz = -bounds[0], -bounds[2], -bounds[4]

        transform = vtk.vtkTransform()
        transform.Translate(dx, dy, dz)

        transform_filter = vtk.vtkTransformPolyDataFilter()
        transform_filter.SetInputData(polydata)
        transform_filter.SetTransform(transform)
        transform_filter.Update()
        polydata = transform_filter.GetOutput()

        # ✅ إنشاء Mapper و Actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*color)
        actor.GetProperty().SetInterpolationToPhong()

        # 🧹 إزالة الشكل السابق فقط
        if self._last_actor:
            self.renderer.RemoveActor(self._last_actor)
        self._last_actor = actor
        self.renderer.AddActor(actor)

        # 🔹 تحديث شبكة القياسات حسب حدود الشكل الجديد
        if hasattr(self, "cube_axes"):
            self.cube_axes.SetBounds(actor.GetBounds())

        # 🔹 FitAll والكاميرا
        self.renderer.ResetCamera()
        self.renderer.ResetCameraClippingRange()
        self.render_window.Render()
        print("✅ [Viewer] STL تم عرضه بنجاح بدون كراش ومع شبكة القياسات.")
