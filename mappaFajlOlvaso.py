import os

def list_files(folder_path):
    return [os.path.join(folder_path, f).replace(os.sep, '/') for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))]
    
print(list_files("./apexFajlok"))