import os
import sys
import json
import struct
import codecs

from . import database as db
from . import config
from .index import quadtree
from .exception import Pgpc2tileException


class Runner:
    _GEOMETRIC_ERROR_DEFAULT = 2000

    def __init__(self, tileset, tiledir, base_url, table, patch_column,
                 id_column, tileset_indent, debug):
        self.tileset = tileset
        self.tiledir = tiledir
        self.base_url = base_url
        self.table = table
        self.patch_column = patch_column
        self.id_column = id_column
        self.tileset_indent = tileset_indent
        self.debug = debug
        self.used_patches = None

        self.treeindex = quadtree.Quadtree()

        if not os.path.isdir(self.tiledir):
            os.makedirs(self.tiledir)

    def __call__(self, bounds, lod_min, lod_max):
        self.used_patches = {}

        tileset = {}
        tileset['asset'] = {'version': '0.0'},
        tileset['geometricError'] = self._GEOMETRIC_ERROR_DEFAULT

        root = self._tile(bounds, lod_min, lod_max,
                          self._GEOMETRIC_ERROR_DEFAULT, 0, 0)

        root['refine'] = 'add'
        tileset['root'] = root

        f = open(self.tileset, 'w')
        f.write(json.dumps(tileset, indent=self.tileset_indent))
        f.close()

    def _tile(self, bounds, lod, lod_max, err, x, y):

        if lod > lod_max:
            return

        patch_wkb = self.select_patch(bounds)
        if not patch_wkb:
            return

        self.create_tile(patch_wkb)

        tile = {}

        bounding_volume = {}
        center_x = (bounds[0] + bounds[2]) / 2.0
        center_y = (bounds[1] + bounds[3]) / 2.0
        bounding_volume['sphere'] = [center_x, center_y, 0.0, 2000]

        tile['boundingVolume'] = bounding_volume
        tile['geometricError'] = err / 2.0

        url = '{}/{}/{}/{}.pnts'.format(self.base_url, lod, x, y)
        tile['content'] = {'url': url}

        bnw, bne, bsw, bse = self.treeindex.split_bounds(bounds)
        tnw = self._tile(bnw, lod + 1, lod_max, err / 2.0,
                         2 * x, 2 * y)
        tne = self._tile(bne, lod + 1, lod_max, err / 2.0,
                         2 * x + 1, 2 * y)
        tsw = self._tile(bsw, lod + 1, lod_max, err / 2.0,
                         2 * x, 2 * y + 1)
        tse = self._tile(bse, lod + 1, lod_max, err / 2.0,
                         2 * x + 1, 2 * y + 1)
        children = [t for t in (tnw, tne, tsw, tse) if t]

        if len(children):
            tile['children'] = children

        return tile

    def select_patch(self, bounds):
        for sql_limit in (10, 20):
            sql = self.tile_sql(bounds, sql_limit)
            if self.debug:
                print(sql)

            rows = db.query(sql)
            if len(rows) == 0:
                return None

            for patch_id, patch_wkb in rows:
                if patch_id not in self.used_patches:
                    break
            else:
                continue
            break
        else:
            if self.debug:
                raise Pgpc2tileException('No unused patches found')

        self.used_patches[patch_id] = True
        return patch_wkb

    def tile_sql(self, bounds, limit):
        sql = '''
        SELECT {0}, PC_Uncompress({1})
        FROM {2}
        WHERE PC_EnvelopeGeometry({1}) && \'{3}\'::geometry
        ORDER BY {4}
        LIMIT {5}
        '''.format(self.id_column, self.patch_column, self.table,
                   self.bounds_wkt(bounds), 'morton', limit)
        return sql

    def create_tile(self, patch_wkb):

        npoints_hexa = patch_wkb[18:26]
        npoints = struct.unpack("I", codecs.decode(npoints_hexa, "hex"))[0]

        #pdt = np.dtype([('X', '<f4'), ('Y', '<f4'), ('Z', '<f4')])
        #cdt = np.dtype([('Red', 'u1'), ('Green', 'u1'), ('Blue', 'u1')])

        print(patch_wkb)
        #features = []
        #for i in range(0, npoints):


    @staticmethod
    def bounds_wkt(bounds):
        return 'LINESTRING ({0} {2},{1} {3})'.format(*bounds)


def main():
    # get command line arguments
    args = config.parse(sys.argv[1:])

    # initialize database connection
    db.init(args.dbstring)

    # create runner object
    run = Runner(args.tileset, args.tiledir, args.base_url, args.table,
                 args.patch_column, args.id_column, args.tileset_indent,
                 args.debug)

    # go!
    run(args.bounds, args.lod_min, args.lod_max)
