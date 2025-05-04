FROM crpi-2zg9hvsh8g8vjhbv.cn-shenzhen.personal.cr.aliyuncs.com/kayzee3327/ubuntu:22.04

USER root
WORKDIR /home/csc3170

# 设置环境变量
ENV FLASK_APP=libsys
ENV FLASK_RUN_HOST=0.0.0.0
ENV TZ=Asia/Shanghai
ENV DEBIAN_FRONTEND=noninteractive

# 更新源并安装必要的包
RUN sed -i 's@//.*archive.ubuntu.com@//mirrors.ustc.edu.cn@g' /etc/apt/sources.list && \
    apt update && \
    apt remove python3 -y && \
    apt install -y python3 pip tzdata

# 设置时区 - 移动到包安装后
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata

# 设置pip
RUN python3 -m pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --upgrade pip && \
    pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

# 复制项目文件并安装依赖
COPY . .
RUN pip3 install -r requirements.txt

# 设置工作目录和权限
WORKDIR /home/csc3170
RUN chmod 755 ./run.sh

# 暴露端口
EXPOSE 5000

# 启动命令
ENTRYPOINT ["./run.sh"]