# 网站程序介绍
网站程序由flask开发，程序通过爬取其他网站的视频获取内容。
同时，还带草榴爬虫哦！
预览：http://www.video4sex.com
特色：
- 多爬虫支持。只要你会爬虫，就可以自己写爬虫，然后入库至mysql中。
- 视频上传openload。为了不被原视频网站受限，通过脚本自动上传视频到openload。
- 自动化。无论是爬虫，还是上传脚本，都通过定时任务自动运行。无需管理
# 文件简单介绍
- init.sh 初始化脚本
- run.py 网站启动脚本
- config.py - 配置信息
- supervisord.conf - supervisor启动文件
- app文件夹 - 系统文件夹
- logs文件夹 - 储存log信息
- fahai.py - 视频爬虫脚本
- cl1024.py - 草榴爬虫脚本
# 安装前准备：
1. 安装nginx、mysql、supervisor，crontab
2. 将文件夹放在/root目录下，文件夹名改为video4sex（必须）
# 安装：
`chmod +x init.sh `
`sh init.sh`
- 会自动安装pip以及安装Python依赖库
- 同时添加快捷命令：
`online_start - 启动网站`
`online_stop - 停止网站`
`online_status - 网站运行状态`
`online_restart - 重新启动网站`
`online_debug - 调试网站状态（只能在网站目录下运行）`
- 添加定时任务
# 初始化数据
1. 创建数据库
    - 命令行进入mysql：`mysql -u root -p`，然后输入密码
    - `create database web DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;`
2. 修改文件`config.py`
    - 将`SQLALCHEMY_DATABASE_URI`这一行中的`password`修改为你自己的密码
    - 同时将`MAIL_USERNAME`和`MAIL_PASSWORD`修改为你自己的gmail账号和密码（用于发送重置密码邮件）
3. 修改文件`run.py`
    - 将#37行的email和password修改为你自己的邮箱和密码，用户名最好别改
4. 初始化数据。在video4sex目录下运行
    - `python run.py deploy`
5. 初始化视频数据。
    -  `python fahai.py`
6. 初始化草榴数据。
    - `python cl1024.py`
# 运行网站
- 假设你之前已经安装好nginx了，将`nginx.conf`里面的配置信息添加到你的nginx配置信息中，并在`server_name`后面添加你的域名，其他信息别改动。
- 在video4sex目录下输入`online_debug`，如果没有报错，继续在浏览器打开`http://你的ip:5432`，看是否有信息
## 不会安装？不会python？
付费安装，联系video4sexroot@gmail.com。
## 为什么没有openload上传脚本？
本程序为精简版代码。如果需要完整版，请联系video4sexroot@gmail.com购买完整版。
完整版包括：
1. 4个视频网站的爬虫
2. openload上传脚本
3. 本人的1个月支持服务。
## 不会写爬虫，但是想爬取一个网站的视频怎么办？
联系video4sexroot@gmail.com。可付费写爬虫

ps. 给你现成的程序了，不会安装，付费给你安装很合理吧？
    以上所有付费内容，均超过100元/次，因此没有付费欲望的莫浪费时间！
