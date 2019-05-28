import pymod.mc

description = 'Save loaded modules'
level = 'short'
section = 'collections'


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument(
        'name', nargs='?',
        default=pymod.names.default_user_collection,
        help='Name of collection to save')
#    subparser.add_argument(
#        '--local', action='store_true', default=False,
#        help='Save the collection locally')


def save(parser, args):
    pymod.mc.collection.save(args.name) #, local=args.local)
