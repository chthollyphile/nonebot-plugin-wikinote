# nonebot-plugin-wikinote
一个简单的插件，使用Mediawiki API将聊天中的信息保存到某个wiki站点（需要有对应站点的机器人权限）
# 安装
将文件夹放入`/plugin`文件夹，在`__init__.py`中填入对应`Mediawiki`的机器人账户（通过`/api.php`获取），wiki的API页面，以及指定的quicknote标题即可。
# 使用
`/记录 内容`

可以将 `内容` 写入`quicknote`词条页面的末端。

`/写入 #标题# 内容`

可以将 `内容` 写入 `标题`页面
