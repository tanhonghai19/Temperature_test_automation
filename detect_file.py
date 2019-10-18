import os

folder = "/media/pi/"
#folder = "E:\\"

def File(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".txt"):
                if "Temperature" in file:
                    file_paths = os.path.join(root, file)
                    #print ([file_paths, root])
                    return [file_paths, root]
                else:
                    pass


if __name__ == '__main__':
    fp =File(folder)[0]
    if os.path.exists(fp):
        print ("Setting file detected:", fp)
    else:
        print ("Setting file not found!")



