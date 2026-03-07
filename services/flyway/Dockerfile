FROM flyway/flyway:12.0.2-alpine

WORKDIR /flyway
COPY ./sql /flyway/sql

CMD ["-url=jdbc:postgresql://db:5432/mydb", "-schemas=public", "-user=postgres", "-password=password", "migrate"]