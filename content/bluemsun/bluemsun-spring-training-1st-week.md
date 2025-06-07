---
title: 蓝旭23春季培训-第1周预习
date: 2023-03-23
---
# IDEA 基本使用和Java基础

## IDEA的基本使用
### 创建项目

![屏幕截图 2023-03-21 181313.png](../data/bluemsun/bluemsun-spring-training-1st-week/25775f599aa14ca880f3d0b8b65cd888~tplv-k3u1fbpfcp-watermark.image)
安装好JDK,设置好环境变量开始创建项目.
语言选择Java.构建系统指的是一个把源代码生成可执行应用程序的过程自动化的程序.

### 新建模块

#### 主界面
![屏幕截图 2023-03-21 183005.png](../data/bluemsun/bluemsun-spring-training-1st-week/239424fbe3474c7eb2b4058221f54699~tplv-k3u1fbpfcp-watermark.image)
左边的项目栏中bluemsun week1节点表示Java模块,其下有多个文件/文件夹.
- src文件夹是用来存放java源代码.
- .iml文件是idea用来存储一些模块开发有关的信息.
- .idea文件夹下存放了项目的配置信息.
#### 新模块
![屏幕截图 2023-03-21 205327.png](../data/bluemsun/bluemsun-spring-training-1st-week/a7e67b5586014d7da0069ae43ea728fc~tplv-k3u1fbpfcp-watermark.image)
> idea中Project是最顶级的结构单元,然后就是Module.一个Project里面可以有多个Module. Project主要起到项目定义,范围约束和规范的作用.
- 对于一个单Module项目,它就是Project.
- 对于一个多Module项目,这些Module彼此可能存在一定关系.
新建了一个Module后,直观的表现是在Project目录下多了一个文件夹.

而每个新建的Module下都有与之对应的.iml文件和src文件夹.
### 新建包和类

![屏幕截图 2023-03-21 185937.png](../data/bluemsun/bluemsun-spring-training-1st-week/769626a6a6a749cd9a9d7c92da0f7394~tplv-k3u1fbpfcp-watermark.image)
在左侧项目视图src节点上右击新建软件包,在软件包上接着右击新建java类,得到如图所示在pack1下的Main类.

### 编写代码

![屏幕截图 2023-03-21 191320.png](../data/bluemsun/bluemsun-spring-training-1st-week/3763ee2ab8be424292db2daaccf3f3f4~tplv-k3u1fbpfcp-watermark.image)
在右侧的编辑器内输入代码,可以在上方的代码菜单栏中选择自动格式化代码对代码进行美化.

### 调试运行

![屏幕截图 2023-03-21 191932.png](../data/bluemsun/bluemsun-spring-training-1st-week/59c54ea00df84632a458ebc5aab2f2e0~tplv-k3u1fbpfcp-watermark.image)
- 调试:单击菜单运行中调试'Main'可以开始编译后开始调试.在下面的调试菜单中给出了如Visual Studio中的调试方法,可以在栏目中看到函数栈和监视窗口.

- 运行:也可以只在运行菜单中单击运行'Main'以运行程序.

在运行前会将类编译成字节码文件放在out文件夹下.

### 其他
#### 删除缓存

![屏幕截图 2023-03-23 082706.png](../data/bluemsun/bluemsun-spring-training-1st-week/9daff48b69814539af0903dc1ce0fd47~tplv-k3u1fbpfcp-watermark.image)
有些时候由于缓存和索引的损坏,idea可能无法打开项目或者自定义界面混乱,这个时候可以在文件菜单中点击清除缓存,这样在下一次打开项目时idea可以自己重新建立索引.

> 而idea建立缓存索引的目的是加快文件查询的速度,进而提高各种查找、代码提示等操作的速度.

#### 导出jar包

1. 在项目->打开模块设置->工件->添加->jar->来自具有依赖项的模块,然后选择想打包的模块和主类确定后就建立好了工件.
![image.png](../data/bluemsun/bluemsun-spring-training-1st-week/e82e9902884546aba8f2aca6021408f1~tplv-k3u1fbpfcp-watermark.image)

2. 在构建->构建工件后选择刚才建立的工件,然后就可以在/out/aitifacts文件夹下找到.jar文件.![image.png](../data/bluemsun/bluemsun-spring-training-1st-week/c583caf3a9f6443fa54a32f12d4a8dc1~tplv-k3u1fbpfcp-watermark.image)

3. 在jar所在文件夹中打开cmd,输入
``
java -jar *.jar
``
即可运行jar文件.

#### 导入jar包

1. 在项目->打开模块设置->模块->依赖->添加->JAR或目录->选择某个.jar文件并确定添加.
![image.png](../data/bluemsun/bluemsun-spring-training-1st-week/4345aaf80510461e8429d11f778ded56~tplv-k3u1fbpfcp-watermark.image)

2. 此时在外部库中就可以看到导入的jar文件,在使用其中的类时记得import.
![image.png](../data/bluemsun/bluemsun-spring-training-1st-week/45006bdf093e416ea18276fb8b6cf00e~tplv-k3u1fbpfcp-watermark.image)

## Java三大特性

### 封装

> 封装指一种将抽象性函式接口的实现细节部分包装,隐藏起来的方法.封装可以被认为是一个保护屏障,防止该类的代码和数据被外部类定义的代码随机访问.

这样就可以让我们的程序更加易读,并且使代码更加安全.
例:
````java
class Pen implements Write
{
    private Color pencolor;//笔墨颜色
    private int ink;//笔中所剩的墨水

    int getInk() {
        return ink;
    }

    void setInk(int ink) {
        this.ink = ink;
    }

    void addInk(int add) {
        this.ink += add;
    }

    void setPencolor(Color pencolor) {
        this.pencolor = pencolor;
    }

    void setPencolor(int pencolor) {
        try {
            this.pencolor = Color.class.getEnumConstants()[pencolor];
        } catch (ArrayIndexOutOfBoundsException ex) {
            System.err.println("Wrong Color!");
        }
    }

    Color getPencolor() {
        return pencolor;
    }

    Pen() {
        setInk(100);
        setPencolor(Color.RED);
    }

    Pen(Color pencolor, int ink) {
        setInk(ink);
        setPencolor(pencolor);
    }

    Pen(int pencolor, int ink) {
        setInk(ink);
        setPencolor(pencolor);
    }
    void usePen() {
        this.addInk(-10);
    }
    
    @Override
    public void writing() {
        System.out.println("I am a simple pen.");
    }
}
````

例子里Pen类中pencolor和ink属性被设为private,而使用setter和getter来操作.

### 继承
> 继承就是子类从父类继承方法和属性,使得子类具有父类相同的行为和特点.

而且子类可以在父类的基础上进行修改,增添多的特性或覆盖原有的特性.

注:
1. 在同一个package下public,protected,默认权限都可以被继承,不再同一个package下,只有package,protected可以被继承.
2. Java不支持多继承.
3. 可以通过super来访问因为重写等被隐藏了的父类的成员.


例:
````java
public class SmallPen extends Pen implements Write
{
    SmallPen() {
        setInk(50);
        setPencolor(1);
    }
    void usePen()
    {
        this.addInk(-5);
    }

    @Override
    public void writing() {
        System.out.println("I am a small pen");
    }
}
````

### 多态

> 多态是同一个行为具有多个不同表现形式或形态的能力。

如同之前的Pen类及其子类SmallPen,在子类SmallPen中重写了方法usePen,使得usePen在面对不同的对象时可以有不同的操作.

同时也可以利用接口实现多态:例如下面的writing方法在SmallPen和Pen类中被重写,达到了不同的效果.
````java
public interface Write
{
    void writing();
}
````

最后放个测试图片完结撒花

![image.png](../data/bluemsun/bluemsun-spring-training-1st-week/0b992dc581994d508fdaac4c5ec5cf39~tplv-k3u1fbpfcp-watermark.image)