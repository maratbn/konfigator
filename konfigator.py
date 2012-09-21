#!/usr/bin/python

class Konfigator:

    def __init__(self):
        self._determineCmdArgs()

        import os.path

        strAbsPath = os.path.abspath(self._dictCmdArgs['kernel'])

        print 'abs path:', strAbsPath


    def _determineCmdArgs(self):
        import argparse

        argument_parser = argparse.ArgumentParser(
                        description='Search the Linux kernel Kconfig files.')

        argument_parser.add_argument(
            '-k', '--kernel',
            default='/usr/src/linux/',
            help='path to the Linux kernel source tree to search (default: %(default)s)',
            metavar='path')

        self._namespaceCmdArgs = argument_parser.parse_args()
        self._dictCmdArgs = vars(self._namespaceCmdArgs)


Konfigator()
