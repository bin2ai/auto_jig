import cadquery as cq
from typing import List, Tuple


class SemiHollowCylinder:
    def __init__(self, cyl_diam: float, hole_diam: float, hole_depth: float, cyl_height: float):
        self.cyl_diam = cyl_diam
        self.hole_diam = hole_diam
        self.hole_depth = hole_depth
        self.cyl_height = cyl_height
        self.body = None
        self.outer_body = None

    def create(self) -> cq.Workplane:
        cylinder = cq.Workplane("XY").circle(
            self.cyl_diam / 2).extrude(self.cyl_height)
        hole = (cq.Workplane("XY")
                .circle(self.hole_diam / 2)
                .extrude(self.hole_depth)
                .translate((0, 0, self.cyl_height - self.hole_depth)))

        self.body = cylinder.cut(hole)
        self.outer_body = cylinder
        return self.body


class TableBody:
    def __init__(self, margin: float,
                 top_legs: List[SemiHollowCylinder], leg_positions: List[Tuple[float, float]],
                 heat_inserts: List[SemiHollowCylinder], heat_insert_positions: List[Tuple[float, float]]):
        self.margin_hole_wall = margin
        self.top_legs = top_legs
        self.leg_positions = leg_positions
        self.heat_inserts = heat_inserts
        self.heat_insert_positions = heat_insert_positions
        self.surface = None

    def create(self) -> cq.Workplane:
        if not all(leg.body for leg in self.top_legs):
            raise ValueError(
                "All legs must be created before assembling the table.")

        max_leg_diam = max(leg.cyl_diam for leg in self.top_legs)
        min_x = min(x for x, _ in self.heat_insert_positions) - \
            max_leg_diam / 2 - self.margin_hole_wall
        max_x = max(x for x, _ in self.heat_insert_positions) + \
            max_leg_diam / 2 + self.margin_hole_wall
        min_y = min(y for _, y in self.heat_insert_positions) - \
            max_leg_diam / 2 - self.margin_hole_wall
        max_y = max(y for _, y in self.heat_insert_positions) + \
            max_leg_diam / 2 + self.margin_hole_wall

        table_width, table_length = max_x - min_x, max_y - min_y
        table_x, table_y = (min_x + max_x) / 2, (min_y + max_y) / 2
        table_z = -max(leg.cyl_height for leg in self.top_legs)

        max_heat_insert_height = max(
            insert.cyl_height for insert in self.heat_inserts)
        table_surface = cq.Workplane("XY").box(
            table_width, table_length, max_heat_insert_height).translate((table_x, table_y, table_z))

        for leg, (x, y) in zip(self.top_legs, self.leg_positions):
            table_surface = table_surface.union(
                leg.body.translate((x, y, -leg.cyl_height)))

        for heat_insert, (x, y) in zip(self.heat_inserts, self.heat_insert_positions):
            table_surface = table_surface.cut(
                heat_insert.outer_body.rotate((0, 0, 0), (1, 1, 0), 180).translate(
                    (x, y, table_z + heat_insert.cyl_height/2)))
            # now place the heat insert at the correct position
            # rotate the heat insert by 180 degrees so that the hole is facing up
            # then translate it to the correct position
            table_surface = table_surface.union(
                heat_insert.body.rotate((0, 0, 0), (1, 1, 0), 180).translate(
                    (x, y, table_z + heat_insert.cyl_height/2)))

        self.surface = table_surface
        return self.surface


if __name__ == "__main__":
    legs = [SemiHollowCylinder(10, 5, 5, 20) for _ in range(3)]
    for leg in legs:
        leg.create()

    heat_inserts = [SemiHollowCylinder(5, 2.5, 2.5, 5) for _ in range(4)]
    for insert in heat_inserts:
        insert.create()

    table = TableBody(
        5,
        legs,
        [(30, 30), (30, 70), (70, 30)],
        heat_inserts, [(0, 0), (0, 100), (100, 0), (100, 100)]
    )
    result = table.create()

    output_filename = "table_with_legs.stl"
    cq.exporters.export(result, output_filename)
    print(f"STL file saved as {output_filename}")
