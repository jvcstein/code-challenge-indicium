# Indicium Tech Code Challenge

Code challenge for Software Developer with focus in data projects.


## Context

At Indicium we have many projects where we develop the whole data pipeline for our client, from extracting data from many data sources to loading this data at its final destination, with this final destination varying from a data warehouse for a Business Intelligency tool to an api for integrating with third party systems.

As a software developer with focus in data projects your mission is to plan, develop, deploy, and maintain a data pipeline.


## The Challenge

*Desafio Indicium – João Stein*

*Setup preliminar*

1.Clonei o repositório do github

mkdir -p /opt/indicium

cd /opt/indicium

git clone <https://github.com/techindicium/code-challenge.git>

2.Utilizando Docker e Docker Compose, subi o container que cria o banco de dados Northwind pela execução do script “/data/northwind.sql” e disponibiliza o arquivo CSV “/data/order_details.csv”

cd /opt/indicium/code-challenge

docker compose up

3.Teste do acesso ao banco de dados para ver se está tudo ok.

psql -U northwind_user -h localhost -p 5432 northwind

Senha para o usuário northwind_user:

psql (16.4 (Ubuntu 16.4-1.pgdg22.04+1), servidor 12.22 (Debian 12.22-1.pgdg120+1))

Digite "help" para obter ajuda.

northwind=# \\dt

Lista de relações

Esquema | Nome | Tipo | Dono

\---------+------------------------+--------+----------------

public | categories | tabela | northwind_user

public | customer_customer_demo | tabela | northwind_user

public | customer_demographics | tabela | northwind_user

public | customers | tabela | northwind_user

public | employee_territories | tabela | northwind_user

public | employees | tabela | northwind_user

public | orders | tabela | northwind_user

public | products | tabela | northwind_user

public | region | tabela | northwind_user

public | shippers | tabela | northwind_user

public | suppliers | tabela | northwind_user

public | territories | tabela | northwind_user

public | us_states | tabela | northwind_user

(13 linhas)

northwind=# /q

4.Instalação do Meltano

pip install meltano

5.Instalação do Airflow

meltano add utility airflow

meltano invoke airflow:initialize

meltano invoke airflow users create -u airflow -p airflow --role Admin -e airflow -f admin -l admin

meltano invoke airflow scheduler &

meltano invoke airflow webserver

*Setup Meltano*

1.Criação do projeto “meltano-postgresql-csv”

meltano init meltano-postgresql-csv

cd meltano-postgresql-csv

2.Adição dos “extractors” e “loaders” ao projeto

meltano add extractor tap-postgres

meltano add extractor tap-csv

meltano add loader target-csv

meltano add loader target-postgres

*Setup do Meltano para o Step 1*

1.Ajustes no arquivo “meltano.yaml” para definição do extractor para o protgresql e loader do csv.

Criação da seção “extractors”.

Para o PostgreSQL será utilizado o extrator “tap-postgres” (<https://hub.meltano.com/extractors/tap-postgres/>). Informados dados de acesso ao banco de dados em execução no container. Na sub-seção “select” é informado que deverão ser selecionados todos os arquivos que estejam no schema/catalogo “public” (public-\) e que sejam trazidas todas as colunas (.\)

plugins:

extractors:

\- name: tap-postgres

variant: meltanolabs

pip_url: git+<https://github.com/MeltanoLabs/tap-postgres.git>

config:

user: northwind_user

password: thewindisblowing

port: 5432

host: localhost

database: northwind

select:

\- public-\.\

Criação da seção “loaders”.

Para o CSV será utilizado o loader “target-csv” (<https://hub.meltano.com/loaders/target-csv/>). Como esse loader será utilizado por mais de uma operação, foi criado um nome adicional “target-csv-postgresql” que herda (inherit_from: target-csv) as definições do nome original “target-csv”. É informado onde deverão ser armazenados os arquivos (output_path: ../data/postgres) e a máscara do path que inclui o nome do arquivo ({stream_name}), a data informada como parâmetro da execução do script ($START_DATE)

&nbsp; - name: target-csv

&nbsp;   variant: meltanolabs

&nbsp;   pip_url: git+<https://github.com/MeltanoLabs/target-csv.git>

&nbsp; - name: target-csv-postgresql

&nbsp;   inherit_from: target-csv

&nbsp;   config:

&nbsp;     output_path: ../data/postgres

&nbsp;     file_naming_scheme: '{stream_name}/$START_DATE/{stream_name}.csv'
