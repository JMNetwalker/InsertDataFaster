import pyodbc
import os
import datetime

SQL_server = 'tcp:servername.database.windows.net,1433'
SQL_database = 'dbname'
SQL_user = 'username'
SQL_password = 'password'

filepath = 'D:\\app\\PYTHON'
filelog = filepath + '\\Error_With_Bcp.log'

chunksize = 10000

def SaveResults( Message, bSaveFile):
    try:
        print(Message)

        if (bSaveFile==True):
            t = datetime.datetime.now()            
            file_object  = open(filelog, "a") 
            file_object.write(datetime.datetime.strftime(t, '%d/%m/%y %H:%M:%S') + '-' + Message + '\n' )
            file_object.close()
    except BaseException as e:
        print('And error occurred - ' , format(e))

def ExecuteSQLTruncate():
    try:
        SaveResults('Truncating the table',True)
        cnxn1 = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};SERVER=" + SQL_server + ";DATABASE=" + SQL_database + ";UID=" +SQL_user+';PWD='+ SQL_password, autocommit=False)
        cursor = cnxn1.cursor()
        cursor.execute("TRUNCATE TABLE [test_data]")     
        cursor.commit()                     
        cnxn1.close()
    except BaseException as e:
            SaveResults('Truncating - an error occurred - ' + format(e),True)

ExecuteSQLTruncate()

for directory, subdirectories, files in os.walk(filepath):
    for file in files:
      name, ext = os.path.splitext(file)
      if ext == '.csv': 
            SaveResults('Reading the file ' + name ,True)
            sCmdExecute = "bcp test_data in " + os.path.join(directory,file)
            sCmdExecute = sCmdExecute + " -c -t, -S " + SQL_server
            sCmdExecute = sCmdExecute + " -d " + SQL_database
            sCmdExecute = sCmdExecute + " -U " + SQL_user
            sCmdExecute = sCmdExecute + " -P " + SQL_password
            sCmdExecute = sCmdExecute + " -b " + str(chunksize)
            sCmdExecute = sCmdExecute + " -F 2" 
            SaveResults('Processed ' + sCmdExecute, True)            
            os.system(sCmdExecute)
            SaveResults('Processed ' + sCmdExecute, True)

