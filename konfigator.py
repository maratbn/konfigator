#!/usr/bin/python

class Konfigator:


    def __init__(self):
        self._determineCmdArgs()
        self._determineAbsPathForKernel()

        print 'abs path:', self._strAbsPathForKernel


    def _determineAbsPathForKernel(self):
        """
        Determines the absolute path to the linux kernel sources based on the
        value specified via command line args, and saves it to the field
        '_strAbsPathForKernel'.
        """
        import os.path
        self._strAbsPathForKernel = os.path.abspath(
                                                   self._dictCmdArgs['kernel'])

    def _determineCmdArgs(self):
        """
        Parses and saves the command line arguments to fields
        '_namespaceCmdArgs' and '_dictCmdArgs'.
        """
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
