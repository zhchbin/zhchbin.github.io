title: "[浏览器安全系列二] 百度浏览器远程命令执行"
date: 2016-09-01 23:49:59
tags: ["安全", "浏览器安全", "XSS"]

---

案例链接：http://wooyun.org/bugs/wooyun-2010-0216027

## 免责声明

本博客提供的部分文章思路可能带有攻击性，仅供安全研究与教学之用，风险自负!

## 百度浏览器远程命令执行

* 版本信息：8.4.100.3514
* 测试环境：(1)Windows 7 64 bit with IE 10 (2)Windows XP 32 bit with IE 8 

### 0x00 套路

为了实现远程命令执行，我们需要有两个条件：（1）下载可执行文件（比如exe，脚本之类的）到用户的系统中（2）启动我们的可执行程序。接下来的分析都是为了实现这个目标而进行的一系列探索及尝试。

### 0x01 UXSS与特权域

一个价值8000美刀的UXSS：https://bugs.chromium.org/p/chromium/issues/detail?id=560011 ，百度浏览器上也存在该问题。各种特权域的XSS问题都已经被之前的老司机们挖没有了，所以我们从UXSS入手是最快捷的方式。那百度浏览器的特权域有什么呢？在使用的过程中发现，百度浏览器应用中心（[https://chajian.baidu.com/2015/](https://chajian.baidu.com/2015/)）这个网站直接能够打开 bdbrowser://settings 这个页面。于是，我就分析了一下里面的代码，发现是使用了
```javascript
widnow.external.StartRequest(1158, "open_url",  "",  "[\"offside","bdbrowser://settings#extension\"]")
```

从而可以确定，这个域名可以使用`window.external.StartRequest`这个API。也就是说：我们可以通过UXSS -> 在百度浏览器应用中心的网站上调用以上的API。

![](http://ww3.sinaimg.cn/large/7184df6bgw1f7eiv3ahsij21020k7qal.jpg)

### 0x02 寻找文件下载

在日常使用浏览器的过程中，我们可以设置一个默认的文件下载路径，然后选择不提示。在百度浏览器中，也存在一个这样子的设置，而且可以直接通过上面的API进行设置。所以，我们可以设置其默认不提示，这样子就不需要用户交互完成文件的下载！那么，我们能知道文件的下载路径吗？一开始我是想像二哥那样：http://wooyun.org/bugs/wooyun-2010-083294 寻找一个能够直接修改其默认下载路径的接口，这样子就可以通过下载文件到用户的开机启动路径中完成RCE。不过，百度浏览器修改了这个设置的API，设置时会弹出选择窗口给用户选择路径。
![](http://ww2.sinaimg.cn/large/7184df6bgw1f7eivrv9qwj20hy03waaa.jpg)
![](http://ww2.sinaimg.cn/large/7184df6bgw1f7eiwf8fu3j213k0ns7ap.jpg)

哎，于是，换一个思路吧。我们尝试看看能不能获取到用户设置的默认路径吧！分析调试设置页面的源代码之后，我发现了以下的操作就可以获取到用户的默认路径！

```javascript
window.external.StartRequest(1162, "fetch_prefs.addListener", "console.log", "[]", "", window);
window.external.StartRequest(1163, "preference_ready", "", "[]", "", window);
```
![](http://ww1.sinaimg.cn/large/7184df6bgw1f7eiwyv7nfj21020k77pi.jpg)

### 0x03 执行？

完成文件的下载，我们又知道了文件在用户系统中的绝对路径。这个能干嘛啊？在寻找的过程中，我搜索了一下，找到了这样的一个链接：http://stackoverflow.com/a/5047811/1634804 这里是指在IE上通过ActiveXObject启动notepad.exe的代码。想到百度浏览器还有一个IE内核的时候，还是试试吧。没想到一试，发现居然可以直接执行，是的，什么提示都没有。一开始我还怀疑是我自己设置了IE的安全级别，发现测了手上的几个系统，还在虚拟机环境下进行测试，都发现能打开notepad。
```html
<script>
ws=new ActiveXObject("WScript.Shell");
ws.Exec("C:\\Windows\\notepad.exe");
</script>
```
![](http://ww4.sinaimg.cn/large/7184df6bgw1f7eixj8ejhj20ky07gdgq.jpg)

而在同一个系统上的IE浏览器，访问这个页面的时候会提示以下的信息。从这可以估计出百度浏览器在使用IE内核的时候，安全性级别设置的比较低。
```
SCRIPT429: Automation 服务器不能创建对象
```
![](http://ww3.sinaimg.cn/large/7184df6bgw1f7eixw2fsmj20fw08375u.jpg)

接下来，我们要怎么利用？在使用的过程中，发现百度浏览器大多会先使用WebKit引擎进行渲染，而且，我查了一下，没有任何可以设置的方式。所以，第一个想到的方案是做个界面欺骗用户切换成IE模式，这样子我们的RCE就大打折扣。

### 0x04 WebKit -> IE

想啊想！心中想起了一句话：中国特色社会主义。在China，很多银行的网站都默认只能使用IE，访问这些网站的时候，百度浏览器会不会很人性化的帮我们切换成IE内核呢？于是，继续测试，发现果然！打开工行，招行等银行的网站时，优先使用的是IE内核。
![](http://ww4.sinaimg.cn/large/7184df6bgw1f7eiyi6sd4j20my04cdgl.jpg)

于是，我们只要找到一个网站是银行的，且这个网站存在XSS或者前端界面可控的，就可以通过这个网站执行ActiveXObject了。不过找银行的貌似挺麻烦的，找了一会之后，我把思路换成了学校，因为学校的网站（edu.cn的子域）也是默认优先IE内核。找啊找，找到一个XSS，被IE的过滤器过滤，找到另外一个不会被过滤的，URL长度有限制且有关键词检查。最后，还是在母校找到了一个站点：
```
http://ecampus.sysu.edu.cn/zsuoa/application/pages/select_frame.jsp?url=http://baidu.com
```
这个页面会去加载使用iframe去加载url里执订的链接，虽然不是XSS，但是更好用！

### 0x05 真的可以执行

思路总结

1. UXSS 到 https://chajian.baidu.com/2015/
2. 修改用户的下载设置：自动下载到默认保存位置 (不再弹窗提醒)
3. 获取用户的的默认下载路径
4. 下载一个文件
5. 跳转到学校的网站，使用ActiveXObject执行我们下载的文件。

测试的GIF截图，下载并启动Everything。
![](http://ww1.sinaimg.cn/large/7184df6bgw1f7eizhdpabg20t10ktal7.gif)
