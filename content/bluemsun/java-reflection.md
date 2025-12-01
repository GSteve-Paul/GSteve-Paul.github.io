---
title: Java反射学习入门
date: 2023-09-09
tags:
  - 蓝旭2023秋季学习
---
# 概念

> Java的反射就是允许程序在运行时，检查和操作类、方法、字段等信息，创建新的对象的实例，而所对应的这些类在编译的时候并没有被明确指定

# Class 对象

要想获取反射，必先获取Class

每一个类都有与之对应的Class对象，用来保存类的一些元数据（字段，方法，注解等等）。

![](https://file.stevepaul.cc/3e0a6eb0bea84f149d258d1c6f1861f5.png)

通过粗略的对Java类加载机制的了解，可以知道：

> 在Java程序启动时，JVM会将一部分类（class文件）先加载（并不是所有的类都会在一开始加载），通过ClassLoader将类加载，在加载过程中，会将类的信息提取出来，同时也会生成一个Class对象存放在内存（堆内存），注意此Class对象只会存在一个，与加载的类唯一对应！

> 可以直接理解为默认情况下（仅使用默认类加载器）每个类都有且只有一个唯一的Class对象存放在JVM中，我们无论通过什么方式访问，都始终是那一个对象。Class对象中包含我们类的一些信息，包括类里面有哪些方法、哪些变量等等。

## 获取Class对象

这里主要介绍4种方法：

（假设Student是我自己定义的一个类,student是Student的一个对象,Student的全限定名是"Student"）
```java
import com.sun.istack.internal.NotNull;
import jdk.Exported;

import javax.annotation.PreDestroy;
import java.util.Objects;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;

@Retention(RetentionPolicy.RUNTIME)
public @interface myAnnotation
{
    String value() default "";
}

public class Student
{
    private String name;
    private int id;
    static long mod;

    static{
        mod = 998244353L;
    }

    public Student() {
    }

    public Student(String name, int id) {
        this.name = name;
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Integer getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    @myAnnotation(value = "gg")
    @NotNull
    private void say(String str) {
        System.out.println(str);
    }

    @NotNull
    public void say(String str,int n) throws Exception {
        if(n <= 0) {
            throw new RuntimeException("n 必须为正数");
        }
        while(n-- != 0) {
            say(str);
        }
    }

    public String getNameCard() {
        return name + id;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Student student = (Student) o;
        return name.equals(student.name) && id == student.id;
    }

    @Override
    public int hashCode() {
        return Objects.hash(name, id);
    }
}

public class Pupil extends Student
{
    private int age;
}

```

```java
Class c;
c = student.getClass();
c = Class.forName("Student");
c = Student.class;
c = ClassLoader.getSystemClassLoader().loadClass("Student");
```
获取到的这些Class对象，都是同一个。

注意到第2个和第4个，字符串里边必须填写的是Student类的全限定名（包名+类名）

[内部类的全限定名](https://blog.csdn.net/lp_cq242/article/details/80465585)

## 基本数据类型的Class对象

上面说Class对象是用来保存类的一些元数据，但是，一些不是类的东西一样可以获取到Class对象。例如：

```java
c = int.class;
c = void.class;
```
这些基本数据类型也有对应的Class，但这些Class和他们的包装类的Class并不相同
```java
int.class != Integer.class
int.class == Integer.TYPE
```
通过查看Integer.TYPE，发现这些基本数据类型的class都是通过函数

`static native Class<?> getPrimitiveClass(String name);`

来获取的，但是看到有`native`关键字就知道这个函数的具体实现不是java写的了，所以也不清楚接下来的内容了。

现在主要认为的还是像int.class是用来占位的，比如一些函数有类型为Class的参数，你就不得不这样传入一个。

# 获取类的信息

## 类的信息

```java
Class<?> myClass = Class.forName("Student");

String className = myClass.getName(); //类名

Field[] fields = myClass.getFields();//只包括public字段
Field[] fields1 = myClass.getDeclaredFields();//还包括了非public字段，但是不包括继承的

Method[] methods = myClass.getMethods(); //方法
Method[] methods1 = myClass.getDeclaredMethods();

Constructor<?>[] constructors = myClass.getConstructors(); //构造函数
Constructor<?>[] constructors1 = myClass.getDeclaredConstructors();

Annotation[] annotations = myClass.getAnnotations(); //注解
Annotation[] annotations1 = myClass.getDeclaredAnnotations();

Class<?> superClass = myClass.getSuperclass(); //父类

Class<?>[] interfaces = myClass.getInterfaces(); //实现的接口
```
[Class的其他方法](https://juejin.cn/post/7251113487317336121)

从xxxdeclaredxxx()的方法就可以看出，利用反射可以在破坏封装性(访问private)的基础上，对对象有更全面的操控能力。

## 构造方法

虽然Class对象自带一个方法newInstance(),但是它相当于就直接调用这个类的无参构造方法来实例化一个对象出来。

所以不如先获取构造方法，然后再用构造方法实例化对象。

类似于Class对象用于存储类的信息，Constructor对象用于存储构造方法的信息。

```java
Constructor<?> constructor = myClass.getConstructor(String.class,int.class);
Object obj = constructor.newInstance("Lijn",36);
```

根据方法重载的特性，要在一众构造方法中选出你想要的那种，只需要确定其参数列表即可，所以Class的getConstructor()方法就填写的是各个参数的class对象，这也是int.class的重要用途。

## 字段

同理，Field对象用于存储某个字段的信息

这里先演示一个获取类的静态变量的值。

```java
Field mod = myClass.getDeclaredField("mod");
//name.setAccessible(true);//private字段所必需的，这个字段是包权限，所以不需要
long value = (long)mod.get(null);
System.out.println(value);
mod.set(null,1000000007L);
value = (long)mod.get(null);
System.out.println(value);
```

因为mod字段是静态的，所以访问它不需要特定的对象，因此在set()和get()的obj参数那一栏填写null

接下来演示一个非静态变量。

```java
Field id = myClass.getDeclaredField("id");
id.setAccessible(true);// MUST
int idValue = (int)id.get(obj);
System.out.println(idValue);
```
这个时候就得填写具体的对象了。而且因为id是一个private的字段，所以必须`id.setAccessible(true);`，这段语句的含义是取消Java的安全检查，所以还能够提升反射的运行速度

## 其他方法

同理Method对象用于存储方法的信息

这里的其他方法 指的是除了构造方法之外的方法。

首先演示调用一个private方法。

```java
Method sayPrivate = myClass.getDeclaredMethod("say",String.class);
sayPrivate.setAccessible(true);
Object sayPrivateValue = sayPrivate.invoke(obj,"qwerty");
```
Method对象的invoke()方法就是用反射的方式调用方法。

然后演示调用一个非private方法

```java
Method sayPublic = myClass.getMethod("say",String.class,int.class);
Object sayPublicValue = sayPublic.invoke(obj,"wasd",5);
```

## 注解

与上面的略有不同的是，Annotation实质就是一个接口。所有的有意义的注解都可以认为是继承了Annotation接口的接口，但是不能直接写作extends Annotation。

要处理 Annotation，需要使用 Java 反射机制来读取 Annotation 的信息。

下面给出一个例子：

```java
Annotation anno = sayPrivate.getDeclaredAnnotation(myAnnotation.class);
myAnnotation myAnno = (myAnnotation) anno;
System.out.println(myAnno.value());
```
这里就可以读取say方法的myAnnotation注解的value值

需要注意的是，因为反射是程序运行时的功能，需要保证这个注解的生命周期能到达运行时。也就是确保注解的`
@Retention(RetentionPolicy.RUNTIME)`

## 修饰符
```java
System.out.println(Modifier.isPublic(sayPrivate.getModifiers()));
```

https://blog.csdn.net/wuqingyu01/article/details/80997010
