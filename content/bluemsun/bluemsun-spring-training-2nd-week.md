---
title: 蓝旭23春季培训-第2周预习
date: 2023-03-31
---
# Java 异常类和常用类、容器、泛型

## Java 异常类

### 异常的定义

> 异常是指程序在运行过程中发生的,由于外部问题导致的程序运行异常事件,异常的发生往往会中断程序的运行.在 Java 这种面向对象的编程语言中,万物都是对象,异常本身也是一个对象,程序发生异常就会产生一个异常对象.

### 异常的分类

![v2-ec78fb9835b93c102aa113208173486c_1440w.webp](../data/bluemsun/bluemsun-spring-training-2nd-week/134f929eec764370a4aafbc688b9cdd9~tplv-k3u1fbpfcp-watermark.image)

1. `Throwable` 类是Java语言中所有错误或异常的顶层父类,其他异常类都继承于该类.`Throwable`类有两个重要的子类:`Exception` 和 `Error`.
2. `Error` 类是程序无法处理的错误,表示运行应用程序中较严重问题。类似于JVM运行时错误,IO上的严重错误,类加载解析时的错误之类的无法挽回的错误.这些异常发生时,JVM一般会选择线程终止.如果需要抛出这种错误,不需要`try catch`或者 `throws`.
3. `Exception`类下的`Runtime Exception`指的是运行时异常.这种错误在编译过程中即便没有`try catch`或`throws`也能够顺利地编译成功,只是在运行时会抛出这种异常.应该让我们在程序编写的逻辑上避免这种异常,就例如下一节的方法2.
4. `Exception`类下除了`Runtime Exception`指的是非运行时异常,这种异常在编译过程中就必须用`try catch`或`throws`才能够编译成功.也就是说,从程序的语法角度上来讲,是必须要处理的异常.

因此我们也可以将`Throwable`分为可查异常和不可查异常.前者包括非运行时异常,后者包括运行时异常和错误.


### 异常的处理

Java异常处理机制为：抛出异常，捕捉异常。
1. 抛出异常:当一个方法出现错误引发异常时,方法创建异常对象并交付运行时系统.
2. 捕捉异常:在方法抛出异常之后，运行时系统将转为在方法调用栈中寻找合适的异常处理器,如果找到了就从那个有合适异常处理器的方法继续执行,如果一个对得上号的都找不到,运行时系统就会终止,Java程序也就终止了.


#### 抛出异常

当我们的代码运行过程中出现了一些不合逻辑,令只因费解的情况时,你所调用的方法体中会抛出来一个异常.

例如:
```java
package com.blumsun.test;

public class Main
{
    public static void main(String[] args) {
        int[] arr = new int[10];
        arr[10] = 10;
    }
}
```
这样就会抛出异常`Exception in thread "main" java.lang.ArrayIndexOutOfBoundsException: 10
at com.blumsun.test.Main.main(Main.java:7)`

Java 使用关键字 `throw` 来抛出一个`Exception`的子类的实例对象表示异常的发生.因此我们也可以手动地在我们想要抛出异常的地方抛出一个异常.

#### 捕捉异常

##### 非运行时异常

对于非运行时异常,我们要么使用`try catch`语句在方法体内把异常处理掉(方法1);要么就要添加异常到方法签名处,也就是添加一个`throws Exception` (方法2),需要注意的是,`Exception`需要考虑到自身方法内能抛出的异常和调用处能处理的能力而选择哪种`Exception`.

方法1和方法2的最大区别就是,方法1是在发生异常的同时就在本方法中就处理好了异常,而方法2是发生异常的方法中不管异常,而让调用处去处理这个异常.

方法1:
```java
public static void main(String[] args) {
    int width=0;
    Scanner sc =new Scanner(System.in);
    Exception ex = new Exception();
    try {
        width = sc.nextInt();
        if(width < 0) {
            throw ex;
        }
    } catch (Exception e) {
        width=0;
    }
    System.out.println("The width is " + width);
}
```

方法2:(这里就是在`getWidth`方法中产生了两种可能的异常,然后让调用它的`main`方法自己分别地去处理)

```java
package com.blumsun.test;

import java.util.Scanner;

public class Main
{
    public static void main(String[] args) {
        int width = 0;
        try {
            width = getWidth();
        } catch (TooLongException ex) {
            width = 100;
        } catch (NegativeException ex) {
            width = 0;
        }
        System.out.println("Width is " + width);
    }

    static int getWidth() throws NegativeException,TooLongException {
        int width = 0;
        Scanner sc = new Scanner(System.in);
        NegativeException ex1 = new NegativeException();
        TooLongException ex2 = new TooLongException();
        width = sc.nextInt();
        if (width < 0) {
            throw ex1;
        }
        if (width > 100) {
            throw ex2;
        }
        return width;
    }
}

class TooLongException extends Exception
{

}

class NegativeException extends Exception
{

}
```

##### 运行时异常和错误

Java规定,它们不必须要捕捉或者上抛.当然了,一般而言运行时异常可以通过捕捉后进行处理而程序继续运行的,而错误一般会造成JVM停止此线程.

##### try catch finally语句

这种语句在Java中执行较为复杂.

首先执行的是`try`语句块中的语句,如果发生异常并能在`catch`块中捕获,则执行对应的第一个`catch`块中的语句,如果在`try`或`catch`块中被`return`,在`try`,`catch`中发生了无法捕获的异常,或`try`,`catch`块已经执行完毕,则开始执行`finally`块中的语句.需要注意的是,`finally`语句中的异常会覆盖`try`,`catch`中发生的异常,并且`try`,`catch`中的`return`并不会一定会退出函数体.

由于有这些特性,`try`中一般放置可能会发生异常的语句,`catch`语句用于处理异常,而`finally`用于处理善后工作,例如取消占用,关闭资源等.

注意事项:
-   `catch` 不能独立于 `try` 存在.
-   在 `try`,`catch` 后面添加 `finally` 块并非强制性要求的.
-   `try` 代码后不能既没 `catch` 也没 `finally`.

### 自定义声明异常

- 如果要自定义可查异常,那么必须继承自Exception
- 如果要自定义不可察异常(运行时异常),那么必须继承自RuntimeException

一个异常类也可往里面写各种属性和方法.

下面是一个示例:针对Pen中restInk和maxInk的问题.

```java
package com.bluemsun.test;

/**
 * @author Steve Paul
 */
public class InvalidInkException extends RuntimeException
{
    private int valueInk;

    InvalidInkException(int valueInk) {
        this.valueInk=valueInk;
    }

    InvalidInkException(){}

    public int getValueInk() {
        return valueInk;
    }

    public void setValueInk(int valueInk) {
        this.valueInk = valueInk;
    }
}
```
```
package com.bluemsun.test;

import java.util.Objects;

/**
 * @author Steve Paul
 */
public class Pen
{
    private int restInk;
    private int maxInk = 100;

    public Pen(int restInk, int maxInk) {

        setRestInk(restInk);
        setMaxInk(maxInk);
    }

    public Pen(int restInk) {
        setRestInk(restInk);
        setMaxInk(100);
    }

    public Pen() {
        setMaxInk(100);
        setRestInk(100);
    }

    public int getRestInk() {
        return restInk;
    }

    public void setRestInk(int restInk) throws InvalidInkException {
        if (restInk < 0 || restInk > maxInk) {
            throw new InvalidInkException(restInk);
        } else {
            this.restInk = restInk;
        }
    }

    public int getMaxInk() {
        return maxInk;
    }

    public void setMaxInk(int maxInk) throws InvalidInkException {
        if (maxInk < restInk) {
            throw new InvalidInkException(maxInk);
        }
        this.maxInk = maxInk;
    }

    public void addInk(int delta) {
        try {
            setRestInk(this.restInk + delta);
        } catch (InvalidInkException ex) {
            System.out.printf("Invalid Value of RestInk! It's %d.\n",ex.getValueInk());
        }
    }

    public void write(String str) {
        if(str==null){
            return;
        }
        int inkUsage = str.length();
        try {
            setRestInk(this.restInk - inkUsage);
            System.out.println(str);
        } catch (InvalidInkException ex) {
            System.out.printf("Short of Ink! It's %d.\n",ex.getValueInk());
        }
    }

    public void write(char ch) {
        int inkUsage = 1;
        try {
            setRestInk(this.restInk - inkUsage);
            System.out.println(ch);
        } catch (InvalidInkException ex) {
            System.out.printf("Short of Ink! It's %d.\n",ex.getValueInk());
        }
    }

    public void writeLine() {
        final int inkUsage = 80;
        try {
            setRestInk(this.restInk - inkUsage);
            for (int i = 1; i <= inkUsage; i++) {
                System.out.print("-");
            }
            System.out.println();
        } catch (InvalidInkException ex) {
            System.out.printf("Short of Ink! It's %d.\n",ex.getValueInk());
        }
    }

    public void writeLine(char ch) {
        final int inkUsage = 80;
        try {
            setRestInk(this.restInk + inkUsage);
            for (int i = 1; i <= inkUsage; i++) {
                System.out.printf("%c", ch);
            }
            System.out.println();
        } catch (InvalidInkException ex) {
            System.out.printf("Short of Ink! It's %d.\n",ex.getValueInk());
        }
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (o == null || this.getClass() != o.getClass()) {
            return false;
        }
        Pen pen = (Pen) o;
        return restInk == pen.restInk && maxInk == pen.maxInk;
    }

    @Override
    public int hashCode() {
        return Objects.hash(restInk, maxInk);
    }

    @Override
    public String toString() {
        return "Pen{" + "restInk=" + restInk + ", maxInk=" + maxInk + '}';
    }
}
```

```java
package com.bluemsun.demo;

import com.bluemsun.test.*;

/**
 * @author Steve Paul
 */
public class Main
{
    public static void main(String[] args) {
        Pen pen = new Pen(100, 200);
        pen.writeLine();
        System.out.println(pen.getRestInk());
        pen.write("Here is a simple sentence for a small test.");
        pen.addInk(300);
        System.out.println(pen.getRestInk());
        pen.addInk(150);
        System.out.println(pen.getRestInk());
        pen.write("Here is an another simple sentence for an another small test.");
        System.out.println(pen.getRestInk());
    }
}
```
标准输出如下:

```
--------------------------------------------------------------------------------
20
Short of Ink! It's -23.
Invalid Value of RestInk! It's 320.
20
170
Here is an another simple sentence for an another small test.
109
```

## Java 常用类

### 包装类

#### 包装类类名

|<p align=center> 基本数据类型 </p> | <p align=center> 包装类型 </p> |
| --- | --- |
| <p align=center> int </p> | <p align=center> Integer </p> |
| <p align=center> byte </p> | <p align=center> Byte </p> |
| <p align=center> short </p> | <p align=center> Short </p> |
| <p align=center> long </p> | <p align=center> Long </p> |
| <p align=center> char </p> | <p align=center> Character</p> |
| <p align=center> float </p> | <p align=center> Float </p> |
| <p align=center> double </p> | <p align=center> Double </p> |
| <p align=center> boolean </p> | <p align=center> Boolean </p> |

这八种包装类都是引用数据类型,他们有共同的父类,即`Number`类.我们使用包装类,就是为了用里面一些很有用的方法.

包装类中除了`Boolean`和`Character`,都有两个常量,叫做`MAX_VALUE`和`MIN_VALUE`,可以借此知道他们可表示的数据范围.

需要注意的是,这些包装类都是`final class`,也就是说不可以被继承.

#### 拆箱和装箱

拆箱指的是把包装类转化为一个基本数据类型的值,而装箱则指的是把一个人基本数据类型的值转化为一个包装类.

##### 装箱

一般而言,有如下方法可以用来装箱:`包装类 name = new 包装类(value);`

然而,这也有某些特性.例如可以用`String`初始化

`Integer int1 = new Integer("100000");`

对于Float,可以用Double初始化

`Float f1 = new Float(12.789);`

除此之外还有一种方法: 直接用等号赋值. 这就是自动装箱.

`Double dou1 = 12.34;`

当然了自动装箱不能用字符串直接赋个值. 而且只有 + - * / % = < > <= >=等会触发自动装箱,像==是不会触发的,它一定是比较两个对象的引用,一般来说都是不相等的,但是对于值-128~127之间的包装类对象,因为是在IntegerCache.cache() 方法产生,会复用已有的对象,因此引用是相等的.

##### 拆箱

可以用.某某Value()来获取

`double dou2 = dou1.doubleValue();`

`char ch02 = new Character('A').charValue();`

当然也甚至可以直接用等号赋值,这种叫做自动拆箱.

`double dou2 = dou1;`

`char ch01 = new Character('A');`

#### 常用方法

可以使用`Integer.parseInt(String s, Int radix)` 把一个字符串按照radix进制转化为一个`int`,其他的同理.

可以使用`Integer.decode(String nm)`把一个字符串按照10进制转化一个`Integer`

可以使用`Float.isNaN(float f)`判断一个`float`是否为一个数字,如果不是,返回`true`.这里说它是否是一个数字是针对非数而言的.

> NaN是Not a Number的缩写，表示“不是一个数字”。在计算机科学中，NaN通常用来表示一个无法确定或未定义的数值。例如，当一个数除以0时，它的结果就是NaN。需要注意的是，NaN与任何数值都不相等，包括它本身。

可以使用`Character.isDigit(char ch)`,`isLetter(char ch)`,`isLetterOrDigit(int codepoint)`,`isLowerCase(char ch)`,`isUpperCase(char ch)`,来判断是否是数字字母大小写;`toLowerCase(char ch)`,`toUpperCase(char ch)`来进行字母大小写的转化.

### Java Object类

Object类是所有类的默认的父类.

#### 方法

##### hashCode()

简而言之就是返回一个int类型的对象的哈希码值. 

大部分而言,哈希码值是把对象的引用给转化成了一个整数的结果.但是对于包装类,他返回的是这个包装类拆包后的值.

##### getClass()

返回的是此对象运行时的类的Class对象.也就是说,我们可以通过一个对象的getClass()方法,从而获知这个对象所在的类的一些性质,例如类的名称,类的继承关系等等.

例如这里就能获取一个类的构造方法.

```java
public class DemoClass
{
    int p1;
    char p2;
    LinkedList<Integer> ll1;
    public DemoClass(){
        System.out.println("构造了一个DemoClass.");
    }
}
```

```java
public class Main
{
    public static void main(String[] args) {
        DemoClass dc = new DemoClass();
        Class cla = dc.getClass();
        Constructor constructor;
        Object obj;
        try {
            constructor = cla.getConstructor();
            obj = constructor.newInstance();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
```

##### toString()

返回该对象的字符串表示.建议在我们自己声明的类中都重写这个方法,相当于少了一个sout时处理字符串的操作.

##### 接收任意引用类型的对象
既然 Object 类是所有对象的父类，则所有的对象都可以向 Object 进行转换，在这其中也包含了数组和接口类型，即一切的引用数据类型都可以使用 Object 进行接收。

### String类

String是字符串,但是它一旦形成就不可以再改变.

#### 构造String对象

可以用字符串常量,另外一个字符串和另外的字符数组来初始化构造一个String

```java
String str1 = new String("awsl");
char[] chstr2 = {'a','w','s','l'};
String str2 = new String(chstr2);
String str3 = new String(str2);
String str4 = new String(chstr2,1,3);
int address = System.identityHashCode(str2);
```
如果想输出String对象的引用,必须使用System.identityHashCode(str);

可以用字符串常量的引用赋值给String对象

```java
String str5;
str5="AWSL";
```

#### 使用方法

1. String对象可以用"+"进行并置运算.
2. 用length()得到了一个int类型的String对象的字符序列长度.
3. equals(String s)用于比较两个字符序列是否相同.
4. startsWith(String s)用于检测s是否为当前对象的前缀.
5. endsWith(String s)用于检测s是否为当前对象的后缀.
6. compareTo(String s)用于比较两字符串,返回值与strcmp()同理.
7. contains(String s)用于判断s是否是当前对象的一个子串.
8. indexOf(String s)返回当前对象第一次出现s的索引位置,如果没有检索到,返回-1.
9. indexOf(String s, int startpoint)返回当前对象从startpoint开始第一次出现s的索引位置,如果没有检索到,返回-1;
10. substring(int start, int end)返回当前String的start位置到end-1位置上的String.
11. trim(),返回一个对象,是原String去掉前后空格的字符串
12. replace(char old,char new),返回一个新的字符串,即原本字符串中所有的old字符变成new字符
13. replace(string old, stirng new),返回一个新的字符串,即原本字符串中所有的old子串变成new串
14. split(String regex),String对象以regex指定的正则表达式来分解当前String对象,并返回一个String数组.

#### 转换

##### String转化为基本型

使用Integer.parseInt(String s),可以把String转化为Int,其他数字包装类同理

```java
String str6 = "114";
int x = Integer.parseInt(str6);
```

##### 基本型转化为String

对于Long和Integer,有下列的静态方法:toBinaryString(int i),toOctalString(int i),toHexString(int i),返回i的二进制,八进制,十六进制的String对象表示.

##### String转化为字符数组

1. 使用getChars(int start, int end, char c[],int offset),把String对象中start~end-1的部分从字符数组c的offset处开始进行放置.
2. toCharArray(),String调用该方法来返回一个字符数组,恰好每个元素能够一一对应上.

##### 字符数组转String

可以使用String.copyValueOf(char[])来把一个字符数组转为String.

### StringTokenizer类

这个类跟String的split方法一样,都是用来分割字符串的,然而,它是使用具体的某些字符来当成分割标记.

#### 构造 StringTokenizer 对象
StringTokenizer(string s),为字符串s构造一个分析器,以空格,换行,回车,制表,进纸符作为分割标记
StringTokenizer(string s, String delim)为字符串s构造一个分析器,以delim中字符的任意排列(相当于delim中有啥字符,就以什么为分隔符).

#### 使用方法

它是一个字符序列的分析器,其中封装的是若干个单词.

因此可以使用nextToken()逐个获取分析器中的下一个单词.而且每调用一次nextToken(),分析器里就会把这个单词给删去,进而得到下一个单词.因此就有一个方法hasMoreTokens()来判断还有没有下一个单词,进而用来控制循环.

例子:

```java
package com.bluemsun.test;

import java.util.StringTokenizer;

public class Main
{
    public static void main(String[] args) {
        StringTokenizer st =new StringTokenizer("1110b5895f5541","bf");
        String temp = new String();
        while(st.hasMoreTokens()){
            temp=st.nextToken();
            System.out.println(Integer.parseInt(temp));
        }
    }
}
```

### Scanner 类
Scanner类可以用来解析字符序列中的单词.可以直接使用构造方法,比如:

```
Scanner sc = new Scanner("i am an artist.");
```

可以使用useDelimiter(String redix)方法将某个正则表达式作为分割标记,如果不特殊说明,就是用空格,换行,制表符来分割.

然后如同StringTokenizer类一样,可以用next()方法依次返回被切割出来的单词,有一个方法hasNext()可以判断是否还有被切割的单词.

并且,可以用nextInt()等来把分割出来的字符串转化为数字,如果不是数字单词,就会出现运行时错误.

例子:

```java
public class Main
{
    public static void main(String[] args) {
        Scanner sc = new Scanner("i am an artist.");
        while(sc.hasNext()){
            System.out.println(sc.next());
        }
```

Scanner与StringTokenizer的区别:
Scanner是仅仅存放着获取单词的分割标记,然后每次单独地获取单词,而StringTokenizer是把分解出来的单词都放到了对象中,然后再一个一个地拿出来.因此Scanner省空间但耗时间,StringTokenizer耗空间但省时间.

### StringBuilder类

它是一种字符串,但是跟String不一样,它形成之后还可以变.但它并不是线程安全的,也因此能效率更快

#### 构造StringBuilder 对象

1. 无参构造,初始容量为16个字符
2. StringBuilder(int capacity)指定初始容量capacity,其中没有任何字符
3. StringBuilder(CharSequence seq),拥有seq中所有的字符
4. StringBuilder(String str)构造一个有指定str的StringBuilder

#### 使用方法

1. append(String s),把s追加到原StringBuilder
2. reverse(),反转原先的字符序列
3. delete(int start, int end),把start~end-1的字符全部删除
4. insert(int offset, int i),把i的字符串形式插入到原字符序列的offset下标前.同理,可以把i换成是char,String
5. replace(int start, int end, String str),把元字符序列中start~end-1全删了,然后再在被删除处插入str
6. capacity()返回当前容量
7. toString(),返回一个String,相当于把StringBuilder转化成了String.
8. charAt(int idx),获取字符串中下标为idx的字符
9. setCharAt(int idx, char ch),把idx下标的字符修改成ch.
10. length(),返回该字符串的长度
11. substring(int start, int end)返回一个新的String,是原先字符序列的start~end-1
12. getChars(int start, int end, char c[],int offset),把StringBuilder对象中start~end-1的部分从字符数组c的offset处开始进行放置.

### StringBuffer类

它是可变字符串类,是线程安全的,但是效率较慢.
使用方法与StringBuilder极度相似.

### 内部类

内部类就是在一个类里面再定义一个完整的类.但是它跟从外部调用一个类不一样,这个类跟成员属性,方法处在一个级别.主打的就是一个增强封装性.甚至可以在一个方法体里面定义一个内部类.

注意到的是,一般的内部类中不能声明静态变量和静态方法,也仅供它的外嵌类来使用,也就是说其他的类不能用某个类的内部类来声明对象.可以在内部类中使用外嵌类的成员.

如果是带有static关键字的内部类,则这个内部类相当于外嵌类的一个基本数据类型,就可以在其他类中使用static的内部类来声明对象了.但这个时候带有static的内部类就不能操作外嵌类的实例成员了.

下面有个例子:

```java
package com.bluemsun.test;

import java.util.Date;

public class Computer
{
    String computerName;
    Date production;
    CPU cpu = new CPU();
    Disk disk;
    Memory memory;

    class CPU
    {
        String cpuName = Computer.this.computerName;
        String brand;
        double frequency;
    }

    class Disk
    {
        String diskName;
        int size;
        int storage;
    }

    class Memory
    {
        int storage;
        double frequency;
    }

    static class BriefIntroduction
    {
        String place = "NENU";
        String owner = "lijn";

        void describe() {
            System.out.println(owner + " " + place);
        }
    }
}
```

### 日期与时间类

#### LocalDate类

LocalDate调用LocalDate of(int year,int month,int dayOfMonth)或者LocalDate now()法可以返回一个LocalDate对象,其中可以利用以下的方法获取时间信息.

1. minusDays(),minusMonths(),minusYears(),在日期对象上减少指定的天数,月数,年数.
2. getYear(),getMonth(),getDayOfMonth():获取日期对象的年月日.
3. isEqual(),isBefore(),isAfter():比较日期对象的先后顺序.
4. withDayOfMonth(),withMonth(),withYear():修改日期对象的年月日.
5. isLeapYear()判断是否是闰年.
6. until(Temporal endExlusive, TemporalUnit unit),用于表示当前日期到指定日期之间的年数月数天数.参数endDateExclusive是计算时间距离的结束日期,不包括结束日期本身.

#### LocalDateTime类

相较于LocalDate类,这种类里面还可以额外封装时分秒和纳秒.

#### 日期格式化

可以使用String.format()的日期格式化方法,与C语言的printf比较相似,都是格式字符串.

所以使用`%tF`和`%tT`指示符来指定日期和时间的格式.`%tF`表示日期格式为`YYYY-MM-DD`,`%tT`表示时间格式为`HH:MM:SS`.

-   `%tY`:表示年份,使用4位数字
-   `%tm`:表示月份,使用2位数字
-   `%td`:表示日期,使用2位数字
-   `%tH`:表示小时,使用24小时制,使用2位数字
-   `%tM`:表示分钟,使用2位数字
-   `%tS`:表示秒,使用2位数字

```java
public static void main(String[] args) { 
    Calendar cal = Calendar.getInstance(); 
    cal.set(2023, 3, 30, 21, 24, 30); 
    String formattedDate = String.format("%tF %tT", cal, cal);
    System.out.println(formattedDate);
}
```

### Math类

Math类是Java中的一个标准类,它提供了许多数学函数和常量.

以下有一些常见的Math类方法:

-   `abs(x)`:返回`x`的绝对值
-   `ceil(x)`:返回不小于`x`的最小整数
-   `floor(x)`:返回不大于`x`的最大整数
-   `round(x)`:返回`x`最接近的整数,如果`x`等于两个整数的平均值，则返回偶数
-   `max(x, y)`:返回`x`和`y`中的最大值
-   `min(x, y)`:返回`x`和`y`中的最小值
-   `sqrt(x)`:返回`x`的平方根
-   `pow(x, y)`:返回`x`的`y`次幂
-   `exp(x)`:返回e的`x`次幂
-   `log(x)`:返回以e为底的`x`的自然对数
-   `sin(x)`:返回`x`的正弦值,`x`的单位为弧度

也有常量PI和E.

### BigInteger类
这个类用于处理任意长度的整数,可以表示比`long`类型更大的整数.

可以用`BigInteger(String val)`构造一个十进制的这个对象.

以下方法都是返回一个新的`BigInteger`.
-   `add`(BigInteger val):+
-   `subtract`(BigInteger val):-
-   `multiply`(BigInteger val):*
-   `divide`(BigInteger val):/
-   `mod`(BigInteger val):%
-   `pow`(int exponent)

### Random类

可以用`Math.Random()`的方法返回一个 0 ~ 1 的随机数, 因此我们可以用这个方法得到a~b的一个随机整数

`(int)(Math.Random()*b)+a`

也可以使用`Random`对象的`nextInt(int n)`方法,得到的是0~n-1的任意整数.

### Array类

就是一个用于操作数组的类,里面的方法都是静态方法.
- `sort(double a[])` 对a进行排序,是升序排序
- `binarySearch(double a[], double key)`,用二分法进行搜索
- `equals(double a[],double b[])`,如果两个数组中的所有元素都对应相等,则认为是相等的
- `copyOf(double[] original,int newLength)`,返回一个新的数组,就是把原数组中的newLength长度的元素复制过去

## 容器类

java容器类声明均为以下形式:
```
ArrayList<Integer> al =new ArrayList<>();
```
其中的`Integer`可以改成其他的引用数据类型,是面向泛型编程的特色.

1.  `ArrayList`

    `ArrayList`基于动态数组,它可以根据需要动态地增加或删除元素.由于内部是基于数组实现的,因此可以快速地进行随机访问.但是复插入和删除的效率很低.

2.  `LinkedList`

    `LinkedList`是一个基于双向链表实现的容器类,可以快速地在中间位置插入或删除元素.但是,随机访问元素的效率较低.

1.  `HashSet`

    `HashSet`是一个基于哈希表实现的集合,它可以快速地查找元素,但是不保证元素的顺序.`HashSet`中不能存储重复元素,因为重复元素的哈希值是相同的,会被视为同一个元素.`HashSet`中的元素是无序的,因为哈希表不保证元素的顺序.注意,需要保证插入进去的元素的类型实现了`hashCode`和`equals`方法.

2.  `TreeSet`

    `TreeSet`是一个基于红黑树实现的有序集合,它可以按照元素的自然顺序或指定的方式进行排序.因为其中的元素均为有序的,所以搜索时都用的二分法.

3.  `HashMap`

    `HashMap`是一个基于哈希表实现的映射.在使用`HashMap`时,需要保证键的类型实现了`hashCode`和`equals`方法,以便计算元素的哈希值和比较键的相等性.其优点就是可以快速地根据键查找对应的值.

4.  `TreeMap`

    `TreeMap`是一个基于红黑树实现的有序映射.与`Hashmap`不一样的是,`TreeMap`中的元素是按照键的顺序进行存储的,可以根据键的自然顺序或指定的比较器进行排序.因此其搜索用的二分法.
    
## 泛型编程

> Java泛型编程是一种将类型参数化的编程技术，它允许在编译时确定不同类型的参数，并在运行时使用它们。它的目的是增强代码的类型安全性和复用性.

需要注意的是,java中泛型参数的传递均为值传递.

### 泛型类

> 泛型类是一种具有类型参数的类,通过类型参数可以定义一种通用的类模板,可以在创建对象时指定具体的类型,从而生成具有指定类型的对象.

例如:

```java
public class ArrSort<T extends Comparable<T>> implements Swap
{
    void bubbleSort(T[] arr){
        int len = arr.length;
        for(int i=0;i<arr.length;i++) {
            for(int j=0;j<arr.length-i;j++){
                if(arr[j].compareTo(arr[j+1]) > 0 ) {
                    swap(j,j+1,arr);
                }
            }
        }
    }
}
```

这里的T相当于某种具体的类型,但是只是一个占位符,在类中使用它的时候,就可以直接当作普通的类型.由于例子中需要比较两个泛型变量的大小,因此要求传入的泛型类能够实现Comparable接口

同样的,泛型类也可以被继承,其子类可以保留父类的泛型参数.

### 泛型接口

> 泛型接口是一种具有类型参数的接口，通过类型参数可以定义一种通用的接口模板，可以在实现接口时指定具体的类型，从而生成具有指定类型的实现类。

例如在java中的一个Swap接口,用来交换数组中的两个变量.

```java
package com.bluemsun.test;

public interface Swap
{
    public static <T> void swap(int idx1, int idx2, T[] arr) {
        T temp = arr[idx1];
        arr[idx1] = arr[idx2];
        arr[idx2] = temp;
    }
}
```

### 泛型方法

> 泛型方法是一种在方法声明中使用泛型类型参数的方法。在泛型方法中，类型参数可以被用于方法的参数类型、返回类型和方法体中的局部变量类型等。

注意,在调用泛型方法时不需要指定类型参数的具体类型,编译器会根据方法参数的类型自动推断出类型参数的值.

```java
package com.bluemsun.test;

/**
 * @author Steve Paul
 */
public class ArrSort implements Swap
{
    static <T extends Comparable<T>> void bubbleSort(T[] arr){
        int len = arr.length;
        for(int i=0;i<arr.length;i++) {
            for(int j=0;j<arr.length-i-1;j++){
                if(arr[j].compareTo(arr[j+1]) > 0 ) {
                    Swap.swap(j,j+1,arr);
                }
            }
        }
    }

    static <T> void printArr(T[] arr){
        for(T ele:arr){
            System.out.print(ele.toString() + " ");
        }
        System.out.println();
    }
}
```

```java
package com.bluemsun.test;

public class Main
{
    public static void main(String[] args) {
        Integer[] intArr = new Integer[50];
        for (int i = 0; i < 50; i++) {
            intArr[i] = 50 - i;
        }
        ArrSort.bubbleSort(intArr);
        ArrSort.printArr(intArr);
    }
}
```

### 泛型通配符

使用泛型通配符 `?` 表示一种不确定的泛型类型,比如说指定一种任意的LinkedList.

注意:`?`只能用于引用参数.

例子:

```java
static void printLL(LinkedList<?> ll){
    for(Object ele:ll){
        System.out.print(ele.toString());
    }
    System.out.println();
}
```
~~太可惜了jdk 1.8 用不了var~~
