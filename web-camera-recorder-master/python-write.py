PATH = '/home/pi/Desktop/gdrive/est.txt'

# opening a file in read mode
quote = 'test'

with open(PATH, 'w', encoding='utf-8') as f:
    f.write(quote)