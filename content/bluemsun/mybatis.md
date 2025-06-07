---
title: MyBatis学习入门
date: 2023-09-12
tags:
  - 蓝旭2023秋季学习
---
# 概念

-    MyBatis 是一款优秀的持久层框架

-   它支持自定义 SQL、存储过程以及高级映射。

-   MyBatis 免除了几乎所有的 JDBC 代码以及设置参数和获取结果集的工作。

-   MyBatis 可以通过简单的 XML 或注解来配置和映射原始类型、接口和 Java POJO（Plain Old Java Objects，普通老式 Java 对象）为数据库中的记录。

# 入门使用

## 添加Maven依赖

```xml
<dependency>
    <groupId>org.mybatis</groupId>
    <artifactId>mybatis</artifactId>
    <version>3.5.13</version>
</dependency>
<dependency>
    <groupId>org.slf4j</groupId>
    <artifactId>slf4j-api</artifactId>
    <version>2.0.5</version>
</dependency>
<dependency>
    <groupId>ch.qos.logback</groupId>
    <artifactId>logback-classic</artifactId>
    <version>1.4.7</version>
</dependency>
<dependency>
    <groupId>ch.qos.logback</groupId>
    <artifactId>logback-core</artifactId>
    <version>1.4.7</version>
</dependency>
<dependency>
    <groupId>mysql</groupId>
    <artifactId>mysql-connector-java</artifactId>
    <version>8.0.28</version>
</dependency>
```
## 添加Mybatis配置文件

在resources文件夹下创建一个文件名叫`mybatis-config.xml`，用于编写配置信息。

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE configuration
        PUBLIC "-//mybatis.org//DTD Config 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-config.dtd">
<configuration>
    <environments default="development">
        <environment id="development">
            <transactionManager type="JDBC"/>
            <dataSource type="POOLED">
                <property name="driver" value="com.mysql.cj.jdbc.Driver"/>
                <property name="url" value="jdbc:mysql://localhost:3306/test?useSSL=true&amp;useUnicode=true&amp;characterEncoding=UTF-8"/>
                <property name="username" value="root"/>
                <property name="password" value="root"/>
            </dataSource>
        </environment>
    </environments>
</configuration>
```

## 编写Mybatis工具类

首先了解Mybatis的基本逻辑架构：


![67AJEFCsKoin3Hd.jpg](../data/bluemsun/mybatis/a37a55fb6990495b9f9a345864706a16~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image)

可通过`SqlSessionFactoryBuilder`读取配置信息的某一个`environment`之后获取一个`SqlSessionFactory`，这个`SqlSessionFactory`就恰好对应这样的一个`environment`了，接着可以由此获取很多的`SqlSession`，每个会话就相当于我在不同的地方登陆一个账号去访问数据库，你也可以认为这就是之前JDBC中的`Statement`对象，会话之间相互隔离，没有任何关联。

而通过`SqlSession`就可以完成几乎所有的数据库操作，我们发现这个接口中定义了大量数据库操作的方法，因此，现在我们只需要通过一个对象就能完成数据库交互了，极大简化了之前的流程。

根据以上信息，编写以下Mybatis工具类

```java
package util;

import org.apache.ibatis.session.SqlSession;
import org.apache.ibatis.session.SqlSessionFactory;
import org.apache.ibatis.session.SqlSessionFactoryBuilder;

public class MybatisUtil
{
    private static SqlSessionFactory sqlSessionFactory;

    static {
        sqlSessionFactory = new SqlSessionFactoryBuilder().build(
                MybatisUtil.class.getResourceAsStream("/mybatis-config.xml"),
                "development");
    }

    public static SqlSession getSession(boolean autoCommit) {
        return sqlSessionFactory.openSession(autoCommit);
    }
}
```

## Mapper配置文件

Mapper配置文件用于将SQL语句与特定的名称建立联系，在这里可以直接利用其自带的动态代理，让Mapper链接到一个dao接口，从而之后利用dao接口的方法来直接执行SQL语句

### 编写实体类

建议将实体类中的字段名称与数据库中的名称起的一样。

```java
package entity;

public class User
{
    String username;
    String password;
    int uuid;
    int id;

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public int getUuid() {
        return uuid;
    }

    public void setUuid(int uuid) {
        this.uuid = uuid;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    @Override
    public String toString() {
        return "User{" +
                "username='" + username + ''' +
                ", password='" + password + ''' +
                ", uuid=" + uuid +
                ", id=" + id +
                '}';
    }
}
```

### 编写Mapper配置文件

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper
        PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="dao.UserDao">
    <select id="selectUser" resultType="entity.User">
        select * from users
    </select>
</mapper>
```

### 编写dao.Userdao接口

注意到刚才的Mapper文件中的标签与这个接口中的方法存在对应关系，所以要注意名称的规范化

```java
package dao;

import entity.User;

import java.util.List;

public interface UserDao
{
    List<User> selectUser();
}
```

### 修改mybatis-config.xml文件

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE configuration
        PUBLIC "-//mybatis.org//DTD Config 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-config.dtd">
<configuration>
    <environments default="development">
        <environment id="development">
            <transactionManager type="JDBC"/>
            <dataSource type="POOLED">
                <property name="driver" value="com.mysql.cj.jdbc.Driver"/>
                <property name="url" value="jdbc:mysql://localhost:3306/test?useSSL=true&amp;useUnicode=true&amp;characterEncoding=UTF-8"/>
                <property name="username" value="root"/>
                <property name="password" value="root"/>
            </dataSource>
        </environment>
    </environments>
    <mappers>
        <mapper resource="mappers/UserMapper.xml"/>
    </mappers>
</configuration>
```
多出来的mappers，就是刚才新创建的UserMapper.xml

### 测试类

首先获取SqlSession，通过Session获取到实现了UserDao的一个代理对象（实现就是UserMapper里的配置），通过这个代理对象来调用方法。

需要注意的是，SqlSession对象必须要被关闭。并且确保它不会被多个线程同时访问，因为它不是线程安全的。所以它的最佳的作用域是请求或方法作用域，最好是把它放在一个Http请求的请求域中。

```java
package test;

import dao.UserDao;
import org.apache.ibatis.session.SqlSession;
import util.MybatisUtil;

public class Main
{
    public static void main(String[] args) {
        try(SqlSession sqlSession = MybatisUtil.getSession(true)) {
            UserDao userDao = sqlSession.getMapper(UserDao.class);
            userDao.selectUser().forEach(System.out::println);
        }
    }
}
```

# 增删查改

## 查询

select标签，其中：
- id属性是对应的接口(namespace)的方法名
- resultType是每一行的返回值，如果有多行，实际返回值是List包装的resultType
- parameterType是参数的类型

```xml
<select id="selectUser" resultType="entity.User">
    SELECT * FROM users
</select>
```

```java
List<User> selectUser();
```

## 增加

```xml
<insert id="insertUser" parameterType="entity.User" useGeneratedKeys="true" keyProperty="id">
    INSERT INTO users (username, password, uuid) VALUES (#{username},#{password},#{uuid})
</insert>
```
需要特殊说明的是，这里的useGeneratedKeys会将插入后产生的主键保存下来，并通过keyProperty注入到User.id中去。

返回值是产生影响的行数。

## 修改

```xml
<update id="updateUser" parameterType="entity.User">
    UPDATE users SET username = #{username} ,password = #{password} WHERE id = #{id}
</update>
```

## 删除

```xml
<delete id="deleteUser" parameterType="int">
    DELETE FROM users WHERE id = #{id}
</delete>
```

# 其余配置信息

https://juejin.cn/post/7201831345415749692