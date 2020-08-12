# "printenv"
echo "===>"
echo "1. Clean UP"
rm -rf /root/lib/* > /dev/null 2>&1

echo "2. Run apache maven extractor"
tar xvf /root/src/apache-maven-3.6.0-bin.tar.gz -C /root/lib/ > /dev/null 2>&1

echo ""
echo "3. Run spark extractor"
tar xvf /root/src/spark-2.4.3-bin-hadoop2.8.tgz -C /root/lib/ > /dev/null 2>&1
mv "/root/lib/spark-2.4.3-bin-spark-2.4.3-bin-hadoop2.8" "/root/lib/spark-2.4.3-bin-hadoop2.8"

echo ""
echo "4. AWS Glue libs"
cp -r /root/src/aws-glue-libs /root/lib/ > /dev/null 2>&1
echo "Glue libs copied to the /root/lib"
cd /root/lib/aws-glue-libs/ || exit
git checkout -b glue-1.0 origin/glue-1.0

# make PyGlue.zip and download additional jar for using with maven
echo ""
echo "5. Run glue-setup"
cd /root/lib/aws-glue-libs || exit
chmod +x /root/lib/aws-glue-libs/bin/glue-setup.sh > /dev/null 2>&1
/root/lib/aws-glue-libs/bin/glue-setup.sh > /root/lib/installation.log

echo ""
echo "6. Replace the line that should not be used anymore (with glue-setup.sh)"
sed -i "s/mvn -f \$ROOT_DIR\/pom\.xml/# mvn -f \$ROOT_DIR\/pom\.xml/g" /root/lib/aws-glue-libs/bin/glue-setup.sh

echo ""
echo "7. Copy correct jar file from the spark to the aws libs"
cp "$SPARK_HOME"/jars/netty-all-4.1.17.Final.jar /root/lib/aws-glue-libs/jarsv1/
