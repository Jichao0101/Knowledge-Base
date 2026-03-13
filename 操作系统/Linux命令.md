# 1 存储与文件系统

## 1.1 df:查看文件系统磁盘占用

- 词源: dist free
- 用途：看“挂载点/分区”层面的容量、已用、可用、使用率
- 参数
	- -h: human-readable
	- -i:显示inode使用情况
	- -T:打印文件系统类型
## 1.2 du：统计文件占用

- 词源:disk usage
- 区别于df:`df` 看分区整体；`du` 看目录/文件累计
- 参数
	- -h
	- -s:summary
- 工程常用
	- `du -h --max-depth=1 /data | sort -h`找最大占用

# 2 搜索、筛选

## 2.1 find：按条件找文件

```
find . -type f -name "*.jpg"
find . -type f -mtime -1          # 1天内改动
find . -type f -size +100M        # 大于100MB

```

## 2.2 grep: 文本匹配

词源: global regular expression print

```
grep -R "ERROR" logs/         # -R 递归
grep -n "timeout" file.log    # -n 行号
grep -i "warning" file.log    # -i 忽略大小写
grep -E "foo|bar" file.log    # -E 扩展正则

```

# 3 进程与资源监控

## 3.1 ps /top /htop

ps：process status
            
- **常用**
    
    `ps aux | grep python`

## 3.2 pidstat/ iostat/ vmstat

- `iostat`：I/O statistics（磁盘读写、await、util）
    
    `iostat -xz 1`
    
- `vmstat`：virtual memory statistics
    
    `vmstat 1`
    
- `pidstat`：按进程统计 CPU/IO
    
    `pidstat -dru 1`

# 4 网络排障

## 4.1 ip/ ss/ ping/ curl

- `ip`：现代网络管理（替代 ifconfig）
	```
	ip a 
	ip r
	```
- `ss`：socket statistics（替代 netstat，查端口占用）
    
    `ss -lntp`
    
- `ping`：连通性/RTT
    
- `curl`：HTTP 请求与调试（服务健康检查）
    
    `curl -v http://127.0.0.1:8080/health`
    

---

# 5 权限与用户

## 5.1 chmod / chown/ umask`

- `chmod`：change mode
    
- `chown`：change owner
    
- `umask`：user mask（默认权限掩码）
    

---

# 6 压缩与归档（部署/传输/备份）

## 6.1 tar/ gzip

- `tar`：tape archive
```
tar -czf out.tar.gz dir/     # c创建 z用gzip f指定文件
tar -xzf out.tar.gz          # x解压

```