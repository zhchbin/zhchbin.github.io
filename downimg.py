import json
import os

PATH = '.'
filelist = [os.path.join(dp, f) for dp, dn, filenames in os.walk(PATH) for f in
        filenames if os.path.splitext(f)[1] == '.md']


for fn in filelist:
    should_replace = False
    with open(fn, 'r') as f:
        content = f.readlines()

        index = 0
        for index in range(0, len(content)):
            line = content[index]
            if not line.startswith('![]'):
                continue
            if 'sinaimg.cn' not in line:
                continue

            url = line.replace('![](', '').replace(')', '').strip()
            target_file_name = url.split('/')[-1]
            line = line.replace(url, f'/images/{target_file_name}')
            should_replace = True
            content[index] = line

    if not should_replace:
        continue

    with open(fn, 'w') as f:
        f.writelines(content)

