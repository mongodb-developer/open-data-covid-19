FROM ubuntu:16.04
RUN sed -i 's|//deb|//ftp.fr|g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y python3 python3-pip unixodbc-dev openssl libgssapi-krb5-2 wget && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install pyodbc && \
    wget "https://github.com/mongodb/mongo-odbc-driver/releases/download/v1.3.0/mongodb-connector-odbc-1.3.0-ubuntu-16.04-64.tar.gz" && \
    tar xvzf mongodb-connector-odbc-1.3.0-ubuntu-16.04-64.tar.gz -C /usr/local/lib && \
    chmod 777 /usr/local/lib/libmdbodbc*.so && \
    rm -rf mongodb-connector-odbc-1.3.0-ubuntu-16.04-64.tar.gz
ADD odbc.ini /etc/odbc.ini
ADD odbc-query.py /odbc-query.py
CMD ["python3", "odbc-query.py"]