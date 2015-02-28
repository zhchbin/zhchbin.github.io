layout: post
title: "如何加入开源项目"
comments: true
category: 
tags: [OpenSource]
---

在过去的一年多时间里，我很幸运地为两个开源项目贡献了几千行代码。在node-webkit的提交记录中，我有34个Commits，在Chromium中，用了六个月的时间也提交了30+个Commits，可以说对如何加入开源社区有一点点的自己的看法了。写这篇博客的目的是为了记录下我的经验，希望可以鼓励更多像我一样希望为开源项目做贡献的学生参与到自己喜欢的开源社区中。说真的，花时间参与一个优秀的开源项目，将你大学期间自学的一些东西应用于实践中，还能接触到你在大学课堂上几乎不可能学到的知识，比起为了拿多那么点分数而努力完成作业值多了。

我为什么会花费这么多精力在这个事情上？

第一点：“大学里时间太多，为了不像周围其他同学一样虚度，做一些有意义的事情，就开始参与 Chromium 了。” 这句话是我发邮件感谢方觉【0】在我第一次提交代码时指导我解决问题的时候他回复我的。参与开源社区就是一个很有意义的事情。当你作为一个开源项目成长的见证者和贡献者，当其他人谈到这个项目的时候，难道不会小心脏稍微激动一下吗？补充一下背景：node-webkit，目前在Github上有7000+的Star的一个C++项目，我在它只有几百个Star就接触到，并且贡献了上千行代码。

第二点：帮人家解决问题是一种能力，也是一种乐趣。在node-webkit的issue list中，有人说这个问题：@zhchbin能解决，还专门发邮件给我让我帮忙看看，然后还说要给我100美刀作为Bounty的时候，我很开心。并不是因为解决问题了能够得到他说的100美刀，而是人家信任你，觉得你有能力去帮助他们解决问题。在Chromium的Issue List中，每当我看到人家给我的代码提交回复一个thanks/awesome的时候，我也会暗喜的，毕竟这些人都是Google的软件工程师，他们在认可你做出的努力。

第三点：学到的总会比付出的翻倍。在做开源项目的过程中，每解决一个问题就会学习到该问题相关领域的知识，比如在这段时间内我接触到了Win32 API/GTK+/X11等。还可以体验到如何与其他人协同工作。Chromium上的Reviewer总能给我一些启发，他可以在代码的层次上直接教你正确的写代码方式以及如何写出其他人也看得懂的代码！在这段期间，我知道了测试代码的重要性，知道了代码风格的重要性。

还有不少点，这里就先不废话了。

我听过不少人想要为开源项目做贡献，却总是被开源项目的门槛吓跑了。的确，我觉得我真正弄懂node-webkit代码的时候是我决定转去Chromium社区的时候，那个时候我已经为node-webkit写了两个多月（IIRC）。而就算我有为node-webkit写过代码的经验，在进入Chromium社区的时候也是遇到了很大的困难。接下来，我就写一下，在我看来，应该怎么样子加入一个开源社区，以为Chromium贡献代码为例子。

第一：感性地认识Chromium，了解源代码目录结构。应该知道Google Chrome浏览器就是依托Chromium这个开源项目的，在每个Chrome浏览器中你都能找到这么一句话：“Google Chrome is made possible by the Chromium open source project and other open source software.”。其实我这里想讲的是编译并运行。在大中华局域网中拉下几个G的代码是个煎熬的过程，而且随时都会断掉然后那个仓库的代码就只能重新下载了。在[Chromium的网站中][1]就能够找到如何在各个平台下编译的指导。简单地说：就是安装必要的开发库，用gclient下载源码并且gyp产生相应的工程文件(gclient sync)，编译(推荐使用ninja)。

第二：阅读相关文档，了解Chromium的整体架构。这里说的相关文档是比较坑爹的，文档那么多。其实要耐心，文档你肯定一开始是看不懂的，比如这篇入门必看文档之：[Chrome的多进程架构][2]。

第三：到Chromium的[Issue List][3]上找一些问题看，在你本地编译出来的Chrome上重现该问题，尝试想想怎么解决，或者看人家怎么解决。上面的问题很多，我这里分享一个我自己看的Issue的标签：Cr-Platform-Apps Hotlist-GoodFirstBug Cr-Platform-Extensions Cr-Platform-Extensions-API Cr-Platform-Apps-AppLauncher Cr-Platform-Apps-Container 都是关于Chrome Extension/Packaged App的，用gmail登录后在 Subscriptions页面中填入这些个标签，在工作日每天你就能收到30+份邮件。这些标签是基于我之前做过一些浏览器的插件和应用，对这个东西还是知道点门路的情况的。因此我很多代码提交都是集中在Chrome Extension/Packaged App APIs上的。

第四：代码搜索工具：https://code.google.com/p/chromium/codesearch， 这个工具太好用，也太重要了！当你在看人家的代码时，可以利用这个工具找到具体的代码实现，而且通常情况下要好好阅读相关代码的注释。

第五：分享一点我解决问题的思路，基于对代码的熟悉程度才能解决的问题这个我没法怎么分享经验。这里想说的其实是如何在如此庞大的项目中定位到需要修改的代码的地方。在遇到程序Crash的时候（经常是空指针的情况），我们其实可以利用gdb（在Linux上），VS2010中Attach to Process的功能（在Windows上）得到程序奔溃的时候的调用栈，然后利用上面的代码搜索工具就可以找到相应的代码了。接下来，就是认真读懂相关的代码，用你的聪明才智想出一个合理的解决方法。如果遇到的问题是chrome://settings/类似URL页面（这些页面都是采用HTML/CSS/JS实现的，webui）中的，那就可以用F12调出开发工具，找到页面元素的ID值，然后还是在上面的搜索工具中查找相关的代码。

......


第N：相信自己。上面讲的那些东西，无非是为了引出最后这个点。如果你真的感兴趣，相信自己，坚持，加油。


“这个事情如果不是我去完成，那么还有谁会去做呢？“


【0】: 在第一次提交代码到Chromium上的时候认识的，当时多亏了他的指导啊，感谢。
[1]: http://www.chromium.org/Home
[2]: http://www.chromium.org/developers/design-documents/multi-process-architecture
[3]: https://code.google.com/p/chromium/issues/list
