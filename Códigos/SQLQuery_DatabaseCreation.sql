-- Criacao da tabela User
CREATE TABLE [User] (
    id INT PRIMARY KEY IDENTITY,
    username NVARCHAR(21) UNIQUE NOT NULL,
    email NVARCHAR(40) UNIQUE NOT NULL,
    password_hash VARBINARY(100) NOT NULL,
    isActive BIT NOT NULL DEFAULT 0
);

-- Criacao da tabela Friendship
CREATE TABLE Friendship (
    user_id1 INT,
    user_id2 INT,
    status_inv NVARCHAR(10),
    created_at DATETIME,
    PRIMARY KEY (user_id1, user_id2),
    FOREIGN KEY (user_id1) REFERENCES [User](id),
    FOREIGN KEY (user_id2) REFERENCES [User](id)
);

-- Criacao da tabela Group
CREATE TABLE [Group] (
    id INT PRIMARY KEY IDENTITY,
    administer INT NOT NULL,
    groupName NVARCHAR(50) NOT NULL,
    details NVARCHAR(30) NOT NULL,
    join_code NVARCHAR(10) NOT NULL,
    p_limit INT NOT NULL,
    active_users INT DEFAULT 0
);

-- Criacao da tabela Message
CREATE TABLE Message (
    id INT PRIMARY KEY IDENTITY,
    content NVARCHAR(110) NOT NULL,
    [timestamp] DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    group_id INT NOT NULL,
    sender_id INT NOT NULL,
    sender_name NVARCHAR(21) NOT NULL,
    FOREIGN KEY (group_id) REFERENCES [Group](id),
    FOREIGN KEY (sender_id) REFERENCES [User](id),
    FOREIGN KEY (sender_name) REFERENCES [User](username)
);

-- Criacao da tabela UserGroup
CREATE TABLE UserGroup (
    user_id INT,
    group_id INT,
    PRIMARY KEY (user_id, group_id),
    FOREIGN KEY (user_id) REFERENCES [User](id),
    FOREIGN KEY (group_id) REFERENCES [Group](id)
);