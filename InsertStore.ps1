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

  $connectionString = "Server=$DatabaseServer;Initial Catalog=$Database;Persist Security Info=False;User ID=$Username;Password=$Password;MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;Packet Size=8192;Pooling=true;Application Name=Test-Insert"

  $connection = New-Object -TypeName System.Data.SqlClient.SqlConnection($connectionString)
  $connection.StatisticsEnabled = 1 
  $command = New-Object -TypeName System.Data.SqlClient.SqlCommand
  $command.CommandTimeout = 60
  $command.CommandType = [System.Data.CommandType]'Text'
  $command.Prepare();
  $command.CommandText = "INSERT INTO [DummyInsert] (ID,NAME1,NAME2,NAME3,NAME4,NAME5) VALUES(@id,@name1,@name2,@name3,@name4,@name5)"
  $command.Parameters.Add("@ID", [System.Data.SqlDbType]::Int) | Out-Null;
  $command.Parameters.Add("@Name1", [System.Data.SqlDbType]::VarChar, 200) | Out-Null;
  $command.Parameters.Add("@Name2", [System.Data.SqlDbType]::VarChar, 200) | Out-Null;
  $command.Parameters.Add("@Name3", [System.Data.SqlDbType]::VarChar, 200) | Out-Null;
  $command.Parameters.Add("@Name4", [System.Data.SqlDbType]::VarChar, 200) | Out-Null;
  $command.Parameters.Add("@Name5", [System.Data.SqlDbType]::VarChar, 200) | Out-Null;
  $bFirstTime=$true
  $TotalTime=0
  for ($iConn=0; $iConn -lt $NumberConnections; $iConn++)
  {
   try
    {
     $command.Connection=$connection
     $connection.Open()
     logMsg("////Database Connection:" +$iConn) (1)

     $data = $connection.RetrieveStatistics()
      logMsg("Connection Time   : " +$data.ConnectionTime)
      logMsg("NetworkServerTime : " +$data.NetworkServerTime)
      logMsg("Execution Time    : " +$data.ExecutionTime)
      logMsg("ServerRoundTrips  : " +$data.ServerRoundtrips)

     $connection.ResetStatistics()
     $TotalTime=0
     for ($iQuery=0; $iQuery -lt $NumberConnections; $iQuery++) 
     {
       $start = get-date
       $command.Parameters["@ID"].Value = $iQuery;
       $command.Parameters["@Name1"].Value = "XXXXXXXXXXXXXXXXXXXXXXXXXXX";
       $command.Parameters["@Name2"].Value = "XXXXXXXXXXXXXXXXXXXXXXXXXXX";
       $command.Parameters["@Name3"].Value = "XXXXXXXXXXXXXXXXXXXXXXXXXXX";
       $command.Parameters["@Name4"].Value = "XXXXXXXXXXXXXXXXXXXXXXXXXXX";
       $command.Parameters["@Name5"].Value = "XXXXXXXXXXXXXXXXXXXXXXXXXXX";
       $command.ExecuteNonQuery() | Out-Null 
       $end =get-date 
       $Diff = (New-TimeSpan -Start $start -End $end).TotalMilliseconds
       $data = $connection.RetrieveStatistics()
       $TotalTime=$TotalTime+$Diff
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