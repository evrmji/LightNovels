# LightNovel

一、用于利用轻之国度最新资源，制作HTML、epub文件

开发基于MacOS，python3.6，方便电子书阅读器离线阅读、语音朗读等

安装 selenium, bs4, opencc

打开 make_epub.py 文件，在其中加入如下命令，替换url， username， password运行即可

1. 单一url制作单一文件

novel = LightNovel('https://www.lightnovel.cn/forum.php?mod=viewthread&tid=930679', 'username', 'password')

title, content, images = novel.get_content()

make_html(title, content)

make_epub(title, content, images)

2. 多个url制作单一文件

url_list = ['https://www.lightnovel.cn/forum.php?mod=viewthread&tid=915987&highlight=为美好',
            'https://www.lightnovel.cn/forum.php?mod=viewthread&tid=928655&highlight=为美好',
            'https://www.lightnovel.cn/forum.php?mod=viewthread&tid=930675&highlight=为美好',
            'https://www.lightnovel.cn/forum.php?mod=viewthread&tid=935285&highlight=为美好']

collect_epubs(url_list, username, password)

3. 运行该文件即可

python make_epub.py



二、翻译繁体中文epub文件为简体中文epub

安装opencc

打开 simplify_Chinese.py 文件

新建变量，输入文件地址或文件夹地址

tf = TranslateEpub('/Volumes/Data/Mine/Novels/騎士&魔法')

加入命令

tf.translate_all()

最后执行

python simplify_Chinese.py即可

联系方式：

Gitter: https://gitter.im/Light-novels/

Email: mk2016a@outlook.com
