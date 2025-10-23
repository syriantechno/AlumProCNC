import vtk


class ExtrudeTool:
    """أداة إنشاء إكسترود 3D من شكل 2D (PolyData) مع دعم الثقوب الداخلية."""

    @staticmethod
    def create_extrude(input_polydata, depth=50.0, axis="Y"):
        if input_polydata is None or input_polydata.GetNumberOfPoints() == 0:
            print("⚠️ [ExtrudeTool] لا يوجد شكل 2D صالح للإكسترود.")
            return None

        axis_map = {"X": (1, 0, 0), "Y": (0, 1, 0), "Z": (0, 0, 1)}
        direction = axis_map.get(axis.upper(), (0, 1, 0))

        try:
            # -------------------------------------------------------------
            # 1️⃣ تنظيف الشكل من النقاط المكررة
            # -------------------------------------------------------------
            cleaner = vtk.vtkCleanPolyData()
            cleaner.SetInputData(input_polydata)
            cleaner.Update()
            clean_data = cleaner.GetOutput()

            # -------------------------------------------------------------
            # 2️⃣ ربط الخطوط لتكوين wire مغلق
            # -------------------------------------------------------------
            stripper = vtk.vtkStripper()
            stripper.SetInputData(clean_data)
            stripper.Update()
            wire_data = stripper.GetOutput()

            # -------------------------------------------------------------
            # 3️⃣ تحويل الخطوط إلى سطح مغلق (Polygon)
            # -------------------------------------------------------------
            boundary = vtk.vtkContourTriangulator()
            boundary.SetInputData(wire_data)
            boundary.Update()
            surface_data = boundary.GetOutput()

            if surface_data.GetNumberOfPolys() == 0:
                print("⚠️ [ExtrudeTool] لم يتمكن من إنشاء سطح مغلق من الخطوط.")
                return None

            # -------------------------------------------------------------
            # 🧠 اكتشاف كل الحلقات (الخارجية + الداخلية)
            # -------------------------------------------------------------
            connect = vtk.vtkPolyDataConnectivityFilter()
            connect.SetInputData(surface_data)
            connect.SetExtractionModeToAllRegions()
            connect.ColorRegionsOn()
            connect.Update()

            num_regions = connect.GetNumberOfExtractedRegions()
            print(f"🔹 [ExtrudeTool] عدد الحلقات المكتشفة: {num_regions}")

            surf_with_regions = connect.GetOutput()
            append = vtk.vtkAppendPolyData()

            for region_id in range(num_regions):
                thresh = vtk.vtkThreshold()
                thresh.SetInputData(surf_with_regions)
                # ✅ الطريقة الحديثة بدل ThresholdBetween
                thresh.SetLowerThreshold(region_id)
                thresh.SetUpperThreshold(region_id)
                thresh.Update()

                geom = vtk.vtkGeometryFilter()
                geom.SetInputConnection(thresh.GetOutputPort())
                geom.Update()
                region_poly = geom.GetOutput()

                if region_poly.GetNumberOfPoints() > 0:
                    append.AddInputData(region_poly)

            append.Update()
            full_surface = append.GetOutput()

            # -------------------------------------------------------------
            # 4️⃣ تنفيذ الإكسترود على كل السطح (بما فيه الثقوب)
            # -------------------------------------------------------------
            extrude = vtk.vtkLinearExtrusionFilter()
            extrude.SetInputData(full_surface)
            extrude.SetExtrusionTypeToVectorExtrusion()
            extrude.SetVector(*direction)
            extrude.SetScaleFactor(depth)
            extrude.SetCapping(1)
            extrude.Update()
            solid = extrude.GetOutput()

            # -------------------------------------------------------------
            # 5️⃣ تنظيف الناتج النهائي
            # -------------------------------------------------------------
            final_cleaner = vtk.vtkCleanPolyData()
            final_cleaner.SetInputData(solid)
            final_cleaner.Update()
            out = final_cleaner.GetOutput()

            print(
                f"✅ [ExtrudeTool] إكسترود ناجح مع الثقوب الداخلية (نقاط={out.GetNumberOfPoints()})"
            )
            return out

        except Exception as e:
            print("🔥 [ExtrudeTool] خطأ أثناء إنشاء الإكسترود:", e)
            return None
