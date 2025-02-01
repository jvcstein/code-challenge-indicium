# Indicium Tech Code Challenge

Code challenge for Software Developer with focus in data projects.


## Context

At Indicium we have many projects where we develop the whole data pipeline for our client, from extracting data from many data sources to loading this data at its final destination, with this final destination varying from a data warehouse for a Business Intelligency tool to an api for integrating with third party systems.

As a software developer with focus in data projects your mission is to plan, develop, deploy, and maintain a data pipeline.


# Preliminar Setup

1. Cloned GitHub repository
		
		mkdir -p /opt/indicium
		cd /opt/indicium
		git clone https://github.com/techindicium/code-challenge.git
	
2. Using Docker and Docker Compose, I started the container that creates the Northwind database by executing the script “/data/northwind.sql” and makes the CSV file “/data/order_details.csv” available.
		
		cd /opt/indicium/code-challenge
		docker compose up
	
3. Test the database access to check if everything is okay.
	
		psql -U northwind_user -h localhost -p 5432 northwind
		Senha para o usuário northwind_user:
		psql (16.4 (Ubuntu 16.4-1.pgdg22.04+1), servidor 12.22 (Debian 12.22-1.pgdg120+1))
		Digite "help" para obter ajuda.

		northwind=# \dt
		                     Lista de relações
		 Esquema |          Nome          |  Tipo  |      Dono
		---------+------------------------+--------+----------------
		 public  | categories             | tabela | northwind_user
		 public  | customer_customer_demo | tabela | northwind_user
		 public  | customer_demographics  | tabela | northwind_user
		 public  | customers              | tabela | northwind_user
		 public  | employee_territories   | tabela | northwind_user
		 public  | employees              | tabela | northwind_user
		 public  | orders                 | tabela | northwind_user
		 public  | products               | tabela | northwind_user
		 public  | region                 | tabela | northwind_user
		 public  | shippers               | tabela | northwind_user
		 public  | suppliers              | tabela | northwind_user
		 public  | territories            | tabela | northwind_user
		 public  | us_states              | tabela | northwind_user
		(13 linhas)

		northwind=# /q
	
4. Meltano Installation
		
		pip install meltano
	
5. Airflow Installation
		
		meltano add utility airflow
		meltano invoke airflow:initialize
		meltano invoke airflow users create -u airflow -p airflow --role Admin -e airflow -f admin -l admin
		meltano invoke airflow scheduler &
		meltano invoke airflow webserver

## Meltano Setup

1. “meltano-postgresql-csv” project creation

		meltano init meltano-postgresql-csv 
		cd meltano-postgresql-csv

2. Adding “extractors” and “loaders” 

		meltano add extractor tap-postgres 
		meltano add extractor tap-csv 
		meltano add loader target-csv 
		meltano add loader target-postgres

# Meltano Setup for Step 1

1. Adjustments in the “meltano.yml” file to define the extractor for PostgreSQL and the loader for CSV.

	Creation of the “extractors” section.  
	For PostgreSQL, the extractor “tap-postgres” ([https://hub.meltano.com/extractors/tap-postgres/](https://hub.meltano.com/extractors/tap-postgres/)) will be used.  
	Access credentials for the database running in the container are provided.  
	In the “select” subsection, it is specified that all files in the “public” schema/catalog (public-_) should be selected, and all columns (._) should be retrieved.

		plugins: 
			extractors: 
				- name: tap-postgres
					variant: meltanolabs 
					pip_url: git+https://github.com/MeltanoLabs/tap-postgres.git 
					config: user: northwind_user 
						password: thewindisblowing 
						port: 5432 
						host: localhost 
						database: northwind 
					select: 
						- public-*.*


	Creation of the “loaders” section.  

	For CSV, the loader “target-csv” ([https://hub.meltano.com/loaders/target-csv/](https://hub.meltano.com/loaders/target-csv/)) will be used.  

	Since this loader will be used for multiple operations, an additional name, “targetcsv-postgresql,” was created, inheriting (`inherit_from: target-csv`) the definitions of the original name, “target-csv.”  
	The storage location for the files is specified (`output_path: ../data/postgres`), along with the path mask that includes the file name (`{stream_name}`) and the execution date parameter (`$START_DATE`).

		- name: target-csv 
		  variant: meltanolabs 
		  pip_url: git+https://github.com/MeltanoLabs/target-csv.git 
		- name: target-csv-postgresql 
		  inherit_from: target-csv 
		  config: 
			  output_path: ../data/postgres 
			  file_naming_scheme: '{stream_name}/$START_DATE/{stream_name}.csv'


2. Adjustments in the “meltano.yaml” file for defining the extractor for CSV in Docker and the local CSV loader

	Creation of the “extractors” section

	For CSV, the extractor “tap-csv” ([https://hub.meltano.com/extractors/tap-csv/](https://hub.meltano.com/extractors/tap-csv/)) will be used.  
	Since this extractor will be used for multiple operations, an additional name, “tap-csv-docker,” was created, inheriting (`inherit_from: tap-csv`) the definitions of the original name, “tap-csv.”

		# shared config for tap-csv (for inheritance)
		- name: tap-csv
		  variant: meltanolabs
		  pip_url: git+https://github.com/MeltanoLabs/tap-csv.git

		# read order_details from csv at Docker path
		- name: tap-csv-docker
		  inherit_from: tap-csv
		  config:
				files: [{entity: order_details, path: $MELTANO_PROJECT_ROOT/../data/order_details.csv, keys: [order_id, product_id, unit_price, quantity, discount]}]

	 Creation of the “loaders” section

	For CSV, the loader “target-csv” ([https://hub.meltano.com/loaders/target-csv/](https://hub.meltano.com/loaders/target-csv/)) will be used.  
	Since this loader will be used for multiple operations, an additional name, “target-csv-postgresql,” was created, inheriting (`inherit_from: target-csv`) the definitions of the original name, “target-csv.”  
	The storage location for the files is specified (`output_path: $MELTANO_PROJECT_ROOT/../data/csv`), along with the path mask that includes the file name (`{stream_name}`) and the execution date parameter (`$START_DATE`).

		# write order_details from Docker container path to csv at local path
		- name: target-csv-csv
		  inherit_from: target-csv
		  config:
				output_path: $MELTANO_PROJECT_ROOT/../data/csv
				file_naming_scheme: $START_DATE/{stream_name}.csv

# Meltano Setup for Step 2

 1. Adjustments in the “meltano.yml” file for defining the extractor for CSV and the loader for PostgreSQL

	 Creation of the “extractors” section

	For CSV, the extractor “tap-csv” ([https://hub.meltano.com/extractors/tap-csv/](https://hub.meltano.com/extractors/tap-csv/)) will be used.  
	Since this extractor will be used for multiple operations, an additional name, “tap-csv-local,” was created, inheriting (`inherit_from: tap-csv`) the definitions of the original name, “tap-csv.”  
	The name of the table to be created is specified as `entity: order_details`.



		# read order_details from csv at local path
		- name: tap-csv-local
		   inherit_from: tap-csv
		   config:
				files: [{entity: order_details, path: $MELTANO_PROJECT_ROOT/../data/csv/$START_DATE/order_details.csv,
					keys: [order_id, product_id, unit_price, quantity, discount]}]


	Creation of the “loaders” section

	For PostgreSQL, the loader “target-postgres” ([https://hub.meltano.com/loaders/target-postgres/](https://hub.meltano.com/loaders/target-postgres/)) will be used.  
	Access credentials for the database running in the container are provided.  
	The schema/catalog where the table should be created is specified (`default_target_schema: public`).

		- name: target-postgres
		  variant: meltanolabs
		  pip_url: meltanolabs-target-postgres
		  config:
				user: northwind_user
				password: thewindisblowing
				port: 5432
				host: localhost
				database: northwind
				default_target_schema: public


## Manual Execution of Step 1

To run the script that extracts tables from PostgreSQL and stores them in CSV files on the local filesystem, specifying the start date (START_DATE) as a parameter:

	START_DATE=2025-01-30 meltano run tap-postgres target-csv-postgresql
	
To run the script that extracts a CSV file from Docker and stores it on the local filesystem, specifying the start date (START_DATE) as a parameter:

	START_DATE=2025-01-30 meltano run tap-csv-docker target-csv-csv

## Manual Execution of Step 2

To run the script that creates the “order_details” table in PostgreSQL from the CSV file on the local filesystem, specifying the start date (START_DATE) as a parameter:

	START_DATE=2025-01-30 meltano run tap-csv-local target-postgres

 ### Airflow Setup

For scheduled execution of the scripts via Airflow, three DAGs were created:

![Airflow](/airflow.png)

## Scheduled Execution of Step 1

The scripts for Step 1 are executed daily.

To execute the script that extracts tables from PostgreSQL and stores them in CSV files on the local filesystem, specifying the start date (START_DATE) as a parameter:

	s1_meltano_dag_extract_docker_postgresql_to_local_csv.py
	
To execute the script that extracts a CSV file from Docker and stores it on the local filesystem, specifying the start date (START_DATE) as a parameter:

	s1_meltano_dag_extract_docker_csv_to_local_csv.py

## Scheduled Execution of Step 2

The execution of the Step 2 script depends on the completion of the Step 1 scripts. The script reads the CSV table from the local filesystem and creates the table in PostgreSQL. An `ExternalTaskSensor` is used to monitor when the two Step 1 scripts have been successfully completed:

	s2_meltano_dag_create_order_details_at_docker_postgresql.py

To generate evidence of the script execution, the following query lists the data from the "orders" and "order_details" tables:

	SELECT o.*
	,      d.*
	FROM orders o
	LEFT OUTER JOIN order_details d
	   ON o.order_id = d.order_id::INTEGER
	ORDER BY o.order_id
	, 		 o.customer_id
	,        o.order_date
	,        d.product_id

To generate a CSV file from the output of this command using psql:

	psql -U northwind_user -h localhost -p 5432 -d northwind -c "\copy (SELECT o., d. FROM orders o LEFT OUTER JOIN order_details d ON o.order_id = d.order_id::INTEGER ORDER BY o.order_id, o.customer_id, o.order_date, d.product_id) TO '/tmp/orders.csv' WITH CSV HEADER;"

This command output is in the directory /data/orders.csv
