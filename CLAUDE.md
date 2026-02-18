# Videoclaw 项目规范

## GitHub 操作

如果 GitHub 操作失败（网络问题），尝试使用代理：

```bash
export http_proxy=http://127.0.0.1:1087; export https_proxy=http://127.0.0.1:1087; git push origin main
```

或者配置 git 使用代理：

```bash
git config --global http.proxy http://127.0.0.1:1087
git config --global https.proxy http://127.0.0.1:1087
```
