---
title: 蓝旭23春季培训-第5周预习
date: 2023-04-21
tags:
  - 蓝旭2023春季学习
---
# MySQL

## 数据库

### 定义

> 数据库是指一个存储数据的仓库,可以存储和管理大量的数据.数据库通常由一个或多个数据表组成,每个表都包含了一系列有关联的数据记录.数据库可以用于存储,管理和查询数据,常用于各种应用程序,网站和服务中.

而MySQL就是一种关系型数据库管理系统,它使用结构化查询语言(SQL)进行管理,具有很高的扩展性和可靠性.而我们就可以利用java中的JDBC API 来访问 MySQL.

### 结构

MySQL作为一种数据库管理系统,它可以管理多个数据库;而每个数据库中又是在用多个表为单位来存储数据;一个表类似于一个二维数组,每一行都是一个记录,每一列都是一个字段;一个字段相当于一个属性;而每个字段相当于其具体表现,类似于是表这个类的一个具体实例.

## SQL 基本语句

以下命令都是在Navicat的命令行界面进行实验的.

注意:
- SQL命令每输入完一个一定要末尾加分号.不然它以为你没输入完.
- 有时候会报错`MySQL server has gone away`,这时候重启一下连接就好了.
- SQL命令中的关键字是不区分大小写的

### 分类

1. 数据定义语言：简称DDL,用来定义数据库对象:数据库,表,列等.例如:`create`(创建数据库对象),`alter`(修改数据库表的字段),`drop`(删除数据库对象),`use`(选择当前会话要使用的数据库)等.

2. 数据操作语言：简称DML,用来对数据库中表的记录进行更新.例如:`insert`(向数据库表中插入记录),`delete`(删除记录),`update`(修改表中现有的记录)等.

3. 数据控制语言：简称DCL,用来控制数据库用户访问权限和数据完整性.例如:`grant`(给用户或用户组授予数据库或表的特定权限),`revoke`(撤销用户或用户组的权限),`commit`(提交数据库事务,并把已完成的更改保存到数据库中),`rollback`(撤销事务所做的所有更改,将数据库恢复到事务开始之前的状态)等.

4. 数据查询语言：简称DQL,用来查询数据库中表的记录.例如:`select`(从数据库中查询数据),`from`(指定一个或多个表),`where`(从表中选择符合某些条件的行)等.

### 操作数据库

1. 查看数据库: `SHOW databases;`执行后就会输出一个数据库的列表.

   ![](https://file.stevepaul.cc/9aa4508e0f234353bd29c638071e6fbf.png)

2. 创建数据库:`CREATE DATABASE database_name;`
3. 删除数据库:`DROP DATABASE database_name;`
4. 使用数据库：`USE database_name;`执行后当前会话就转到了这个数据库中


   ![](https://file.stevepaul.cc/f31ebbb7d9f344029e1ab2eb58682013.png)
   
### 操作数据库表

#### MySQL数据类型

在谈论MySQL建立数据库表的各种命令之前,应当先基本了解各种数据类型.
1.  整型(INT,TINYINT,SMALLINT,MEDIUMINT,BIGINT,BOOLEAN)
2.  浮点型(FLOAT,DOUBLE,DECIMAL)
3.  字符串型(CHAR,VARCHAR,TEXT,MEDIUMTEXT,LONGTEXT)
4.  日期型(DATE,TIME,DATETIME,TIMESTAMP)
5.  枚举型(ENUM)
6.  集合型(SET)
7.  二进制类型(BINARY,VARBINARY,BLOB)
8.  空间数据类型(POINT,LINESTRING,POLYGON,GEOMETRY,MULTIPOINT,MULTILINESTRING,
MULTIPOLYGON,GEOMETRYCOLLECTION)

特别的:
- 整型可以通过添加unsigned 关键字(例如int unsigned)来声明一个无符号整数.
- DECIMAL是一种以字符串形式存储的数字,可以通过`DECIMAL(M,D)`表示长度为M(包括小数点),精度为小数点后D为位.但它仍然有限制,只能表示$-10^{38}-1$~$10^{38}-1$的数字.
- var代表的是可变长度
- 关于日期型比较复杂 这里用图表示:

  ![](https://file.stevepaul.cc/7347af9202534ac8b017babdbfe2e20e.png)
-  枚举型enum其实是一种字符串型,作用是规定了某个字段的有效值的列表,也就是说,向里面插入的记录的值必须是枚举中的一种.并且其中枚举索引从1开始,如果索引为0,说明是个空字符串错误值.
-  set也是一个字符串对象,可以有零或多个值,其值来自表创建时规定的允许的一列值.但它的索引与enum的不同,它的每一种合法取值都事先被定义好了索引.
-  二进制类型binary和varbinary与char和varchar很相似,但是二进制类型里面装的是类似的字节字符串而非字符字符串.而BLOB与DECIMAL类似,是使用字符串维护的大型二进制.
-  空间数据类型其实是一堆几何图形罢了.

#### 创建数据库表

```sql
CREATE TABLE table_name (
    column1 datatype1,
    column2 datatype2,
    column3 datatype3,
    ...
);
```
column就是每一列的字段,后面就是这个字段对应的类型.

![](https://file.stevepaul.cc/73e2208bd0fd441686bcecad0a6fd915.png)

在这个student表中,有4个字段,分别是id,gender,name和birthday.

其中的id字段中有参数auto_increment表示自动递增,name字段有参数 charset utf8表示该字符串的字符集是UTF-8.

下面是一些常用的字段参数:

1. 数据类型和长度,前文中已有所叙述.
2. 默认值,用default关键字,例如`name varchar(60) default 'Zhang San'`
3. 不准为空,用not null 关键字修饰.
4. 主键,用primary,例如`primary key (id)`
5. 自动递增,用auto_increment修饰
6. 设置字符集,用charset,例如`name varchar(60) charset utf8`

#### 删除数据库表

```sql
DROP TABLE table_name;
```

![](https://file.stevepaul.cc/f07a7579b4044022b27aed9b4b6b8da6.png)

#### 修改数据库表

对于数据库表中字段和本身名字的修改操作,一般采取`alter`命令,其用法十分广泛:

##### 修改表名
```sql
ALTER TABLE table_name RENAME TO new_table_name;
```

![](https://file.stevepaul.cc/5790f90e46dc4f0583712df8ed143730.png)

##### 添加新列
```sql
ALTER TABLE table_name ADD COLUMN column_name data_type;
```

![](https://file.stevepaul.cc/f897e86f4b2d4733acfb52aaa25214a4.png)

关于添加的字段,比较类似于创建数据库表的形式,依然一样可以添加参数.

注意:如果想要该字段出现在第一列,可以在后面添加FIRST关键字,如果出现在中间,可以用AFTER + 它上一个字段.

##### 修改列名和数据类型
```sql
ALTER TABLE table_name CHANGE COLUMN old_column_name new_column_name new_data_type;
```

![](https://file.stevepaul.cc/997162e1c27b49f2b29412e5da8f8991.png)

对于修改的字段,一样的,比较类似于创建数据库表的形式,依然一样可以添加参数.

##### 删除列

```sql
ALTER TABLE table_name DROP COLUMN column_name;
```

![](https://file.stevepaul.cc/1c3de0e4e4cd4dd0b5c330370746290d.png)

##### 修改列的数据类型

```sql
ALTER TABLE table_name MODIFY COLUMN column_name new_data_type;
```

![](https://file.stevepaul.cc/d262e3bd2092488b8e9ed26aa4f32f7c.png)

这里先创建了一个字段sleeptime,然后再把这个int类型的字段改成了一个float(2,1)类型的.

#### 向数据库表中添加记录

```sql
INSERT INTO table_name (column1, column2, column3, ...) VALUES (value1, value2, value3, ...);
```

![](https://file.stevepaul.cc/2215d15cda20423c9145a189bba52191.png)

####  向数据库表中更新记录

```sql
UPDATE table_name SET column1 = value1, column2 = value2, ... WHERE condition;
```

![](https://file.stevepaul.cc/84ade5ca676f4c008568b63a2e4f1b46.png)

这里是通过只因哥的名字来更改对应的birthday.

注意:
- 设置多个字段,就必须用逗号隔开.
- 如果不加条件(where),则相当于改变所有记录的这些字段.

![](https://file.stevepaul.cc/2858a645ab9941a88aa341ea16b0ebff.png)

#### 向数据库表中删除记录

```sql
DELETE FROM table_name WHERE condition;
```
![](https://file.stevepaul.cc/77b290a889d847c09b97b70831304160.png)

这里通过id = 2的条件将坤坤删掉了.

注意:
- 如果不加条件,相当于删除表中所有记录.

#### 查询数据库表中的记录
```sql
SELECT column1, column2, ... 
FROM table_name 
WHERE condition;
```

![](https://file.stevepaul.cc/082a058f4f984d9b964f27f3b44d36ab.png)

注意:
- select后面要查询的字段可以用`*`表示所有字段.但是不能用于from.
- 如果没有条件,所有的记录都会被显示.

##### 字符串匹配

SQL中,利用like进行字符串匹配.  % 表示任意个数的字符, _ 表示任意的单个字符.

![](https://file.stevepaul.cc/9f048192d517428eabf2ec2d0e5c59ba.png)

##### 自动去重

```sql
SELECT DISTINCT column1, column2, ...
FROM table_name;
```

![](https://file.stevepaul.cc/b1a0c06b22ea4349be664d8121b4f921.png)

##### 分组

使用group by,可以对于某一个列的结果进行分组.其中select后面的字段要么是聚合函数,要么就必须在group by后被分组.

举个例子:
在这个表中:
```unk
+----+---------------+------------------+------+
| id | name          | coursename       | time |
+----+---------------+------------------+------+
|  1 | Li Jiangnan   | Java             |    8 |
|  2 | Li Jiangnan   | C++              |    5 |
|  3 | Li Jiangnan   | Maths            |    5 |
|  4 | Li Jiangnan   | Visual Basic.NET |    5 |
|  5 | Administrator | Algorithm        |    5 |
|  6 | Administrator | Java             |    8 |
+----+---------------+------------------+------+
```
执行以下命令:
```sql
select name from course group by name;
```
会出现:
```unk
+---------------+
| name          |
+---------------+
| Administrator |
| Li Jiangnan   |
+---------------+
```
还可以有其他的用法,例如使用聚合函数计算avg和sum.

![](https://file.stevepaul.cc/de1b2412d61544819a99adbd5d634c36.png)

##### 排序

使用order by可以对查询结果进行排序,后面指定排序的字段名.ASC表示升序,DESC表示降序

举个例子:
在这个表中:
```unk
+----+---------------+------------------+------+
| id | name          | coursename       | time |
+----+---------------+------------------+------+
|  1 | Li Jiangnan   | Java             |    8 |
|  2 | Li Jiangnan   | C++              |    5 |
|  3 | Li Jiangnan   | Maths            |    5 |
|  4 | Li Jiangnan   | Visual Basic.NET |    5 |
|  5 | Administrator | Algorithm        |    5 |
|  6 | Administrator | Java             |    8 |
+----+---------------+------------------+------+
```
执行以下命令:

```sql
select name,coursename from course order by time;
```
会出现:
```unk
+---------------+------------------+
| name          | coursename       |
+---------------+------------------+
| Li Jiangnan   | C++              |
| Li Jiangnan   | Maths            |
| Li Jiangnan   | Visual Basic.NET |
| Administrator | Algorithm        |
| Li Jiangnan   | Java             |
| Administrator | Java             |
+---------------+------------------+
```

它还可以和其他的连用:

![](https://file.stevepaul.cc/1eb36132b33443cd867f921cb7af44b7.png)

除此之外,还可以用`BETWEEN AND`进行范围查询,用`IS NULL`进行空值查询.

#### 查看数据库表结构

查看数据库表的结构其实就是查看各字段的属性.

##### 以表格形式

```sql
DESCRIBE table_name;
```

![](https://file.stevepaul.cc/62d958eebe594b83a43f2ff614906423.png)

##### 以sql语句形式

```sql
SHOW CREATE TABLE table_name;
```

![](https://file.stevepaul.cc/c4513bac1af44b0d9c5c58988a033423.png)

### SQL事务

> SQL事务是一组关联的SQL操作,它们被视为一个单独的工作单元,如果其中一个操作失败,则整个事务将被回滚并且不会被提交.

理解为SQL事务是一组有后悔药的命令.

要编写一个SQL事务,需要在开头写上`BEGIN TRANSACTION`,在操作完成后进行`COMMIT`操作,如果中途有错误,就可以使用`ROLLBACK`操作以回滚.

举个简单的例子:

原表:
```unk
+----+---------------+------------------+------+
| id | name          | coursename       | time |
+----+---------------+------------------+------+
|  1 | Li Jiangnan   | Java             |    8 |
|  2 | Li Jiangnan   | C++              |    5 |
|  3 | Li Jiangnan   | Maths            |    5 |
|  4 | Li Jiangnan   | Visual Basic.NET |    5 |
|  5 | Administrator | Algorithm        |    5 |
|  6 | Administrator | Java             |    8 |
|  7 | Alex          | Minecraft        |   10 |
|  8 | Steve         | Minecraft        |    5 |
+----+---------------+------------------+------+
```
执行以下命令:
```sql
start transaction;
update course set time = 4 where name = 'Steve';
insert into course (name) values ('Herobrine');
commit;
```
得出结果是:
```unk
+----+---------------+------------------+------+
| id | name          | coursename       | time |
+----+---------------+------------------+------+
|  1 | Li Jiangnan   | Java             |    8 |
|  2 | Li Jiangnan   | C++              |    5 |
|  3 | Li Jiangnan   | Maths            |    5 |
|  4 | Li Jiangnan   | Visual Basic.NET |    5 |
|  5 | Administrator | Algorithm        |    5 |
|  6 | Administrator | Java             |    8 |
|  7 | Alex          | Minecraft        |   10 |
|  8 | Steve         | Minecraft        |    4 |
|  9 | Herobrine     | NULL             |    5 |
+----+---------------+------------------+------+
```
注意:
1. 保存点:类似于一个存档点,如果后续操作有误,则只需要SL到这个保存点即可.,创建一个存档点只需要`SAVEPOINT savepoint_name;`,回滚到一个存档点可以`
ROLLBACK TO SAVEPOINT savepoint_name;`当然,如果在该保存点之后已经commit了,那么rollback是无效的.
2. 隔离级别:利用该语句来声明隔离级别`SET TRANSACTION ISOLATION LEVEL <isolation_level>`.隔离级别就是为了解决事务的并发执行会导致多个事务可能会访问到同一个数据,从而导致数据不一致的问题.有四种事务隔离级别:`Read Uncommitted`,`Read Committed`,`Repeatable Read`和`Serializable`.第一种指允许一个事务读取另一个事务未提交的数据;第二种指要求一个事务只能读取已经提交的数据;第三种指保证在同一个事务中多次读取同一数据时,读取的数据是一致的;第四种是最高的隔离级别,通过强制事务串行执行来避免幻读问题.

## 用户和用户权限

### 创建用户

```sql
CREATE USER 'username'@'host' IDENTIFIED BY 'password';
```

### 删除用户

```sql
DROP USER 'username'@'localhost';
```

### 授予权限

```sql
GRANT permission_type ON object_name TO user_or_role;
```
- permission_type指的是一些指令,例如SELECT,INSERT,ALTER,CREATE.
- object_name表示的是要授予权限的对象名称.
- uer_or_role表示要授予权限的用户或角色名称.

### 撤销权限

```sql
REVOKE permission_type ON object_name FROM user_or_role;
```
与GRANT互为逆命令,参数都是一个意思.

![](https://file.stevepaul.cc/4ad143e7e3144835bdb48cd166494b1f.png)

### 更改一个对象的所有者

```sql
ALTER AUTHORIZATION ON <object_type>::<object_name> TO <new_owner> [WITH NORESET, <other_options>];
```
- object_type指对象类型,
- 参数WITH NORESET表示不会重置对象权限.