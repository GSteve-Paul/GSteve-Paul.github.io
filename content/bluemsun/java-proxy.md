---
title: Java代理学习入门
date: 2023-09-09
---
# 概念

> 代理模式是一种比较好理解的设计模式。简单来说就是 我们使用代理对象来代替对真实对象(real object)的访问，这样就可以在不修改原目标对象的前提下，提供额外的功能操作，扩展目标对象的功能。
> 
> 代理模式的主要作用是扩展目标对象的功能，比如说在目标对象的某个方法执行前后你可以增加一些自定义的操作。

举个例子：在方法调用前后记录日志，计算方法执行的花费时间。

之后的Spring面向切面编程就用到了Java代理。

感觉有点像`Servlet`中的`Filter`。

<hr>

# 代理模式的分类

代理模式分为静态代理和动态代理两种实现的方式。

两种方式的区别就是：

**静态代理**在编译时就已经确定好了接口，目标类和代理类。可以简单地认为是静态代理直接就给你写死了。

**动态代理**是运行时专门生成一个代理类，重写了方法达到了代理的效果。

这两个概念看上去很抽象，没看懂没关系，先往下面看。

# 静态代理

开发中很少利用静态代理，但是他对我们理解JDK动态代理有其独特的意义。

要在编译层面就完成代理的逻辑，那就直接来：

实现步骤：

1. 定义一个接口和它的实现类
2. 创建一个代理类，这个代理类也得实现这个接口
3. 将实现类的实例注入代理类中。

这样一来，我们就可以用代理类屏蔽对最基础的实现类的访问，并且在目标方法前后添加新的东西，而不需要改变目标方法本身。

示例代码：

背景：我在Steam上玩游戏，想给游戏安装模组。

```java
//定义模组操作的接口
public interface IModOperation
{
    int install(String mod);
}


//实现上面的接口
public class ModRealization implements IModOperation
{

    @Override
    public int install(String mod) {
        System.out.println("安装" + mod + "模组");
        if (mod.isEmpty()) {
            return 0;
        } else {
            return 1;
        }
    }
}

//创建代理类，并注入实现类
public class ModProxy implements IModOperation
{
    IModOperation target;

    ModProxy(IModOperation target) {
        this.target = target;
    }

    @Override
    public int install(String mod) {
        //在install之前干的事：
        System.out.println("before");


        int value = target.install(mod);


        //在install之后干的事
        System.out.println("after");


        return value;
    }
}
```

代理类的测试：

```java
public class Main
{
    public static void main(String[] args) {
        IModOperation modOperation = new ModRealization();
        IModOperation proxy = new ModProxy(modOperation);
        proxy.install("FPS booster");
    }
}
```

输出为：
```
before
安装FPS booster模组
after
```

代理的基本逻辑是实现了，但是他也有他的缺陷：

1. 如果需要在接口中新添加方法，从接口到实现类再到代理类全部都得进行修改
2. 每个接口都得写一个代理类，这样一来，如果以后不止有模组相关的，还有什么评论相关，DLC相关，他们都各是一个接口，那么代理类就会越来越多

# 动态代理

相较于静态代理，动态代理更加灵活，我们不再需要自己手动实现代理类，可以让一些工具帮助我们在运行时动态生成代理类，这些动态生成的方式用到了Java的反射。

## JDK动态代理

JDK动态代理是JDK 1.3后引入的特性，其核心API是`Proxy`类和`InvocationHandler`接口，前者就是代理类，而后者有点类似于Servlet的Filter，用于指明在需要代理的方法前后需要干的事。它的原理是利用反射机制在运行时生成代理类的字节码。

好像说的这些很空洞，那还是整理一下逻辑：

1. 定义一个接口及其实现类。
2. 自定义 `InvocationHandler` 并重写`invoke`方法，在 `invoke` 方法中我们会调用原生方法（被代理类的方法）并自定义一些处理逻辑。
3. 通过 `Proxy.newProxyInstance(ClassLoader loader,Class<?>[] interfaces,InvocationHandler h)` 方法创建代理对象。

说着很抽象，还是看一个例子：

```java
//基础接口
public interface IModOperation
{
    int install(String mod);
}

//基础接口的实现
public class ModRealization implements IModOperation
{

    @Override
    public int install(String mod) {
        System.out.println("安装" + mod + "模组");
        if (mod.isEmpty()) {
            return 0;
        } else {
            return 1;
        }
    }
}

//InvocationHandler
public class LogHandler<T> implements InvocationHandler
{
    T target;

    public LogHandler(T target) {
        this.target = target;
    }

    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        //do sth before
        System.out.println("before invoking");

        Object value = method.invoke(target, args);

        //do sth after
        System.out.println("after invoking");

        return value;
    }
}

//ProxyFactory
public class ProxyFactory
{
    public static <T> T getLogProxy(T target) {
        return (T) Proxy.newProxyInstance(
                target.getClass().getClassLoader(),
                target.getClass().getInterfaces(),
                new LogHandler(target));
    }
}
```

测试：
```java
public class Main
{
    public static void main(String[] args) {
        //System.getProperties().put("sun.misc.ProxyGenerator.saveGeneratedFiles", "true");
        //System.getProperties().put("jdk.proxy.ProxyGenerator.saveGeneratedFiles", "true");

        IModOperation modProxy = ProxyFactory.getLogProxy(new ModRealization());
        modProxy.install("Infinity Money");
    }
}
```

### 代理类对象怎么生成

凭感觉，也知道这个对象应该是通过反射实例化的，毕竟这里也没有现成的类容它`new`一个出来，更别说这些类还不一定长得一样。

那么下面请欣赏类Proxy的源码：
这里只截取有用的`newProxyInstance`这一个方法的代码：
```java
@CallerSensitive
public static Object newProxyInstance(ClassLoader loader,
                                      Class<?>[] interfaces,
                                      InvocationHandler h)
    throws IllegalArgumentException
{
    Objects.requireNonNull(h);

    final Class<?>[] intfs = interfaces.clone();
    final SecurityManager sm = System.getSecurityManager();
    if (sm != null) {
        checkProxyAccess(Reflection.getCallerClass(), loader, intfs);
    }

    /*
     * Look up or generate the designated proxy class.
     */
    Class<?> cl = getProxyClass0(loader, intfs);

    /*
     * Invoke its constructor with the designated invocation handler.
     */
    try {
        if (sm != null) {
            checkNewProxyPermission(Reflection.getCallerClass(), cl);
        }

        final Constructor<?> cons = cl.getConstructor(constructorParams);
        final InvocationHandler ih = h;
        if (!Modifier.isPublic(cl.getModifiers())) {
            AccessController.doPrivileged(new PrivilegedAction<Void>() {
                public Void run() {
                    cons.setAccessible(true);
                    return null;
                }
            });
        }
        return cons.newInstance(new Object[]{h});
    } catch (IllegalAccessException|InstantiationException e) {
        throw new InternalError(e.toString(), e);
    } catch (InvocationTargetException e) {
        Throwable t = e.getCause();
        if (t instanceof RuntimeException) {
            throw (RuntimeException) t;
        } else {
            throw new InternalError(t.toString(), t);
        }
    } catch (NoSuchMethodException e) {
        throw new InternalError(e.toString(), e);
    }
}
```

第18行，获取了代理类的Class对象，说明这个时候代理类已经加载了。

接着在`try`块里看到利用这个Class对象在获取构造方法，结合到`Proxy`类中的字段：
`private static final Class<?>[] constructorParams =
        { InvocationHandler.class };`，可以推断出这个构造方法应该是长这个样子的：`XXXProxy(InvocationHandler){.....}`
        
最后返回值则是这个构造方法构造出来的对象了，也就是代理类对象

### 代理类对象如何调用方法

凭感觉，`LogHandler`对象中注入了实现类，并且其`invoke()`方法中对某个方法取得了调用，那么假如我们的代理类能够调用这个`invoke`方法并且传入正确的参数，那么就可以实现动态代理了。

在反编译`modProxy`所对应类的字节码文件之后，发现还真是这么一回事：

```java
public final class $Proxy0 extends Proxy implements IModOperation {
    private static Method m1;
    private static Method m3;
    private static Method m2;
    private static Method m0;

    public $Proxy0(InvocationHandler var1) throws  {
        super(var1);
    }

    public final boolean equals(Object var1) throws  {
        try {
            return (Boolean)super.h.invoke(this, m1, new Object[]{var1});
        } catch (RuntimeException | Error var3) {
            throw var3;
        } catch (Throwable var4) {
            throw new UndeclaredThrowableException(var4);
        }
    }

    public final int install(String var1) throws  {
        try {
            return (Integer)super.h.invoke(this, m3, new Object[]{var1});
        } catch (RuntimeException | Error var3) {
            throw var3;
        } catch (Throwable var4) {
            throw new UndeclaredThrowableException(var4);
        }
    }

    public final String toString() throws  {
        try {
            return (String)super.h.invoke(this, m2, (Object[])null);
        } catch (RuntimeException | Error var2) {
            throw var2;
        } catch (Throwable var3) {
            throw new UndeclaredThrowableException(var3);
        }
    }

    public final int hashCode() throws  {
        try {
            return (Integer)super.h.invoke(this, m0, (Object[])null);
        } catch (RuntimeException | Error var2) {
            throw var2;
        } catch (Throwable var3) {
            throw new UndeclaredThrowableException(var3);
        }
    }

    static {
        try {
            m1 = Class.forName("java.lang.Object").getMethod("equals", Class.forName("java.lang.Object"));
            m3 = Class.forName("JDKProxy.IModOperation").getMethod("install", Class.forName("java.lang.String"));
            m2 = Class.forName("java.lang.Object").getMethod("toString");
            m0 = Class.forName("java.lang.Object").getMethod("hashCode");
        } catch (NoSuchMethodException var2) {
            throw new NoSuchMethodError(var2.getMessage());
        } catch (ClassNotFoundException var3) {
            throw new NoClassDefFoundError(var3.getMessage());
        }
    }
}
```

注意其中的`Method m3`,构造方法和`public final int install(String var1) throws`这三个东西。

在代理类初始化的时候，`m3 = Class.forName("JDKProxy.IModOperation").getMethod("install", Class.forName("java.lang.String"));`，明显使用了反射来获取方法信息

代理类构造实例时，调用`super(var1)`，使得这个实例对象的`InvocationHandler h`字段的值即为我们传入的那个`handler`

代理类调用函数`install()`时，调用的其实是`handler`的`invoke()`方法。

这下就把 `modProxy.install("Infinity Money");`给整明白了。

### 另

为了提高`ProxyFactory`中代码的可重用性，可以作以下修改：
```java
public class ProxyFactory
{
    public static <T> T getLogProxy(T target, Class<?> handler) {
        try {
            Constructor<?> cons = handler.getConstructors()[0];
            InvocationHandler invocationHandler = (InvocationHandler) cons.newInstance(target);

            return (T) Proxy.newProxyInstance(
                    target.getClass().getClassLoader(),
                    target.getClass().getInterfaces(),
                    invocationHandler);
        } catch (Exception e) {
            return null;
        }
    }
}
```
测试：
```java
public class Main
{
    public static void main(String[] args) {
        //System.getProperties().put("sun.misc.ProxyGenerator.saveGeneratedFiles", "true");
        //System.getProperties().put("jdk.proxy.ProxyGenerator.saveGeneratedFiles", "true");

        IModOperation modProxy = ProxyFactory.getLogProxy(new ModRealization(),LogHandler.class);
        modProxy.install("Infinity Money");
    }
}
```
这样就可以指定委托的`InvocationHandler`

同时也可以增加更多的`InvocationHandler`和接口，而不需要对`ProxyFactory`作改动
## CGLIB动态代理

JDK动态代理虽然好，但是它毕竟需要委托的方法得在接口里边。

如果没有接口，就可以去使用CGLIB动态代理，它的代理类是实现类的一个子类。

CGLIB的核心API是`MethodInterceptor` 接口和`Enhancer` 类，我们需要自定义一个`MethodInterceptor`，在其中拦截实现类的方法，与JDK动态代理中的`InvocationHandler`很像。而`Enhancer`类是用来获取代理类的。

因为这是第三方的，所以需要先添加依赖：
```xml
 <dependency>
    <groupId>cglib</groupId>
    <artifactId>cglib</artifactId>
    <version>3.3.0</version>
</dependency>
```

然后编写代码步骤如下：

1.  定义一个类
1.  自定义 `MethodInterceptor` 并重写 `intercept` 方法
1.  通过 `Enhancer` 类的 `create()`方法创建代理类

示例代码：
```java
//实现类
public class Mod
{
    public int install(String mod) {
        System.out.println("安装" + mod + "模组");
        if (mod.isEmpty()) {
            return 0;
        } else {
            return 1;
        }
    }
}

//MethodInterceptor
public class LogMethodInterceptor implements MethodInterceptor
{
    /** 
      * @param o 被代理的对象（需要增强的对象） 
      * @param method 被拦截的方法（需要增强的方法)
      * @param args 方法入参
      * @param methodProxy 用于调用原始方法 
      */
    @Override
    public Object intercept(Object o, Method method, Object[] objects, MethodProxy methodProxy) throws Throwable {
        //do sth before
        System.out.println("before");
        Object value = methodProxy.invokeSuper(o, objects);
        //do sth after
        System.out.println("after");
        return value;
    }
}

//ProxyFactory
public class ProxyFactory
{
    public static <T> T getProxy(T target, Class<?> methodInterceptor) {
        try {
            Enhancer enhancer = new Enhancer();
            enhancer.setClassLoader(target.getClass().getClassLoader());
            enhancer.setSuperclass(target.getClass());
            Constructor<?> constructor = methodInterceptor.getConstructors()[0];
            MethodInterceptor methodInterceptor1 = (MethodInterceptor) constructor.newInstance();
            enhancer.setCallback(methodInterceptor1);
            return (T) enhancer.create();
        } catch (Exception e) {
            return null;
        }
    }
}
```

测试：
```java
public class Main
{
    public static void main(String[] args) {
        //System.setProperty(DebuggingClassWriter.DEBUG_LOCATION_PROPERTY, "./proxyByCglib");

        Mod modProxy;

        modProxy = ProxyFactory.getProxy(new Mod(), LogMethodInterceptor.class);
        modProxy.install("TM:PE");
    }
}
```

### 分析

参考资料：
https://www.jianshu.com/p/9a61af393e41

### 代理类如何调用方法

如同JDK动态代理，我们期望的是代理类中会有一个`install()`方法，这个方法调用了我们编写的`LogMethodinterceptor`中的`intercept方法`。

再想办法反编译代理类后，我们得到了三个文件：


先看`Mod$$EnhancerByCGLIB$$491ee2af.class的反编译文件`
```java
//
// Source code recreated from a .class file by IntelliJ IDEA
// (powered by FernFlower decompiler)
//

package CGLIBProxy;

import java.lang.reflect.Method;
import net.sf.cglib.core.ReflectUtils;
import net.sf.cglib.core.Signature;
import net.sf.cglib.proxy.Callback;
import net.sf.cglib.proxy.Factory;
import net.sf.cglib.proxy.MethodInterceptor;
import net.sf.cglib.proxy.MethodProxy;

public class Mod$$EnhancerByCGLIB$$491ee2af extends Mod implements Factory {
    private boolean CGLIB$BOUND;
    public static Object CGLIB$FACTORY_DATA;
    private static final ThreadLocal CGLIB$THREAD_CALLBACKS;
    private static final Callback[] CGLIB$STATIC_CALLBACKS;
    private MethodInterceptor CGLIB$CALLBACK_0;
    private static Object CGLIB$CALLBACK_FILTER;
    private static final Method CGLIB$install$0$Method;
    private static final MethodProxy CGLIB$install$0$Proxy;
    private static final Object[] CGLIB$emptyArgs;
    private static final Method CGLIB$equals$1$Method;
    private static final MethodProxy CGLIB$equals$1$Proxy;
    private static final Method CGLIB$toString$2$Method;
    private static final MethodProxy CGLIB$toString$2$Proxy;
    private static final Method CGLIB$hashCode$3$Method;
    private static final MethodProxy CGLIB$hashCode$3$Proxy;
    private static final Method CGLIB$clone$4$Method;
    private static final MethodProxy CGLIB$clone$4$Proxy;

    static void CGLIB$STATICHOOK1() {
        CGLIB$THREAD_CALLBACKS = new ThreadLocal();
        CGLIB$emptyArgs = new Object[0];
        Class var0 = Class.forName("CGLIBProxy.Mod$$EnhancerByCGLIB$$491ee2af");
        Class var1;
        Method[] var10000 = ReflectUtils.findMethods(new String[]{"equals", "(Ljava/lang/Object;)Z", "toString", "()Ljava/lang/String;", "hashCode", "()I", "clone", "()Ljava/lang/Object;"}, (var1 = Class.forName("java.lang.Object")).getDeclaredMethods());
        CGLIB$equals$1$Method = var10000[0];
        CGLIB$equals$1$Proxy = MethodProxy.create(var1, var0, "(Ljava/lang/Object;)Z", "equals", "CGLIB$equals$1");
        CGLIB$toString$2$Method = var10000[1];
        CGLIB$toString$2$Proxy = MethodProxy.create(var1, var0, "()Ljava/lang/String;", "toString", "CGLIB$toString$2");
        CGLIB$hashCode$3$Method = var10000[2];
        CGLIB$hashCode$3$Proxy = MethodProxy.create(var1, var0, "()I", "hashCode", "CGLIB$hashCode$3");
        CGLIB$clone$4$Method = var10000[3];
        CGLIB$clone$4$Proxy = MethodProxy.create(var1, var0, "()Ljava/lang/Object;", "clone", "CGLIB$clone$4");
        CGLIB$install$0$Method = ReflectUtils.findMethods(new String[]{"install", "(Ljava/lang/String;)I"}, (var1 = Class.forName("CGLIBProxy.Mod")).getDeclaredMethods())[0];
        CGLIB$install$0$Proxy = MethodProxy.create(var1, var0, "(Ljava/lang/String;)I", "install", "CGLIB$install$0");
    }

    final int CGLIB$install$0(String var1) {
        return super.install(var1);
    }

    public final int install(String var1) {
        MethodInterceptor var10000 = this.CGLIB$CALLBACK_0;
        if (var10000 == null) {
            CGLIB$BIND_CALLBACKS(this);
            var10000 = this.CGLIB$CALLBACK_0;
        }

        if (var10000 != null) {
            Object var2 = var10000.intercept(this, CGLIB$install$0$Method, new Object[]{var1}, CGLIB$install$0$Proxy);
            return var2 == null ? 0 : ((Number)var2).intValue();
        } else {
            return super.install(var1);
        }
    }

    final boolean CGLIB$equals$1(Object var1) {
        return super.equals(var1);
    }

    public final boolean equals(Object var1) {
        MethodInterceptor var10000 = this.CGLIB$CALLBACK_0;
        if (var10000 == null) {
            CGLIB$BIND_CALLBACKS(this);
            var10000 = this.CGLIB$CALLBACK_0;
        }

        if (var10000 != null) {
            Object var2 = var10000.intercept(this, CGLIB$equals$1$Method, new Object[]{var1}, CGLIB$equals$1$Proxy);
            return var2 == null ? false : (Boolean)var2;
        } else {
            return super.equals(var1);
        }
    }

    final String CGLIB$toString$2() {
        return super.toString();
    }

    public final String toString() {
        MethodInterceptor var10000 = this.CGLIB$CALLBACK_0;
        if (var10000 == null) {
            CGLIB$BIND_CALLBACKS(this);
            var10000 = this.CGLIB$CALLBACK_0;
        }

        return var10000 != null ? (String)var10000.intercept(this, CGLIB$toString$2$Method, CGLIB$emptyArgs, CGLIB$toString$2$Proxy) : super.toString();
    }

    final int CGLIB$hashCode$3() {
        return super.hashCode();
    }

    public final int hashCode() {
        MethodInterceptor var10000 = this.CGLIB$CALLBACK_0;
        if (var10000 == null) {
            CGLIB$BIND_CALLBACKS(this);
            var10000 = this.CGLIB$CALLBACK_0;
        }

        if (var10000 != null) {
            Object var1 = var10000.intercept(this, CGLIB$hashCode$3$Method, CGLIB$emptyArgs, CGLIB$hashCode$3$Proxy);
            return var1 == null ? 0 : ((Number)var1).intValue();
        } else {
            return super.hashCode();
        }
    }

    final Object CGLIB$clone$4() throws CloneNotSupportedException {
        return super.clone();
    }

    protected final Object clone() throws CloneNotSupportedException {
        MethodInterceptor var10000 = this.CGLIB$CALLBACK_0;
        if (var10000 == null) {
            CGLIB$BIND_CALLBACKS(this);
            var10000 = this.CGLIB$CALLBACK_0;
        }

        return var10000 != null ? var10000.intercept(this, CGLIB$clone$4$Method, CGLIB$emptyArgs, CGLIB$clone$4$Proxy) : super.clone();
    }

    public static MethodProxy CGLIB$findMethodProxy(Signature var0) {
        String var10000 = var0.toString();
        switch (var10000.hashCode()) {
            case -508378822:
                if (var10000.equals("clone()Ljava/lang/Object;")) {
                    return CGLIB$clone$4$Proxy;
                }
                break;
            case 1440131895:
                if (var10000.equals("install(Ljava/lang/String;)I")) {
                    return CGLIB$install$0$Proxy;
                }
                break;
            case 1826985398:
                if (var10000.equals("equals(Ljava/lang/Object;)Z")) {
                    return CGLIB$equals$1$Proxy;
                }
                break;
            case 1913648695:
                if (var10000.equals("toString()Ljava/lang/String;")) {
                    return CGLIB$toString$2$Proxy;
                }
                break;
            case 1984935277:
                if (var10000.equals("hashCode()I")) {
                    return CGLIB$hashCode$3$Proxy;
                }
        }

        return null;
    }

    public Mod$$EnhancerByCGLIB$$491ee2af() {
        CGLIB$BIND_CALLBACKS(this);
    }

    public static void CGLIB$SET_THREAD_CALLBACKS(Callback[] var0) {
        CGLIB$THREAD_CALLBACKS.set(var0);
    }

    public static void CGLIB$SET_STATIC_CALLBACKS(Callback[] var0) {
        CGLIB$STATIC_CALLBACKS = var0;
    }

    private static final void CGLIB$BIND_CALLBACKS(Object var0) {
        Mod$$EnhancerByCGLIB$$491ee2af var1 = (Mod$$EnhancerByCGLIB$$491ee2af)var0;
        if (!var1.CGLIB$BOUND) {
            var1.CGLIB$BOUND = true;
            Object var10000 = CGLIB$THREAD_CALLBACKS.get();
            if (var10000 == null) {
                var10000 = CGLIB$STATIC_CALLBACKS;
                if (var10000 == null) {
                    return;
                }
            }

            var1.CGLIB$CALLBACK_0 = (MethodInterceptor)((Callback[])var10000)[0];
        }

    }

    public Object newInstance(Callback[] var1) {
        CGLIB$SET_THREAD_CALLBACKS(var1);
        Mod$$EnhancerByCGLIB$$491ee2af var10000 = new Mod$$EnhancerByCGLIB$$491ee2af();
        CGLIB$SET_THREAD_CALLBACKS((Callback[])null);
        return var10000;
    }

    public Object newInstance(Callback var1) {
        CGLIB$SET_THREAD_CALLBACKS(new Callback[]{var1});
        Mod$$EnhancerByCGLIB$$491ee2af var10000 = new Mod$$EnhancerByCGLIB$$491ee2af();
        CGLIB$SET_THREAD_CALLBACKS((Callback[])null);
        return var10000;
    }

    public Object newInstance(Class[] var1, Object[] var2, Callback[] var3) {
        CGLIB$SET_THREAD_CALLBACKS(var3);
        Mod$$EnhancerByCGLIB$$491ee2af var10000 = new Mod$$EnhancerByCGLIB$$491ee2af;
        switch (var1.length) {
            case 0:
                var10000.<init>();
                CGLIB$SET_THREAD_CALLBACKS((Callback[])null);
                return var10000;
            default:
                throw new IllegalArgumentException("Constructor not found");
        }
    }

    public Callback getCallback(int var1) {
        CGLIB$BIND_CALLBACKS(this);
        MethodInterceptor var10000;
        switch (var1) {
            case 0:
                var10000 = this.CGLIB$CALLBACK_0;
                break;
            default:
                var10000 = null;
        }

        return var10000;
    }

    public void setCallback(int var1, Callback var2) {
        switch (var1) {
            case 0:
                this.CGLIB$CALLBACK_0 = (MethodInterceptor)var2;
            default:
        }
    }

    public Callback[] getCallbacks() {
        CGLIB$BIND_CALLBACKS(this);
        return new Callback[]{this.CGLIB$CALLBACK_0};
    }

    public void setCallbacks(Callback[] var1) {
        this.CGLIB$CALLBACK_0 = (MethodInterceptor)var1[0];
    }

    static {
        CGLIB$STATICHOOK1();
    }
}
```

注意：
1. 看到这个类是`Mod`的一个子类，说明如果`Mod`是`final`类，那么将无法使用CGLIB动态代理
2. 53行方法`final int CGLIB$install$0(String var1)`直接返回了`Mod`中的原先的实现，相当于没有代理
3. 57行方法`public final int install(String var1)`，首先是判断有没有所需的`MethodInterceptor`，如果没有就直接返回了`Mod`中的原先的实现，相当于没有代理，如果有，就调用的是这个`MethodInterceptor`的`intercept()`方法

这个时候就要去试图考察`MethodInterceptor`的`intercept()`方法中的`methodProxy.invokeSuper()`到底干了些啥。

通过强行调断点，发现：
1. main()方法中的modProxy的类就是`Mod$$EnhancerByCGLIB$$491ee2af`，坐实了它就是代理类
2. 调用的`methodProxy.invokeSuper()`的参数一个是刚才代理类对象，一个是参数列表。问题就来了——指定的方法跑哪儿去了？

那么继续看methodProxy的源码，观察invokeSuper()的代码:
```java
public Object invokeSuper(Object obj, Object[] args) throws Throwable {
    try {
        init();
        FastClassInfo fci = fastClassInfo;
        return fci.f2.invoke(fci.i2, obj, args);
    } catch (InvocationTargetException e) {
        throw e.getTargetException();
    }
}
```

通过调断点发现`f2`是刚才代理类对象的一个`FastClass`，`fci.i2`是一个int编号，obj是代理类对象，args是方法参数。 所以可以大胆的猜测，这个int编号就从某种程度上成为了`install()`方法的代号。

从网上查阅资料后，发现CGLIB中调用方法的方式并非是Java的反射，而是把代理类的那些方法给编了个号，通过编号来对应那些方法，强行写switch来调用方法。

反编译这个`FastCLass`（`Mod$$EnhancerByCGLIB$$491ee2af$$FastClassByCGLIB$$cad6a4b0.class`）后，也证实了这一切：

```java
//
// Source code recreated from a .class file by IntelliJ IDEA
// (powered by FernFlower decompiler)
//

package CGLIBProxy;

import CGLIBProxy.Mod..EnhancerByCGLIB..491ee2af;
import java.lang.reflect.InvocationTargetException;
import net.sf.cglib.core.Signature;
import net.sf.cglib.proxy.Callback;
import net.sf.cglib.reflect.FastClass;

public class Mod$$EnhancerByCGLIB$$491ee2af$$FastClassByCGLIB$$cad6a4b0 extends FastClass {
    public Mod$$EnhancerByCGLIB$$491ee2af$$FastClassByCGLIB$$cad6a4b0(Class var1) {
        super(var1);
    }

    public int getIndex(Signature var1) {
        String var10000 = var1.toString();
        switch (var10000.hashCode()) {
            case -2055565910:
                if (var10000.equals("CGLIB$SET_THREAD_CALLBACKS([Lnet/sf/cglib/proxy/Callback;)V")) {
                    return 12;
                }
                break;
            case -1882565338:
                if (var10000.equals("CGLIB$equals$1(Ljava/lang/Object;)Z")) {
                    return 15;
                }
                break;
            case -1457535688:
                if (var10000.equals("CGLIB$STATICHOOK1()V")) {
                    return 20;
                }
                break;
            case -1411842725:
                if (var10000.equals("CGLIB$hashCode$3()I")) {
                    return 17;
                }
                break;
            case -894172689:
                if (var10000.equals("newInstance(Lnet/sf/cglib/proxy/Callback;)Ljava/lang/Object;")) {
                    return 6;
                }
                break;
            case -623122092:
                if (var10000.equals("CGLIB$findMethodProxy(Lnet/sf/cglib/core/Signature;)Lnet/sf/cglib/proxy/MethodProxy;")) {
                    return 14;
                }
                break;
            case -508378822:
                if (var10000.equals("clone()Ljava/lang/Object;")) {
                    return 3;
                }
                break;
            case -419626537:
                if (var10000.equals("setCallbacks([Lnet/sf/cglib/proxy/Callback;)V")) {
                    return 9;
                }
                break;
            case 560567118:
                if (var10000.equals("setCallback(ILnet/sf/cglib/proxy/Callback;)V")) {
                    return 8;
                }
                break;
            case 811063227:
                if (var10000.equals("newInstance([Ljava/lang/Class;[Ljava/lang/Object;[Lnet/sf/cglib/proxy/Callback;)Ljava/lang/Object;")) {
                    return 5;
                }
                break;
            case 973717575:
                if (var10000.equals("getCallbacks()[Lnet/sf/cglib/proxy/Callback;")) {
                    return 10;
                }
                break;
            case 1221173700:
                if (var10000.equals("newInstance([Lnet/sf/cglib/proxy/Callback;)Ljava/lang/Object;")) {
                    return 4;
                }
                break;
            case 1230699260:
                if (var10000.equals("getCallback(I)Lnet/sf/cglib/proxy/Callback;")) {
                    return 11;
                }
                break;
            case 1306468936:
                if (var10000.equals("CGLIB$toString$2()Ljava/lang/String;")) {
                    return 16;
                }
                break;
            case 1355964014:
                if (var10000.equals("CGLIB$install$0(Ljava/lang/String;)I")) {
                    return 19;
                }
                break;
            case 1440131895:
                if (var10000.equals("install(Ljava/lang/String;)I")) {
                    return 7;
                }
                break;
            case 1584330438:
                if (var10000.equals("CGLIB$SET_STATIC_CALLBACKS([Lnet/sf/cglib/proxy/Callback;)V")) {
                    return 13;
                }
                break;
            case 1800494055:
                if (var10000.equals("CGLIB$clone$4()Ljava/lang/Object;")) {
                    return 18;
                }
                break;
            case 1826985398:
                if (var10000.equals("equals(Ljava/lang/Object;)Z")) {
                    return 0;
                }
                break;
            case 1913648695:
                if (var10000.equals("toString()Ljava/lang/String;")) {
                    return 1;
                }
                break;
            case 1984935277:
                if (var10000.equals("hashCode()I")) {
                    return 2;
                }
        }

        return -1;
    }

    public int getIndex(String var1, Class[] var2) {
        switch (var1.hashCode()) {
            case -1776922004:
                if (var1.equals("toString")) {
                    switch (var2.length) {
                        case 0:
                            return 1;
                    }
                }
                break;
            case -1295482945:
                if (var1.equals("equals")) {
                    switch (var2.length) {
                        case 1:
                            if (var2[0].getName().equals("java.lang.Object")) {
                                return 0;
                            }
                    }
                }
                break;
            case -1053468136:
                if (var1.equals("getCallbacks")) {
                    switch (var2.length) {
                        case 0:
                            return 10;
                    }
                }
                break;
            case -394068476:
                if (var1.equals("CGLIB$install$0")) {
                    switch (var2.length) {
                        case 1:
                            if (var2[0].getName().equals("java.lang.String")) {
                                return 19;
                            }
                    }
                }
                break;
            case -124978609:
                if (var1.equals("CGLIB$equals$1")) {
                    switch (var2.length) {
                        case 1:
                            if (var2[0].getName().equals("java.lang.Object")) {
                                return 15;
                            }
                    }
                }
                break;
            case -60403779:
                if (var1.equals("CGLIB$SET_STATIC_CALLBACKS")) {
                    switch (var2.length) {
                        case 1:
                            if (var2[0].getName().equals("[Lnet.sf.cglib.proxy.Callback;")) {
                                return 13;
                            }
                    }
                }
                break;
            case -29025555:
                if (var1.equals("CGLIB$hashCode$3")) {
                    switch (var2.length) {
                        case 0:
                            return 17;
                    }
                }
                break;
            case 85179481:
                if (var1.equals("CGLIB$SET_THREAD_CALLBACKS")) {
                    switch (var2.length) {
                        case 1:
                            if (var2[0].getName().equals("[Lnet.sf.cglib.proxy.Callback;")) {
                                return 12;
                            }
                    }
                }
                break;
            case 94756189:
                if (var1.equals("clone")) {
                    switch (var2.length) {
                        case 0:
                            return 3;
                    }
                }
                break;
            case 147696667:
                if (var1.equals("hashCode")) {
                    switch (var2.length) {
                        case 0:
                            return 2;
                    }
                }
                break;
            case 161998109:
                if (var1.equals("CGLIB$STATICHOOK1")) {
                    switch (var2.length) {
                        case 0:
                            return 20;
                    }
                }
                break;
            case 495524492:
                if (var1.equals("setCallbacks")) {
                    switch (var2.length) {
                        case 1:
                            if (var2[0].getName().equals("[Lnet.sf.cglib.proxy.Callback;")) {
                                return 9;
                            }
                    }
                }
                break;
            case 1154623345:
                if (var1.equals("CGLIB$findMethodProxy")) {
                    switch (var2.length) {
                        case 1:
                            if (var2[0].getName().equals("net.sf.cglib.core.Signature")) {
                                return 14;
                            }
                    }
                }
                break;
            case 1543336189:
                if (var1.equals("CGLIB$toString$2")) {
                    switch (var2.length) {
                        case 0:
                            return 16;
                    }
                }
                break;
            case 1811874389:
                if (var1.equals("newInstance")) {
                    switch (var2.length) {
                        case 1:
                            String var10001 = var2[0].getName();
                            switch (var10001.hashCode()) {
                                case -845341380:
                                    if (var10001.equals("net.sf.cglib.proxy.Callback")) {
                                        return 6;
                                    }
                                    break;
                                case 1730110032:
                                    if (var10001.equals("[Lnet.sf.cglib.proxy.Callback;")) {
                                        return 4;
                                    }
                            }
                        case 2:
                        default:
                            break;
                        case 3:
                            if (var2[0].getName().equals("[Ljava.lang.Class;") && var2[1].getName().equals("[Ljava.lang.Object;") && var2[2].getName().equals("[Lnet.sf.cglib.proxy.Callback;")) {
                                return 5;
                            }
                    }
                }
                break;
            case 1817099975:
                if (var1.equals("setCallback")) {
                    switch (var2.length) {
                        case 2:
                            if (var2[0].getName().equals("int") && var2[1].getName().equals("net.sf.cglib.proxy.Callback")) {
                                return 8;
                            }
                    }
                }
                break;
            case 1905679803:
                if (var1.equals("getCallback")) {
                    switch (var2.length) {
                        case 1:
                            if (var2[0].getName().equals("int")) {
                                return 11;
                            }
                    }
                }
                break;
            case 1951977610:
                if (var1.equals("CGLIB$clone$4")) {
                    switch (var2.length) {
                        case 0:
                            return 18;
                    }
                }
                break;
            case 1957569947:
                if (var1.equals("install")) {
                    switch (var2.length) {
                        case 1:
                            if (var2[0].getName().equals("java.lang.String")) {
                                return 7;
                            }
                    }
                }
        }

        return -1;
    }

    public int getIndex(Class[] var1) {
        switch (var1.length) {
            case 0:
                return 0;
            default:
                return -1;
        }
    }

    public Object invoke(int var1, Object var2, Object[] var3) throws InvocationTargetException {
        Mod..EnhancerByCGLIB..491ee2af var10000 = (Mod..EnhancerByCGLIB..491ee2af)var2;
        int var10001 = var1;

        try {
            switch (var10001) {
                case 0:
                    return new Boolean(var10000.equals(var3[0]));
                case 1:
                    return var10000.toString();
                case 2:
                    return new Integer(var10000.hashCode());
                case 3:
                    return var10000.clone();
                case 4:
                    return var10000.newInstance((Callback[])var3[0]);
                case 5:
                    return var10000.newInstance((Class[])var3[0], (Object[])var3[1], (Callback[])var3[2]);
                case 6:
                    return var10000.newInstance((Callback)var3[0]);
                case 7:
                    return new Integer(var10000.install((String)var3[0]));
                case 8:
                    var10000.setCallback(((Number)var3[0]).intValue(), (Callback)var3[1]);
                    return null;
                case 9:
                    var10000.setCallbacks((Callback[])var3[0]);
                    return null;
                case 10:
                    return var10000.getCallbacks();
                case 11:
                    return var10000.getCallback(((Number)var3[0]).intValue());
                case 12:
                    491ee2af.CGLIB$SET_THREAD_CALLBACKS((Callback[])var3[0]);
                    return null;
                case 13:
                    491ee2af.CGLIB$SET_STATIC_CALLBACKS((Callback[])var3[0]);
                    return null;
                case 14:
                    return 491ee2af.CGLIB$findMethodProxy((Signature)var3[0]);
                case 15:
                    return new Boolean(var10000.CGLIB$equals$1(var3[0]));
                case 16:
                    return var10000.CGLIB$toString$2();
                case 17:
                    return new Integer(var10000.CGLIB$hashCode$3());
                case 18:
                    return var10000.CGLIB$clone$4();
                case 19:
                    return new Integer(var10000.CGLIB$install$0((String)var3[0]));
                case 20:
                    491ee2af.CGLIB$STATICHOOK1();
                    return null;
            }
        } catch (Throwable var4) {
            throw new InvocationTargetException(var4);
        }

        throw new IllegalArgumentException("Cannot find matching method/constructor");
    }

    public Object newInstance(int var1, Object[] var2) throws InvocationTargetException {
        Mod..EnhancerByCGLIB..491ee2af var10000 = new Mod..EnhancerByCGLIB..491ee2af;
        Mod..EnhancerByCGLIB..491ee2af var10001 = var10000;
        int var10002 = var1;

        try {
            switch (var10002) {
                case 0:
                    var10001.<init>();
                    return var10000;
            }
        } catch (Throwable var3) {
            throw new InvocationTargetException(var3);
        }

        throw new IllegalArgumentException("Cannot find matching method/constructor");
    }

    public int getMaxIndex() {
        return 20;
    }
}
```

注意：

159行：getIndex()方法中，把`CGLIB$install$0`方法映射到了19

336行：invoke()方法，把19对应到了`new Integer(var10000.CGLIB$install$0((String)var3[0]));`

恰好，发现`fci.i2`就是19。

这就说明这个语句调用了代理类的`CGLIB$install$0()`方法。

而之前所说的代理类的`CGLIB$install$0`就相当于直接运行原先的实现，这就给说通了。