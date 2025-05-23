USE [DIRDB]
GO

/****** Object:  Table [dbo].[FILEINFO]    Script Date: 2019/5/26 上午 03:45:27 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[FILEINFO](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[DIR_ID] [int] NOT NULL,
	[FULLNAME] [nvarchar](2048) NOT NULL,
	[FILE_NAME] [nvarchar](1024) NOT NULL,
	[FILE_EXT] [nchar](200) NOT NULL,
	[FILE_SIZE] [bigint] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO

