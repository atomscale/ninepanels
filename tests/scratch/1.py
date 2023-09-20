from collections import deque

example = deque([], maxlen=3)

# example.pop(0)
example.append(1)
example.append(2)
example.append(3)
example.append(4)

if example:
    print(sum(example) / len(example))