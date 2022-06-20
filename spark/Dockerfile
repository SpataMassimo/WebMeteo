FROM openjdk:8-jre
ENV PATH $SPARK_DIR/bin:$PATH
ENV SPARK_VERSION=3.2.1
ENV SPARK_DIR=/opt/spark
ENV PATH $SPARK_DIR/bin:$PATH
EXPOSE 4040

ADD setup/spark-${SPARK_VERSION}-bin-hadoop3.2.tgz /opt
COPY requirements.txt ./
RUN apt-get update && apt-get -y install bash python3 python3-pip netcat
RUN pip3 install --upgrade protobuf==3.20.0
RUN pip3 install pyspark==${SPARK_VERSION} 
RUN pip3 install --no-cache-dir -r requirements.txt
# Create Sym Link 
RUN ln -s /opt/spark-${SPARK_VERSION}-bin-hadoop3.2 ${SPARK_DIR} 

#ADD dataset /opt/tap/spark/dataset
# Add Python Code
#ADD code/*  /opt/tap/
# Add Java Code
#ADD apps /opt/tap/apps
# Add Spark Manager
#ADD spark-manager.sh $SPARK_DIR/bin/spark-manager

WORKDIR ${SPARK_DIR}