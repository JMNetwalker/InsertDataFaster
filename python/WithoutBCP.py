import csv
import pyodbc
import threading
import os
import datetime

SQL_server = 'tcp:servername.database.windows.net,1433'
SQL_database = 'databasename'
SQL_user = 'username'
SQL_password = 'password'

filepath = 'D:\\app\\PYTHON'
filelog = filepath + '\\Error.log'

chunksize = 10000

class ThreadsOrder:
    Threads = []

    def Clean(self,NumberThreads):
        for t in range(0,NumberThreads):
            self.Threads.append(0)            
            
    def Available(self):
        slot=-1
        for t in self.Threads:
            slot+= 1
            if( t == 0 ):
                self.ChangeStatus(slot,1)
                return slot
        return -1      

    def ExecuteSQL(self,n,a):
        TExecutor = threading.Thread(target=ExecuteSQLcc,args=(a,n,))
        TExecutor.name = "Process - " + str(n)
        TExecutor.start()
         
    def ChangeStatus(self,n,value):
        threading.Lock()
        SaveResults('Thread ' + str(n) + ' changed to ' + str(value),False)                              
        self.Threads[n]=value

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


def ExecuteSQLcc(a,n):
    try:
        pThreadOrder.ChangeStatus(n,-2)
        sTableName = "[#test_data_" + str(n) + "]"
        cnxn1 = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};SERVER=" + SQL_server + ";DATABASE=" + SQL_database + ";UID=" +SQL_user+';PWD='+ SQL_password, autocommit=False)
        cursor = cnxn1.cursor()
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
        cursor.fast_executemany = True
        cursor.executemany("INSERT INTO " + sTableName +" WITH (TABLOCK) ([Key], Num_TEST, TEST_01, TEST_02, TEST_03, TEST_04, TEST_05, TEST_06, TEST_07, TEST_08, TEST_09, TEST_10, TEST_11, TEST_12, TEST_13, TEST_14, TEST_15, TEST_16, TEST_17, TEST_18, TEST_19, TEST_20) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",a)                          
        cursor.commit()
        cursor.fast_executemany = False        
        cursor.execute("INSERT INTO [dbo].[test_data] SELECT * FROM " + sTableName + ' WITH (TABLOCK)')
        cursor.commit()
        cnxn1.close()
    except BaseException as e:
            SaveResults('Executing SQL - an error occurred - ' + format(e),True)
    finally:
        pThreadOrder.ChangeStatus(n,0)


def ExecuteSQLLimpia():
    try:
        SaveResults('Truncating the table',True)
        cnxn1 = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};SERVER=" + SQL_server + ";DATABASE=" + SQL_database + ";UID=" +SQL_user+';PWD='+ SQL_password, autocommit=False)
        cursor = cnxn1.cursor()
        cursor.execute("TRUNCATE TABLE [test_data]")     
        cursor.commit()                     
        cnxn1.close()
    except BaseException as e:
            SaveResults('Truncating - an error occurred - ' + format(e),True)



pThreadOrder = ThreadsOrder()
pThreadOrder.Clean(100)
ExecuteSQLLimpia()
nThread=0
line_total = 0

for directory, subdirectories, files in os.walk(filepath):
    for file in files:
      name, ext = os.path.splitext(file)
      if ext == '.csv': 
            a=[]
            line_count = 0
            SaveResults('Reading the file ' + name ,True)
            with open(os.path.join(directory,file), mode='r') as csv_file:
              csv_reader = csv.reader(csv_file, delimiter=',')
              for row in csv_reader:
                    line_count+= 1  
                    line_total+=1
                    if line_count>1:    
                        a.append(row)

                    if (line_count%chunksize)==0:
                        nThread = pThreadOrder.Available()
                        while(nThread==-1):
                            nThread = pThreadOrder.Available()
                            print('Waiting for available Thread ' + str(line_total))

                        SaveResults('Review Thread ' + str(nThread) + ' process rows ' + str(line_count),True)                              
                        pThreadOrder.ExecuteSQL(nThread,a)               
                        a=[]
              if(a.count!=0):
                 pThreadOrder.ExecuteSQL(nThread,a)                       
              SaveResults('Processed ' + str(line_count) + ' lines for the file ' + name, True)

