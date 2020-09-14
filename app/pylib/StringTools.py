def lastIndexOf(string, char):
    '''
    Finds the last index of a given character in a string.\n
    Parameters:\n
    :string (str): String to find index in.\n
    :char (str): Which character to look for.\n
    lastIndexOf(`string`, `char`) -> int(index)
    '''
    index = 0
    for i in range(len(string)):
            if string[i]==char:
                    index = i
    return index

def secondLastIndexOf(string, char):
    '''
    Finds the second last index of a given character in a string.\n
    Parameters:\n
    :string (str): String to find index in.\n
    :char (str): Which character to look for.\n
    secondLastIndexOf(`string`, `char`) -> int(index)
    '''
    index = 0
    index2 = 0
    for i in range(len(string)):
            if string[i]==char:
                    index2 = index
                    index = i
                    print("Index: " + str(index) + ", Index2: " + str(index2))
    return index2

def removeBetween(string, index0, index1):
    '''
    Slices a string and removes the content between the two indexes.\n
    Parameters:\n
    :string (str): String that is going to be sliced.\n
    :index0 (int): Beginning index.\n
    :index1 (int): Ending index.\n
    removeBetween(`string`, `index0`, `index1`) -> str(`string[0:index0]` + `string[index1:-1]`)
    '''
    snippet0 = string[0:index0]
    snippet1 = string[index1:-1]
    result = str(snippet0)+str(snippet1)
    return result

def getFileName(path):
    '''
    Finds the last index of a `/` or `\\` and then returns the filename.\n
    Parameters:\n
    :path (str): Path to the file.\n
    getFileName(`path`) -> str(filename)
    '''
    for i in range(len(path)-1, 0, -1):
        if path[i] == "/":
            return path[i+1:]
    for i in range(len(path)-1, 0, -1):
        if path[i] == "\\":
            return path[i+1:]

def getFileExt(path):
    '''
    Finds the file extension for the file and then returns the extension.\n
    Parameters:\n
    :path (str): Path to the file.\n
    getFileExt(`path`) -> str(ext)
    '''
    for i in range(len(path)-1, 0, -1):
        if path[i] == ".":
            return path[i:]

if __name__ == "__main__":
    url="http://ad.ionracing.no/contact/form/ION-WS0/"
    print(removeBetween(url, secondLastIndexOf(url, "/"), lastIndexOf(url, "/")))
    path = "/uploads/images/members/2020/sondre.aase.jpg"
    print(getFileName(path))
    print(getFileExt(path))