def get_all_py_path(root):
    results = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirpath = dirpath+'\\'
        for filename in filenames:
            if filename[0]!='.':
                filename = dirpath+filename
                if filename[len(filename)-3:len(filename)]=='.py' and filename[0]!='.':
                    results.append(filename)
    return results


def get_all_py_content(file_paths):
    codes = []
    for path in file_paths:
        f = open(path,'r+',errors='ignore')
        code = f.read()
        f.close()
        codes.append(code)
    return codes


