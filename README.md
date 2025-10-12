# BDA Airflow Assignment

to create the containers:
`docker-compose up -d`

to create the admin account:
`docker-compose run airflow-worker airflow users create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin`

to stop all services:
`docker-compose down --volumes --remove-orphans`
