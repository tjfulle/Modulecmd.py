import os
import modulecmd.third_party.rst2ansi as rst2ansi
import modulecmd.paths
from modulecmd.xio import pager
from modulecmd._util.tty import redirect_stdout

try:
    import docutils
except ImportError:  # pragma: no cover
    docutils = None

try:
    from docutils import nodes, core  # noqa: F401
except ImportError:  # pragma: no cover
    docutils = -1


description = "Display Modulecmd.py guides in the console"
section = "info"
level = "short"


available_guides = dict(
    [
        (os.path.splitext(f)[0], os.path.join(modulecmd.paths.docs_path, f))
        for f in os.listdir(modulecmd.paths.docs_path)
    ]
)


def setup_parser(subparser):
    subparser.add_argument(
        "guide", choices=available_guides, help="Name of guide to display"
    )


def guide(parser, args):
    if docutils is None:  # pragma: no cover
        raise ImportError("Guides require docutils module")
    elif docutils == -1:  # pragma: no cover
        msg = (
            "There was an error importing several docutils components and "
            "the guides cannot be displayed"
        )
        raise ImportError(msg)

    filename = available_guides[args.guide]
    with redirect_stdout():
        pager(rst2ansi.rst2ansi(open(filename, "r").read()))
