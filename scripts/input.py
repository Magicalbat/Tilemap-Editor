import pygame
import json

class Input:
    def loadFromFile(self, filePath):
        data = ""
        with open(filePath, 'r') as f:
            data = f.read()
        data = json.loads(data)

        if "input" in data: data = data["input"]
        if "Input" in data: data = data["Input"]

        for action, keyNames in data.items():
            self.currentActionMap[action] = False
            self.prevActionMap[action] = False

            for keyName in keyNames:
                key = pygame.key.key_code(keyName)

                if key in self.keyActions:
                    self.keyActions[key].append(action)
                else:
                    self.keyActions[key] = [action]
            
        self.printKeyActions()
    
    def printKeyActions(self):
        for key, actions in self.keyActions.items():
            print(pygame.key.name(key), end=": [")
            for action in actions:
                print(action, end=", ")
            print("\b\b]")

    def __init__(self, filePath=""):
        self.keyActions = {}
        self.currentActionMap = {}
        self.prevActionMap = {}

        if filePath != "":
            self.loadFromFile(filePath)
    
    def eventUpdate(self, event):
        pass
    
    def passiveUpdate(self):
        self.prevActionMap = self.currentActionMap