FROM crpi-2zg9hvsh8g8vjhbv.cn-shenzhen.personal.cr.aliyuncs.com/kayzee3327/ubuntu:22.04

USER root
WORKDIR /home/csc3170

ENV FLASK_APP=libsys
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5000

COPY . .

RUN sed -i 's@//.*archive.ubuntu.com@//mirrors.ustc.edu.cn@g' /etc/apt/sources.list && apt update

RUN apt remove python3 -y && apt install python3 pip -y

RUN python3 -m pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --upgrade pip

RUN pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

RUN pip3 install -r requirements.txt

WORKDIR /home/csc3170

RUN chmod 755 ./run.sh

ENTRYPOINT [ "./run.sh" ]