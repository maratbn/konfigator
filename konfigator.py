#!/usr/bin/python

class Konfigator:


    def __init__(self):
        self._determineCmdArgs()
        self._determineAbsPathForKernel()
        self._scanKconfigFiles()
        print 'abs path:', self._strAbsPathForKernel
        print 'list items:', self._listItems

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

    def _scanKconfigFiles(self):
        """
        Scans through the Linux source tree for the 'Kconfig' files.
        """
        def _getDirListing():
            import os
            try:
                return os.listdir(self._strAbsPathForKernel)
            except OSError as o_s_error:
                import sys
                print >> sys.stderr, 'konfigator:  ' + str(o_s_error)
                print >> sys.stderr, ('konfigator:  Encountered an operating \
system error while attempting to open the path \'' + self._strAbsPathForKernel
+ '\'.  Make sure to specify the correct path to the Linux kernel source tree \
to search.')
                exit()
        self._listItems = _getDirListing()

Konfigator()
