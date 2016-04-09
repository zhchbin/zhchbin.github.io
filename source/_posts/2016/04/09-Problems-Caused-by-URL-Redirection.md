title: "一个URL跳转引发的一系列“惨案”"
date: 2016-04-09 13:45:01
tags: [XSS, 安全]
---

## 前言

在知乎的题目和答案中，插入的链接都会变成`https://link.zhihu.com/target=xxx`的形式进行URL跳转，如下图。然而这个看似简单的功能的实现上，曾引发过一系列的问题，过程挺精彩，所以我就来做个总结，以重新体验一下这个过程。声明：以下小节中提到的问题均来自WooYun已经公开的漏洞，复现的代码也是纯属我个人YY。
![ZhihuURLRedirect](/images/20160409140054.png)

## 0x00 没有任何过滤

案例：[知乎 URL 跳转造成的 XSS](http://www.wooyun.org/bugs/wooyun-2016-0171240)

猜测知乎可能的实现方式：
```python
# -*- coding: utf-8 -*-

from flask import Flask, request
app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    target = request.args.get('target')
    return '''<script>window.location.href = "%s"</script>''' % (target)


if __name__ == "__main__":
    app.run(debug=True)

```

在上面这个实现中，我们可以发现对于`"`并没有进行转义，因此我们可以传入`"`来闭合前面的双引号，然后再插入我们的JS代码。运行上面的程序`python server.py`，然后使用curl请求：
```bash
$ curl '127.0.0.1:5000/?target=";alert(1);window.location.href="http://www.zhihu.com'
<script>window.location.href = "";alert(1);window.location.href="http://www.zhihu.com"</script>
```
![XSS_1](/images/20160409141842.png)

## 0x01 对参数做了urlencode编码

在上面的漏洞报告之后，（猜测）知乎的工程师按照了洞主给出的修复方案进行代码的修改，修改后的代码如下：

```python
# -*- coding: utf-8 -*-

import urllib
from flask import Flask, request
app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    target = request.args.get('target')
    return '''<script>
var URI="%s";
window.location.href = decodeURIComponent(URI);
</script>''' % (urllib.quote(target))


if __name__ == "__main__":
    app.run(debug=True)
```
现在，我们如果在target参数中传入`"`，则先会被转义成`%22`插入在页面中，从而无法闭合之前的双引号。看似一个挺好的的解决方案吧，然而，却还不够。案例：[知乎某处XSS+刷粉超详细漏洞技术分析](http://www.wooyun.org/bugs/wooyun-2016-0179329)。我们可以看到后台将输入的target参数传入给URI参数，解码以后赋值于location.href。问题解决了？没有，可以利用JavaScript:伪协议执行js代码，如
```
http://127.0.0.1:5000/?target=javascript:alert(1);
```
![XSS_2](/images/20160409143927.png)

强烈推荐仔细阅读这个案例哦，洞主的分析利用过程保证你看了会觉得很有收获。

## 0x02 使用WTForm进行URL校验

（猜测开发内心OS）既然如此，Python不是有个叫做`WTForm`的库可以帮我们校验用户的输入是否合法吗？我们可以利用里面的[wtforms.validators.URL](http://wtforms.readthedocs.org/en/latest/validators.html?highlight=URL#wtforms.validators.URL)进行URL的检查，这样子用户的输入该合法了吧。
```python
# -*- coding: utf-8 -*-

from flask import Flask, request
from wtforms import StringField
from wtforms.form import Form
from wtforms.validators import DataRequired, URL

import urllib

app = Flask(__name__)


class UrlForm(Form):
    target = StringField(validators=[DataRequired(), URL()])


@app.route('/', methods=['GET'])
def index():
    form = UrlForm(request.args)
    if not form.validate():
        return "Bad Boy!"

    target = form.target.data.encode('utf8')
    return '''<script>
var URI="%s";
window.location.href = decodeURIComponent(URI);
</script>''' % (urllib.quote(target))


if __name__ == "__main__":
    app.run(debug=True)
```

这里也有可能是开发自己写正则进行匹配，问题本质上都是一样的，正则写的不好。上面的写法虽然已经能过滤到前面提到的情况，然而，WTForm的正则过滤并没有写好，导致继续被XSS。如下的URL：
```
http://127.0.0.1:5000/?target=javascript://www.baidu.com/%E2%80%A8alert(1)
```
![XSS_3](/images/20160409151521.png)

具体分析见案例[知乎某处XSS导致刷粉](http://www.wooyun.org/bugs/wooyun-2016-0182145)及[从WTForm的URLXSS谈开源组件的安全性](http://drops.wooyun.org/papers/13058)

## 0x03 除了XSS之外的一个彩蛋

这里本身其实是一个任意URL调整，可以在某些实现不严格的OAuth2.0的过程中利用偷取用户的授权code，然后使用用户的身份进行登录哦。在我之前的博客已经分析过这个问题，这里就不再写了。案例：[微博上你点我链接我就上你绑定过的知乎账号](http://www.wooyun.org/bugs/wooyun-2016-0174018)

## 总结

做一个程序员不容易啊！请善待我们。