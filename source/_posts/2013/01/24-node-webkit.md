---
layout: post
title: "node-webkit系列（00）：什么是node-webkit？"
description: ""
category: node-webkit
comments: true
tags: []
---

这两个月来接触到一个开源项目：node-webkit（项目地址：[Link](https://github.com/rogerwang/node-webkit)），也做了一点点小小的CodeContribution。打算开始写一些文章，介绍一下这个开源项目，以及相关的技术细节实现。这是第0篇，就先作为一个简要的介绍吧。

###是什么？

node-webkit是一个基于chromium和node.js实现的应用程序运行时环境，也即是说我们可以通过HTML，CSS，JavaScript实现一个本地化的应用程序。整个项目最具创意的部分就是将node.js整合进来，使得应用开发者能够直接在DOM里使用node.js模块，大大增强了Web端JavaScript的能力。该项目是由Intel开源项目中心开发与维护的。

###架构概览

目前node-webkit是基于chrome content api实现的，架构图如下：  

![Arch](/images/arch.png)  

如果熟悉chrome这个浏览器架构的人一眼就可以看出来，node-webkit所处的层次与chrome是一致的，换句话说：node-webkit就是一个功能极简的web浏览器，它可以用来加载网页，执行JS脚本，不论是本地的html文件还是服务器端的文件。

* 至于什么是chrome content api呢？该模块的主要功能是采用多进程（包含Browser进程，Render进程以及GPU进程）的模型渲染一个页面。它包含了几乎所有的HTML5的特性以及GPU加速渲染。该模块的目的就是让想在应用程序中嵌入浏览器模块，但又不想包含全部浏览器所有功能的开发者使用的。
* 为什么要采用chrome content api而不是其他？
> * Content API提供了公开且稳定的接口，且相对于CEF3更加灵活。CEF3也是基于Content API实现的一个可以将渲染网页的功能嵌入到应用程序之中的框架，虽然其接口经过封装后使用起来相比比较简单和方便，但是当需要使用到Content API的很多功能时候，CEF3的接口可能做不到。
> * V8引擎的高效。众所周知，V8引擎对于Javascript这门语言的重要性，chrome浏览器的成功也得益于其执行Javascript的快速！而对于node-webkit，作为一个本地化的应用程序运行环境，javascript代码执行的效率也是至关重要的，使得应用程序与用户之间的交互更接近Native Application的流畅性。
> * 前面介绍Content API的时候也提到了，HTML5的特性以及GPU加速，对WebGL等的支持。最新版本在html5test.com测试得到的分数是：460。

###如何使用其进行开发？

接下来的这个部分将完成一个简单的应用程序。主要想体现的是：（1）使用node.js模块；（2）nw提供的增加本地化应用特性的API；（3）打包并发布你的应用程序。

* 了解应用程序结构。如下图所示，每个应用程序都会有一个package.json文件来描述应用程序的相关信息以及初始窗口的属性等。
![package](/images/package.png)

示例程序的package.json文件内容如下：（关于各个参数所代表的含义可以在wiki上查找：[Link](https://github.com/rogerwang/node-webkit/wiki/Manifest-format)）
```json
{
  "name": "nw-demo",
  "main": "index.html",
  "window": {
    "toolbar": false,
    "width": 500,
    "height": 600
  }
}
```
index.html文件的内容如下，该段代码主要是使用node.js的fs模块读取"E:/"目录下的文件夹，在每个文件夹的点击事件中，我们调用node-webkit中提供的shell接口在窗口管理器中打开该文件夹。

```html
<html>
  <head>
    <title>Hello World</title>
    <style type="text/css">
      body {font-family: Georgia,serif;}
      h1 {color: #527bbd;margin-bottom: 1.0em;line-height: 1.3;
        border-bottom: 2px solid silver;}
      .item {border-bottom: 2px solid silver;padding: 10px;cursor: pointer;}
    </style>
  </head>
  <body>
    <h1>Filesystem of your E:</h1>
    <script type="text/javascript">
      // Load native UI library.
      var gui = require('nw.gui');
      require('fs').readdir('E:/', function(err, files) {
        if (err) {
          document.write(err);
        } else {
          for (var i = 0; i < files.length; ++i) {
            var div = document.createElement('div'); 
            div.className = "item";
            var content = document.createTextNode(files[i]);
            div.appendChild(content);
            document.body.appendChild(div);
            div.onclick = function() {
              gui.Shell.openItem('E:/' + this.innerText);
            }
          }
        }
      });
    </script>
  </body>
</html>
```

* 打包应用并发布。具体的打包方法[Link](https://github.com/rogerwang/node-webkit/wiki/How-to-package-and-distribute-your-apps)。效果图

![effect](/images/effect.png)

###扯点node-webkit与chrome packaged app的不同。

* 更少的开发限制，更自由：在node-webkit中，我们可以发现其sandbox特性已经被关闭。熟悉chrome packaged app或者extension开发的人都知道其对安全性的要求之严格，比如CSP的限制。而在node-webkit中，这些限制都不存在，作为一个本地化的应用程序运行时环境，我个人觉得这个是非常重要的一点！

* 更本地化的接口：node-webkit实现了很多有关窗口操作的API，同时也实现了像菜单栏，系统的托盘图标支持，系统剪贴板等的API，目前还在不断的完善中。（我自己也参与到了一部分API的开发中，同时也修复了一些小bug。）

最后：目前采用node-webkit开发出来的应用程序列表：[Link](https://github.com/rogerwang/node-webkit/wiki/List-of-apps-and-companies-using-node-webkit)，据我所知道[LightTable](http://www.lighttable.com/)也是基于node-webkit实现的。
