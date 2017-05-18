import argparse

from .exception import Pgpc2tileException


class BoundsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        bounds_string = values
        bounds = bounds_string.split(',')
        try:
            bounds = tuple(map(float, bounds))
        except ValueError:
            raise Pgpc2tileException('bounds include non-numeric values')
        setattr(namespace, self.dest, bounds)


def parse(*args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--dbstring', '-d',
                        help='The postgresql database connection string '
                             '(example: user:password@localhost:5432/db)',
                        required=True)
    parser.add_argument('--table', '-t',
                        help='The database table',
                        required=True)
    parser.add_argument('--patch-column', '-p',
                        help='The name of the patch column',
                        required=True)
    parser.add_argument('--id-column', '-i',
                        help='The name of the id column',
                        required=True)
    parser.add_argument('--bounds', '-b',
                        help='The tileset bounds',
                        required=True,
                        action=BoundsAction)
    parser.add_argument('--lod-min', '-m',
                        help='The minimum lod level',
                        type=int,
                        required=True)
    parser.add_argument('--lod-max', '-M',
                        help='The maximun lod level',
                        type=int,
                        required=True)
    parser.add_argument('--tileset', '-n',
                        help='The name of the tileset file to create '
                             '(default is tileset.json)',
                        default='tileset.json')
    parser.add_argument('--tiledir', '-l',
                        help='The directory where the tiles are stored '
                             '(default is "data")',
                        default='data')
    parser.add_argument('--base-url', '-u',
                        help='The base url for tiles '
                             '(defaut is the empty string)',
                        default='')
    parser.add_argument('--tileset-indent', '-s',
                        help='Number of spaces for indentation of the tileset '
                             'file (default is no indentation)',
                        type=int)
    parser.add_argument('--debug',
                        help='Display debug messages',
                        action='store_true')
    return parser.parse_args(*args)
