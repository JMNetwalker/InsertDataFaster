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

  $newProducts =  New-Object -TypeName System.Data.DataTable("NewRows");
  $newProducts.Columns.Add("ID", [System.Type]::GetType("System.Int32")) | Out-Null;
  $newProducts.Columns.Add("Name1", [System.Type]::GetType("System.String")) | Out-Null;
  $newProducts.Columns.Add("Name2", [System.Type]::GetType("System.String")) | Out-Null;
  $newProducts.Columns.Add("Name3", [System.Type]::GetType("System.String")) | Out-Null;
  $newProducts.Columns.Add("Name4", [System.Type]::GetType("System.String")) | Out-Null;
  $newProducts.Columns.Add("Name5", [System.Type]::GetType("System.String")) | Out-Null;
  
  $connection = New-Object -TypeName System.Data.SqlClient.SqlConnection($connectionString)
  $connection.StatisticsEnabled = 1 
  $bFirstTime=$true
  $TotalTime=0
  for ($iConn=1; $iConn -lt $NumberConnections; $iConn++)
  {
   try
    {
     $command.Connection=$connection
     $connection.Open()
     $SqlBulkCopy = New-Object -TypeName System.Data.SqlClient.SqlBulkCopy($connection)
     $SqlBulkCopy.EnableStreaming = $false
     $SqlBulkCopy.DestinationTableName = "DummyInsert"
     $SqlBulkCopy.BatchSize = 1000000 
     $SqlBulkCopy.BulkCopyTimeout = 0 
     logMsg("////Database Connection:" +$iConn) (1)

     $data = $connection.RetrieveStatistics()
      logMsg("Connection Time   : " +$data.ConnectionTime)
      logMsg("NetworkServerTime : " +$data.NetworkServerTime)
      logMsg("Execution Time    : " +$data.ExecutionTime)
      logMsg("ServerRoundTrips  : " +$data.ServerRoundtrips)

     $connection.ResetStatistics()
     $lTimes=0
     $start = get-date
     $TotalTime=0
     for ($iQuery=1; $iQuery -lt $NumberConnections; $iQuery++) 
     {

       $row = $newProducts.NewRow()
       $row["ID"] = $iQuery
       $row["Name1"] = "XXXXXXXXXXXXXXXXXXXXXXXXXXX"
       $row["Name2"] = "XXXXXXXXXXXXXXXXXXXXXXXXXXX"
       $row["Name3"] = "XXXXXXXXXXXXXXXXXXXXXXXXXXX"
       $row["Name4"] = "XXXXXXXXXXXXXXXXXXXXXXXXXXX"
       $row["Name5"] = "XXXXXXXXXXXXXXXXXXXXXXXXXXX"
       $newProducts.Rows.Add($row)
       $lTimes++

       if($lTimes -eq 100)
       {

        $SqlBulkCopy.WriteToServer($newProducts)
        $newProducts.Clear()
        $lTimes=0
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
         $start = get-date
         $connection.ResetStatistics()
       }
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