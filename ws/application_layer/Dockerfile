FROM mrmrcoleman/python_webapp

MAINTAINER mrmrcoleman

EXPOSE 5000

ADD mitosis_web/ /opt/mitosis_web/
ADD mitosis.wsgi /var/www/flaskapp/flaskapp.wsgi
CMD service apache2 start && tail -F /var/log/apache2/error.log
