import os
def main():
    path = "original/"
    for f in os.listdir(path):
        if os.path.isfile(path + f):
            if not f.endswith(" 0.png"):
                os.rename(
                    path + f,
                    os.path.splitext(path + f)[0] + " 0.png"
                )
            elif f.endswith(" 0.pn"):
                os.rename(
                    path + f,
                    os.path.splitext(path + f)[0] + "g"
                )
    for f in os.listdir(path):
        if os.path.isfile(path + f):
            if "glazed_terracotta" in f:
                os.rename(
                    path + f,
                    path + f[0:16] + f[16:-1]
                )

if __name__ == '__main__':
    main()
