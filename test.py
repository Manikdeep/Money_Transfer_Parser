import os
lol = '101,365.00'
sum = [lol, 1]
try:
    print(int(lol))
except Exception:
    print("sum")

picture = "photo_251988@20-02-2022_16-25-00.txt"
realPicture = picture[0:-3] + "jpg"
print(realPicture)
color_file = "C:/Users/jonat/OneDrive/Documents/EBCS Research/TestPhotos/" + realPicture
os.remove(color_file)