CREATE DATABASE IF NOT EXISTS `unittest` ;

CREATE USER 'unittest'@'%' IDENTIFIED BY 'unittest' ;
GRANT ALL ON `unittest`.* TO 'unittest'@'10.0.0.0/255.0.0.0' IDENTIFIED BY 'unittest' ;
GRANT ALL ON `unittest`.* TO 'unittest'@'172.16.0.0/255.240.0.0' IDENTIFIED BY 'unittest' ;
GRANT ALL ON `unittest`.* TO 'unittest'@'192.168.0.0/255.255.0.0' IDENTIFIED BY 'unittest' ;
