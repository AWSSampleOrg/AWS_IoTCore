```sh
ats_endpoint=$(aws iot describe-endpoint --endpoint-type iot:Data-ATS --query endpointAddress --output text)
openssl s_client -connect ${ats_endpoint}:8883 -showcerts > ats_endpoint.pem 2>&1 < /dev/null
openssl x509 -noout -text -in ats_endpoint.pem
```

Show all ciphers that server accepts.

```sh
nmap -sV --script ssl-enum-ciphers -p 8883 ${ats_endpoint}
```
