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

def getFileName(path=""):
    '''
    Finds the last index of a `/` or `\\` and then returns the filename.\n
    Parameters:\n
    :path (str): Path to the file.\n
    getFileName(`path`) -> str(filename)
    '''
    if type(path) is None or path is None:
        return ""
    if path == "":
        return ""
    for i in range(len(path)-1, 0, -1):
        if path[i] == "/":
            return path[i+1:]
    for i in range(len(path)-1, 0, -1):
        if path[i] == "\\":
            return path[i+1:]
    return path

def getFileExt(path):
    '''
    Finds the file extension for the file and then returns the extension.\n
    Parameters:\n
    :path (str): Path to the file.\n
    getFileExt(`path`) -> str(ext)
    '''
    if type(path) is None:
        return ""
    for i in range(len(path)-1, 0, -1):
        if path[i] == ".":
            return path[i:]
    return ""

def getTableFields(cursor=None, table=""):
    '''
    Uses a MySQL DB `cursor` to query for field names for a specific table.
    Parameters:\n
    :cursor (MySQLCursor): Cursor object for MySQL DB.\n
    :table (str): Name of the table you want to find the field names for.\n
    getTableFields(`cursor`, `table`) -> {int: str}
    '''
    if not cursor or table == "":
        return {}
    q = "SHOW COLUMNS FROM %s" % table
    cursor.execute(q)
    res = cursor.fetchall()
    r = {}
    for i in range(len(res)):
        r[i] = res[i][0]
    return r

def getSingleResult(fetchedone=(), cursor=None, table=""):
    '''
    Constructs a dict from a single result from DB i.e. `cursor.fetchone()` and 
    return it with keys from the column names.\n
    Parameters:\n
    :fetchedone (tuple): `fetchone()` from cursor which will be a tuple.\n
    :cursor (MySQLCursor): Cursor object for MySQL DB.\n
    :table (str): Name of the table you want to find the field names for.\n
    getSingleResult(`fetchedone`, `cursor`, `table`) -> {str(column_name): str(value)}
    '''
    if fetchedone == () or cursor == None or table == "":
        return {}
    r = {}
    for k, v in getTableFields(cursor=cursor, table=table).items():
        r[v] = fetchedone[k]
    return r

def getMultipleResults(fetchedall=[], cursor=None, table=""):
    '''
    Constructs a dict from multiple results from DB i.e. `cursor.fetchall()` and
    returns it as a dict with the keys \"fields\" - column names and \"values\" - 
    a dict with the column names as key for their values.\n
    Parameters:\n
    :fetchedall (list[()]): result from `cursor.fetchall()` which is a list of N-tuples.\n
    :cursor (MySQLCursor): Cursor object for MySQL DB.\n
    :table (str): Name of the table you want to find the field names for.\n
    getMultipleResults(`fetchedall`, `cursor`, `table`) -> {"fields": str, "values": {str(`self["fields"][i]`): str}}
    '''
    if fetchedall == [] or cursor == None or table == "":
        return []
    r = {}
    table_fields = getTableFields(cursor=cursor, table=table)
    r["fields"] = table_fields.values()
    if fetchedall == []:
        return r
    r["values"] = {}
    for row in fetchedall:
        r["values"] = {} 
        for k, v in table_fields.items():
            r["values"][v] = row[k]
    return r

def decodeJSONAndSplit(string="", separator=","):
    '''
    Load a JSON string with separated values.\n
    Parameters:\n
    :string (Bytes|str): JSON data to decode and split.\n
    :separator (str): Value separator.\n
    decodeJSONAndSplit(`string`, `separator`) -> list[str]
    '''
    data = string.decode("utf-8", "strict").replace("%2C", ",").replace("%20", " ")
    data = data.split("=")[-1].split(",")
    if data[-1] == "":
        return data[0:-1]
    else:
        return data

if __name__ == "__main__":
    url="http://ad.ionracing.no/contact/form/ION-WS0/"
    print(removeBetween(url, secondLastIndexOf(url, "/"), lastIndexOf(url, "/")))
    path = "/uploads/images/members/2020/sondre.aase.jpg"
    print(getFileName(path))
    print(getFileExt(path))