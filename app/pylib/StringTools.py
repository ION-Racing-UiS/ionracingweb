def lastIndexOf(string, char):
    index = 0
    for i in range(len(string)):
            if string[i]==char:
                    index = i
    return index

def secondLastIndexOf(string, char):
    index = 0
    index2 = 0
    for i in range(len(string)):
            if string[i]==char:
                    index2 = index
                    index = i
                    print("Index: " + str(index) + ", Index2: " + str(index2))
    return index2

def removeBetween(string, index0, index1):
    snippet0 = string[0:index0]
    snippet1 = string[index1:-1]
    result = str(snippet0)+str(snippet1)
    return result

def getFileName(path):
    '''
    Finds the last index of a `/` or `\\` and the returns the filename.\n
    Arguments:\n
    :param path: Path to the file <type:str>
    '''
    for i in range(len(path)-1, 0, -1):
        if path[i] == "/":
            return path[i+1:]
    for i in range(len(path)-1, 0, -1):
        if path[i] == "\\":
            return path[i+1:]

if __name__ == "__main__":
    url="http://ad.ionracing.no/contact/form/ION-WS0/"
    print(removeBetween(url, secondLastIndexOf(url, "/"), lastIndexOf(url, "/")))
    path = "/uploads/images/cars/2016.jpg"
    print(getFileName(path))