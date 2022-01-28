"""def cleanNumber(num):
    cleanNum = ""
    for i in range(len(num)):
        if num[i] == '.' and i != len(num) - 3:
            continue
        elif num[i] == ',':
            continue
        else:
            cleanNum += num[i]
    return cleanNum

print(cleanNumber("9,12.2.98"))"""

colors = {}
colors["photo1"] = [.09999]
#colors["photo1"].append[]
test = [1,('r',3),('b',5),6]

#file = "C:/Users/jonat/OneDrive/Documents/money-transfer-sample-images\photo_3055@28-12-2021_07-36-43.jpg"
file = "C:/Users/jonat/OneDrive/Documents/money-transfer-sample-images - Copy\photo_2590@18-12-2021_23-52-16.jpg"
print(file[-34:-4])