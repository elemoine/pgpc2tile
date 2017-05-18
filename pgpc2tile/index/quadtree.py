class Quadtree:

    @staticmethod
    def split_bounds(bounds):
        center_x = (bounds[0] + bounds[2]) / 2.0
        center_y = (bounds[1] + bounds[3]) / 2.0
        bnw = (bounds[0], center_y, center_x, bounds[3])
        bne = (center_x, center_x, bounds[2], bounds[3])
        bsw = (bounds[0], bounds[1], center_x, center_y)
        bse = (center_x, bounds[1], bounds[2], center_x)
        return (bnw, bne, bsw, bse)
