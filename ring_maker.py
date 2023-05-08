import rhinoscriptsyntax as rs
import json

js = open("./params.json", "r")
set = json.load(js)
js.close()

ring_size = set["ring size"]
top_size = set["top diameter"]
top_thickness = set["top thickness"]
band_width = set["band width"]
mid_thickness = set["band thickness"]

ring_radius = ring_size / 2
head_radius = top_size / 2
half_band_width = band_width / 2

top_point = ring_radius + top_thickness
side_point = ring_radius + mid_thickness
bottom_point = -abs(ring_radius + mid_thickness)

ZX = rs.WorldZXPlane()  # ring center
XY = rs.WorldXYPlane()

base_circle = rs.AddCircle(ZX, ring_radius)
top_circle = rs.AddCircle(XY, head_radius)
bottom_circle = rs.AddCircle(XY, 0.1)
central_line = rs.AddLine([0,0,0], [0,10,0])
cutting_line_1 = rs.AddLine([0,0,0], [0,0,-15])
cutting_line_1 = rs.RotateObject(cutting_line_1, "0,0,0", -45.0, "0,1,0", True)
cutting_line_2 = rs.AddLine([0,0,0], [0,0,-15])
cutting_line_2 = rs.RotateObject(cutting_line_2, "0,0,0", 45.0, "0,1,0", True)
top_line_1 = rs.AddLine([0,0,0], [0,head_radius,0])
top_line_2 = rs.AddLine([0,0,0], [head_radius,0,0])
top_short_line_1 = rs.AddLine([0,head_radius,0], [0,head_radius,2])
top_short_line_2 = rs.AddLine([head_radius,0,0], [head_radius,0,2])
move = "0, 0," + str(top_point)
rs.MoveObjects([top_circle,
                top_line_1,
                top_line_2, 
                top_short_line_1,
                top_short_line_2
                ], move)

rs.MoveObject(bottom_circle, [0,0,bottom_point])

mid_line_1 = rs.AddLine([side_point,half_band_width,0], [side_point,0,0])
mid_line_2 = rs.AddLine([0,half_band_width,0], [side_point,half_band_width,0])
mid_short_line_1 = rs.AddLine([0,half_band_width,0], [0,half_band_width,-2])

mid_fillet_curve = rs.AddFilletCurve(mid_line_1, mid_line_2, radius=half_band_width * 0.70)
rs.DeleteObjects([mid_line_1,mid_line_2])
start_point = rs.CurveStartPoint(mid_fillet_curve)
end_point = rs.CurveEndPoint(mid_fillet_curve)
mid_line_3 = rs.AddLine(start_point, [side_point,0,0])
mid_line_4 = rs.AddLine([0,half_band_width,0], end_point)

bottom_curve_1 = rs.RotateObject(mid_fillet_curve, "0,0,0", 90.0, "0,1,0", True)
bottom_curve_2 = rs.RotateObject(mid_line_3, "0,0,0", 90.0, "0,1,0", True)
# bottom_curve = rs.JoinCurves([bottom_curve], True)
domain_crv0 = rs.CurveDomain(mid_short_line_1)
domain_crv1 = rs.CurveDomain(bottom_curve_1)
params = domain_crv0[1], domain_crv1[1]
revs = False, False
cont = 0,0
bl = rs.AddBlendCurve([mid_short_line_1, bottom_curve_1], params, revs, cont)

shape_1 = rs.JoinCurves([
    mid_line_4,
    mid_fillet_curve,
    mid_line_3
], True)

shape_2 = rs.MirrorObject(shape_1, [0,0,0], [10,0,0], True)

mid_half_shape_1 = rs.JoinCurves([
    shape_1,
    shape_2,
], True)

mid_half_shape_2 = rs.MirrorObject(mid_half_shape_1, [0,0,0], [0,10,0], True)

mid_base_shape = rs.JoinCurves([
    mid_half_shape_1,
    mid_half_shape_2,
], True)

bottom_arc = rs.AddArc(ZX, side_point, 90)
rs.RotateObject(bottom_arc, [0,0,0], 90.0, [0,1,0])

domain_crv0 = rs.CurveDomain(top_short_line_2)
domain_crv1 = rs.CurveDomain(bottom_arc)
params = domain_crv0[0], domain_crv1[0]
revs = False, True
cont = 0,2
blend_1 = rs.AddBlendCurve([top_short_line_2, bottom_arc], params, revs, cont)
blend_1 = rs.JoinCurves([blend_1, bottom_arc], True)
blend_2 = rs.MirrorObject(blend_1, [0,0,0], [0,10,0], True)

domain_crv0 = rs.CurveDomain(top_short_line_1)
domain_crv1 = rs.CurveDomain(mid_short_line_1)
params = domain_crv0[0], domain_crv1[0]
revs = True, True
cont = 1,2
blend_3 = rs.AddBlendCurve([top_short_line_1, mid_short_line_1], params, revs, cont)
blend_3 = rs.JoinCurves([blend_3, mid_short_line_1,bottom_curve_1, bottom_curve_2, bl], True)
blend_4 = rs.MirrorObject(blend_3, [0,0,0], [10,0,0], True)

network_curves = [mid_base_shape, top_circle, blend_1, blend_3, blend_2, blend_4, bottom_circle]
surf = rs.AddNetworkSrf(network_curves,0,0,0,0)
rs.CapPlanarHoles(surf)

extr = rs.ExtrudeCurve(base_circle, central_line)
rs.MoveObject(extr, [0,-5,0])
rs.CapPlanarHoles(extr)
obj = rs.BooleanDifference(surf, extr, True)

plane_1 = rs.ExtrudeCurveStraight(cutting_line_1, [0,0,0], [0,10,0])
plane_2 = rs.ExtrudeCurveStraight(cutting_line_2, [0,0,0], [0,10,0])
plane_3 = rs.JoinSurfaces([plane_1, plane_2], True)
plane_3 = rs.MoveObject(plane_3, [0,-5,0])
obj = rs.TrimBrep(obj, plane_3)
rs.DeleteObject(plane_3)
border_curve = rs.DuplicateSurfaceBorder(obj)
border_curve_2 = rs.RotateObject(border_curve[0], [0,0,0], 45.0, [0,1,0], True)
surface_1 = rs.AddSweep1(base_circle, [border_curve[0], border_curve_2], False)
surface_2 = rs.MirrorObject(surface_1, [0,0,0], [0,10,0], True) 
obj = rs.JoinSurfaces([obj, surface_1, surface_2], True)