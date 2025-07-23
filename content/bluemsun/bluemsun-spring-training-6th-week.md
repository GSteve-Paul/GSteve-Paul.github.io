---
title: 蓝旭23春季培训-第6周预习
date: 2023-05-05
tags:
  - 蓝旭2023春季学习
---
# JDBC

## JDBC是什么

> JDBC 是一个用于在 Java 应用程序和数据库之间进行通信的 API,它提供了一系列接口,使得我们可以使用 Java 代码访问各种关系型数据库.

意思就是:官方定义了一系列的操作关系型数据库的接口,使其成为了一种规范,然后各大数据库厂商自己去做这些接口的实现,这些实现类被他们打包成了jar包.我们后端程序员就只需要去下载这些jar包然后去用他们就行了.

可以利用maven自动下载:
```xml
<dependencies>
    <!-- https://mvnrepository.com/artifact/mysql/mysql-connector-java -->
    <dependency>
        <groupId>mysql</groupId>
        <artifactId>mysql-connector-java</artifactId>
        <version>8.0.28</version>
    </dependency>
</dependencies>
```

JDBC结构图:

![20140612101655500.png](../data/bluemsun/bluemsun-spring-training-6th-week/c241ae7eba8e47549100bf050ff03145.image)

## 加载驱动

```java
Class.forName("com.mysql.jdbc.Driver");
```
这里利用的是Java的反射机制,动态加载驱动类.

## 创建连接

### 直接用uri,username和password

```java
//uri格式:"jdbc:mysql://host:port/database",后面可以跟上连接参数,例如指定字符集.  
String uri = "jdbc:mysql://localhost:3306/mydb02?useUnicode=true&characterEncoding=UTF-8"; 
//用户名  
String usn = "root";  
//密码  
String psw = "root";  
try {  
    Connection conn = DriverManager.getConnection(uri, usn, psw);  
} catch (SQLException ex) {  
    //登录账户错误或者uri无效  
}
```
通过获取`uri`,`username`和`password`获取`java.sql.Connection`对象.有了它就可以与数据库进行连接(会话).

### 读取资源文件以获取所需参数

因为数据库,用户名和密码不一定直接在程序中能得到,因此需要会读取资源文件.

#### 创建资源文件

![屏幕截图 2023-05-05 130753.png](../data/bluemsun/bluemsun-spring-training-6th-week/8ba8a7646943470db9f109d573c1d1be.image)

在main文件夹下与java文件夹同级的地方建立一个资源文件夹,里面新建资源文件db.properties,然后键入需要的各个属性.

#### 读取资源文件

```java
InputStream is = JDBCDemo.class.getResourceAsStream("/db.properties");  
Properties prop = new Properties();  
prop.load(is);
```
Properties对象依靠一个InputStream对象来读取资源.

#### 获取对应属性

如同Map一样,可以用键值对的形式获取各个属性:
```java
Connection conn = null;
//uri  
String uri = prop.getProperty("jdbc.uri");  
//用户名  
String usn = prop.getProperty("jdbc.username");  
//密码  
String psw = prop.getProperty("jdbc.password");  
conn = DriverManager.getConnection(uri, usn, psw);
```

## 处理SQL语句

### Statement

它表示用于执行静态SQL语句并返回它所生成结果的对象.它每次执行的时候都要被编译一次,因为它是静态的,也不能被指定参数.

```java
Statement stat = conn.createStatement();
stat.executeQuery("select * from student");
```

> `executeQuery()`方法通常用于查询语句,它会返回一个`ResultSet`对象,该对象包含了查询结果集中的所有数据.

> `executeUpdate()`方法通常用于更新语句,它会返回一个整数,表示受影响的行数.

### PreparedStatement

PreparedStatement 是 Statement 的一个子接口,表示一个预编译的 SQL 语句的对象.它和 Statement 的最大不同它的SQL语句被预编译过,可以通过多次传参的方式反复调用,其运行效率较高.也是因为如此,它可以防止被SQL注入攻击.

```java
Statement stat = conn.prepareStatement("SELECT * FROM course WHERE coursename = ?");  
stat.setString(1,"Java");
stat.executeQuery();
```

它使用`?`作为一个占位符,在下面用`setString()`方法来设置参数,对第几个问号传递什么参数,就在第一个参数中写几,然后第二个参数中填入字符串.

因此,他比传统的Statement硬来连接字符串更加清晰易懂.

### CallableStatement

CallableStatement 是 PreparedStatement 的子接口,它用于执行已经存储在数据库中的存储过程.

其基本语法如下:
```java
CallableStatement cstmt = con.prepareCall("{call procedure_name(?)}");
```
`procedure_name` 是要调用的存储过程的名称,问号表示存储过程的参数.可以使用 `setXXX` 方法为参数设置值,然后使用 `execute` 方法执行存储过程.

首先设定一个存储过程:
```sql
CREATE DEFINER=`root`@`localhost` PROCEDURE `proceduretest`(IN col VARCHAR(50))
BEGIN
    SET @cmd = CONCAT('SELECT ', col, ' FROM course');
    PREPARE stat FROM @cmd;
    EXECUTE stat;
    DEALLOCATE PREPARE stat;
END
```
这段代码的目的就是查询course表中的指定的列.

这里利用了动态SQL语句,首先用`CONCAT`构建一个sql命令,然后用`PREPARE`把这个字符串编译成一个语句对象stat,接着执行这个语句对象stat,最后利用`DEALLOCATE PREPARE`释放这个stat的资源.

然后编写如下Java代码:
```java
CallableStatement stat = conn.prepareCall("CALL proceduretest(?)");  
stat.setString(1,"name");
stat.executeQuery();
```
与PreparedStatement相似,他也使用问号作为占位符当做参数,然后利用setXXX来给定每一个参数.

## 获取结果

### excuteUpdate

Statement.excuteUpdate()这个方法会返回一个整数,表示受到了影响的行数.

对于这个表:
```text
+----+--------+---------------+------------+-----------+
| id | gender | name          | birthday   | sleeptime |
+----+--------+---------------+------------+-----------+
|  1 | male   | Li Jiangnan   | 1970-01-01 |       8.0 |
|  3 | female | Admin         | NULL       |       8.0 |
|  4 | female | Administrator | 1999-12-31 |       9.0 |
|  5 | male   | Admin         | NULL       |       8.0 |
+----+--------+---------------+------------+-----------+
4 rows in set (0.01 sec)
```
执行以下Java语句:
```java
Statement stat = null;  
int rs = -1;
stat = conn.createStatement();  
rs = stat.executeUpdate("UPDATE student SET birthday = '2000-01-01' WHERE birthday IS NULL");  
System.out.println(rs);
```
标准输出得到:
```
2
```

得到的新表是:
```text
+----+--------+---------------+------------+-----------+
| id | gender | name          | birthday   | sleeptime |
+----+--------+---------------+------------+-----------+
|  1 | male   | Li Jiangnan   | 1970-01-01 |       8.0 |
|  3 | female | Admin         | 2000-01-01 |       8.0 |
|  4 | female | Administrator | 1999-12-31 |       9.0 |
|  5 | male   | Admin         | 2000-01-01 |       8.0 |
+----+--------+---------------+------------+-----------+
4 rows in set (0.01 sec)
```
可以发现确实是有且仅有第二行,第四行有变化.

### excuteQuery

Statement.excuteQuery()的返回值是一个ResultSet.其中包含了满足条件的所有查询记录.

类似于Java中的容器,我们可以使用next()移动ResultSet的迭代器,进而逐行访问,当next()方法返回false时代表已经到达了末行.使用`getInt()`、`getString()`获取各个列的值.

当然了,也可以使用absolute(),relative()等方法移动迭代器

对于这个表:
```text
+----+--------+---------------+------------+-----------+
| id | gender | name          | birthday   | sleeptime |
+----+--------+---------------+------------+-----------+
|  1 | male   | Li Jiangnan   | 1970-01-01 |       8.0 |
|  3 | female | Admin         | 2000-01-01 |       8.0 |
|  4 | female | Administrator | 1999-12-31 |       9.0 |
|  5 | male   | Admin         | 2000-01-01 |       8.0 |
+----+--------+---------------+------------+-----------+
4 rows in set (0.01 sec)
```
执行以下Java语句:

```java
Connection conn = null;  
Statement stat = null;  
ResultSet rs = null;
conn = DriverManager.getConnection(uri, usn, psw);  
stat = conn.createStatement();  
rs = stat.executeQuery("SELECT * FROM student");  
while(rs.next()) {  
    int id = rs.getInt(1);  
    String name = rs.getString("name");  
    String gender = rs.getString(2);  
    Date birthday = rs.getDate("birthday");  
    float sleepTime = rs.getFloat("sleeptime");  
    String out = String.format("id=%4d name=%15s gender=%8s birthday=%10s sleeptime=%2.1f",  
        id,name,gender,birthday,sleepTime);  
    System.out.println(out);
}
```
标准输出得到:
```
id=   1 name=    Li Jiangnan gender=    male birthday=1970-01-01 sleeptime=8.0
id=   3 name=          Admin gender=  female birthday=2000-01-01 sleeptime=8.0
id=   4 name=  Administrator gender=  female birthday=1999-12-31 sleeptime=9.0
id=   5 name=          Admin gender=    male birthday=2000-01-01 sleeptime=8.0
```

需要注意的是:
- 如果某一记录中存在有NULL字段,那么对应字段的用getXXX()方法得到的返回值将会是null.
- getXXX()中按列的下标进行获取的方法中,下标从1开始.

## JDBC事务

使用事务可以将多个操作视为一个操作,可以在中途选择放弃,也可以最终提交.

一般而言由于连接默认是自动提交(输入一个语句就提交一次)而无法模拟事务,因此需要取消掉自动提交.
```java
//关闭自动提交
conn.setAutoCommit(false);
//提交
conn.commit();
//设置存档点
conn.setSavePoint();
//回滚
conn.rollback();
```

举个例子:
```java
public static void main(String[] args) throws SQLException {
    Connection conn = null;
    Statement stat1 = null;
    PreparedStatement stat2 = null;
    Savepoint p = null;
    try {
    
        //利用java的反射机制来动态加载Mysql的jdbc驱动
        
        Class.forName("com.mysql.cj.jdbc.Driver");
        
        //创建数据库连接
        
        InputStream is = JDBCDemo.class.getResourceAsStream("/db.properties");
        Properties prop = new Properties();
        prop.load(is);
        //uri
        String uri = prop.getProperty("jdbc.uri");
        //用户名
        String usn = prop.getProperty("jdbc.username");
        //密码
        String psw = prop.getProperty("jdbc.password");
        conn = DriverManager.getConnection(uri, usn, psw);
        
        //处理事务语句
        conn.setAutoCommit(false);

        p = conn.setSavepoint();
        //第一条语句
        stat1 = conn.createStatement();
        stat1.executeUpdate("UPDATE student SET birthday = '2004-03-31' WHERE name = 'Li Jiangnan'");

        p = conn.setSavepoint();
        //第二条语句
        stat2 = conn.prepareStatement("INSERT INTO student (gender, name, birthday, sleeptime) VALUES (?, ?, ?, ?)");
        stat2.setString(1,"female");
        stat2.setString(2,"t1");
        stat2.setString(3,"2003-05-05");
        stat2.setFloat(4,9.5f);
        stat2.executeUpdate();
        //提交
        conn.commit();

    } catch (SQLException | ClassNotFoundException | IOException ex1) {
        ex1.printStackTrace();
        //遇到有报错,就回滚
        if (conn != null) {
            conn.rollback(p);
        }
    } finally {
        if (stat1 != null) {
            stat1.close();
        }
        if (stat2 != null) {
            stat2.close();
        }
        if (conn != null) {
            conn.close();
        }
    }
}
```


## 关闭连接

与JAVA IO相同,在数据库访问完毕之后,应该关闭掉数据库.其顺序也有讲究:要先关闭ResultSet,然后关闭Statement,最后关闭Connection,否则会造成资源泄露.

以下给出一个较为完整的小型的数据库访问程序:

```java
public static void main(String[] args) throws SQLException {
    Connection conn = null;
    Statement stat = null;
    ResultSet rs = null;
    try {
        //利用java的反射机制来动态加载Mysql的jdbc驱动
        Class.forName("com.mysql.cj.jdbc.Driver");
        //创建连接
        //uri格式:"jdbc:mysql://host:port/database",后面可以跟上连接参数,例如指定字符集.
        String uri = "jdbc:mysql://localhost:3306/mydb02?useUnicode=true&characterEncoding=UTF-8";
        //用户名
        String usn = "root";
        //密码
        String psw = "root";
        conn = DriverManager.getConnection(uri, usn, psw);
        //处理语句
        stat = conn.createStatement();
        //获取结果
        rs = stat.executeQuery("SELECT * FROM student");
        while (rs.next()) {
            int id = rs.getInt(1);
            String name = rs.getString("name");
            String gender = rs.getString(2);
            Date birthday = rs.getDate("birthday");
            float sleepTime = rs.getFloat("sleeptime");
            String out = String.format("id=%4d name=%15s gender=%8s birthday=%10s sleeptime=%2.1f",
                    id, name, gender, birthday, sleepTime);
            System.out.println(out);
        }
    } catch (SQLException | ClassNotFoundException ex1) {
        ex1.printStackTrace();
    } finally {
        if (rs != null) {
            rs.close();
        }
        if (stat != null) {
            stat.close();
        }
        if (conn != null) {
            conn.close();
        }
    }
}
```