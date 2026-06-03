from tkinter import filedialog

def openFile(): #not finished - add try and except
    """
    allows the user upload a file
    :return: bytes of the file in hex, type of the file
    """
    filepath = filedialog.askopenfilename(initialdir="C:",
                                          title="Upload file")
    with open(filepath, "rb") as file:
        raw = file.read()
    type = filepath.split(".")[-1]
    print(raw.hex() is None)
    return  raw.hex(), type
#openFile()

def saveFile(data, type): #not finished - add try and except
    """
    allows the user download a file
    :param raw: bytes of the file (as hex)
    :param type: the type of the file
    :return:
    """
    raw = bytes.fromhex(data)
    file_path = filedialog.asksaveasfilename(initialdir="C:",  #gets path
                                    filetypes=[("Text file",".txt"),("All files", ".*"), ])
    print(file_path)
    if file_path is None:
        return
    if not file_path.endswith(f".{type}"):#adds the required type
        file_path += f".{type}"
    with open(file_path, "wb") as file:
        file.write(raw)



#with open("pic.jpg", "rb") as file:
 #   print(saveFile(file.read(),'jpg'))
