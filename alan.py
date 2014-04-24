#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""alan - a fully configurable turing machine module in python.

autor: Markus Barthel
mail: markus.barthel.mb@gmail.com
version: 0.1d
"""

#TODO: Keller-Band implementieren                                           
#TODO: versteckt getter und setter-Methoden für Atribute
#TODO: Benutzung des Moduls dokumentieren
#TODO: Syntax des Programms dokumentieren

##### imports ####
import random

from exceptions import *

##### constants ####
SYMBOL_EOF = 'eof'
SYMBOL_IGNORE = '-'
ONE_CHAR_COMMANDS = ('R', 'L', 'N')
TWO_CHAR_COMMANDS = ('R', 'L', 'W')

##### classes ####

class TransitionFunction(object):
    """a function which needs the current state of the turing machine and the current symbols on the tapes
    and specified the commands for the tapes and the new state of the turing machine"""

    def __init__(self, requireState, symbols, commands, newState):
        self.requireState = requireState
        self.symbols = symbols
        self.commands = commands
        self.newState = newState

    def __str__(self):
        functStr = str(self.requireState) + '; '
        if len(self.symbols) < 2:
            functStr += self.symbols[0]
        else:
            for symbol in self.symbols[:-1]:
                functStr += str(symbol) + ', '
            functStr += str(self.symbols[-1])
        functStr += ' -> '

        if len(self.commands) < 2:
            functStr += self.commands[0]
        else:
            for command in self.commands[:-1]:
                functStr += str(command) + ', '
            functStr += str(self.commands[-1])
        functStr += '; ' + str(self.newState)

        return functStr


class Tape(object):
    """a tape of the turing machine. It determines the allowed action and its behavior"""

    def __init__(self, leftInfinite=True, rightInfinite=True, rightMax=None, kellerTape=None, values=[''], currentPosition=0,  description=''):
        self.leftInfinite = leftInfinite
        self.rightInfinite = rightInfinite
        self.rightMax = rightMax
        self.kellerTape = kellerTape
        self.__blankSymbol = '_'
        self.__values = values
        self.__currentPosition = currentPosition
        self.description = description

        self.__setEof()

    #protected attributes (no class attributes)
    values = property(getValues, setValues)
    #no setter-method. This attributes will only set on the init of the object
    currentPosition = property(getCurrentPosition)
    blankSymbol = property(getBlankSymbol)

    def getValues(self):
        return self._values

    def setValues(self, values):
        self.__values = values  

    def getCurrentPosition(self):
        return self.__currentPosition

    def getBlankSymbol(self):
        return self.__blankSymbol

    def readSymbol(self):
        """returns the symbol on the tape on the current position of the head."""

        currentSymbol = self.values[self.currentPosition]
        #return the specified blankSymbol if current symbol is an empty string - only for compatiblity
        return (currentSymbol if currentSymbol != '' else self.__blankSymbol)

    def writeSymbol(self, symbol):
        """writes a symbol on the position of the head. Write an empty String, if the specified blank symbol was given."""

        self.values[self.currentPosition] = symbol

    def goRight(self):
        """puts the head a position to the right in according to all specified characteristics of the tape"""

        if not self.rightInfinite & self.currentPosition < len(self.values)-1:
            self.currentPosition +=1
        if self.rightInfinite:
            if self.currentPosition == len(self.values) -1:
                self.values.append(self.__blankSymbol)
            self.currentPosition += 1

    def goLeft(self):
        """puts the head a position to the right in according to all specified characteristics of the tape"""

        if not self.leftInfinite & self.currentPosition > 0:
            self.currentPosition -= 1
        if self.leftInfinite:
            if self.currentPosition == 0:
                self.values.insert(0, self.__blankSymbol)
            self.currentPosition -= 1

    def __setEof(self):
        """writes the specified symbol to mark the end of a finite tape for the program."""

        if not self.rightInfinite:
            try:
                if self.rightMax > 0:
                    self.values[self.rightMax-1] = SYMBOL_EOF
                else:
                    raise AlanInitError("Die rechte Grenze des nach rechts begrentzten Bandes ist nicht größer 0.", lineNr)
            except TypeError:
                raise AlanInitError("Die rechte Grenze des nach rechts begrentzten Bandes ist nicht angegeben.", lineNr)
        if not self.leftInfinite:
            self.values[0] = SYMBOL_EOF


class TM(object):
    """the turing machine object"""

    def __init__(self, alphabet=('a', 'b', 'c'), tapes=(), program=(), allowedStates=('q0', 'q1', 'f'), blankSymbol='_', ignoreSymbol='-', initState='q0', finalStates=('f', )):
        self.alphabet = alphabet
        self.__tapes = tapes
        self.__program = program
        self.allowedStates = allowedStates
        self.blankSymbol = blankSymbol
        self.ignoreSymbol = ignoreSymbol
        self.__initState
        self.setInitState(initState)
        self.__finalStates 
        self.setFinalStates(finalStates)

        self.__currentState = initState

    #protected attributes (no class attributes)
    initState = property(getInitState, setInitState)
    finalStates = property(getFinalStates, setFinalStates)
    #no setter-method.
    tapes = property(getTapes)
    program = property(getProgram)

    def getInitState(self):
        return self.__initState

    def setInitState(self, initState):
        if initState in self.allowedStates:
            self.__initState = initState
        else:
            raise AlanInitError("InitState ist nicht in den erlaubten Statuse")

    def getFinalStates(self):
        return self.__finalStates

    def setFinalStates(self, finalStates):
        for state in finalStates:
            if state not in self.allowedStates:
                raise AlanInitError("Die FinalStates sind keine erlaubten Statuse")
        self.__finalStates = finalStates

    def addTape(self, tape):
        """adds a tape to the turing machine"""

        #set blankSymbol of the tape to the blankSymbol of the turing machine
        tape.blankSymbol = self.__blankSymbol
        self._tapes += (tape, )

    def getTapes(self):
        return self.__tapes

    def addFunction(self, function):
        """adds a function to the program of the turing machine"""

        self._program += (function, )

    def parseProgram(self, programStr):
        """parse programs into single transitional functions and adds them to the program of the turing machine"""

        if len(self._tapes) == 0:
            raise AlanInitError("Vor dem Parsen des Programmes bitte zuerst die Bänder konfigurieren", None )

        #split the program on newline, store it in a list and remove whitespace at the end and the start
        lines = [l.strip() for l in programStr.splitlines()]
        for line, lineNr in zip(lines, xrange(1, len(lines)+1)):
            leftLine, rightLine = line.split('->')
            requireState, symbols = leftLine.split(';')
            commands, newState = rightLine.split(';')

            str = []
            for s in requireState, symbols, commands, newState:
                str.append(s.strip())
            requireState, symbols, commands, newState = str

            if requireState not in self.allowedStates:
                raise AlanSyntaxError("Anfangsstatus der Regel muss erlaubter Status sein", lineNr)
            if requireState in self.finalStates:
                raise AlanSyntaxError("Anfangsstatus der Regel darf kein finaler Status sein.", lineNr)

            #split current symbols on comma, store it in a list and strip
            symbols = [s.strip() for s in symbols.split(',')]
            if len(symbols) != len(self._tapes):
                #if more or less symbols as tapes exists 
                raise AlanSyntaxError("Die Anzahl der Symbole muss mit der Anzahl der Tapes übereinstimmen.", lineNr)
            #check if every symbol is in the allowed
            for symbol, tape in zip(symbols, self._tapes):
                if symbol not in self.alphabet + (tape.blankSymbol, SYMBOL_IGNORE):
                    raise AlanSyntaxError("Symbol nicht erlaubt", lineNr)

            commands = [s.strip() for s in commands.split(',')]
            if len(commands) != len(self._tapes):
                raise AlanSyntaxError("Die Anzahl der Befehle muss mit der Anzahl der Tapes übereinstimmen.", lineNr)
            for command in commands:
                try:                        
                    #check if the length of the commands are right and if the command are allowed
                    if len(command) not in (1, 2):
                        raise AlanSyntaxError("Unbekannter Befehl.", lineNr)
                    if len(command) == 1 and command[0] not in ONE_CHAR_COMMANDS:
                        raise AlanSyntaxError("Unbekannter Befehl.", lineNr)
                    if len(command) == 2 and command[0] not in TWO_CHAR_COMMANDS:
                        raise AlanSyntaxError("Unbekannter Befehl.", lineNr)
                    
                    #check if symbol after two-char command is writable
                    if len(command) == 2 and command[1] not in self.alphabet + (tape.blankSymbol, ):
                            raise AlanSyntaxError("zu schreibendes Symbol nicht erlaubt", lineNr)
                except IndexError:
                    raise AlanSyntaxError("Unbekannter Befehl.", lineNr)

            if newState not in self.allowedStates:
                raise AlanSyntaxError("Endstatus muss ein erlaubter Status sein.", lineNr)

            self.addFunction(TransitionFunction(requireState, tuple(symbols), tuple(commands), newState))

    def getProgram(self):
        return [str(func) for func in self.__program]

    def choseNextFunction(self):
        """"choses the TransitionFunction which must be run as next

        if there are more than one function that fits, one of these functions will chose randomly.
        """

        matchedFunctions = []
        #store all current symbols of all tapes in a tuple
        currentSymbols = tuple([tape.readSymbol() for tape in self._tapes])
        for funct in self._program:
            if funct.requireState == self.currentState and funct.symbols == currentSymbols:
                matchedFunctions.append(funct)
        if len(matchedFunctions) == 0:
            return None
        elif len(matchedFunctions) > 1:
            #non-deterministic; run a random function
            return random.choice(matchedFunctions)
        else:
            return matchedFunctions[0]

    def runFunction(self, function):
        """run a function on these turing machine"""

        for command, tape in zip(function.commands, self._tapes):
            try:
                tape.writeSymbol(command[1])
            except IndexError:
                pass
            if command[0] == 'R':
                tape.goRight()
            elif command[0] == 'L':
                tape.goLeft()

        self.currentState = function.newState

        #return true if turing maschine entered one in final state or False if not
        if self.currentState in self.finalStates:
            return True
        else:
            return False

#
#testregel = TransitionFunction('0', (5, 2, 9), ('R', 'R', 'W'), '1')
#testregel
