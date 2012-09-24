#!/usr/bin/python

#   Konfigator -- Searches the Linux kernel source tree Kconfig files.
#
#   Copyright (C) 2012  Marat Nepomnyashy  maratbn@gmail
#
#   Licensed under the GNU General Public License Version 3.
#
#   This file is part of Konfigator.
#
#   Konfigator is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Konfigator is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Konfigator.  If not, see <http://www.gnu.org/licenses/>.

class Konfigator:


    def __init__(self):
        self._determineCmdArgs()
        self._determineAbsPathForKernel()
        self._scanKconfigFiles()
    #enddef __init__(self)

    def _determineAbsPathForKernel(self):
        """
        Determines the absolute path to the linux kernel sources based on the
        value specified via command line args, and saves it to the field
        '_strAbsPathForKernel'.
        """
        import os.path
        self._strAbsPathForKernel = os.path.abspath(
                                                   self._dictCmdArgs['kernel'])
    #enddef _determineAbsPathForKernel(self)

    def _determineCmdArgs(self):
        """
        Parses and saves the command line arguments to fields
        '_namespaceCmdArgs' and '_dictCmdArgs'.
        """
        import argparse
        argument_parser = argparse.ArgumentParser(
              description='Search the Linux kernel source tree Kconfig files.')
        argument_parser.add_argument(
            '-k', '--kernel',
            default='/usr/src/linux/',
            help='path to the Linux kernel source tree to search (default: %(default)s)',
            metavar='path')
        self._namespaceCmdArgs = argument_parser.parse_args()
        self._dictCmdArgs = vars(self._namespaceCmdArgs)
    #enddef _determineCmdArgs(self)

    def _scanKconfigFiles(self):
        """
        Scans through the Linux source tree for the 'Kconfig' files.
        """
 
        def _scanDir(strPathDir, depth=0):
            import os

            def _getDirListing():
                try:
                    listDir = os.listdir(strPathDir)
                    listDir.sort()
                    return listDir
                except OSError as o_s_error:
                    import sys
                    print >> sys.stderr, 'konfigator:  ' + str(o_s_error)
                    return None
            #enddef _getDirListing()

            def _processFile(strFilename):
                """
                Processes the file specified by the Kconfig file format syntax
                tokens.
                """

                def _scanFile():
                    """
                    Returns a list of dictionaries corresponding to each line
                    in the file.  Each dictionary includes the original line,
                    its indentation level, its left-trimmed version, and a list
                    of all its tokens.
                    """
                    file = open(strFilename, 'rU')
                    listLines = list()
                    import re
                    patternLtrim = re.compile(r'^([ \t]*)(.*)')
                    patternWS = re.compile(r'\s+')
                    for strLine in file:
                        match = patternLtrim.match(strLine)
                        strLtrimmed = match.group(2)
                        listTokens = re.split(patternWS, strLtrimmed)
                        if len(listTokens) == 1 and len(listTokens[0]) == 0:
                            listTokens = None
                        dictLine = {
                            'orig': strLine,
                            'indent': len(match.group(1)),
                            'ltrimmed': strLtrimmed,
                            'tokens':listTokens}
                        listLines.append(dictLine)
                    file.close()
                    return listLines
                #enddef _scanFile()

                listLines = _scanFile()
                dictLineNodeLast = None

                def _determineLineNodeParent(dictLine):
                    """
                    Determines what the parent line node should be for the line
                    specified.
                    """
                    if dictLineNodeLast is None:
                        return None
                    dictLineNodeLastParent = dictLineNodeLast['parent']
                    indent = dictLine['indent']
                    indentLast = dictLineNodeLast['line']['indent']
                    if indent == indentLast:
                        return dictLineNodeLastParent
                    elif indent > indentLast:
                        return dictLineNodeLast
                    else:
                        dictLineNodeAncestor = dictLineNodeLastParent
                        while (dictLineNodeAncestor and
                             dictLineNodeAncestor['line']['indent'] >= indent):
                            dictLineNodeAncestor = (dictLineNodeAncestor
                                                                    ['parent'])
                        return dictLineNodeAncestor
                # enddef _determineLineNodeParent(dictLine)

                listLineNodesRoot = list()
                for dictLine in listLines:
                    dictLineNodeParent = _determineLineNodeParent(dictLine)
                    dictLineNode = {'parent': dictLineNodeParent,
                                          'children': list(), 'line': dictLine}
                    listAppendTo = (dictLineNodeParent['children']
                                  if dictLineNodeParent else listLineNodesRoot)
                    listAppendTo.append(dictLineNode)
                    dictLineNodeLast = dictLineNode

                def _printLineNodes(listLineNodes):
                    for dictLineNode in listLineNodes:
                        print ((' ' * dictLineNode['line']['indent']) +
                                          repr(dictLineNode['line']['tokens']))
                        _printLineNodes(dictLineNode['children'])
                #enddef _printLineNodes(listLineNodes)

                _printLineNodes(listLineNodesRoot)
            #enddef _processFile(strFilename)

            listDirItems = _getDirListing()
            if (depth == 0 and listDirItems is None):
                import sys
                print >> sys.stderr, ('konfigator:  Encountered an operating \
system error while attempting to open the path \'' + self._strAbsPathForKernel
+ '\'.  Make sure to specify the correct path to the Linux kernel source tree \
to search.')
                sys.exit(1)
            for strItem in listDirItems:
                strPathItem = strPathDir + os.sep + strItem
                if os.path.islink(strPathItem):
                    continue
                if os.path.isdir(strPathItem):
                    _scanDir(strPathItem, depth + 1)
                elif os.path.isfile(strPathItem):
                    if strItem == 'Kconfig' or strItem.find('Kconfig.') == 0:
                        print strPathItem
                        _processFile(strPathItem)
        #enddef _scanDir(strPathDir, depth=0)

        _scanDir(self._strAbsPathForKernel)
    #enddef _scanKconfigFiles(self)
#endclass Konfigator

Konfigator()
