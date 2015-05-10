# FreeChat
腾讯移动终端开发课程项目-服务器端

## http server
  
1.处理用户的注册和登录事件  
2.使用md5加密用户密码  
3.使用mysql存储用户信息  
  
## tcp server
    
1.使用python的select模块处理socket消息  
2.用户上传自己的name，服务器返回所有在线用户name  
3.维护name:socket字典来转发消息  

### 传输格式如下，考虑了tcp包被拆包发送的情况 
1.文本消息：数据类型(Tag) + JSON长度 + JSON 
2.图片语言消息：数据类型(Tag) + 图片/语音byte长度 + fromName + toName + 图片/语音byte
 

