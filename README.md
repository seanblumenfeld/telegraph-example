#telegraph-example

##Requirements
Docker and Docker Compose are required to run this application. Installation guides can be found here:
* https://docs.docker.com/engine/installation/
* https://docs.docker.com/compose/install/

##Usage
This application uses make as its interface.
* To run the application do `make up`
* To run all tests do `make test`
* To tear down the application do `make down`
* To run the linter do `make lint`

The airflow UI should be reachable at localhost:8080.

In order to process a hitlog file:
* Move a valid `hitlog.csv` file into the data directory
* Navigate to the UI localhost:8080
* Flick the toggle on the left hand side to turn ON the hitlog dag. Note, if you do not so this then the dag will never start
* Click on the "trigger dag" button to start a run.
* An output file will created in the data directory called `out.csv`
