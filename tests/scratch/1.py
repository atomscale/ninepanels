panels = [
    'cure',
    'destroy',
    'alleviate'
]

for i in range(1,10):
    try:
        print(panels[i - 1])
        if len(panels) == i:
            print("plus icon")
    except IndexError:

        print('blank dashed')
