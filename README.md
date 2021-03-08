# InsertDataFaster
The main idea about these 3 PowerShell commands is to capture time and show an example how to insert the data in 3 different way and time taken. You could see bulkcopy process takes less time that other ones.

# Structure of DummyInsert table

CREATE TABLE [dbo].[DummyInsert](
	[ID] [int] NOT NULL,
	[NAME1] [varchar](200) NOT NULL,
	[NAME2] [varchar](200) NOT NULL,
	[NAME3] [varchar](200) NOT NULL,
	[NAME4] [varchar](200) NOT NULL,
	[NAME5] [varchar](200) NOT NULL
) ON [PRIMARY]
