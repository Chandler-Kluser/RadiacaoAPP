from os import path

name_conf_file = 'Preferences.conf'

opts = ["showMessage","ola"]
opts_def = [False,False]

def CheckConfFile():
    ThereIsFile = path.isfile(name_conf_file)

    if (not ThereIsFile):
        # builds a sample file and saves it in cwd
        pref=open(name_conf_file,'w')
        print("Preferences.conf not found. Building a sample...")
        pref.write("# Default Configuration\n")
        for i in opts:
            pref.write(str(i)+" = "+str(opts_def[opts.index(i)])+"\n")
        pref.close()
    else:
        # reads the user defined options
        print("Preferences.conf found! Reading configurations...")
        with open(name_conf_file) as mytxt:
            for line in mytxt:
                for opt in opts:
                    if (opt in line) and ("=" in line):
                        if ("True" in line) or ("true" in line):
                            opts_def[opts.index(opt)] = True
                            print("Set "+opt+" to True")
                        elif ("False" in line) or ("false" in line):
                            opts_def[opts.index(opt)] = False
                            print("Set "+opt+" to False")