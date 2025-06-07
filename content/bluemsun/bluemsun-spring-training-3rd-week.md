---
title: 蓝旭23春季培训-第3周预习
date: 2023-04-06
---
# Java IO

## Java IO 简介

Java IO是就是用Java 执行输入输出操作.它能够让用户们通过input和output来访问不同的数据源和目的地.其中input指的是从外部输入到程序的内部,而output指的是从程序的内部输出到外部.io分为java.io和java.nio,前者会造成线程的阻塞,而后者不会.

由上述可知,要给Java中的流分类,可以分为:
- 输入流,输出流 (很显然
- 字符流,字节流 (前者流中最小的数据单元是1个字符,即2个字节;而后者最小的数据单元是1个字节)
- 节点流,处理流 (前者是从一个特定的地方读写数据,直接连接数据源;而后者是对一个已存在的流的连接和封装，是一种典型的装饰器设计模式)
- 其他(转换流,缓冲流,对象流)


![1290084-20180415203406453-566524870.png](../data/bluemsun/bluemsun-spring-training-3rd-week/90173816e941434fa73eefe5ec989975~tplv-k3u1fbpfcp-watermark.image)

## Java IO 四大基流

|  | 字节流 | 字符流 |
| --- | --- | --- |
| 输出流 | OutputStream | Writer |
| 输入流 | InputStream | Reader |

注意到这四个类都是抽象类,只是在这四个类中声明了一些抽象方法.

### 输出流

首先说明一下输出流的工作过程:当数据写入输出流时,它首先被存储在缓冲区中,然后在适当的时候将其从缓冲区刷新到底层数据源中,例如某个文件.这样一来可以减少io操作的次数,提高程序的运行效率.

一般而言这个适当的时候就是缓冲区被填满的时候,然而,对于数据的最后部分我们需要自己手动地输出到底层数据源中,因为它不一定能填满缓冲区.

#### OutputStream 字节输出流

该类中主要声明了该如何去输出字节.

该抽象类中主要有三种方法,分别是write,flush,close.

#### write

最基本的write方法是`public void write(byte b[], int off, int len) throws IOException`
其意思为将字节数组b中从off开始的len长度的字节输出到外界的目标区域去.

它还有两个重载,有一个是:`public abstract void write(int b) throws IOException`意思是把一个int类型的b变量的最低的8位二进制码给输出出去,前面的那24位就被直接忽略了.

另一个是`public void write(byte b[]) throws IOException` 相当于就是把字节数组b中所有的字节全部输出到外界的目标区域去.

##### flush

这个方法的意思就是强制将缓冲区中的数据输出到目标设备,并清空缓冲区,以避免数据滞留.一般而言要在输出的最后flush一下,确保不会有残余数据留在缓冲区中.

##### close

这个方法的意思就是把这个输出流关闭.在输出流关闭之后,这个流就废了,啥事也不能干.

#### Writer 字符输出流

该类中主要声明了该如何去输出字符.

其成员规定了输出的缓冲区和缓冲区大小(默认是1024个字符,即2048个字节)以及一个lock,用于控制多个线程访问同一个`Writer`实例时的并发安全问题.它的两个构造方法也都是用于处理lock的.

该抽象类中还主要有四种方法,分别是`write`,`append`,`flush`,`close`.

后两者的意义跟`OutputStream`的几乎一样,因此不再赘述.

##### write

最基本的write方法是`abstract public void write(char cbuf[], int off, int len) throws IOException`, 其意义为将字符数组cbuf中从off开始的len长度的字节输出到外界的目标区域去.

它还有数个重载,`public void write(int c) throws IOException`是输出一个int类型变量的最低的16位,`public void write(char cbuf[]) throws IOException`是把整个字符数组cbuf都输出出去.

而`public void write(String str) throws IOException`和`public void write(String str, int off, int len) throws IOException`更像是上述方法的String版本.

##### append

最基本的`append`方法是`public Writer append(CharSequence csq, int start, int end) throws IOException`,其意义为将字符序列csq的start~end-1这个子串追加到输出区域.

它还有一个重载,`public Writer append(char c) throws IOException`,其意义为往后追加一个字符c.

### 输入流

同样的,首先说明输入流的工作原理: 其实与输出流很类似,它是将数据先存放在内存中的一个缓存区域,然后从缓存区域中读取数据,以提高读取数据的效率.缓冲区的大小默认是8192字节.

#### InputStream 字节输入流

该抽象类中主要声明了如何从外部输入数据到程序内部.

它主要有七种方法,分别是`read`,`skip`,`available`,`close`,`mark`,`reset`,`markSupported`.

##### read

该方法有多个重载,有:
- `public abstract int read() throws IOException` 意为读取一个字节,并返回读取到的这个字节的int形式变量.
- `public int read(byte b[], int off, int len) throws IOException`和`public int read(byte b[]) throws IOException`与之前的说到的输出流意思几乎一样,只不过这个是输入到b数组里边去.返回值为读取到的字节总数.

注意到的是,如果已经到达流的末尾或下一个字节无法读取,则会返回-1.其中,如果因为某种原因无法读取下个字节会造成线程堵塞.

##### skip

`public long skip(long n) throws IOException`这个方法的意义是从输入流中跳过数个字节,返回值就是实际上跳过的字节数.其返回值和n不一定相等,原因是有可能剩下没有足够的字节数供其跳过.

一般而言,这个方法是用来跳过输入流中不必要的内容的,例如说空格,换行,制表符之类的.

##### mark,reset,markSupported

这三个方法是用来在输入流中重复性地读入数据的.

`public synchronized void mark(int readlimit)`方法用来在流中放置一个标记,并且说明从这个标记处往后最多读`readlimit`个字节,标记都是有效的.这个标记地位置其实就是当前流的位置.

`public synchronized void reset() throws IOException`方法用来将流重新定位到之前的标记处.如果之前没有调用过`mark`方法或者已经超出了`readlimit`的限制就会报异常.

这样一来就相当于可以从流的一个标记出发,反复地读取`readlimit`字节长度的数据

当然了,要能使用`mark`和`reset`,必须要确保这个输入流能够支持.因此需要先利用`markSupported`方法询问是否可以用`mark`和`reset`.

##### close

这个方法代表着对输入流的关闭,释放系统资源. 当然也可以使用`try-with-resources`语句自动关闭输入流.这样就不需要显式地调用close方法了.

#### Reader 字符输入流

与`InputStream`很相似, 这个类也声明了输入,只不过输入的是字符.

它主要有如下的方法:`read`,`skip`,`ready`,`markSupported`,`mark`,`reset`,`close`等.

其`read`,`skip`,`markSupported`,`mark`,`reset`,`close`方法与`InputStream`大同小异,就只特别说明一下`ready`方法

##### ready

这个方法就是用于判断是否可以从输入流中读取数据而不会被阻塞.

## Java 常用流

首先说明一下java中怎么使用流:
1. 选择合适的流类型.
2. 创建一个流的对象.
3. 合理运用流的方法进行输入输出工作.
4. 关闭流,并释放资源.

### 字节输入流和字节输出流

下面是一个复制文件的例子,是把一个C++程序复制了一份.

原理是先把一个C++程序读到一个字节数组中,再把这个字节数组输出到一个文件中去.

```java
package com.bluemsun.test;  
  
import java.util.concurrent.atomic.AtomicInteger;  
  
/**  
* @author Steve Paul  
*/  
public class Main  
{  
    static final int MAXN = (int) 1e7;  

    public static void main(String[] args) {  
        byte[] arr = new byte[MAXN];  
        AtomicInteger len = new AtomicInteger(0);  
        Demo01.readFromFile(arr, len);  
        Demo01.writeIntoFile(arr, len);  
    }  
}
```
```java
package com.bluemsun.test;  
  
import java.io.*;  
import java.util.concurrent.atomic.AtomicInteger;  
  
/**  
* @author Steve Paul  
*/  
public class Demo01  
{  
/**  
* @param arr 需要输入进去的数组  
*/  
    public static void readFromFile(byte[] arr, AtomicInteger len) {  
        File f1 = new File("cppprogram.exe");  
        FileInputStream fis = null;  
        try {  
            fis = new FileInputStream(f1);  
            len.set(fis.read(arr));  
        } catch (IOException ex) {  
            ex.printStackTrace();  
        } finally {  
            try {  
                if (fis != null) {  
                fis.close();  
                }  
            } catch (IOException ex1) {  
                ex1.printStackTrace();  
            }  
        }  
    }  
  
/**  
* @param arr 需要输出的数组  
*/  
    public static void writeIntoFile(byte[] arr, AtomicInteger len) {  
        File f2 = new File("copiedcppprogram.exe");  
        FileOutputStream fos = null;  
        try {  
            f2.createNewFile();  
            fos = new FileOutputStream(f2, false);  
            fos.write(arr, 0, len.get());  
        } catch (IOException exIo) {  
                exIo.printStackTrace();  
        } finally {  
            try {  
                if (fos != null) {  
                    fos.flush();  
                    fos.close();  
                }  
            } catch (IOException ex) {  
                ex.printStackTrace();  
            }  
        }  
    }  
}
```

![image.png](../data/bluemsun/bluemsun-spring-training-3rd-week/02ba47195c8a44a28b60a39a978d2f12~tplv-k3u1fbpfcp-watermark.image)


![image.png](../data/bluemsun/bluemsun-spring-training-3rd-week/ba7ac30e42414addaff6bab7df79fa9e~tplv-k3u1fbpfcp-watermark.image)

比较SHA-256,发现是一样的,说明复制成功.

需要注意的是:

1. 程序中用了`AtomicInteger`来达到一个按址修改数字型参数的效果.
2. `FileOutputStream`中虽然没有`append`方法,但是可以在构造或者`write`时添加一个布尔参数,`true`代表追加,而`false`代表覆盖

但是上面的这个程序存在一定的问题,因为它需要文件的大小小于byte数组的大小,如果要解决这个问题,我们就应当将文件分成块,一块一块地输入进字节数组然后再一块一块地输出.

因此可以修改为:

```java
package com.bluemsun.test;  
  
import java.io.File;  
  
/**  
* @author Steve Paul  
*/  
public class Main  
{  
    static final int MAXN = (int) 1e7;  

    public static void main(String[] args) {  
        long begin = System.nanoTime();  
        File f1 = new File("cppprogram.exe");  
        File f2 = new File("newcppprogram.exe");  
        Demo01.copyFile(f1, f2);  
        long end = System.nanoTime();  
        System.out.println(end - begin + " ns");  
    }  
}
```
```java
package com.bluemsun.test;  
  
import java.io.*;  
  
/**  
* @author Steve Paul  
*/  
public class Demo01  
{  
    public static void copyFile(File f1, File f2) {  
        final int MAXN = 32 * 1024;  
        byte[] temp = new byte[MAXN];  
        FileInputStream fis = null;  
        FileOutputStream fos = null;  
        try {  
            fis = new FileInputStream(f1);  
            fos = new FileOutputStream(f2, false);  
            int rest = 0;  
            while ((rest = fis.available()) > 0) {  
                fis.read(temp, 0, Math.min(temp.length, rest));  
                fos.write(temp, 0, Math.min(temp.length, rest));  
            }  
        } catch (IOException ex) {  
            ex.printStackTrace();  
        } finally {  
            try {  
                if (fis != null) {  
                    fis.close();  
                }  
            } catch (IOException ex) {  
                ex.printStackTrace();  
            }
            try {
                if (fos != null) {  
                    fos.flush();  
                    fos.close();  
                }  
            } catch (IOException ex) {  
                ex.printStackTrace();  
            }  
        }  
    }  
}
```
比较SHA-256,发现是一样的,说明复制成功.

### 字符输入流 字符输出流 打印流和缓冲流

一般而言,字符流只能用来输入输出字符. 下面这个示例是用来利用缓冲流来从一个文本文档里面读取字符然后输出在标准输出上.

```java
package com.bluemsun.test;  
  
import java.io.File;  
  
/**  
* @author Steve Paul  
*/  
public class Main  
{  
    static final int MAXN = (int) 1e7;  

    public static void main(String[] args) {  
        Demo01.printTextFile(new File("testtext.txt"));  
    }  
}
```

```java
package com.bluemsun.test;  
  
import com.sun.xml.internal.ws.policy.privateutil.PolicyUtils;  
  
import java.io.*;  
  
/**  
* @author Steve Paul  
*/  
public class Demo01  
{  
    public static void printTextFile(File f1) {  
        FileReader fr = null;  
        BufferedReader br = null;  
        PrintWriter pw = null;  
        BufferedWriter bw = null;  
        char ch;  
        try {  
            fr = new FileReader(f1);  
            br = new BufferedReader(fr, 128);  
            pw = new PrintWriter(System.out);  
            bw = new BufferedWriter(pw);  
            while (br.ready()) {  
                bw.write(br.read());  
            }  
        } catch (IOException ex) {  
            ex.printStackTrace();  
        } finally { 
            try {  
                if (br != null) {  
                    br.close();  
                }  
            } catch(IOException ex) {  
                ex.printStackTrace();  
            }  
            try{  
                if (bw != null) {  
                bw.flush();  
                bw.close();  
                }  
            } catch (IOException ex) {  
                ex.printStackTrace();  
            }  
        }  
    }  
}
```

在这个程序中,我们使用了缓冲流.它与其他流最大的不同就是它自带一个缓冲区域,这样就可以一次性通过IO获取大量数据,然后按需求读取,减少整体的IO次数,从而以空间换时间,提升效率.

注意到缓冲流实际上是一种包装流,我们使用包装流包装了节点流,程序直接操作包装流,而底层还是节点流和IO设备操作.但是我们在关闭包装流后就不要关闭其中的节点流了,因为在关闭最外层流的时候就会自动把内层的流关闭.

### 字节数组流

Java中的`ByteArrayInputStream`和`ByteArrayOutputStream`是基于字节数组的流.它们主要用于将数据写入内存或者从内存中读取数据.为何不把数据存硬盘里呢?因为硬盘相比内存还是太慢.

- `ByteArrayInputStream`相当于把一个字节数组作为输入源输入到程序中来
- `ByteArrayOutputStream`相当于把程序中的内容输出到一个字节数组中去

```java
package com.bluemsun.test;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;

/**
 * @author Steve Paul
 */
public class Main
{
    static final int MAXN = (int) 1e7;

    public static void main(String[] args) {
        byte[] temp = {1, 2, 3, 4, 5, 6, 7, 8, 9};
        ByteArrayInputStream bis = new ByteArrayInputStream(temp);
        int a;
        while ((a = bis.read()) != -1) {
            System.out.print(a);
        }
        System.out.println();
    }
}
```

```java
package com.bluemsun.test;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.util.Scanner;

/**
 * @author Steve Paul
 */
public class Main
{
    static final int MAXN = (int) 1e7;

    public static void main(String[] args) {
        byte[] temp;
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        Scanner sc = new Scanner(System.in);
        bos.write(sc.nextInt());
        temp = bos.toByteArray();
        try {
            bos.flush();
        } catch (IOException ex) {
            ex.printStackTrace();
        }
        try {
            bos.close();
        } catch (IOException ex) {
            ex.printStackTrace();
        }
        System.out.println(temp[0]);
    }
}
```

### 数据流

它是一种处理流,之所以是数据是因为他有输入和输出所有Java的基本数据类型和String的方法.但是它只能处理字节流.

有`DataInputStream`和`DataOutputStream`两个类,均继承自过滤流,有相似的共同祖先字节输入输出流.


![屏幕截图 2023-04-06 081150.png](../data/bluemsun/bluemsun-spring-training-3rd-week/3aa23285b98a48d6b0551901f4f0a147~tplv-k3u1fbpfcp-watermark.image)

可以用图上的方法对流进行装饰.

```java
public static void trydis() {
    byte[] temp;
    ByteArrayOutputStream bos = new ByteArrayOutputStream();
    DataOutputStream dos = new DataOutputStream(new BufferedOutputStream(bos));
    try{
        dos.writeBoolean(true);
        dos.writeUTF("ABCDEFG");
        dos.writeDouble(12.5);
        dos.writeInt(2365);
    } catch (IOException ex) {
            ex.printStackTrace();
    } finally {
        try{
            dos.flush();
        } catch (IOException ex) {
            ex.printStackTrace();
        }
        temp = bos.toByteArray();
        try {
            dos.close();
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }
    ByteArrayInputStream bis = new ByteArrayInputStream(temp);
    DataInputStream dis = new DataInputStream(new BufferedInputStream(bis));
    try{
        System.out.println(dis.readBoolean());
        System.out.println(dis.readUTF());
        System.out.println(dis.readDouble());
        System.out.println(dis.readInt());
    } catch (IOException ex) {
        ex.printStackTrace();
    } finally {
        try{
            dis.close();
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }
}
```

### 转换流

转换流也是一种处理流,它负责的是字节到字符之间的转化.`InputStreamReader`将字节输入流转化为字符输入流,而`OutputStreamReader`将字符输出流转化为字节输出流. 

其实就是前者负责解码,而后者负责编码. 而对于这个编解码的问题,最核心的其实是编码表.只有在对应的编码表下字符显示才不会乱码.

比如下面例子中我使用了分别以UTF-8,UTF-16,GBK三种编码来解码一段UTF-8编码格式的文本文档:

```java
public static void tryconv() {
    InputStreamReader isr1 = null;
    char[] buffer = new char[MAXN];
    try {
        isr1 = new InputStreamReader(new BufferedInputStream(new FileInputStream("testtext.txt")), "UTF-8");
        int len;
        while ((len = isr1.read(buffer)) != -1) {
            System.out.println(new String(buffer, 0, len));
        }
    } catch (IOException ex) {
        ex.printStackTrace();
    } finally {
        try {
            isr1.close();
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }

    try {
        isr1 = new InputStreamReader(new BufferedInputStream(new FileInputStream("testtext.txt")), "UTF-16");
        int len;
        while ((len = isr1.read(buffer)) != -1) {
            System.out.println(new String(buffer, 0, len));
        }
    } catch (IOException ex) {
        ex.printStackTrace();
    } finally {
        try {
            isr1.close();
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }

    try {
        isr1 = new InputStreamReader(new BufferedInputStream(new FileInputStream("testtext.txt")), "ASCII");
        int len;
        while ((len = isr1.read(buffer)) != -1) {
            System.out.println(new String(buffer, 0, len));
        }
    } catch (IOException ex) {
        ex.printStackTrace();
    } finally {
        try {
            isr1.close();
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }
}
```

得到的输出在IDEA的控制台中显示如下:

![屏幕截图 2023-04-06 091352.png](../data/bluemsun/bluemsun-spring-training-3rd-week/31da6bd0568143aab8651fa200fd0fd0~tplv-k3u1fbpfcp-watermark.image)

### 对象流

对象流顾名思义就是管理java中对象的输入输出的流,它有两个类,分别是`ObjectInputStream` 和 `ObjectOutputStream`.前者负责的是把二进制的编码输入到程序中并转换成java对象,而后者负责的是把程序里的java对象转换成二进制编码并输出到外部.

当然了,它们的超类肯定是字节输入输出流.

这里写了一个三角形的类,然后对一个三角形实例用对象流进行输入输出

```java
package com.bluemsun.test;

import java.io.Serializable;

/**
 * @author Steve Paul
 */
public class Triangle implements Serializable
{
    private double a, b, c;
    public Triangle(double a, double b, double c) {
        this.a = a;
        this.b = b;
        this.c = c;
    }
    public double getA() {
        return a;
    }
    public void setA(double a) {
        this.a = a;
    }
    public double getB() {
        return b;
    }
    public void setB(double b) {
        this.b = b;
    }
    public double getC() {
        return c;
    }
    public void setC(double c) {
        this.c = c;
    }

    @Override
    public String toString() {
        return new Double(a).toString() + " " + new Double(b).toString() + " " + new Double(c).toString();
    }
}
```

```java
public static void OutputTriangle() {
        Triangle t1 = new Triangle(10, 20, 25);
        File f1 = new File("Triangle1");
        ObjectOutputStream oos = null;
        try {
            oos = new ObjectOutputStream(new BufferedOutputStream(new FileOutputStream(f1)));
            oos.writeObject(t1);
        } catch (IOException ex) {
            ex.printStackTrace();
        } finally {
            try {
                oos.flush();
            } catch (IOException ex) {
                ex.printStackTrace();
            }
            try {
                oos.close();
            } catch (IOException ex) {
                ex.printStackTrace();
            }
        }
        Triangle t2;
        ObjectInputStream ois = null;
        try {
            ois = new ObjectInputStream(new BufferedInputStream(new FileInputStream(f1)));
            t2 = (Triangle) ois.readObject();
            System.out.println(t2.toString());
        } catch (IOException ex) {
            ex.printStackTrace();
        } catch (ClassNotFoundException ex) {
            ex.printStackTrace();
        } finally {
            try {
                ois.close();
            } catch (IOException ex) {
                ex.printStackTrace();
            }
        }
    }
```

看看输出出来的二进制文件(看不懂):

![屏幕截图 2023-04-06 213455.png](../data/bluemsun/bluemsun-spring-training-3rd-week/1dd4e5569fe44d2590e602f8666019d5~tplv-k3u1fbpfcp-watermark.image)

注意:
- 如果要对一个类的实例用对象流输入输出,就必须要这个类实现接口`Serializable`.不然会报`java.io.NotSerializableException`这个运行时异常. 
- 实现了序列化的类,在被序列化的时候用 `transient` 关键字修饰的字段是不会被序列化的,换句话说,不会被`ObjectOutputStream`输出出去.

### 随机访问流

这种流比较的特殊,它既不是`InputStream`也不是`OutputStream`的子类.因为它可以在文件的任意位置进行访问,不会受到顺序的限制.而且它能够既可读也可写.但是它主要还是操作二进制文件,因为它总之还是基于字节的.

他的构造方法有点特殊:
- `RandomAccessFile(String filename, String mode)`使用指定的文件名和访问模式创建随机访问流对象.其中，filename 是要访问的文件的路径,mode 是访问模式,r表示只读模式,rw表示读写模式,rws 表示读写模式并同步文件内容,rwd表示读写模式并同步文件内容和元数据.
- 当然了,就跟其他的一样,也可以用File对象..

> 这里的同步文件内容指的是在将数据写入内存缓冲区的时候,立即将缓冲区中的数据刷新到磁盘文件.


> 而元数据指的是一个文件的描述文件本身的信息,例如文件的属性,创建时间,修改时间,大小,文件权限等.

下面给出一个简单的例子:

```java
public static void ranAcc() {
    File f1 = new File("mytest");
    RandomAccessFile raf = null;
    try{
        f1.createNewFile();
    } catch (IOException ex) {
        ex.printStackTrace();
    }
    try {
        raf = new RandomAccessFile(f1, "rws");
        raf.writeChar('F');
        raf.writeChars("A Interesting String");
        raf.seek(0);
        raf.writeChar('G');
    } catch (IOException ex) {
        ex.printStackTrace();
    } finally {
        try{
            if(raf!=null){
                raf.close();
            }
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }
}
```

输出文件中是`GA Interestring String`

然后发现RandomAccessFile在用seek方法定位到已经有数据的地方后,write方法会覆盖掉原有的数据.所以如果想要插入的话,就必须要先把后面的读到一个字节数组里面去,然后再write.

就可以改成这个:

```java
public static void ranAcc() {
    File f1 = new File("mytest");
    RandomAccessFile raf = null;
    try {
        f1.createNewFile();
    } catch (IOException ex) {
        ex.printStackTrace();
    }
    try {
        raf = new RandomAccessFile(f1, "rws");
        raf.writeChar('F');
        raf.writeChars("A Interesting String");
        raf.seek(0);
        byte[] buffer = new byte[1000];
        int len = raf.read(buffer, 0, (int) raf.length());
        raf.seek(0);
        raf.writeChar('G');
        raf.write(buffer, 0, len);
    } catch (IOException ex) {
        ex.printStackTrace();
    } finally {
        try {
            if (raf != null) {
                raf.close();
            }
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }
}
```
这个输出文件中就是`GFA Interestring String`

# 总结
1. 全限定名:包名+类名.
2. 相对路径的写法: .表示当前目录, ..表示上一级目录 例如.\..\..\ 相当于是向上两级
3. Unicode是一种字符编码标准, 它定义了字符与其在计算机内部表示之间的映射关系, 而UTF是一种Unicode的编码方式, 它相当于实现了Unicode的标准, 使得以这一标准把字符写成二进制编码形式. 常用的有UTF-8 UTF-16 UTF-32.writeUTF是以UTF-8形式写入
4. ~~可以不断地复制一个图片自身以获得一个很大的图片(物理~~
5. File.separator作为分隔符,对linux和windows都能用
6. 每次输入的时候可以用一个n来记录输入的字节/字符数.