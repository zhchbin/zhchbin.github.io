---
layout: post
title: "What is Pay Me to Learn"
category: 
tags: [OpenSource]
---

### 背景
今天早上才想起来，自己还欠着一件事情没有做完。很久在人人上之前看到过这样的一句话：
> I dropped out of college after Google SoC, because I had work that paid me to learn.

然后就在微博上大发感慨说：“突发奇想：等我搞定Google Summer of Code（不管最终结果如何），我就写一篇文章：什么叫做pay me to learn!”，事实上，估计我写的东西没有多少人会看。不过既然说了就要做到！好吧，接下来将写一下以下几点：

1. Google Summer of Code简介
2. 我怎么就能被选上呢？
3. 在参加GSoC的过程中我做了什么事情？
4. 我学到了什么呢？

### Google Summer of Code简介
Google从2005年其就开始举办这样的全球性活动，简单地用一句话概括一下，就是Google出钱给学生为开源项目写代码，而这个项目是在学生暑假期间举行，被选择上并成功完成的学生最终能够获得`5000美刀`的奖金。当然，Google的这个项目最想得到的是：提供给学生机会参与到真实的软件开发中，在项目结束后能够有所收获，并且还能继续投入到开源中，为开源社区做贡献。Google提供的是一个平台，在这上面开源项目可以找到对可能对项目发展有帮助的学生，学生可以申请参与到某个开源项目中。以上是我个人的一点理解，当然，也只有Google这样的公司才能耗费如此大的财力和物力做这样的一件事情，每年150+个开源项目， 1000+遍布世界的学生，这得花多少钱。哈哈，虽然对于大公司来说这个是小钱啊。

更详细官方的介绍还是要自己去官网上了解啊，这里提供一个[传送门][0]。

### 我怎么就能被选上呢？
当时我正大四下学期，从`Intel`实习结束回来的我还在努力地为node-webkit写着代码，每天查邮件，查issue，写代码的生活虽然很枯燥，但在解决问题及与人交流的过程中也学到不少。看着一个开源项目从`1000+ star`慢慢地增长到Github C++排名前几的过程对于我来说也算是一件值得骄傲的事情，尽管我只是一个默默无闻的贡献者。也就在这个过程中，在微博上看到了GSoC的宣传微博，顿时就觉得我应该可以去申请参与这样的一个事情。吸引我的另外一点当然还是钱的问题，毕竟那可以用来支付我研究生的一年的学费和生活费了。

看到可以申请的开源项目公布的时候，我有点失望的是node-webkit没有去申请。抱着一点点的希望，我扫了一遍那个列表，当发现有Chromium的时候有点欣喜。但同时我也在怀疑自己有没有机会。补充点点背景知识，node-webkit是一个将chromium和node.js整合在一起的App运行环境，也就是说，对于Chromium这么大的一个项目，我是有一点点....点点基础的。于是我就开始准备写申请。在chromium-dev的邮件列表中可以找到要求的大概是什么[传送门][1]？简简单单的几句话就完了，而且好像也没有多少人关注。

照着要求，我就开始挑些比较简单的Bug。我第一个选择的bug是[Issue 148463][2]：Report an error when chrome.app.window.create is called with a URL that doesn't exist. 看上去很简单解决嘛，直接加个代码检查文件是否存在不就OK了。但是问题远没有想象中的简单，当时我还不知道这样的一个操作是很耗费时间的IO过程，就算文件存在也不一定能够被加载等等问题。具体细节有兴趣的话可以看看当时我用我蹩脚的英文写的记录，[传送门][3]。

在第一个Bug未能解决后，坚哥建议我去看一下他发现的一个问题。[Issue 159302][4]: Extension icon doesn't refresh after reload the extension in chrome://extensions. 虽然一开始很顺利的解决，但是reviewer不赞同这样子的做法。经过一段曲折的过程，最终还是我解决的。中间的过程就忽略吧。而我第一个成功提交到chromium代码树中的是一个关于Content Shell的Tooltips在windows上不能够显示出来的问题，在提交的过程中还是遇到了一些小问题，不同平台下的文件换行符真是害死人啊，好在当时方觉给了点Tips！在这里顺便再次感谢。哈哈，从这个commit开始，源代码目录下的Author文件就有了我的名字和邮箱！

而我具体写的申请是在chrome的extensions/apps中加入全局快捷键的支持，发出去之后一直没有收到回复，所以我就觉得应该还做点什么事情的。幸运的事情是我看到了Chromium的Issue List中有人提到了相应的需求但是没有被实现，于是我就果断地发了一封邮件给了提需求的Google的工程师。他帮我把邮件转发给了另外一个感兴趣的组，当时我收到回复的时候真心感动得哭了！也就在他的帮助下，我觉得我应该能够被选中了！哈哈。

就这个样子，我就成了luck dog.

### 在参加GSoC的过程中我做了什么事情？

这一部分估计是一个很长很长的过程。在这期间，其实我每周都会记录下大概做了什么事情并给我的Mentor汇报工作，还是用的蹩脚的英文，感兴趣可以到[这里][5]阅读。总结成一句话就是，我在不断地找我能够解决的问题，写代码解决问题，测试，提交，照着reviewer的意见修改直到能够得到他们的`LGTM`。

第一个我比较满意的Change List是解决了Chrome Packaged App在多屏幕下的问题，具体的Bug是这个样子的，当电脑中外接了一个显示屏，将App的窗口拖到另外一个显示器上，关闭该窗口，断开显示器之后，窗口就没法重新在主屏幕上出现了。虽然一开始不知道从哪里下手，面对代码如此庞大的一个项目，但是慢慢地在尝试的过程中，我发现出现这个问题的原因是Chrome记录下了上一次窗口关闭的位置，当显示区域改变的时候，位置并没有跟着更新。经过一番思索之后，我觉得应该可以也记录下窗口的所在的屏幕大小，然后在创建窗口的时候去检查是否发生了改变，如果变了，就做一些调整窗口位置的操作，使得窗口能够在显示屏中出现。事实上，这个做法被接受了！！[最终代码][6]由@scheib帮我提交进去了。

第二件比较OK的事情就是利用X11的API将Ubuntu Unity Window Manager下GTK+没有了窗口的最小化事件。这个好像是Unity的一个Bug，也有可能是人家故意的。做法其实很简单，就是通过给窗口添加了一个Event Filter的函数，获取对应窗口属性，检查他是否有相应的最小化时应该有属性，然后将这个事件传递给应用窗口就可以顺利解决了！

其实在这期间我解决的问题不少，但都是类似的这种小问题，不过解决起来挺有挑战性的！每当解决一个问题的时候就能够学到该问题相关领域的知识。

接下来还是讲讲我的Proposal的事情。因为我要添加的是一个新的功能，所以得经过一定的流程，[具体流程][7]。一开始我也没有考虑到什么问题，觉得采用以下的API设计方式就搞定了。

```idl
namespace globalHotKeys {
  ...
  interface Functions {
    // Register a global hot key.
    static void register(HotKey hotKey);

    // Unregister a global hot key.
    static void unregister(HotKey hotKey);

    // Gets an array of all the global hot keys.
    static void getAll(optional GetAllCallback callback);
  };
  ...
};
```
实际上，这样子的设计根本就不可能被接受，因为这样子的设计方式给开发者太高的权限，Extension/App可以随时的修改全局快捷键。经过一段时间的讨论后，@Finnur建议从扩展chrome.commands入手，因为chrome.commands提供了chrome在有焦点的情况下的快捷键，可以共有不少代码。于是乎，最终的设计变成了如下所示。具体讨论的过程可以到相应的API Proposal中查看，[传送门][8]

```json
{
  "name" : "my extension",
  ...
  "commands": {
    "toggle-feature-foo": {
      "suggested_key": {
        "default": "Ctrl+Shift+Y",
        "mac": "Command+Shift+Y"
      },
      "description": "Toggle feature foo",
      "global": true                     ← default: false
    }
  },
  ...
}
```
在提议这个的过程中，我还接触到了Google的一位应该是PM的人，由于Chrome中NPAPI在2014年其就要被淘汰了以及在Packaged App中不支持NPAPI，而某个功能又需要能够检测到多媒体键的按键信息。比如说下一首，上一首，停止等多媒体键。所以，我的API Proposal也扩展成了现在这个样子，能够让chrome.commands支持多媒体键。虽然这个Proposal在最近才有代码上的进展，对于我自己来说，能够参与到这样子的一个过程，看着自己的想法正在一步步地实现中，有点小骄傲的说！！

关于这个功能的具体实现过程，有我在linux平台上的实现哦，有兴趣浏览一下代码的可以看看[这里][9]. 希望这个功能能够早点被大家所用啊！！

### 我学到了什么呢？
我觉得很多人都会不知道我上面那一段是在胡扯些什么。算了，不详细介绍上面的细节，要证明能参加GSoC的学生还是有点料的。

在前一段时间GSoC 2013就不知不觉地结束了，也就在这个时候，我意识到了这么有意义的三个月就Over了。打从心里觉得我提交了的代码根本不值那5000美刀，相反地，是Google给我了这些钱，让我去学习。Google给我机会去参与到真实的软件开发过程中。每次想到自己的代码能够通过Chrome这个产品被全世界那么多人使用到，觉得自己花了那么大的精力也值得啊。

哦，好像忘记了什么？在这个过程中，我觉得我的C++水平提高很多，这样子的实践机会比起学院里的那些作业来得有效多了。在这个过程中，我好像学了些HTML/CSS/JavaScript。在这个过程中，我掌握了一些Win32下的API。在这个过程中，我学习了GTK+，X11等，虽然没有深入学习，但会用。我还知道了很多在学校里学不到的东西，比如老师会告诉你测试很重要，但却不会提供给你机会去实践在一个具体问题下应该怎么设计来得合理。又比如老师会跟你讲设计模式多么多么重要，但却又不会给你实际的应用机会，有的只是类似于《大话设计模式》那本书上的例子。再比如老师会跟你讲语言的知识点，但却很少跟你强调代码风格的重要性，等等。

如果有一天，毕业论文能够变成：你在某个被大家所认可的开源社区中做出多少贡献。

最后，我也不说开源怎么怎么了，推荐阅读两篇文章：[什么是开源精神][10] 和[OPEN SOURCE MADE ME THE MAN I AM][11]。

Updates: 我觉得我应该感谢当时给我机会实习的Intel OTC以及那里的人！！在那里我开始了解各种开源协议（我还记得当时给我们讲课的可是英特尔首席开源科学家Fleming），听到各种高端的分享（印象最深的是一位韩国的工程师，Firefox的Developer），等等！！没有这些，我估计也没有什么机会参加上这种活动。

[0]: https://developers.google.com/open-source/soc/
[1]: https://groups.google.com/a/chromium.org/forum/#!topic/chromium-dev/-a7dsB88KxA
[2]: https://code.google.com/p/chromium/issues/detail?id=148463
[3]: http://zhchbin.github.io/coding/2013/04/25/first-attempt-to-fix-a-bug-of-chromium/
[4]: https://code.google.com/p/chromium/issues/detail?id=148463
[5]: http://zhchbin.github.io/2013/05/30/recordofmygsoc2013/
[6]: https://chromiumcodereview.appspot.com/17564005
[7]: http://www.chromium.org/developers/design-documents/extensions/proposed-changes/apis-under-development
[8]: https://docs.google.com/document/d/1mFmxLoYrcwdg1pouXpC_MC4SF-nMWDzWaMNrIHgM1pM/edit?usp=sharing
[9]: https://code.google.com/p/chromium/issues/detail?id=302437
[10]: https://github.com/lifesinger/lifesinger.github.com/issues/167
[11]: http://cubiq.org/open-source-made-me-the-man-i-am
