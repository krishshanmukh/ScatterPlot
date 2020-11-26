def findClosestPoints(a, B):

    x, y, minimum = -1, -1, float("+inf")
    # print(a, B)
    for pt in B:
        if abs(a[0] - pt[0]) < minimum and abs(a[0] - pt[0]) < 10:
            minimum = abs(a[0] - pt[0])
            x, y = pt
    # print(x, y, (x, y) in B)
    
    if y != -1:
        B.remove((x, y))

    return y


