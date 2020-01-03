# Author: Alex Kastanek
# Date: November 29, 2019
# Script: Image Generator
# Description: Generates an image by constructing a list of
#   3 functions for the R, G, and B channels of the image.
#   It does this by randomly generating a set of expressions
#   separated by a set of operators from a given list of simple
#   expressions such as cos(PI*x) and sin(PI*x)
# Reference: This script is highly based on the algorithm seen
#   in a tutorial, which can be accessed using the link below.
# https://jeremykun.com/2012/01/01/random-psychedelic-art/

import random, math
import re
from PIL import Image

redFunctionCalls = []
greenFunctionCalls = []
blueFunctionCalls = []
currentFunctionCalls = []

def sinPiX(x):
    return math.sin(math.pi * x)

def sinPiXY(x, y):
    return math.sin(math.pi * x * y)

def cosPiX(x):
    return math.cos(math.pi * x)

def cosPiXY(x, y):
    return math.cos(math.pi * x * y)

def tanPiX(x):
    return math.tan(math.pi * x)

def tanPiXY(x, y):
    return math.tan(math.pi * x * y)

def lnX(x):
    if (x <= 0):
        x = 0.0000001
    return math.log(x)

def plotImage(redFunctionCalls, greenFunctionCalls, blueFunctionCalls, pixelsPerUnit = 150):
    # create a canvas for each color
    redCanvas = plotColor(redFunctionCalls, pixelsPerUnit)
    greenCanvas = plotColor(greenFunctionCalls, pixelsPerUnit)
    blueCanvas = plotColor(blueFunctionCalls, pixelsPerUnit)

    # merge the colors together
    return Image.merge("RGB", (redCanvas, greenCanvas, blueCanvas))

def plotColor(functionCalls, pixelsPerUnit):
    # initialize blank canvas
    canvasWidth = 2 * pixelsPerUnit + 1
    print("canvasWidth = " + str(canvasWidth))
    canvas = Image.new("L", (canvasWidth, canvasWidth))

    #DEBUG
    # x = 1
    # y = 2
    # value = evaluateExpression(expression,[x,y])
    # print("Plot Color - Value: " + str(value))
    # return
    
    # draw the image
    for it1 in range(canvasWidth):
        # print("loop lv 0: it1 = " + str(it1))
        for it2 in range(canvasWidth):
            # print("loop lv 1: it1 = " + str(it2))
            # convert pixel location to [-1,1]
            x = float(it2 - pixelsPerUnit) / pixelsPerUnit
            y = -float(it1 - pixelsPerUnit) / pixelsPerUnit
            # print("From plotColor(): ("+str(x)+","+str(y)+")")
            z = evaluateFunctionCalls(functionCalls,(x,y))
            # if (it1 == 0 and it2 == 0):
            #     print(str(currentFunctionCalls))
            #     newZ = evaluateExpressionFromFunctionCalls(currentFunctionCalls,(x,y))
            #     print("Final value from evalFromFunctionCalls(): " + str(newZ))
            #     print("Final actual value: " + str(z))
            # print("Final value: " + str(z))

            # scale [-1,1] result to [0,255].
            intensity = int(z * 127.5 + 127.5)
            if (intensity < 0):
                intensity = 0
            elif (intensity > 255):
                intensity = 255
            canvas.putpixel((it2,it1), intensity)   
    
    return canvas

# an expression can be defined as a set of expressions which may or may not be separated by an operator
def buildExpression(prob = 0.9):
    #print("From buildExpression(): ("+str(x)+","+str(y)+")")
    if random.random() < prob:
        return random.choice([
            "s(" + buildExpression(prob*prob) + ")",
            "c(" + buildExpression(prob*prob) + ")",
            "t(" + buildExpression(prob*prob) + ")",
            "l(" + buildExpression(prob*prob) + ")",
            random.choice(["s(" + buildExpression(prob*prob) + ")*s(" + buildExpression(prob*prob) + ")",
                "s(" + buildExpression(prob*prob) + ")*c(" + buildExpression(prob*prob) + ")",
                "s(" + buildExpression(prob*prob) + ")*t(" + buildExpression(prob*prob) + ")"]),
            random.choice(["c(" + buildExpression(prob*prob) + ")*c(" + buildExpression(prob*prob) + ")",
                "c(" + buildExpression(prob*prob) + ")*s(" + buildExpression(prob*prob) + ")",
                "c(" + buildExpression(prob*prob) + ")*t(" + buildExpression(prob*prob) + ")"]),
            random.choice(["t(" + buildExpression(prob*prob) + ")*t(" + buildExpression(prob*prob) + ")",
                "t(" + buildExpression(prob*prob) + ")*s(" + buildExpression(prob*prob) + ")",
                "t(" + buildExpression(prob*prob) + ")*c(" + buildExpression(prob*prob) + ")"])
        ])
    else:
        return random.choice(["x","y"])

def evaluateExpression(parentExpression):
    global currentFunctionCalls

    # get list of expressions and operators
    expressionsAndOperators = tokenizeExpression(parentExpression)
    expressions = expressionsAndOperators[0]
    operators = expressionsAndOperators[1]
    # print("Expressions (" + str(len(expressionsAndOperators[0])) + "): " + str(expressionsAndOperators[0]))
    # print("Operators (" + str(len(expressionsAndOperators[1])) + "): "+ str(expressionsAndOperators[1]))

    # if there are no expressions or operators, then the parent expression contains just a variable, so return the corresponding value
    if (len(expressions) == 0 and len(operators) == 0):
        if (parentExpression[0] == 'x'):
            # print("Returning " + str(params[0]))
            currentFunctionCalls.append("(")
            currentFunctionCalls.append("x")
            currentFunctionCalls.append(")")
            return 0
        elif (parentExpression[0] == 'y'):
            # print("Returning " + str(params[1]))
            currentFunctionCalls.append("(")
            currentFunctionCalls.append("y")
            currentFunctionCalls.append(")")
            return 1

    # for each expression, determine the nested expression and evaluate it
    currentFunctionCalls.append("(")
    values = []
    for expression in expressions:
        nestedExpression = determineNestedExpression(expression)
        # print("Nested Expression: " + str(nestedExpression))
        if (expression[0] == 's'):
            #currentFunctionCalls.append("s(")
            values.append(sinPiX(evaluateExpression(nestedExpression)))
            currentFunctionCalls.append("s")
        elif (expression[0] == 'c'):
            # currentFunctionCalls.append("c(")
            values.append(cosPiX(evaluateExpression(nestedExpression)))
            currentFunctionCalls.append("c")
        elif (expression[0] == 't'):
            # currentFunctionCalls.append("t(")
            values.append(tanPiX(evaluateExpression(nestedExpression)))
            currentFunctionCalls.append("t")
        elif (expression[0] == 'l'):
            # currentFunctionCalls.append("l(")
            values.append(lnX(evaluateExpression(nestedExpression)))
            currentFunctionCalls.append("l")
    
    # apply the set of operators to the values
    #TODO: make below functionality actually apply order of operations
    #NOTE: below functionality currently only multiplies all elements of values together
    # print("Values: " + str(values))
    finalValue = values[0]
    if (len(values) > 1):
        for value in values[1:]:
            finalValue *= value
            currentFunctionCalls.append("*")

    # print("Final Value: " + str(finalValue))
    currentFunctionCalls.append(")")
    return 2

def tokenizeExpression(parentExpression):
    # will return a wrapper for a list of expressions and a list of operators
    possibleOperators = ['*']
    expressions = []
    operators = []
    # using a stack to determine what is a full expression
    finishedExpression = True
    parenthesisStack = []
    expression = []
    for symbol in parentExpression:
        #print(str(symbol) + " - symbol in possible operators? " + str(symbol in possibleOperators) + ". finished expression ? " + str(finishedExpression) + ".")
        if ((finishedExpression) and (symbol in possibleOperators) == True):
            operators.append(symbol)
        else:
            expression.append(symbol)
        if (symbol == '('):
            parenthesisStack.append(1)
            finishedExpression = False
        elif (symbol == ')'):
            parenthesisStack.pop()
        #print(str(parenthesisStack))
        if ((not finishedExpression) and len(parenthesisStack) == 0):
            finishedExpression = True
            expressions.append(expression)
            expression = []
    expressionsAndOperators = [expressions, operators]
    return expressionsAndOperators

def determineNestedExpression(expression):
    nestedExpression = []
    parenthesisStack = []
    for symbol in expression:
        if (symbol == '('):
            parenthesisStack.append(1)
            if (len(parenthesisStack) == 1):
                continue
        elif (symbol == ')'):
            parenthesisStack.pop()
        if (len(parenthesisStack) > 0):
            nestedExpression.append(symbol)
    return nestedExpression

def convertToFunctionCalls(expression, color):
    global currentFunctionCalls
    global redFunctionCalls
    global blueFunctionCalls
    global greenFunctionCalls

    currentFunctionCalls = []
    if (color == 'r'):
        redFunctionCalls = []
        # do processing
        evaluateExpression(expression)
        redFunctionCalls = currentFunctionCalls
    elif (color == 'g'):
        greenFunctionCalls = []
        # do processing
        evaluateExpression(expression)
        greenFunctionCalls = currentFunctionCalls
    elif (color == 'b'):
        blueFunctionCalls = []
        # do processing
        evaluateExpression(expression)
        blueFunctionCalls = currentFunctionCalls

def evaluateFunctionCalls(functionCalls, params):
    # print("evalFromFunctionCalls() entry")
    expressionStack = [[]]
    currentExpression = []
    for symbol in functionCalls:
        # print("symbol: " + str(symbol))
        if (symbol == '('):
            expressionStack.append(currentExpression)
            # print("pushed " + str(currentExpression) + " to stack: " + str(expressionStack))
            currentExpression = []
        elif (symbol == ')'):
            currentExpression = expressionStack.pop()
            # print("popped " + str(currentExpression) + " from stack: " + str(expressionStack))
            # solve current expression
            value = solveExpression(currentExpression, params)
            expressionStack[-1].append(value)
            currentExpression = []
        else:
            expressionStack[-1].append(symbol)
            # print("pushing to top of stack: "+ str(expressionStack))
    # print("final expressionStack" + str(expressionStack))
    # print("evalFromFunctionCalls() exit")
    return expressionStack[0][0]

def solveExpression(expression, params):
    # print("solveExpression entry")
    # print("params = " + str(params))
    values = []
    for symbol in expression:
        if (symbol == 'x'):
            values.append(params[0])
        elif (symbol == 'y'):
            values.append(params[1])
        elif (symbol == 's'):
            values[len(values) - 1] = sinPiX(values[-1])
        elif (symbol == 'c'):
            values[len(values) - 1] = cosPiX(values[-1])
        elif (symbol == 't'):
            values[len(values) - 1] = tanPiX(values[-1])
        elif (symbol == 'l'):
            values[len(values) - 1] = lnX(values[-1])
        elif (symbol == '*'):
            firstValue = values.pop(0)
            values[0] = values[0] * firstValue
        else:
            values.append(symbol)
    # print("Values list: " + str(values))
    # print("solveExpression exit")
    return values[0]

def main():
    global redFunctionCalls
    global greenFunctionCalls
    global blueFunctionCalls

    random.seed()
    for it in range (0, 100):
        redExpression = buildExpression(0.925)
        greenExpression = buildExpression(0.925)
        blueExpression = buildExpression(0.925)
        print("Expressions: ")
        print("R:"+redExpression)
        print("G:"+greenExpression)
        print("B:"+blueExpression)

        convertToFunctionCalls(redExpression, 'r')
        convertToFunctionCalls(greenExpression, 'g')
        convertToFunctionCalls(blueExpression, 'b')
        print("Function Calls: ")
        print("R:"+str(redFunctionCalls))
        print("G:"+str(greenFunctionCalls))
        print("B:"+str(blueFunctionCalls))

        image = plotImage(redFunctionCalls, greenFunctionCalls, blueFunctionCalls, 150)
        image.save("test" + str(it) + ".png", "PNG")

if __name__ == "__main__":
    main()