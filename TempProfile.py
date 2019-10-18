import linecache
import detect_file

# folder = "/media/pi/"
# FILE_NAME = detect_file.File(folder)[0]


def readTempProfile(filename):
    lines = linecache.getlines(filename)
    flist = []
    timelist = []
    for line in lines:
        linestr = line.strip("\n")
        linestrlist = linestr.split(",")
        step = list(map(float, linestrlist))
        flist.append(step)
        time_step = list(map(eval, linestrlist))[0]
        timelist.append(time_step)
    return [flist, sum(timelist)]


if __name__ == '__main__':
    print(readTempProfile("D:\Temperature_profile.txt")[0])
