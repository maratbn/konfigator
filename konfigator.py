#!/usr/bin/python

#   Konfigator -- Searches the Linux kernel source tree Kconfig files.
#   https://github.com/maratbn/Konfigator/
#
#   Version: 0.1
#
#   Copyright (C) 2012  Marat Nepomnyashy  http://maratbn.com  maratbn@gmail
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


from __future__ import print_function


class Konfigator:


    def __init__(self):
        self._determineCmdArgs()
        self._processCmdArgs()
        self._scanKconfigFiles()
    #enddef __init__(self)

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
        argument_parser.add_argument(
            '-s', '--search',
            required=True,
            help='string to search for in the config tokens and descriptions, \
can be in quotes',
            metavar='string')
        self._namespaceCmdArgs = argument_parser.parse_args()
        self._dictCmdArgs = vars(self._namespaceCmdArgs)
    #enddef _determineCmdArgs(self)

    def _processCmdArgs(self):
        """
        Determines and processes various command line arguments and saves them
        as class fields.
        """
        import os.path
        self._strAbsPathForKernel = os.path.abspath(
                                                   self._dictCmdArgs['kernel'])
        import re
        strSearch = re.sub(r'\\', '\\\\', self._dictCmdArgs['search'])
        strSearch = re.sub(r'\s+', '\\s', strSearch)
        self._patternSearch = re.compile('.*' + strSearch + '.*', re.IGNORECASE)
    #enddef _processCmdArgs(self)

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
                    print('konfigator:  ' + str(o_s_error), file=sys.stderr)
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
                    file = open(strFilename, 'rU', errors='ignore')
                    listLines = list()
                    import re
                    patternLtrim = re.compile(r'^([ \t]*)(.*)')
                    patternWS = re.compile(r'\s+')
                    numLine = 1
                    for strLine in file:
                        match = patternLtrim.match(strLine)
                        strLtrimmed = match.group(2)
                        listTokens = re.split(patternWS, strLtrimmed)
                        if len(listTokens) == 1 and len(listTokens[0]) == 0:
                            listTokens = None
                        dictLine = {
                            'num': numLine,
                            'orig': strLine,
                            'indent': len(match.group(1)),
                            'ltrimmed': strLtrimmed,
                            'tokens':listTokens}
                        listLines.append(dictLine)
                        numLine += 1
                    file.close()
                    return listLines
                #enddef _scanFile()

                def _processLinesIntoLineNodes(listLines):
                    """
                    Takes a list of dictionaries corresponding to each line,
                    and returns a list of dictionaries representing root nodes
                    of a hierarchial tree structure into which the lines are
                    assembled based on their indentation level.
                    """
                    dictLineNodeLast = None

                    def _determineLineNodeParent(dictLineNode):
                        """
                        Determines what the parent line node should be for the
                        line node specified.
                        """
                        if dictLineNodeLast is None:
                            return None
                        dictLineNodeLastParent = dictLineNodeLast['parent']
                        indent = dictLineNode['indent']
                        indentLast = dictLineNodeLast['indent']
                        if indent == indentLast:
                            return dictLineNodeLastParent
                        elif indent > indentLast:
                            return dictLineNodeLast
                        else:
                            dictLineNodeAncestor = dictLineNodeLastParent
                            while (dictLineNodeAncestor and
                                 dictLineNodeAncestor['indent'] >= indent):
                                dictLineNodeAncestor = (dictLineNodeAncestor
                                                                    ['parent'])
                            return dictLineNodeAncestor
                    # enddef _determineLineNodeParent(dictLine)

                    listLineNodesRoot = list()
                    for dictLine in listLines:
                        dictLineNode = {'children': list(), 'line': dictLine}
                        listLineTokens = dictLine['tokens']
                        if listLineTokens is None or len(listLineTokens) == 0:
                            dictLineNode['indent'] = (dictLineNodeLast
                                         ['indent'] if dictLineNodeLast else 0)
                        else:
                            dictLineNode['indent'] = dictLine['indent']
                        dictLineNodeParent = _determineLineNodeParent(
                                                                  dictLineNode)
                        dictLineNode['parent'] = dictLineNodeParent
                        listAppendTo = (dictLineNodeParent['children'] if
                                     dictLineNodeParent else listLineNodesRoot)
                        listAppendTo.append(dictLineNode)
                        dictLineNodeLast = dictLineNode
                    return listLineNodesRoot
                #enddef _processLinesIntoLineNodes()

                def _printLineNodes(listLineNodes):
                    for dictLineNode in listLineNodes:
                        print((' ' * dictLineNode['indent']) +
                                          repr(dictLineNode['line']['tokens']))
                        _printLineNodes(dictLineNode['children'])
                #enddef _printLineNodes(listLineNodes)

                def _findHelpNode(dictLineNode):
                    listChildren = dictLineNode['children']
                    for dictChild in listChildren:
                        listTokens = dictChild['line']['tokens']
                        if (listTokens and len(listTokens) > 0 and
                                (listTokens[0] == 'help' or listTokens[0] ==
                                                                 '---help---')):
                            return dictChild
                        dictHelpFound = _findHelpNode(dictChild)
                        if dictHelpFound:
                            return dictHelpFound
                    return None
                #enddef _findHelpNode(dictLineNode)

                listLineNodesRoot = _processLinesIntoLineNodes(_scanFile())
                listConfigs = list()
                for dictLineNode in listLineNodesRoot:
                    listTokens = dictLineNode['line']['tokens']
                    if (not listTokens or len(listTokens) == 0 or
                                                    listTokens[0] != 'config'):
                        continue
                    strConfig = listTokens[1] if len(listTokens) > 1 else ''
                    dictHelpNodeParent = _findHelpNode(dictLineNode)
                    if not dictHelpNodeParent:
                        continue
                    listLinesHelp = list()
                    listHelpNodeChildren = dictHelpNodeParent['children']
                    indentLowest = None
                    for dictHelpNodeChild in listHelpNodeChildren:
                        indentHelpNodeChild = dictHelpNodeChild['indent']
                        if indentLowest == None:
                            indentLowest = indentHelpNodeChild
                        elif indentHelpNodeChild < indentLowest:
                            indentLowest = indentHelpNodeChild
                        listLinesHelp.append(dictHelpNodeChild['line'])
                    listHelpTrimmed = list()
                    listHelpTrimmedNum = list()
                    for dictLineHelp in listLinesHelp:
                        strHelpOrig = dictLineHelp['orig']
                        strHelp = strHelpOrig[indentLowest:]
                        if len(strHelp) == 0:
                            strHelp = strHelpOrig
                        listHelpTrimmed.append(strHelp)
                        listHelpTrimmedNum.append(repr(dictLineHelp['num']) +
                                              ':    ' + strHelp)
                    strHelpTrimmed = ''.join(listHelpTrimmed)
                    strHelpTrimmedNum = ''.join(listHelpTrimmedNum)
                    if (self._patternSearch.match(strConfig) or
                                    self._patternSearch.match(strHelpTrimmed)):
                        dictLine = dictLineNode['line']
                        print(strFilename)
                        print(repr(dictLine['num']) + ':  ' +
                                                          dictLine['ltrimmed'])
                        print(strHelpTrimmedNum)
                        print()
            #enddef _processFile(strFilename)

            listDirItems = _getDirListing()
            if (depth == 0 and listDirItems is None):
                import sys
                print('konfigator:  Encountered an operating system error \
while attempting to open the path \'' + self._strAbsPathForKernel + '\'.  \
Make sure to specify the correct path to the Linux kernel source tree to \
search.', file=sys.stderr)
                sys.exit(1)
            for strItem in listDirItems:
                strPathItem = strPathDir + os.sep + strItem
                if os.path.islink(strPathItem):
                    continue
                if os.path.isdir(strPathItem):
                    _scanDir(strPathItem, depth + 1)
                elif os.path.isfile(strPathItem):
                    if strItem == 'Kconfig' or strItem.find('Kconfig.') == 0:
                        _processFile(strPathItem)
        #enddef _scanDir(strPathDir, depth=0)

        _scanDir(self._strAbsPathForKernel)
    #enddef _scanKconfigFiles(self)
#endclass Konfigator

Konfigator()
