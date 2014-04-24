#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Own exceptions for alan
AlanInitError
AlanSyntaxError
AlanRuntimeError
"""
##### imports ####

##### constants ####

##### classes ####
class AlanInitError(Exception):
    def __init__(self, message, value):
        self.message = message
        self.value = value
    
    def __str__(self):
        return "Fehler beim Konfigurieren der Turing-Maschine: \n" + self.message + " Wert: " + str(self.value)

class AlanSyntaxError(Exception):
    def __init__(self, message, line):
        self.message = message
        self.line = line
    
    def __str__(self):
        return "Syntaxfehler in Turing-Programm: \n" + self.message +  " Zeile: " + str(self.line)

class AlanRuntimeError(Exception):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return "Laufzeitfehler in Turing-Maschine: \n" + self.message
