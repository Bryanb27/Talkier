-- Criacao da tabela User
CREATE TABLE User (
    id INT PRIMARY KEY IDENTITY,
    username NVARCHAR(100) UNIQUE NOT NULL,
    email NVARCHAR(100) UNIQUE NOT NULL,
    password_hash VARBINARY(100) NOT NULL,
    isActive BIT NOT NULL DEFAULT 0,
);

-- Criacao da tabela Friendship
CREATE TABLE Friendship (
    user_id1 INT,
    user_id2 INT,
    status_inv NVARCHAR(50),
    created_at DATETIME,
    PRIMARY KEY (user_id1, user_id2),
    FOREIGN KEY (user_id1) REFERENCES [User](id),
    FOREIGN KEY (user_id2) REFERENCES [User](id)
);

-- Criacao da tabela Group
CREATE TABLE Group (
    id INT PRIMARY KEY IDENTITY,
    administer INT NOT NULL,
    groupName NVARCHAR(100) NOT NULL,
    details NVARCHAR(100) NOT NULL,
    join_code NVARCHAR(100) NOT NULL
);

-- Criacao da tabela Message
CREATE TABLE Message (
    id INT PRIMARY KEY IDENTITY,
    content NVARCHAR(255) NOT NULL,
    [timestamp] DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    group_id INT NOT NULL,
    FOREIGN KEY (group_id) REFERENCES [Group](id)
);

-- Criacao da tabela UserGroup
CREATE TABLE UserGroup (
    user_id INT,
    group_id INT,
    PRIMARY KEY (user_id, group_id),
    FOREIGN KEY (user_id) REFERENCES [User](id),
    FOREIGN KEY (group_id) REFERENCES [Group](id)
);