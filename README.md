# Self-Patch Alist

本体安装

```shell
curl -fsSL "https://raw.githubusercontent.com/oneclickvirt/alist/refs/heads/main/install.sh" -o v3.sh && bash v3.sh
```

```shell
curl -fsSL "https://cdn.spiritlhl.net/https://raw.githubusercontent.com/oneclickvirt/alist/refs/heads/main/install.sh" -o v3.sh && bash v3.sh
```

配置域名，末尾不带/号

```shell
nano /opt/alist/data/config.json
```

安装nginx，配置

```shell
nano /etc/nginx/sites-available/alist-proxy.conf
```

```shell
server {
    listen 80;
    server_name storage.spiritlhl.net;
    location / {
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header Range $http_range;
    proxy_set_header If-Range $http_if_range;
    proxy_redirect off;
    proxy_pass http://127.0.0.1:5244;
    # 上传的最大文件尺寸
    client_max_body_size 999999m;
    }
}
```

```shell
sudo nginx -t
sudo ln -s /etc/nginx/sites-available/alist-proxy.conf /etc/nginx/sites-enabled/alist-proxy.conf
```

```shell
sudo systemctl restart nginx
```
