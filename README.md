# 服务器端
## web管理页面
flask+sqlalchemy+mysql构建后端传回restful api，前端使用html+js简单开发
效果图
![web端页面](https://github.com/user-attachments/assets/40dd2a46-1867-435a-8685-58c46fd26d01)


## 单独程序
tcp_forward_server.py 为可独立运行的透传服务，直接使用
```
python tcp_forward_server.py
```
即可
效果图
![本地云服务器联通测试](https://github.com/user-attachments/assets/3dbf2f6b-67d7-41f6-9b99-de7598b53b5e)


# 客户端
使用python开发的简单串口-tcp包双向转换即客户端-服务器-客户端双向收发信息的程序
