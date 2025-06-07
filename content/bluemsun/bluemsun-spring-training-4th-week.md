---
title: 蓝旭23春季培训-第4周预习
date: 2023-04-04
---
# Servlet

## 什么是Servlet

> Java Servlet 是运行在 Web 服务器或应用服务器上的程序，它是作为来自 Web 浏览器或其他 HTTP 客户端的请求和 HTTP 服务器上的数据库或应用程序之间的中间层。

我们可以把Servlet理解为服务器端处理数据的Java小程序.可以通过Servlet来让我们的Java程序与网页进行交互.

这是一个~~从网上扒来的~~简要的流程图:

![16034279-a3206d8fefca7f97.webp](../data/bluemsun/bluemsun-spring-training-4th-week/f3b0eb5bb6fe41dabb136325a89cbcbc~tplv-k3u1fbpfcp-watermark.image)

我们安装的Tomcat就是Web容器,也就是图片中灰白色圆角矩形的那部分,也就是HTTP服务器+Servlet容器.

首先用户在浏览器中(最左边)发送请求,HTTP服务器程序收到请求并解析之后就转交给了Servlet容器,于是乎,Servlet容器就把这一大坨的请求给转换为一个`HttpServletRequest`对象.紧接着,会读取我们写的`web.xml` 配置,找到能够处理这个请求的Servlet类,并将其实例化,将 `HttpServletRequest` 对象, `HttpServletResponse` 对象作为参数传入 `service()` 方法中,然后在根据不同的HTTP请求调用不同的方法,例如`doGet`用来处理GET请求之类的.

在这些方法中的有关网页的操作也会被逆向地由Tomcat转化为HTTP响应,然后再由HTTP服务器程序对浏览器进行响应.

## 如何在Idea中部署Tomcat

1.  要在环境变量中添加CATALINA_BASE CATALINA_HOME Path CLASSPATH之类的东西.
2.  在idea-设置-构建执行部署-应用程序服务器中添加应用程序服务器,并在库中添加Tomcat安装目录中lib文件夹里面的jar文件.
3.  右击模块-添加框架支持,选择Java EE中的Web应用程序确认创建web.xml并确定
4.  在工件中添加Web应用程序:展开形,并单击基于模块,于是就新建了一个WAR包,然后注意要把输出目录改到tomcat安装目录的webapps文件夹下
5.  在模块中要把记得添加这个Web框架,并且在依赖菜单栏中添加库Tomcat
6.  单击运行/调试配置,创建一个本地的Tomcat服务器,创建后在部署菜单栏中中把之前新建的工件添加进去,在服务器菜单栏的URL中写入:`http://localhost:端口号+部署菜单中的应用程序上下文`

[贴一个解决了我404问题的一个链接](https://blog.csdn.net/fannyoona/article/details/113933113)

## 以Servlet为基础的webapp的结构

其实,在上一节中第3步我们就借助了idea帮我们完成了这一webapp目录结构的搭建工作.

![屏幕截图 2023-04-13 195559.png](../data/bluemsun/bluemsun-spring-training-4th-week/aee1d7c07ccd48fa8ed7f7235a184feb~tplv-k3u1fbpfcp-watermark.image)

由于规定了WEB-INF文件夹是Java的Web应用安全目录,客户端无法访问而服务端可以访问,因此能给客户端访问的静态资源应该放在外面,而java的字节码文件就放在classes里.

### web.xml

针对这个web.xml文件,他是用来配置初始化信息的.比如Welcome页面、servlet、servlet-mapping、filter、listener、启动加载级别等.

比较常用的标签有:

*   servlet : 给一个Servlet类和一个名字联系起来
*   servlet-mapping : 给一个servlet绑定一个uri的路径(注意这个uri的路径一定要以/开头)
*   init-param : 定制初始化的参数
*   welcome-file-list :指定一个欢迎界面,欢迎页默认就是进入网站后弹出来的第一个页面
*   error-page :设置一个对应错误码的错误页面
*   filter : 拦截 Servlet 请求和响应,对其进行处理或修改.
*   filter-mapping : 与servlet-mapping类似,这是指定filter的拦截的url范围
*   listener : 设置监听,主要用于在某些请求或事件发生时能够迅速地响应
*   session : 会话,它是一种存储机制,用于在多个请求之间保存和共享数据.(有点类似于我的世界末影箱) 这这里可以配置其超时时间,Cookie属性之类的

```xml
    <?xml version="1.0" encoding="UTF-8"?>

    <web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee http://xmlns.jcp.org/xml/ns/javaee/web-app_4_0.xsd"
          version="4.0"> 
          
          <!-- 一般路过的欢迎页 --> 
          
          <welcome-file-list> 
              <welcome-file>/static/test2.html</welcome-file> 
              <welcome-file>/static/index.jsp</welcome-file> 
          </welcome-file-list> 
          
          <!-- 这个是用来定义Servlet的,是把一个名字和一个全限定名的类联系起来 --> 
          
          <servlet> <servlet-name>MyServlet</servlet-name> 
              <servlet-class>com.bluemsun.test.MyServlet</servlet-class> 
              <init-param> 
                  <param-name>param2</param-name> 
                  <param-value>awsl</param-value> 
              </init-param> 
          </servlet>
          
        <!-- 这个是用来映射Servlet到一个URL的 -->
        
        <servlet-mapping>
            <servlet-name>MyServlet</servlet-name>
            <url-pattern>/myservlet</url-pattern>
        </servlet-mapping>

    </web-app>
```

## 编写Servlet类

### Servlet程序的生命周期

Servlet与其它有生命的东西一样,都有从创建到销毁的过程,不过专业地讲,就是初始化阶段,运行时阶段和销毁阶段.

#### 初始化阶段

一般而言,是Web容器第一次请求到这个Servlet(而不是Tomcat服务器启动)的时候这个对应的Servlet类将会被实例化并调用方法init().

注意:

1.  由于这个Servlet类的实例化是经由Java反射调用其无参构造方法形成的,因此一定要确保这个Servlet类有一个无参的构造方法.
2.  一个Servlet的init()在其生命周期内有且有就只会被调用一次.

#### 运行时阶段

当处于运行时阶段,只要Servlet容器收到了客户端请求,就如上文所说,会创建`ServletRequest` 对象和 `ServletResponse` 对象并把它们作为参数传入 `service()` 方法中.

请求处理完毕后,就会用这个ServletResponse来响应用户.当响应信息被传回客户端后,这两个对象会被销毁掉.

#### 销毁阶段

当Servlet容器被关闭或者这个实例被销毁的时候,容器就会调用destroy()方法,可以重写这个方法比如在里面关闭IO流,关闭数据库连接之类的以释放资源.

### 实现Servlet接口

![14021Mc6-0.png](../data/bluemsun/bluemsun-spring-training-4th-week/bdf9ccb62fa243c6afad70bd4074b5ce~tplv-k3u1fbpfcp-watermark.image)

先从这个图看到Servlet,GenericServlet,HttpServlet和我们程序员自己创建的MyServlet的关系

Servlet是一个大的抽象的接口,而GenericServlet是一个实现了Servlet接口的类,而HttpServlet是GenericServlet的一个子类.

#### 直接实现Servlet接口

一般来说,要实现Servlet接口,只需要这样:

```java
class Servlet1 implements Servlet
{
    ServletConfig sc;
    @Override
    public void init(ServletConfig servletConfig) throws ServletException {
        this.sc=servletConfig;
    }

    @Override
    public ServletConfig getServletConfig() {
        return sc;
    }

    @Override
    public void service(ServletRequest servletRequest, ServletResponse servletResponse) throws ServletException, IOException {

    }

    @Override
    public String getServletInfo() {
        return "正在下载Ubuntu 22.04";
    }

    @Override
    public void destroy() {
        
    }
}
```

##### ServletConfig

其中ServletConfig用于获取当前Servlet的配置信息.可以在init()的时候把参数ServletConfig参数存储下来来获取,也可以调用`this.getServletConfig()`.

可以通过调用ServletConfig的getServletName获得Servlet的名字,getServletContext获得对应的ServletContext,getInitParameter获得对应Servlet的init-param.

注意:对应于某一个Servlet的init-param不可以用ServletContext来读取,ServletContext只能读取全局的init-param.

##### ServletContext

而所谓的ServletContext官方叫法是Servlet上下文,Web服务器会给一个项目创建一个可供所有Servlet程序访问的且唯一的ServletContext.从它的范围可知,我们可以用它在不同的Servlet之间传递数据.

如果要向其中存储数据,可以采取setAttribute(name,value)方法,把一个键值对存进去,getAttribute(name)就可以访问读取,而removeAttribute(name)就可以删除.总之:用法类似于Map.

当然,它也可以用于读取全局的init-param,即getInitParameter(name).还可以通过getResourcePaths(name)等等获取各种Web资源文件,细节可以反编译ServiceContext.java后看到.

#### 利用GenericServlet实现

但是一般我们都用不着重写所有的这些方法,比如init(),destroy(),getServletInfo()方法,这个时候就可以构建一个GenericServlet的子类,这个时候就只需要重写service()方法即可,使得我们不用写一堆冗余的代码,而将精力集中到service上.

```java
public class Servlet1 extends GenericServlet
{
    @Override
    public void service(ServletRequest servletRequest, ServletResponse servletResponse) throws ServletException, IOException {
        servletResponse.setContentType("text/html;charset=utf-8");
        servletResponse.getWriter().println("不管遇到什么Request,我都会出现的");
    }
}
```

#### 利用HttpServlet实现

考虑到Servlet通常都用于处理HTTP请求和响应,所以说为了方便,就做了一个GenericServlet的http特化版的HttpServlet.

如果我们程序员以它为父类写了一个Servlet子类,那可以把精力集中到处理HTTP的各种请求上,例如有GET,POST,DELETE,PUT等请求. 因为在HttpServlet中已经把service()方法重写成了按照不同的请求调用不同的do请求()方法,因此我们只需要重写do请求()方法.

最好不要直接重写service()方法,因为如果没有为所有种类的请求都给出处理方法,就容易发生405错误.

下面是一个处理GET请求的Servlet

```java
public class MyServlet extends HttpServlet
{
    @Override
    public void init() throws ServletException {
        System.out.println("Servlet启动");
    }
    @Override
    public void doGet(HttpServletRequest request,HttpServletResponse response) throws ServletException,IOException {
        String param1 = request.getParameter("param1");
        response.setContentType("text/html;charset=utf-8");
        response.getWriter().println("Servlet收到了HTTP传来的GET请求");
        response.getWriter().println("但它不准备做任何的事");
        response.getWriter().println("因为它一心只想要输出输进来的参数param1的值:" + param1);
        String param2 = this.getServletConfig().getInitParameter("param2");
        response.getWriter().println("除此之外这个Servlet还有一个initParam是:" + param2);
    }
    @Override
    public void destroy() {
        System.out.println("Servlet关闭");
    }
}
```

可以使用查询字符串即在URL后面添加上`?param1=value1&param2=value2`来发送一个GET请求.就像这样`http://localhost:8080/ServletDemo/myservlet?param1=154841545`,于是我们就能得到我们想要的结果:

![屏幕截图 2023-04-14 085409.png](../data/bluemsun/bluemsun-spring-training-4th-week/4e2290f1507f481b9445c056e06540a6~tplv-k3u1fbpfcp-watermark.image)

也可以再重写一个doPost()方法来处理POST请求,他不能用查询字符串来发送,因为查询字符串默认是GET请求,我们可以写一个Java程序来发送POST请求并接收响应.

```java
@Override
protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
    response.setContentType("text/html;charset=utf-8");
    response.getWriter().println("Servlet收到了HTTP传来的POST请求<br>");
    String param1 = request.getParameter("param1");
    response.getWriter().println("有一个param1 = " + param1 + "<br>");
}
```

应当说明的是,一个成熟的HTTP请求包括:请求行、请求头和消息主体数据.

格式如图所示:

![v2-bf990b661bcff759a17ce344416c7b15\_1440w.webp](../data/bluemsun/bluemsun-spring-training-4th-week/7baae7e2108d491497743e30d712ce93~tplv-k3u1fbpfcp-watermark.image)

例如,下面就是一个简单的的HTTP请求报文:

        POST /ServletDemo/myservlet HTTP/1.1
        Host: localhost:8080
        Content-Type: application/x-www-form-urlencoded
        Content-Length: 13

        {param1: value1}

于是我们可以用Java中的HttpURLConnection来发送一个POST请求报文

```java
public class Main
{
    public static void main(String[] args) {
        String targetUrl = "http://localhost:8080/ServletDemo/myservlet";
        String postData = "{param1:value1}"; 

        try {
            URL url = new URL(targetUrl);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("POST");
            //请求头
            connection.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");
            connection.setRequestProperty("Content-Length", Integer.toString(postData.length()));
            connection.setRequestProperty("Host","localhost:8080");
            //请求体
            connection.setDoOutput(true);
            DataOutputStream dos = new DataOutputStream(connection.getOutputStream());
            dos.writeBytes(postData);
            dos.flush();
            dos.close();

            int responseCode = connection.getResponseCode();
            System.out.println("Response Code: " + responseCode);
            BufferedReader br = new BufferedReader(new InputStreamReader(connection.getInputStream()));
            String inputLine;
            StringBuffer response = new StringBuffer();
            while ((inputLine = br.readLine()) != null) {
                response.append(inputLine);
            }
            br.close();
            System.out.println("Response: " + response.toString());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

Idea控制台输出是:
```
    Response Code: 200
    Response: Servlet收到了HTTP传来的POST请求<br>有一个param1 = value1<br>
```
##### HttpServletRequest

在HttpServletRequest中,可以访问有关HTTP请求的东西.

一般而言,要获取参数,可以利用HttpServletRequest的getParameter(name)方法,

同时还可以利用getHeader(var1)获取对应请求头的值,

getCookies()返回一个 Cookie 数组,表示客户端请求中包含的所有 Cookie,

getRemoteAddr()获取客户端的IP,

getMethod()获取HTTP请求的请求方式,

getRequestURI() 是一个URI的路径,

getContextPath()返回Servlet应用的名字.

##### RequestDispatcher

当我们想要在某一个Servlet实例中使用其他的Servlet的service()方法,我们就应当把当前的这个请求转发给另一个Servlet.这个时候就需要利用RequestDispatcher

要获取一个RequestDispatcher接口对象,可以调用HttpServletRequest.getRequestDispatcher(s)方法,s指的是其他资源的路径.

然后调用RequestDispatcher的forward()方法或者include()方法,

forward()方法指的是方法将当前请求转发给其他的 Web 资源进行处理,因此原先的Servlet的响应就作废了,只看被转发到的最终的一个Servlet的响应.

而include()方法指的是把另一个servlet处理过后的内容拿过来,意思就是之前Servlet的响应仍然保留,且存在先后关系.

但是他们还是有共通点的:他们都可以共享请求域,意思就是说在之前的Servlet中的setAttribute在之后转发到的Servlet也可以访问得到.

举个例子:
```java
public class MyServlet extends HttpServlet
{
    @Override
    public void init() throws ServletException {
        System.out.println("Servlet启动");
    }

    @Override
    public void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        String param1 = request.getParameter("param1");
        response.setContentType("text/html;charset=utf-8");
        response.getWriter().println("Servlet收到了HTTP传来的GET请求<br>");
        response.getWriter().println("但它不准备做任何的事<br>");
        response.getWriter().println("因为它一心只想要输出输进来的参数param1的值:" + param1 + "<br>");
        String param2 = this.getServletConfig().getInitParameter("param2");
        response.getWriter().println("除此之外这个Servlet还有一个initParam是:" + param2 + "<br>");
        request.setAttribute("name","Li Jiangnan");
        RequestDispatcher rd = request.getRequestDispatcher("/servlet1");
        rd.include(request,response);//rd.forward(request,response)
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        response.setContentType("text/html;charset=utf-8");
        response.getWriter().println("Servlet收到了HTTP传来的POST请求<br>");
        String param1 = request.getParameter("param1");
        response.getWriter().println("有一个param1 = " + param1 + "<br>");
    }

    @Override
    public void destroy() {
        System.out.println("Servlet关闭");
    }
}

public class Servlet1 extends GenericServlet
{
    @Override
    public void service(ServletRequest servletRequest, ServletResponse servletResponse) throws ServletException, IOException {
        servletResponse.setContentType("text/html;charset=utf-8");
        servletResponse.getWriter().println("不管遇到什么Request,我都会出现的");
        servletResponse.getWriter().println("Written by " + servletRequest.getAttribute("name"));
    }
}

```

使用forward()的效果是:

![屏幕截图 2023-04-14 180808.png](../data/bluemsun/bluemsun-spring-training-4th-week/6d6b5a7a88a84de880800fe6b6041aa3~tplv-k3u1fbpfcp-watermark.image)

使用include()的效果是

![屏幕截图 2023-04-14 175645.png](../data/bluemsun/bluemsun-spring-training-4th-week/a9c23bb77ce841668c01269bac338082~tplv-k3u1fbpfcp-watermark.image)

##### HttpServletResponse

首先贴一个防止输出乱码的一行代码,总之就是设置内容的编码为utf-8,MIME为html
`response.setContentType("text/html;charset=utf-8");`

先还是了解一下HTTP响应报文的格式:

![屏幕截图 2023-04-14 181603.png](../data/bluemsun/bluemsun-spring-training-4th-week/41b9039def604440bae1209b1a242268~tplv-k3u1fbpfcp-watermark.image)

首行为HTTP版本,状态码和状态码对应的信息,可以在https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Status 查询

响应头是关于响应的一些元信息,类似于请求头,也一样的和后面的正文有一个空行.

最后的是响应体,可以是各种各样的东西,主要看Content-Type是什么,客户机就怎么对响应体解析. 

因此对于状态行,可以setStatus(int)设置状态码并生成状态信息.

对于响应头,addHeader()可以增加一个响应头

而setHeader()可以设置一个响应头,

setContentType(str,str)用于设置MIME类型和字符编码,一般来说是设置成`response.setContentType("text/html;charset=utf-8");`

对于响应体,则采用类似于IO流的getOutputStream()和 getWriter()前者能写字节,后者写的是字符.

### Servlet重定向

重定向就是服务器收到客户机的请求后,响应让客户机重新发送一个另外的uri的请求的过程. 它和转发都做到了跳转Servlet,但是重定向有一个服务器通知客户机重新发送另一个请求的过程. 也是因为如此,得在ServletResponse中调用方法sendRedirect(String location)来给客户机发送一个302响应码,并且浏览器的URL栏是会变化的.

因为这完全是两个过程了,所以请求域都是不可共享的.

有如下例子:
```java
public class MyServlet extends HttpServlet
{
    @Override
    public void init() throws ServletException {
        System.out.println("Servlet启动");
    }

    @Override
    public void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        String param1 = request.getParameter("param1");
        response.setContentType("text/html;charset=utf-8");
        response.getWriter().println("Servlet收到了HTTP传来的GET请求<br>");
        response.getWriter().println("但它不准备做任何的事<br>");
        response.getWriter().println("因为它一心只想要输出输进来的参数param1的值:" + param1 + "<br>");
        String param2 = this.getServletConfig().getInitParameter("param2");
        response.getWriter().println("除此之外这个Servlet还有一个initParam是:" + param2 + "<br>");
        request.setAttribute("name","Li Jiangnan");
        response.sendRedirect("servlet1");
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        response.setContentType("text/html;charset=utf-8");
        response.getWriter().println("Servlet收到了HTTP传来的POST请求<br>");
        String param1 = request.getParameter("param1");
        response.getWriter().println("有一个param1 = " + param1 + "<br>");
    }

    @Override
    public void destroy() {
        System.out.println("Servlet关闭");
    }
}

public class Servlet1 extends GenericServlet
{
    @Override
    public void service(ServletRequest servletRequest, ServletResponse servletResponse) throws ServletException, IOException {
        servletResponse.setContentType("text/html;charset=utf-8");
        servletResponse.getWriter().println("不管遇到什么Request,我都会出现的<br>");
        servletResponse.getWriter().println("Written by " + servletRequest.getAttribute("name"));
    }
}
```

访问`http://localhost:8080/ServletDemo/myservlet`就会立马被重定向到`http://localhost:8080/ServletDemo/servlet1`,显示出:

![屏幕截图 2023-04-14 190147.png](../data/bluemsun/bluemsun-spring-training-4th-week/6b1b4765d45a445c949ea7e122ab93aa~tplv-k3u1fbpfcp-watermark.image)

## Cookie

> Cookie 属于客户端会话技术，它是服务器发送给浏览器的小段文本信息，存储在客户端浏览器的内存中或硬盘上。当浏览器保存了 Cookie 后，每次访问服务器，都会在 HTTP 请求头中将这个 Cookie 回传给服务器。

例如说为什么在登陆一些网站后在一定时间内不用再次登录就利用到了Cookie

如果想在我们的网页中也用上Cookie,可以调用HttpServletResponse.addCookie(cookie)方法.其中构造1个cookie需要一组键值对.构造后也可以设定其路径,域和存储的最大有效时间等.

举个例子:
```java
public class MyServlet extends HttpServlet
{
    @Override
    public void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        response.setContentType("text/html;charset=utf-8");
        response.getWriter().println("接收到了GET请求<br>");
        Cookie co = new Cookie("cookie1","一个曲奇");
        co.setDomain("localhost");
        co.setPath("/ServletDemo/myservlet");
        response.addCookie(co);
        for(Cookie c : request.getCookies()) {
            if("cookie1".equals(c.getName())) {
                response.getWriter().println("cookie1 = " + c.getValue() + "<br><br>");
            }
        }
        RequestDispatcher rd = request.getRequestDispatcher("/servlet1");
        rd.include(request,response);
    }
}

public class Servlet1 extends HttpServlet
{
    @Override
    public void service(HttpServletRequest servletRequest, HttpServletResponse servletResponse) throws ServletException, IOException {
        servletResponse.setContentType("text/html;charset=utf-8");
        for(Cookie c : servletRequest.getCookies()) {
            if("cookie1".equals(c.getName())) {
                servletResponse.getWriter().println("cookie1 = " + c.getValue());
            }
        }
    }
}
```
```xml
<?xml version="1.0" encoding="UTF-8"?>
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee http://xmlns.jcp.org/xml/ns/javaee/web-app_4_0.xsd"
         version="4.0">
    <!-- 一般路过的欢迎页 -->
    <welcome-file-list>
        <welcome-file>/static/test2.html</welcome-file>
        <welcome-file>/static/index.jsp</welcome-file>
    </welcome-file-list>
    <!-- 这个是用来定义Servlet的,是把一个名字和一个全限定名的类联系起来 -->
    <servlet>
        <servlet-name>MyServlet</servlet-name>
        <servlet-class>com.bluemsun.test.MyServlet</servlet-class>
        <init-param>
            <param-name>param2</param-name>
            <param-value>awsl</param-value>
        </init-param>
    </servlet>

    <!-- 这个是用来映射Servlet到一个URL的 -->
    <servlet-mapping>
        <servlet-name>MyServlet</servlet-name>
        <url-pattern>/myservlet</url-pattern>
    </servlet-mapping>

    <servlet>
        <servlet-name>Servlet1</servlet-name>
        <servlet-class>com.bluemsun.test.Servlet1</servlet-class>
    </servlet>

    <servlet-mapping>
        <servlet-name>Servlet1</servlet-name>
        <url-pattern>/servlet1</url-pattern>
    </servlet-mapping>

</web-app>
```

如果访问`http://localhost:8080/ServletDemo/myservlet`,
第一次会得到

`接收到了GET请求`

而第二次才会得到
```
接收到了GET请求  
cookie1 = 一个曲奇  
  
cookie1 = 一个曲奇
```

如果访问`http://localhost:8080/ServletDemo/servlet1` 则无论如何都是500错误

这是因为第一次添加Cookie的时候事实上是响应后到达客户端才添加上的,因此是找不到这个Cookie的.

由于Cookie的限定域在`/ServletDemo/myservlet`中,因此直接访问其他的域是找不到这个Cookie的,而对于转发,由于用的是include()方法,之前的response依然保留,则找得到Cookie,可以预见的是,如果采用forward()进行转发,那就肯定找不到Cookie了.

## Session

> Session是一种用于在客户端和服务器之间维护状态的机制,通常用于在多个请求之间保持用户会话状态.

相比Cookie,他最大的优点就是安全性更好,毕竟Session中的真正有用的值是存储在服务器端的,而暴露给客户机的只有一个SessionId.

在Servlet中,Session 是通过 HttpSession 接口来表示的.通过 HttpServletRequest.getSession() 方法可以获得 HttpSession 对象

它有如下的这些方法:

1.  setAttribute(String name, Object value): 向Session中设置一个键值对.
2.  getId(): 获取 SessionId,这个Id会出现在Cookie中
3.  getCreationTime(): 获取 Session 的创建时间.
4.  getLastAccessedTime(): 获取 Session 的最后访问时间.
5.  invalidate(): 使 Session 失效，即将 Session 从服务器端删除.
6.  setMaxInactiveInterval(int interval): 设置 Session 的最大不活动时间间隔，超过该时间间隔没有请求访问 Session 则会自动失效.
```
public class MyServlet extends HttpServlet
{
    @Override
    public void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        response.setContentType("text/html;charset=utf-8");
        response.getWriter().println("接收到了GET请求<br>");
        HttpSession hs = request.getSession();
        response.getWriter().println(hs.getId());
    }
}
```

访问`http://localhost:8080/ServletDemo/myservlet`后能看到:

![屏幕截图 2023-04-14 204812.png](../data/bluemsun/bluemsun-spring-training-4th-week/84d5fe2ff360464d8f4da81b1e0ecbd0~tplv-k3u1fbpfcp-watermark.image)

注意到的是,只要Session没有失效,则Session对本次会话期间的所有Servlet都有效.

## Filter

> Filter 不是一个Servlet,但它能够对 Servlet 容器传给 Web 资源的 request 对象和 response 对象进行检查和修改.

总之,它负责的就是拦截请求和响应并对Request和Response进行修改,也还能把拦截给传递下去,让另外的Filter继续或者交给一个Servlet.

要传递这个拦截,就可以用`filterChain.doFilter(servletRequest,servletResponse);`

这个Filter的链会从通过这句代码传递,直到遇到一个没有这句代码的Filter为止或者遇到最终的Servlet然后开始返回.

web.xml中filter-mapping的前后顺序便能够确定Filter链中Filter的前后关系.

举个栗子:

```
public class MyFilter implements Filter
{

    @Override
    public void init(FilterConfig filterConfig) throws ServletException {

    }

    @Override
    public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws IOException, ServletException {
        servletResponse.setContentType("text/html;charset=utf-8");
        servletResponse.getWriter().println("我是一个过滤器.现在是在处理请求.<br>");
        filterChain.doFilter(servletRequest,servletResponse);
        servletResponse.getWriter().println("我是一个过滤器.现在是在处理响应.<br>");
    }

    @Override
    public void destroy() {

    }
}

public class MyServlet extends HttpServlet
{
    @Override
    public void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        response.setContentType("text/html;charset=utf-8");
        response.getWriter().println("接收到了GET请求<br>");
        HttpSession hs = request.getSession();
        response.getWriter().println(hs.getId() + "<br>");
    }
}
```
在web.xml中添加

```xml
<filter>
    <filter-name>MyFilter</filter-name>
    <filter-class>com.bluemsun.filter.MyFilter</filter-class>
</filter>
<filter-mapping>
    <filter-name>MyFilter</filter-name>
    <url-pattern>/myservlet</url-pattern>
</filter-mapping>
```

访问`http://localhost:8080/ServletDemo/myservlet`得到的是:
```
我是一个过滤器.现在是在处理请求.  
接收到了GET请求  
6F9A78DE909AC588727881568471F22E  
我是一个过滤器.现在是在处理响应.
```

## Listener

> 监听器 Listener 是一个实现特定接口的 Java 程序，这个程序专门用于监听另一个 Java 对象的方法调用或属性改变，当被监听对象发生上述事件后，监听器某个方法将立即自动执行。

例如:ServletRequestListener就会监听ServletRequest,在它创建/销毁的时候就会自动开始运作.
而ServletContextAttributeListener就会监听ServletContext 对象的属性新增、移除和替换.

```java
public class MyListener implements ServletRequestListener
{
    @Override
    public void requestInitialized(ServletRequestEvent servletRequestEvent) {
        System.out.println("有个ServletRequest开始了!");
    }

    @Override
    public void requestDestroyed(ServletRequestEvent servletRequestEvent) {
        System.out.println("有个ServletRequest结束了!");
    }
}
```

```xml
<listener>  
    <listener-class>com.bluemsun.listener.MyListener</listener-class>  
</listener>
```

其中参数ServletRequestEvent可以获取到ServletContext和ServletRequest,然后就可以进行一定操作.

然后一旦进入某个网页,都会弹出
```
有个ServletRequest开始了!
有个ServletRequest结束了!
```

# 总结
1. MVC指的是一种软件设计模式,控制器负责接受用户的数据输入并根据用户不同的输入采取不同的模型和视图进行处理,模型负责应用程序的数据和业务逻辑,例如和数据库交互之类的,而视图则用于展示模型的数据,使之在用户面前可视化,现在变成了前端的任务.
2. `connection: keep alive`这个HTTP请求头表示客户端希望与服务器保持在处理完当前请求后不关闭连接,可以继续用于后续请求.这样可以减少每次请求的连接建立和断开开销,提高性能.
3. 在整个webapp的运行过程中,每个Servlet类都只会有一个实例存在,这就意味着Servlet的成员变量对于所有的客户端都是共享的,容易导致并发访问时的线程安全问题.
4. `load on startup`是servlet中的一个配置参数,用于指定 Servlet 在 Web 应用程序启动时是否自动加载,并指定加载的顺序.数字越小加载优先级越高.
5. servlet中的三个域:应用域>会话域>请求域.应用域指的是在整个 Web 应用程序中,存储在 ServletContext 对象中的数据,它可以在多个Servlet之间共享,直到Web程序被销毁.会话域指的是在用户会话过程中,存储在 HttpSession 对象中的数据.会话域中的数据可以在同一用户的多个请求之间共享,在用户会话结束后会被销毁.最小的是请求域,它指的是在一次 HTTP 请求过程中,存储在 HttpServletRequest 对象中的数据.请求域中的数据只在当前请求中有效,在请求结束后会被销毁.