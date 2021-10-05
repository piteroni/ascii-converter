FROM python:3.6

RUN apt-get update -y && \
    apt-get install -yq make cmake gcc g++ unzip wget build-essential gcc zlib1g-dev libgl1-mesa-dev && \
    ln -s /usr/include/libv4l1-videodev.h /usr/include/linux/videodev.h

WORKDIR /tmp/opencv

RUN wget -P /tmp/ https://github.com/Itseez/opencv/archive/3.1.0.zip && \
    unzip /tmp/3.1.0.zip && \
    cd opencv-3.1.0 && \
    cmake CMakeLists.txt -DWITH_TBB=ON \
    -DINSTALL_CREATE_DISTRIB=ON \
    -DWITH_FFMPEG=OFF \
    -DWITH_IPP=OFF \
    -DCMAKE_INSTALL_PREFIX=/usr/local && \
    make -j2 && \
    make install && \
    pip3 install --upgrade setuptools pip && \
    pip3 install jupyter matplotlib opencv-python opencv-contrib-python

COPY docker-entrypoint.sh /

CMD ["/docker-entrypoint.sh"]
