FROM nginx:alpine

# 复制 Nginx 配置文件
COPY nginx.conf /etc/nginx/nginx.conf

# 复制首页
COPY index.html /usr/share/nginx/html/index.html

# 暴露 80 端口
EXPOSE 80

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]
