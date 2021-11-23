import pygame
import json, copy

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
    
    # state is True or False based on key down or up
    def eventUpdate(self, key, state):
        self.prevActionMap = copy.deepcopy(self.currentActionMap)
        if key in self.keyActions:
            for action in self.keyActions[key]:
                self.currentActionMap[action] = state
    
    def passiveUpdate(self):
        self.prevActionMap = copy.deepcopy(self.currentActionMap)
    
    def isActionPressed(self, action):
        return self.currentActionMap[action]
    
    def isActionReleased(self, action):
        return not self.currentActionMap[action]
    
    def isActionJustPressed(self, action):
        return self.currentActionMap[action] and not self.prevActionMap[action]
    
    def isActionJustReleased(self, action):
        return not self.currentActionMap[action] and self.prevActionMap[action]