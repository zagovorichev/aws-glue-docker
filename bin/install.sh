# "printenv"
echo "Clean UP"
rm -rf /root/lib/* > /dev/null 2>&1

echo "1. Run apache maven extractor"
tar xvf /root/src/apache-maven-3.6.0-bin.tar.gz -C /root/lib/ > /dev/null 2>&1

## add to path
# PATH=/root/lib/apache-maven-3.6.0/bin:$PATH; export PATH ## for the session only
NEW_PATH=/root/lib/apache-maven-3.6.0/bin:$PATH
sed -i 's/PATH=.*//g' /etc/environment
echo "PATH=$NEW_PATH" >> /etc/environment
PATH=$NEW_PATH
echo "path with maven: $PATH"

echo ""
echo "2. Run spark extractor"
tar xvf /root/src/spark-2.4.3-bin-hadoop2.8.tgz -C /root/lib/ > /dev/null 2>&1
## add to path
SPARK_HOME="/root/lib/spark-2.4.3-bin-spark-2.4.3-bin-hadoop2.8"; export SPARK_HOME
echo "SPARK_HOME=$SPARK_HOME" >> /etc/environment
echo "path to spark: $SPARK_HOME"

echo ""
echo "3. AWS Glue libs"
cp -r /root/src/aws-glue-libs /root/lib/ > /dev/null 2>&1
echo "Glue libs copied to the /root/lib"
cd /root/lib/aws-glue-libs/ || exit
git checkout -b glue-1.0 origin/glue-1.0

# make PyGlue.zip and download additional jar for using with maven
echo ""
echo "4. Run glue-setup"
cd /root/lib/aws-glue-libs || exit
chmod +x /root/lib/aws-glue-libs/bin/glue-setup.sh > /dev/null 2>&1
/root/lib/aws-glue-libs/bin/glue-setup.sh > /root/lib/installation.log

echo ""
echo "5. Replace the line that should not be used anymore (with glue-setup.sh)"
sed -i "s/mvn -f \$ROOT_DIR\/pom\.xml/# mvn -f \$ROOT_DIR\/pom\.xml/g" /root/lib/aws-glue-libs/bin/glue-setup.sh

echo ""
echo "6. Copy correct jar file from the spark to the aws libs"
cp $SPARK_HOME/jars/netty-all-4.1.17.Final.jar /root/lib/aws-glue-libs/jarsv1/

# Set environment variables
# The AWS provided scripts that launch Glue have limitations, but under the hood they basically run Spark after setting up particular environment variables. We need to set those manually to run Spark like Glue in our own way.
echo ""
echo "7. Set environment variables"
SPARK_CONF_DIR=/root/lib/aws-glue-libs/conf; export SPARK_CONF_DIR
echo "SPARK_CONF_DIR=$SPARK_CONF_DIR" >> /etc/environment
PYTHONPATH="${SPARK_HOME}/python:${SPARK_HOME}/python/lib/py4j-0.10.7-src.zip:/root/lib/aws-glue-libs/PyGlue.zip:${PYTHONPATH}"; export PYTHONPATH
echo "PYTHONPATH=$PYTHONPATH" >> /etc/environment

echo "environment variables: "
echo "================"
"printenv"
echo "================"
