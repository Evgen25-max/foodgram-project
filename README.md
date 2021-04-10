![example event parameter](https://github.com/github/docs/actions/workflows/main.yml/badge.svg?event=pull_request)

![](https://github.com/Evgen25-max/yamdb_final/workflows/yamdb_final-app/badge.svg)

![](https://github.com/Evgen25-max/foodgram-project/workflows/ffff/main.yml/badge.svg)



# Foodgram project. Yandex Praktikum - final sprint.
This is an online service where users can publish recipes, subscribe to other users ' publications, 
add their favorite recipes to the Favorites list, and download a summary list of products needed to 
prepare one or more selected dishes before going to the store.

## Functionality:
Authorization: email verification with a confirmation code.

What I used:
- [Django Version: 3.0](https://www.djangoproject.com/)
- [Django REST Version: 3.12.2](https://www.django-rest-framework.org/)
- [PostgreSQL Version: 13.1](https://www.postgresql.org/docs/13/release-13-1.html)

## Pre-installation
You need to install [docker](https://www.docker.com/products/docker-desktop "use the link if necessary") on your server 
## Getting Started

- Clone the repository to your server.
-  Create your own **.env** file. You can use the **.example_env** file as a base. In the file, you must specify the data for the correct operation of the Django framework and the postgresql database:
   * DJANGO_SECRET_KEY
   * DB_ENGINE   
   * DB_NAME   
   * POSTGRES_DB
   * POSTGRES_USER
   * POSTGRES_PASSWORD
   * DB_HOST
   * DB_PORT
   * DEFAULT_FROM_EMAIL
   * EMAIL_USE_TLS
   * EMAIL_HOST
   * EMAIL_HOST_USER
   * EMAIL_HOST_PASSWORD
   * EMAIL_PORT
- Go to the root folder of the project and run the following commands (use ```sudo``` if superuser rights are required):
  - ```docker-compose up```
  - Log in to your container with the ```docker exec-it <CONTAINER ID> bash```    
    command, where <CONTAINER ID> is the container ID named "app_web_1". Get your <CONTAINER ID>    
    with the ```docker container ls``` command.
    - Apply django migrate ```python manage.py migrate```    
    - Create superuser: ```python manage.py createsuperuser```   
    - To collect the static files: ```python manage.py collectstatic```
    - Load the initial data, *if necessary*: ```python manage.py loaddata fixtures/new_fixt.json```

# Example of a working site
http://www.foodgram-proj.ml/
   
Use a request ```http://localhost/``` to make sure everything works.    

### Author:
- GitHub:  [github.com/Evgen25-max](https://github.com/Evgen25-max)

