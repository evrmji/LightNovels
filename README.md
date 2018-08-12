# LightNovel

开发基于MacOS，python3.6
用于利用轻之国度最新资源，制作HTML、epub文件，方便电子书阅读器离线阅读、语音朗读等

需要安装的Modules
selenium, bs4, opencc

使用说明，案例如下

novel = LightNovel('https://www.lightnovel.cn/forum.php?mod=viewthread&tid=930679', 'username', 'password')

title, content, images = novel.get_content()

make_html(title, content)

make_epub(title, content, images)

需替换url， username， password即可


Email: mk2016a@outlook.com
