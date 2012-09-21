#!/usr/bin/python

class Konfigator:

    def __init__(self):
        cmd_args = vars(self.getCmdArgs())
        print cmd_args

        import os.path

        strAbsPath = os.path.abspath(cmd_args['kernel'])

        print 'abs path:', strAbsPath


    def getCmdArgs(self):
        import argparse

        argument_parser = argparse.ArgumentParser(
                        description='Search the Linux kernel Kconfig files.')

        argument_parser.add_argument(
            '-k', '--kernel',
            default='/usr/src/linux/',
            help='path to the Linux kernel source tree to search (default: %(default)s)',
            metavar='path')

        return argument_parser.parse_args()

Konfigator()
