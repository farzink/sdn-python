import sqlite3
from sqlite3 import Error
import os
import variables as settings



#c = connection.cursor()
#c.execute('''CREATE TABLE stocks (date text, trans text, symbol text, qty real, price real)''')

global connection

def prepareConnection():
    global connection
    connection = connect(settings.tcsDbPath + settings.tcsDbName)




def connect(dbname):
    try:
        if os.path.isfile(dbname):            
            connection = sqlite3.connect(dbname)
            return connection
        else:
            print("file does not exist")
    except Error as ex:        
        print(ex)
    return None



def getFilesInDirectory(directory):
    for file in os.listdir(directory):        
        print(file)
    #if filename.endswith(".asm") or filename.endswith(".py"): 
        # print(os.path.join(directory, filename))
     #   continue
    #else:
     #   continue


def getTableNames():    
    global connection
    cur = connection.cursor().execute("SELECT Name FROM sqlite_master WHERE type='table'");    
    return cur.fetchall()

def getTablesCount():
    global connection    
    cur = connection.cursor().execute("SELECT Name FROM sqlite_master WHERE type='table'");    
    return len(cur.fetchall())
    
def getTableRows(tableName):    
    global connection
    query = "SELECT * FROM " + tableName
    #print(query)
    cur = connection.cursor().execute(query)
    rows = []
    for row in cur.fetchall():
        rows.append(row[1].split("=")[1])
    return rows


#print(settings.tcsDbPath + settings.tcsDbName)
#connection = connect(settings.tcsDbPath + settings.tcsDbName)
#rows = getTableNames(connection)
# for row in rows:
#     if str(row).find("PEER") != -1:
#         print(row)




# for i in range(len(rows)):
#     values =getTableRows(connection, str(rows[i][0]))
#     for value in values:     
#      print(value[1])
#     print("------------------------------")
        