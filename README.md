## 安装

### 安装Python

至少Python3.5以上

### 安装Redis

安装好之后将Redis服务开启

ip代理池的获取参考
https://github.com/germey/proxypool
但是由于此ip代理池是爬取的网上公开代理源上的ip，可用性较差，可以选择购买ip，价格不贵，可用性稍好。
参考的是崔庆才大神的github，ip代理池的代码也是来源于其github.
###
除spider.py外的文件都是用于是搭建ip代理池的，spider.py可以和其他文件配合使用，也可以单独使用，单独使用时，请根据实际情况更换脚本中的proxy_pool_url，proxy_pool_url是购买的ip的API接口
详细步骤参考：知乎
