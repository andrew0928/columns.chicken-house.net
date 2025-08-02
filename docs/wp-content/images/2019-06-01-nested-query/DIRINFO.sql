USE [DIRDB]
GO

/****** Object:  Table [dbo].[DIRINFO]    Script Date: 2019/5/26 上午 03:45:12 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[DIRINFO](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[PARENT_ID] [int] NULL,
	[FULLNAME] [nvarchar](2048) NOT NULL,
	[NAME] [nvarchar](1024) NOT NULL,
	[LEFT_INDEX] [int] NULL,
	[RIGHT_INDEX] [int] NULL,
	[LEVEL_INDEX] [int] NULL,
	[PATH0] [nvarchar](255) NULL,
	[PATH1] [nvarchar](255) NULL,
	[PATH2] [nvarchar](255) NULL,
	[PATH3] [nvarchar](255) NULL,
	[PATH4] [nvarchar](255) NULL,
	[PATH5] [nvarchar](255) NULL,
	[PATH6] [nvarchar](255) NULL,
	[PATH7] [nvarchar](255) NULL,
	[PATH8] [nvarchar](255) NULL,
	[PATH9] [nvarchar](255) NULL,
	[PATH10] [nvarchar](255) NULL,
	[PATH11] [nvarchar](255) NULL,
	[PATH12] [nvarchar](255) NULL,
	[PATH13] [nvarchar](255) NULL,
	[PATH14] [nvarchar](255) NULL,
	[PATH15] [nvarchar](255) NULL,
	[PATH16] [nvarchar](255) NULL,
	[PATH17] [nvarchar](255) NULL,
	[PATH18] [nvarchar](255) NULL,
	[PATH19] [nvarchar](255) NULL,
	[PATH20] [nvarchar](255) NULL,
 CONSTRAINT [PK__tmp_ms_x__3214EC27E9827703] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO

