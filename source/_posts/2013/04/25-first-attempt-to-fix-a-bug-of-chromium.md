---
layout: post
title: "First attempt to fix a bug of chromium"
description: "Share my first failed experience about code contribution to chromium."
category: Coding
tags: [OpenSource, C++]
---

### Background

Recently I spent most of my time in fixing a tricky [bug][0] of chromium. By now, my patch is still in my local repo though it seems to solve the problem. This post is to record what I have learned from my failed attempt.

### Detail
Issue title: Report an error when chrome.app.window.create is called with a URL that does not exist.

In the background js of chrome packaged app, the app developer can pass a url to the api of creating a window. Currently this api will try to load the url in spite of the existence of the file. So the purpose of this issue is to add some code which can check the existence of the url, if it can't be loaded, report an error. For example, in the following javascript code, the `aoeuaoeu.html` doesn't exist, an error should be reported.

```js
chrome.app.runtime.onLaunched.addListener(function() {
  return chrome.app.window.create('aoeuaoeu.html');
});
```

OK......It can to be done easily just adding serveral lines of code before the window is shown at my first sight. So after one afternoon, I finish it with the following patch.

```diff
diff --git a/chrome/browser/extensions/api/app_window/app_window_api.cc b/chrome/browser/extensions/api/app_window/app_window_api.cc
index 1f726db..b838cb8 100644
--- a/chrome/browser/extensions/api/app_window/app_window_api.cc
+++ b/chrome/browser/extensions/api/app_window/app_window_api.cc
@@ -5,6 +5,8 @@
 #include "chrome/browser/extensions/api/app_window/app_window_api.h"
 
 #include "base/command_line.h"
+#include "base/file_util.h"
+#include "base/stringprintf.h"
 #include "base/time.h"
 #include "base/values.h"
 #include "chrome/browser/app_mode/app_mode_utils.h"
@@ -32,6 +34,8 @@ namespace extensions {
 namespace app_window_constants {
 const char kInvalidWindowId[] =
     "The window id can not be more than 256 characters long.";
+
+const char kInvalidURL[] = "Could not load invalid url '%s'.";
 }
 
 const char kNoneFrameOption[] = "none";
@@ -86,12 +90,27 @@ bool AppWindowCreateFunction::RunImpl() {
   EXTENSION_FUNCTION_VALIDATE(params.get());
 
   GURL url = GetExtension()->GetResourceURL(params->url);
+  bool is_component_app_and_has_scheme = false;
+
   // Allow absolute URLs for component apps, otherwise prepend the extension
   // path.
   if (GetExtension()->location() == extensions::Manifest::COMPONENT) {
     GURL absolute = GURL(params->url);
-    if (absolute.has_scheme())
+    if (absolute.has_scheme()) {
       url = absolute;
+      is_component_app_and_has_scheme = true;
+    }
+  }
+
+  // Do not check the absolute URLs for component apps.
+  if (!is_component_app_and_has_scheme) {
+    base::ThreadRestrictions::ScopedAllowIO allow_io;
+    if (!file_util::PathExists(
+            GetExtension()->GetResource(params->url).GetFilePath())) {
+      error_ = base::StringPrintf(app_window_constants::kInvalidURL,
+                                  url.spec().c_str());
+      return false;
+    }
   }
 
   bool inject_html_titlebar = false;
-- 
```

All of my change is only located in `app_window_api.cc`, the implementation of `chrome.app.window.create`. This api is working in the UI thread, so IO should be allowed in order to check the file existence using `file_util::PathExists`. I was very happy when I finished this patch. Everything seems to work well, once the file doesn't exist, an error message will report in the console. Then I just begin to upload this to review. But I couldn't do that because my code didn't pass presubmit check. What? The reason I can get is

> New code should not use ScopedAllowIO. Post a task to the blocking pool or the FILE thread insead.

Suddenlly I didn't know how to solve this problem, though the message give me a direction. Then I email one of the engineers of the chromium who is the owner of this issue that `git cl upload` suggested. My mail contont is

> Sorry for disturb first. I am a student who want to contribute code to chromium. The first issue I choose is the http://crbug.com/148463. In the patch I need to check whether a FilePath exists sync? This will not block the UI thread as far as I can see(Maybe I am wrong? I'm just an newbie), so I use ScopedAllowIO here. In the attach files is my stupid patch, any suggestion?

He is a very nice man and give me kindly reply.
> Checking whether a FilePath exists is definitely a blocking I/O operation, and must not be done on the UI thread. For example, if that part of the file system is not cached in RAM, it might be the case that the disk will have to:
>
> (1) spin up from standing, if it wasn't already spinning,
>
> (2) seek to one or more file system tables on the disk, and
>
> (3) read them out.
> 
> That could actually take a really long time (up to several hundred milliseconds), during which time no other code would be able to run on the UI thread! That's totally unacceptable :)
>
> In addition, your patch has a couple other issues:
>
> (1) there's a race condition -- it's possible that, between when you check for the existence of the file and when it is loaded in the web view, the file is removed, and
>
> (2) the mere existence of a path is insufficient to determine whether it can successfully be loaded: it could be non-readable by the user, or it could be a broken symlink, or it could be a folder.
>
> Good luck! You picked a slightly tricky bug :)

This does really teach me a lot!! Things become more interesting for me now!

[0]: http://crbug.com/148463
