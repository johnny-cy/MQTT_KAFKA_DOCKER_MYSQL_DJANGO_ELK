CREATE DATABASE IF NOT EXISTS `django` ;

CREATE USER 'django'@'%' IDENTIFIED BY 'django' ;
GRANT ALL ON `django`.* TO 'django'@'10.0.0.0/255.0.0.0' IDENTIFIED BY 'django' ;
