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

if __name__ == "__main__":
    url="http://ad.ionracing.no/contact/form/ION-WS0/"
    print(removeBetween(url, secondLastIndexOf(url, "/"), lastIndexOf(url, "/")))