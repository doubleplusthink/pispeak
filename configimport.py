#!project_pispeak/bin/python

configFile = open('config.conf','r')

for line in configFile.readlines():
    if 'token' in line.lower():
        token = line.split("=")[1].strip()
    elif 'logfile' in line.lower():
        pilogfile = line.split("=")[1].strip()
    elif 'audiodir' in line.lower():
        audiotopath = line.split("=")[1].strip()
    elif 'gttstempdir' in line.lower():
        audiofilepath = line.split("=")[1].strip()
    elif 'botname' in line.lower():
        botName = line.split("=")[1].strip()


def main():
    print('Token: ' + token)
    print('LogFile: ' + pilogfile)
    print('AudioDir: ' + audiotopath)
    print('GttsTempDir: ' + audiofilepath)

if __name__ == '__main__': 
    main()

