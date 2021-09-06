def translate(value, leftMin, leftMax, rightMin, rightMax):
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    valueScaled = float(value - leftMin) / float(leftSpan)
    result = rightMin + (valueScaled * rightSpan)
    return result

def reversed_iterator(iter):
    return reversed(list(iter))
