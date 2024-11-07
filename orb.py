###
# resolver implementation in python for the json based origins mod datapack defenition file format orb.
# copyright 2024 pin (https://pinmac.neocities.org)
# this is free software, as in freedom, to use, modify, rework the code as long as you give proper credit, don't claim the original as your own and warn the user if the code has been modified!
# this software is provided as is, with no warranty, use at one's own risk!
###
# version 241107a
###

try:
    import argparse
    import jstyleson as json
    import time
    import os
    import shutil
except ImportError as e:
    print("!some imports have failed!\nplease verify if you have to following libraries:")
    print("""   argparse
    jstyleson
    time
    os
    shutil""")
    exit(-1)
    
EPILOG = """resolver implementation in python for the json based origins mod datapack defenition file format orb. |
copyright 2024 pin (https://pinmac.neocities.org) |
this is free software, as in freedom, to use, modify, rework the code as long as you give proper credit, don't claim the original as your own and warn the user if the code has been modified! |
this software is provided as is, with no warranty, use at one's own risk! |
|
version 241106a
"""

argparser = argparse.ArgumentParser(prog="orb", description="resolver implementation in python for the json based origins mod datapack defenition file format orb.", epilog=EPILOG)
argparser.add_argument('filepath')
argparser.add_argument('workspace')
argparser.add_argument('-v', '--verbose', action="store_true")
arguments = argparser.parse_args()

class Statistics:
    files = 0
    folders = 0
    characters = 0
    clock_start = time.time()
    
    def getChars(self) -> int:
        return self.characters
    def getFilesFolders(self) -> int:
        return self.folders + self.files
    def getTime(self) -> float:
        return time.time() - self.clock_start
    
    def incrFile(self, int: int | None = 1) -> None:
        self.files = self.files + int
    def incrFolder(self, int: int | None = 1) -> None:
        self.folders = self.folders + int

def message(msg: str, end: str | None = '\n') -> None:
    """
print a message ending in a char if verbose mode is true
    """
    if arguments.verbose == True:
        print(msg, end=end)
        
def error(msg: str, end: str | None = '\n') -> None:
    """
print a message ending in a char and exits with code 1
    """
    print(msg, end=end)
    exit(1)
    
statistics_recorder = Statistics()
message("loading parameters\n")

# step 1: load stuff
try:
    ORBDEFFILE = json.loads(open(arguments.filepath, "r").read())
    statistics_recorder.incrFile()
    message("loaded orb file")
except Exception as e:
    error(f"{type(e).__name__}: {e}")
try:
    NAMESPACE = ORBDEFFILE["namespace"]
    message(f"defined namespace as {NAMESPACE}")
except KeyError as e:
    error(f"{type(e).__name__}: json key {e} not found!")
try:
    PACKFORMAT = ORBDEFFILE["format"]
    message(f"defined pack format as {PACKFORMAT}")
except KeyError as e:
    error(f"{type(e).__name__}: json key {e} not found!")
try:
    INDENT = ORBDEFFILE["indent"]
    message(f"defined indent level as {INDENT}")
except KeyError as e:
    error(f"{type(e).__name__}: json key {e} not found!")
try:
    DOPOWERLIST = ORBDEFFILE["do_powerlist"]
    message(f"should do powerlist/index.md: {DOPOWERLIST}")
except KeyError as e:
    DOPOWERLIST = False
WORKSPACEPATH = arguments.workspace
message(f"defined workspace path as {WORKSPACEPATH}")
message("\nloaded parameters\n")

message("creating files and folders\n")
# step 2: create stuff

INDEXFILE = ""

# step 2.1: create folders
try:
    os.chdir(WORKSPACEPATH)
    os.makedirs(NAMESPACE + "/data/" + NAMESPACE + "/origins")
    statistics_recorder.incrFolder(4)
    os.makedirs(NAMESPACE + "/data/" + NAMESPACE + "/powers")
    statistics_recorder.incrFolder()
    os.makedirs(NAMESPACE + "/data/origins/origin_layers")
    statistics_recorder.incrFolder(2)
    message(f"constructed folder structure, made {statistics_recorder.getFilesFolders()} folders.")
except Exception as e:
    error(f"{type(e).__name__}: {e}")
    
# step 2.2: create files
# pack.mcmeta
try:
    MCMETADICT = {
        "pack":{
            "description": ORBDEFFILE["description"],
            "pack_format": PACKFORMAT
        }
    }
    open(NAMESPACE + "/pack.mcmeta", "x").write(json.json.dumps(MCMETADICT, indent=INDENT))
    statistics_recorder.incrFile()
    message("constructed pack.mcmeta")
except Exception as e:
    error(f"{type(e).__name__}: {e}")
# origins and layer
ORIGINLIST = []
for current in ORBDEFFILE["origins"]:
    ID = current["id"]
    ORIGINLIST.append(NAMESPACE + ":" + ID)
    try:
        del current["id"]
        open(NAMESPACE + "/data/" + NAMESPACE + "/origins/" + ID + ".json", "x").write(json.json.dumps(current, indent=INDENT))
        statistics_recorder.incrFile()
        INDEXFILE = INDEXFILE + f"""# {current["name"]}
## Impact: {current["impact"]}
## {current["description"]}

"""
        message(f"constructed origin {NAMESPACE}:{ID}")
    except Exception as e:
        error(f"{type(e).__name__}: {e}")
try:
    LAYERDICT = {
        "replace": False,
        "origins": ORIGINLIST
    }
    open(NAMESPACE + "/data/origins/origin_layers/origin.json", "x").write(json.json.dumps(LAYERDICT, indent=INDENT))
    statistics_recorder.incrFile()
    message(f"constructed layer file containing {len(ORIGINLIST)} origins")
except Exception as e:
    error(f"{type(e).__name__}: {e}")
# powers
for current in ORBDEFFILE["powers"]:
    ID = current["id"]
    try:
        CATEGORY = current["category"] + "/"
    except KeyError:
        CATEGORY = ""
    try:
        del current["id"]
        try:
            del current["category"]
        except KeyError:
            pass
        try:
            os.makedirs(NAMESPACE + "/data/" + NAMESPACE + "/powers/" + CATEGORY)
        except FileExistsError:
            pass
        statistics_recorder.incrFolder()
        #                                                             "/"
        open(NAMESPACE + "/data/" + NAMESPACE + "/powers/" + CATEGORY + ID + ".json", "x").write(json.json.dumps(current, indent=INDENT))
        statistics_recorder.incrFile()
        INDEXFILE = INDEXFILE + f"""### {current["name"]}
{current["description"]}
"""
        message(f"constructed file {NAMESPACE}:{CATEGORY}{ID}")
    except Exception as e:
        error(f"{type(e).__name__}: {e}")
# tags
for current in ORBDEFFILE["tags"]:
    ID = current["id"]
    CATEGORY = current["category"] + "/"
    try:
        del current["id"]
        try:
            del current["category"]
        except KeyError:
            pass
        try:
            os.makedirs(NAMESPACE + "/data/" + NAMESPACE + "/tags/" + CATEGORY)
        except FileExistsError:
            pass
        statistics_recorder.incrFolder()
        #                                                             "/"
        open(NAMESPACE + "/data/" + NAMESPACE + "/tags/" + CATEGORY + ID + ".json", "x").write(json.json.dumps(current, indent=INDENT))
        statistics_recorder.incrFile()
        message(f"constructed file {NAMESPACE}:{CATEGORY}{ID}")
    except Exception as e:
        error(f"{type(e).__name__}: {e}")
# indexfile
try:
    if DOPOWERLIST != True:
        pass
    else:
        INDEXFILE = INDEXFILE + "\n\n-# made with: **orb** by pin"
        open(NAMESPACE + "/index.md", "x").write(INDEXFILE)
        statistics_recorder.incrFile()
except Exception as e:
    error(f"{type(e).__name__}: {e}")

message("\ncreated files and folders\n")

# 2.3: zip that mf!!
shutil.make_archive(NAMESPACE, "zip", NAMESPACE)
message("zipped folder tree\n")

message(f"job done in {statistics_recorder.getTime()} seconds. processed {statistics_recorder.getFilesFolders()} files and folders.")