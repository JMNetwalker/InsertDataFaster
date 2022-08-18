import csv
import pyodbc
import threading
import os
import datetime 

class ThreadsOrder: #Class to run in parallel the process.
    def ExecuteSQL(self,a,s,n):
        TExecutor = threading.Thread(target=ExecuteSQL,args=(a,s,n,))
        TExecutor.start()

def SaveResults( Message, bSaveFile): #Save the details of the file.
    try:
        print(Message)

        if (bSaveFile==True):
            file_object  = open(filelog, "a") 
            file_object.write(datetime.datetime.strftime(datetime.datetime.now(), '%d/%m/%y %H:%M:%S') + '-' + Message + '\n' )
            file_object.close()
    except BaseException as e:
        print('And error occurred - ' , format(e))


def ExecuteSQLcc(sTableName):
    try:
        cnxn1 = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};APP=Bulk Insert Test;SERVER=" + SQL_server + ";DATABASE=" + SQL_database + ";UID=" +SQL_user+';PWD='+ SQL_password, autocommit=False, Timeout=3600)
        cursor = cnxn1.cursor()
        cursor.execute("DROP TABLE IF EXISTS" + sTableName )
        cursor.commit()
        cursor.execute("CREATE TABLE " + sTableName + " (" \
                            "	[Key] [int] NOT NULL," \
                            "	[Num_TEST] [int] NULL," \
                            "	[TEST_01] [varchar](6) NULL," \
                            "	[TEST_02] [varchar](6) NULL," \
                            "	[TEST_03] [varchar](6) NULL," \
                            "	[TEST_04] [varchar](6) NULL," \
                            "	[TEST_05] [varchar](6) NULL," \
                            "	[TEST_06] [varchar](6) NULL," \
                            "	[TEST_07] [varchar](6) NULL," \
                            "	[TEST_08] [varchar](6) NULL," \
                            "	[TEST_09] [varchar](6) NULL," \
                            "	[TEST_10] [varchar](6) NULL," \
                            "	[TEST_11] [varchar](6) NULL," \
                            "	[TEST_12] [varchar](6) NULL," \
                            "	[TEST_13] [varchar](6) NULL," \
                            "	[TEST_14] [varchar](6) NULL," \
                            "	[TEST_15] [varchar](6) NULL," \
                            "	[TEST_16] [varchar](6) NULL," \
                            "	[TEST_17] [varchar](6) NULL," \
                            "	[TEST_18] [varchar](6) NULL," \
                            "	[TEST_19] [varchar](6) NULL," \
                            "	[TEST_20] [varchar](6) NULL)")
        cursor.commit()
        cursor.execute("CREATE CLUSTERED INDEX [ix_ms_example] ON " + sTableName + " ([Key] ASC) WITH (STATISTICS_NORECOMPUTE = OFF, DROP_EXISTING = OFF, ONLINE = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = ON) ON [PRIMARY]")
        cursor.commit()
    except BaseException as e:
            SaveResults('Executing SQL - an error occurred - ' + format(e),True)


def ExecuteSQL(a,sTableName,n):
    try:
        Before = datetime.datetime.now()   
        
        if n==-1:
            sTypeProcess = "NoAsync"
        else:
            sTypeProcess="Async - Thread:" + str(n) 
        SaveResults('Executing at ' + str(Before) + " Process Type: " + sTypeProcess, True )      
        cnxn1 = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};APP=Bulk Insert Test;SERVER=" + SQL_server + ";DATABASE=" + SQL_database + ";UID=" +SQL_user+';PWD='+ SQL_password, autocommit=False, Timeout=3600)

        cursor = cnxn1.cursor()
        cursor.fast_executemany = True
        cursor.executemany("SET NOCOUNT ON;INSERT INTO " + sTableName +" ([Key], Num_TEST, TEST_01, TEST_02, TEST_03, TEST_04, TEST_05, TEST_06, TEST_07, TEST_08, TEST_09, TEST_10, TEST_11, TEST_12, TEST_13, TEST_14, TEST_15, TEST_16, TEST_17, TEST_18, TEST_19, TEST_20) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",a)                          
        cursor.commit()
        SaveResults('Time Difference INSERT process ' + str(datetime.datetime.now() - Before) + " " + sTypeProcess, True )  

    except BaseException as e:
            SaveResults('Executing SQL - an error occurred - ' + format(e),True)


#Connectivity details.
SQL_server = 'tcp:servername.database.windows.net,1433'
SQL_database = 'databasename'
SQL_user = 'username'
SQL_password = 'Password'


#file details to read 
filepath = 'c:\\k\\' ##To Read the demo file
filelog = filepath + '\\Error.log' #Save the log.

chunksize = 10000 #Transaction batch rows.
sTableName = "[test_data]" #Table Name (dummy)

pThreadOrder = ThreadsOrder()
nThread = 0 #Number of Threads -- Right now, we provided an unlimited threads.

ExecuteSQLcc(sTableName)

Before = datetime.datetime.now()  
line_count = 0         
for directory, subdirectories, files in os.walk(filepath):
    for file in files:
      name, ext = os.path.splitext(file)
      if ext == '.csv': 
            a=[]
            SaveResults('Reading the file ' + name ,True)
            BeforeFile= datetime.datetime.now()             
            with open(os.path.join(directory,file), mode='r') as csv_file:
              csv_reader = csv.reader(csv_file, delimiter=',')
              for row in csv_reader:
                    line_count+= 1  
                    if line_count>1:    
                        a.append(row)

                    if (line_count%chunksize)==0:
                        deltaFile = datetime.datetime.now() - BeforeFile
                        nThread=nThread+1                        
                        SaveResults('Time Difference Reading file is ' + str(deltaFile) + ' for ' + str(line_count) + ' rows', True )                        
                        pThreadOrder.ExecuteSQL(a,sTableName,nThread) #Open a new theard per transaction batch size.
                        #ExecuteSQL(a,sTableName,-1)   
                        a=[]
            BeforeFile= datetime.datetime.now() 

SaveResults('Total Time Difference Reading file is ' + str(datetime.datetime.now() - Before) + ' for ' + str(line_count) + ' rows for the file: ' + name , True )  

