# LightNovel

开发基于MacOS，python3.6
用于利用轻之国度最新资源，制作HTML、epub文件，方便电子书阅读器离线阅读、语音朗读等

需要安装的Modules
selenium, bs4, opencc

使用说明，案例如下：
在文件中加入如下命令，替换url， username， password运行即可

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

联系方式：
Gitter: https://gitter.im/Light-novels/
Email: mk2016a@outlook.com
