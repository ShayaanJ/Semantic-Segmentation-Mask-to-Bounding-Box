from ntpath import join


file = ""
with open("/home/shayaan/Downloads/temp.png", "rb") as f:
    file = f.read()
    print(file)
# string = ""
# for i in file:
#     string += i
# with open("temp.txt", "w") as f:
#     f.write(string)