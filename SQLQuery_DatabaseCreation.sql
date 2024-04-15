-- Criação da tabela User
CREATE TABLE [User] (
    id INT PRIMARY KEY IDENTITY,
    username NVARCHAR(100) UNIQUE NOT NULL,
    email NVARCHAR(100) UNIQUE NOT NULL,
    password_hash VARBINARY(100) NOT NULL
);

-- Criação da tabela Group
CREATE TABLE [Group] (
    id INT PRIMARY KEY IDENTITY,
    name NVARCHAR(100) NOT NULL,
    join_code NVARCHAR(100) NOT NULL
);

-- Criação da tabela Message
CREATE TABLE Message (
    id INT PRIMARY KEY IDENTITY,
    content NVARCHAR(255) NOT NULL,
    [timestamp] DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    group_id INT NOT NULL,
    FOREIGN KEY (group_id) REFERENCES [Group](id)
);

-- Criação da tabela UserGroup
CREATE TABLE UserGroup (
    user_id INT,
    group_id INT,
    PRIMARY KEY (user_id, group_id),
    FOREIGN KEY (user_id) REFERENCES [User](id),
    FOREIGN KEY (group_id) REFERENCES [Group](id)
);