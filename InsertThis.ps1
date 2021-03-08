$DatabaseServer = "yourserver"
$Database = "yourDBName"
$Username = "YourUserName"
$Password = "YourPassword" 
$NumberConnections =1000
$NumberExecutions=1000

function logMsg
{
    Param
    (
         [Parameter(Mandatory=$true, Position=0)]
         [string] $msg = "",
         [Parameter(Mandatory=$false, Position=2)] 
         [int] $InfoDate = 0

    )
  try
   {
    If($InfoDate -eq 0) { Write-Output $msg }
    else {Write-Output ((Get-Date -format "yyyy-MM-dd HH:mm:ss") + $msg) } 
   }
  catch
  {
    Write-Output $msg 
  }
}

cls

  $sw = [diagnostics.stopwatch]::StartNew()

  $connectionString = "Server=$DatabaseServer;Initial Catalog=$Database;Persist Security Info=False;User ID=$Username;Password=$Password;MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;Packet Size=8192;Pooling=True;Application Name=Test-Insert"

  $connection = New-Object -TypeName System.Data.SqlClient.SqlConnection($connectionString)
  $connection.StatisticsEnabled = 1 
  $command = New-Object -TypeName System.Data.SqlClient.SqlCommand
  $command.CommandTimeout = 60
  $command.CommandType = [System.Data.CommandType]'Text'
  $command.CommandText = "INSERT INTO [DummyInsert] (ID,NAME1,NAME2,NAME3,NAME4,NAME5) VALUES(1,REPLICATE('X',20),REPLICATE('X',20),REPLICATE('X',20),REPLICATE('X',20),REPLICATE('X',20))"
  $bFirstTime=$true
  $TotalTime=0
  for ($iConn=1; $iConn -le $NumberConnections; $iConn++)
  {
   try
    {
     $command.Connection=$connection
     $connection.Open()
     logMsg("////Database Connection:" +$iConn) (1)

     $data = $connection.RetrieveStatistics()
     $TotalTime=0
      logMsg("Connection Time   : " +$data.ConnectionTime)
      logMsg("NetworkServerTime : " +$data.NetworkServerTime)
      logMsg("Execution Time    : " +$data.ExecutionTime)
      logMsg("ServerRoundTrips  : " +$data.ServerRoundtrips)

     $connection.ResetStatistics()
     for ($iQuery=1; $iQuery -le $NumberConnections; $iQuery++) 
     {
       $start = get-date
       $command.ExecuteNonQuery() | Out-Null 
       $end = get-date 
       $Diff = (New-TimeSpan -Start $start -End $end).TotalMilliseconds
       $TotalTime=$TotalTime+$Diff
       $data = $connection.RetrieveStatistics()
       logMsg(" ------<New>-------") (1)
       logMsg("Iteration        : " +$iQuery + " / Conn: " + $iConn + " Time required: " +$Diff)
       logMsg("NetworkServerTime: " +$data.NetworkServerTime + " Execution Time: " +$data.ExecutionTime + " ServerRoundTrips: " +$data.ServerRoundtrips)
       logMsg("Average          : " +$TotalTime/($iQuery+1) + " of " + $TotalTime)

       If($bFirstTime -eq $true)
       {
         logMsg("BuffersReceived: " +$data.BuffersReceived)
         logMsg("SelectRows     : " +$data.SelectRows) 
         logMsg("SelectCount    : " +$data.SelectCount)
         logMsg("BytesSent      : " +$data.BytesSent)
         logMsg("BytesReceived  : " +$data.BytesReceived)
         $bFirstTime=$false
       }

       $connection.ResetStatistics()
      }
      $connection.Close()
     }
    catch
   {
    logMsg("Issue:" + $Error[0].Exception ) 
   }
   
}
logMsg("Time spent (ms) Procces :  " +$sw.elapsed) 
logMsg("Review: https://docs.microsoft.com/en-us/dotnet/framework/data/adonet/sql/provider-statistics-for-sql-server") 