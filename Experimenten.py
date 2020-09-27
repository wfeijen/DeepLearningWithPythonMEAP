a = [1] * 3
b = [4,5,6]
c = []
c.extend(a)
c.extend(b)
c[0] = 0
print(a)
