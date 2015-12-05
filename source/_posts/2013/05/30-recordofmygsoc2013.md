---
layout: post
title: "Record Of My GSoC 2013"
comments: true
description: "I will record my status every week within GSoC 2013."
category: 
tags: [OpenSource]
---

#### About
This is used to record my status and updates while fighting for GSoC 2013 weekly. Being the lucky dog that can take part in GSoC is the most wonderful moment in my life recently. The open source project I applied to is chromium, which is a monolithic application. __Cause my English is poor, there will be many stupid grammar mistakes in this post. Sorry for it.__

#### Week 00
1. Successfully be admitted. I was very thrilled when I got the congratulation email at about 03:00 am.
2. Finish the ToDo list: Enrollment Form and Tax Form.
3. Prepare for the implementation of my [proposal](http://www.google-melange.com/gsoc/project/google/gsoc2013/zhchbin/6001), such as reading the code about chrome.command, which will be a good example for me.

#### Week 01
1. Commit a fix for content shell on windows: Enable visual styles via adding shell.exe.manifest. [Review URL](https://chromiumcodereview.appspot.com/15649020). This help me understand how to commit to the source tree successfully.
2. Writing New API Proposal as my mentor recommend.
3. Worry about my project because I didn't hear anything from my mentor after I was selected even though I email him twice.

#### Week 02~03
1. The Dragon Boat Festival, at home. Looking into several issues and try to fix them for warm-up.
2. Working for the patch which can help the app window fit on screen when the screen layout changed. [Code Review Url 17378003](https://codereview.chromium.org/17378003/)

#### Week 04
1. Update my proposal and send it to be reviewed.
2. Fix several trivial bugs. The previous patch 17378003 landed with the help of scheib. [Code Review Url 17564005](https://chromiumcodereview.appspot.com/17564005/)

#### Week 05~07
1. Investigate workarounds for missing minimize event in Ubuntu's unity window manager. [Code Review URL 18741006](https://codereview.chromium.org/18741006/). In the unity window manager in ubuntu, when you minimize a window it doesn't let the application know via the normal GTK API's. In this patch, it will use XEvent to catch the PropertyNotify event and check `_NET_WM_STATE` of the window to determine whether the state of the window is minimized.
2. Fix a memory link within the patch for "Links in platform apps should open in the system default browser". I find out when adding a test case for `ShellWindowLinkDelegate::OpenURLFromTab`. My patch used `scoped_ptr` to manage the ShellWindowLinkDelegate. [Code Review URL 18051015](https://codereview.chromium.org/18051015/).
3. Try to add a test case for `ShellWindowLinkDelegate::OpenURLFromTab`. However, the codereview is pending and waiting for reply. While developing this patch, I learn something about ASAN of chromium and find out the root cause of [ASAN use-after-free errors](https://chromiumcodereview.appspot.com/10915047#msg27). You can find it within my comments: [Code Review URL 18192003](https://codereview.chromium.org/18192003/).
4. Add code to clear existing alarms when uninstalling extension. I fixed it after one hour the bug was reported. [Code Review URL 18713004](https://codereview.chromium.org/18713004/).
5. Help to fix a Pri-1 issue: [Apps on NTP cannot be dragged](https://code.google.com/p/chromium/issues/detail?id=257273). My revision "209944" is suspected to cause this issue. However, the revision will only influence code in the windows platform and shouldn't be relevant to. In order to prove it, I did some detective work to find out which revision introduced this bug. My work was praised in the [comment#10](https://code.google.com/p/chromium/issues/detail?id=257273#c10).
6. Help to narrow down cause of issue: 'App APIs REPL' app crashes. The crash is caused by incomplete API removal of managedModePrivate. [My Comment](https://code.google.com/p/chromium/issues/detail?id=256981#c2).
7. There are also several trivial commits that I have landed. For example, dragging the icon of the app out of the app launcher when its downloading is in process would crash Chrome. [Review URL](https://chromiumcodereview.appspot.com/18153015) fix this problem.
8. Report some bugs that I have found: (1) [Issue 257750](http://crbug.com/257750), Continue Reload of chrome://extensions will break it. (2) [Issue 252663](http://crbug.com/252663), Using the Apps Developer Tool, restart the disabled unpacked platform app will crash chrome. I fixed it also. 

#### Week 08
1. Begin to work on media keys support via extending chrome.commands. My proposal is adding an attribution `enable_media_keys` and some build-in commands into chrome.commands. For more detail, please refer to the [comment](https://code.google.com/p/chromium/issues/detail?id=131612#c14) I post on the http://crbug.com/131612. And I also wrote down the [problem](https://docs.google.com/document/d/1t1s7RD3Nh_5TX6r7bwf-_QGkGTNXb3-IoGmDbDsmqsQ/edit?usp=sharing) that I have met.
2. Finish issue 18741006: [GTK] Report isMinimized and correctly restore app windows. I ignored to check `_NET_SUPPORTED` first of all to determine whether the absence of `_NET_WM_STATE_HIDDEN` infers that the window is not iconified. Thanks for the help from all the reviewers. [Code Review URL 18741006](https://codereview.chromium.org/18741006).

#### Week 09
1. [Issue 263968][263968]: Packing extension with bad private key causes crash. It is caused by the code ignored a sign zip error. [Code Review URL 20142007][20142007]. However, it got an not lgtm because Daniel Nishi has another patch out.
2. [Issue 264645][264645]: Icons for the apps are flickering while launching. Because when launching the apps, the unpacked icon url will be changed due to [r209895][209895]. The revision is to fix a bug where extension's icon was not updated on reload. So it used an Date.now() to prevent the cache of image. My [Code Review URL 20728002][20728002] is on the way.
3. [Issue 264624][264624]: App APIs REPL app Crashes while launching. This is a regression issue. The root cause is an incomplete API removal: pageLauncher in the `_api_features.json`. [Code Review URL 21028005][21028005] remove remaining code related to pageLauncher, and add a test case to prevent future incomplete API removals in the `_api_features.json`. Still on the way. 
4. [Issue 261996][261996]: Chevron icon (>>) appears in the browser action area for one extension. In the function BrowserActionsContainer::BrowserActionAdded of `chrome/browser/ui/views/browser_actions_container.cc`, if the extension is marked as upgrading, it will stop enlarge the container if it was already at maximum size. The upgrading extension didn't remove the browser action, so it works correctly. However, when a extension is crashed (The browser action will be removed if it has) and reloaded (will add the browser action icon back if it has), it shouldn't be marked as upgrading. The bug is introduced by [r196634][196634]. [Code Review URL 20909002][20909002] still being reviewed.

#### Week 10
1. Finish the CLs I submitted last week as reviewers' comments.
2. Investigate and follow up [Issue 265798][265798]: Unable to add extension from webstore. It looks like a regression because after the [r213568][213568], Chrome will load icon => "64" field, before it chrome only load: 16, 48, 128, and the field of "64" is ignored, so it works OK in the previous version.
3. Report a weird [issue][266891]: Browser action container shrink and only chevron icon is shown when "ExtensionToolbarModel::OnExtensionToolbarPrefChange" is called. Spend my time on finding the way to reproduce the problem reliably. But it seems to happen only in my computer at last.

#### Week 11
Last week I went back home to take a break, but I still keep my eyes on several issues.

1. [Issue 267187][267187]: Apps Developer Tool, Installation warnings are not shown properly. This is easy to fix because the Apps Developer Tool should keep consistence with the `chrome://extensions`, so I use the same appearance as the page. [Code Review URL 22191003][22191003].
2. [Issue 257474][257474]: Firefox bookmarks file with `<HR>` tags and folders doesn't import correctly. This is a Hotlist-GoodFirstBug. Because the HTML file exported from Firefox will contain `<HR>` tags, which is the bookmark entries separator in Firefox that Chrome does not support. Note that there can be multiple `<HR>` tags at the beginning of a single line. My fix is simply skipping over the tags. And by the way, as the suggestion of @gab, I refactor the `bookmark_html_reader_unittest` to avoid repeating the initialization code that all of these tests have in common. [Code Review URL 22408007][22408007].

#### Week 12
This week I have to check in and take a medical examination because our school started. It's a waste of time and energy.

1. The first issue I working on this week is [Issue 269450][269450]: Extensions page is scrolling down and up while scrolling on the "keyboard shotcuts" page. Thanks for the help from @xiyuan and @miket first of all. My first patch is using a css style "no-scroll" to remove the scrollability of page when showing the overlay. However, the page will change when the scrollbar disappears/shows. The problem is more apparent when the browser window is not wide enough. Finally, with @xiyuan's instruction, we fixed it with following [CL][22661007]. The pacth also expose a [Blink bug][276043] luckily.
2. Pick up [Issue 131612][131612]: Multimedia keys API support. And ask for @finnur and @mek for suggestion. Now I have known how to continue my proposal clearly.

#### Week 13
1. [Issue 270844][270844]: GTalk pinned to Taskbar: Chrome window opens instead of GTalk window. When panel widnow is pinned to the taskbar, the relaunch behavior is weird to the user. Panel windows are created and used by the extensions. When they are pinned to the taskbar, the icon will change to Chrome instead of the original icon. What's more, the relaunch behavior (Close all panel windows and then click the pinned icon will open a chrome new window) will confuse the user. Why we can't implement the support to pin the panel window on the taskbar? It is because launching chrome executable with extension id (in this case, hangout id), will launch chrome browser with Hangout options page, instead of the chat window. The [Code Review URL 23146009][23146009]: Remove "Pin this program to taskbar" of panel window. Use `SHGetPropertyStoreForWindow` to remove it.
2. [Code Review URL 22859067][22859067]: Revert r217952 to make behavior of horizontal scroll bar in page `chrome://extensions` keep consistence with `chrome://settings`. My `r217952` has side effect, [Issue 277974][277974]: Horizontal scroll bar issue for `chrome://extensions/` page. So I revert it and use my original patch to deal with the [http://crbug.com/269450][269450].
3. [Code Review URL 22801019][22801019]: Provide i18n support for descriptions in commands API.
4. [Code Review URL 23290007][23290007]: Fix nit of chrome.commands doc: invalid json format. 

#### Week 14
1. [Issue 131612][131612]: Multimedia keys API support. I focused on this issue this week. My CL has committed. It will allow the user to use the media keys: MediaNextTrack', 'MediaPrevTrack', 'MediaStop', 'MediaPlayPause' with named command. [Code Review URL 23445013][23445013]: Parse media keys for named command in the manifest.
2. [Code Review URL 23486008][23486008]: Fix wrong description of chrome.commands example.

#### Week 15
I'm almost crazy this week due to heavy homework. I worked on serveral issues but got nothing. Sorry for it.

1. [Issue 242790][242790]: App windows with ids should remember fullscreen state. It can be fixed easilly on windows and linux platform just adding trivial change to the `native_app_window_views.cc` etc. Sadly, it's reverted. The reason for revert: Causes PlatformAppBrowserTest.ShellWindowRestoreState to fail on Mac OS X 10.6. But I didn't have OS X 10.6 for testing. Note: it can pass try job: `mac_rel`. Though the issue didn't being fixed successfully, I also found a bug: [Issue 287596][287596]: App Window return false of isFullscreen when initially created with {state: "fullscreen"}.
2. [Issue 259040][259040]: Extensions with very long names push dialog off screen. I proposal to show the whole name with adding a line of code on `views` platform. Also looking into how it can be done on `gtk`. But I didn't have enough time to finish it.
3. Help triage [Issue 288625][288625] to the right person.

#### From 16th Week...

In this period I was working with @Finnur to implement first part of supporting global extension commands. As my proposal, chrome will read an optional "global" flag from the manifest and register the shortcuts as global if it is set to true. Now the [CL][23812010] had got `LGTMs` from the reviewers and waiting for committing to the source tree. And I will continue to do a followup CL after @Finnur's stuff in.

In the meantime, I passed the final evaluation successfully. I owe great thanks to my mentor Marijn, the excellent software engineers from Google, especially the reviewers (@kalman, @finnur, @scheib, @Daniel Nishi, @miket etc) who had taught me a lot that I will not learn in school. Finnally, great thanks to Google.

#### The End

From Google Open Source Blog, [9th Year of Google Summer of Code draws to a close](http://google-opensource.blogspot.com/2013/10/9th-year-of-google-summer-of-code-draws.html)

The end of summer in the Northern Hemisphere also signals the end of the 2013 Google Summer of Code, our program designed to introduce university students from around the world to open source development.

In June, 1,192 university students from 69 countries began writing code for 177 open source organizations with the help of 2,218 mentors from 71 countries -- quite the team effort! We are excited to announce that 88.6%* (1056) of the students passed their final evaluations. If you would like to read about more numbers on the Google Summer of Code program you can view a variety of statistics on the previous eight years of the program.

Stay tuned to this blog each Friday until the end of the year for wrap up posts from many of this year’s Mentoring organizations.

Now that the program has concluded, the students are busy preparing their code samples for all eyes to see. Soon you will be able to go to the program site where organizations will have links to the student’s code repositories.

Thank you to all of the students, mentors and organization administrators that have helped to make this 9th year of the Google Summer of Code a great success!

By Carol Smith, Open Source Programs


#### It's not the End.

[263968]: https://code.google.com/p/chromium/issues/detail?id=263968
[264645]: https://code.google.com/p/chromium/issues/detail?id=264645
[264624]: https://code.google.com/p/chromium/issues/detail?id=264624
[261996]: https://code.google.com/p/chromium/issues/detail?id=261996
[265798]: https://code.google.com/p/chromium/issues/detail?id=265798
[266891]: https://code.google.com/p/chromium/issues/detail?id=266891
[267187]: https://code.google.com/p/chromium/issues/detail?id=267187
[257474]: https://code.google.com/p/chromium/issues/detail?id=257474
[269450]: https://code.google.com/p/chromium/issues/detail?id=269450
[131612]: https://code.google.com/p/chromium/issues/detail?id=131612
[276043]: https://code.google.com/p/chromium/issues/detail?id=276043
[270844]: https://code.google.com/p/chromium/issues/detail?id=270844
[277974]: https://code.google.com/p/chromium/issues/detail?id=277974
[242790]: https://code.google.com/p/chromium/issues/detail?id=242790
[287596]: https://code.google.com/p/chromium/issues/detail?id=287596
[259040]: https://code.google.com/p/chromium/issues/detail?id=259040
[288625]: https://code.google.com/p/chromium/issues/detail?id=288625#c3

[20142007]: https://codereview.chromium.org/20142007/
[20728002]: https://codereview.chromium.org/20728002/
[21028005]: https://codereview.chromium.org/21028005/
[20909002]: https://codereview.chromium.org/20909002/
[22191003]: https://chromiumcodereview.appspot.com/22191003
[22408007]: https://chromiumcodereview.appspot.com/22408007
[22661007]: https://chromiumcodereview.appspot.com/22661007
[23146009]: https://codereview.chromium.org/23146009/
[22801019]: https://codereview.chromium.org/22801019/
[22859067]: https://codereview.chromium.org/22859067/
[23290007]: https://codereview.chromium.org/23290007/
[23445013]: https://codereview.chromium.org/23445013/
[23486008]: https://codereview.chromium.org/23486008/
[23812010]: https://codereview.chromium.org/23812010/

[209895]: https://src.chromium.org/viewvc/chrome?revision=209895&view=revision
[196634]: http://src.chromium.org/viewvc/chrome?revision=196634&view=revision
[213568]: http://src.chromium.org/viewvc/chrome?revision=213568&view=revision
