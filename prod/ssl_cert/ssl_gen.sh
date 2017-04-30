openssl genrsa -des3 -out ssl.key 4096
openssl req -new -key ssl.key -out ssl.csr
openssl rsa -in ssl.key -out quokka.key
openssl x509 -req -days 730 -in ssl.csr -signkey quokka.key -out quokka.crt

