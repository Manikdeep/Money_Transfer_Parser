x = 3
for i in range(10):
    try:
        print(x/i)
    except Exception as e:
        print("cant do this because: ", e)
        pass

print("finished loop")
