# 4c Insights Take-Home Assignment

## Instructions 

Examine the ``Database Design Exercise (Mediaocean-4C).docx`` document in the root folder

## Entity Relationship Diagram

![ERD Database Logical Design](Database-ERD.png)

# Setting Up

## Pre-requisites
- [Python 3](https://www.python.org/)
- [MySQL](https://dev.mysql.com/) - Follow the docs to set up your DB and DB User
 
## Instructions

* Clone repo:

  ```bash
  $ git clone git@github.com:kangaliaisaac/4c-insights-take-home-assignment.git
  ```

* `cd` into the root directory and activate virtualenv

    ```bash
    $ cd /path/to/root/directory/
    $ python3 -m virtualenv venv
    $ . venv/bin/activate
    $ . .env
    ```
  
    In your ``.env`` file export the following variables
    
    ```bash
    #! /usr/bin/bash

    export DB_USER=""
    export DB_PASS=""
    export DB_NAME=""

    ```
 
* Install requirements

    ```bash
    $ pip install --upgrade pip
    $ pip install -r requirements.txt
    ```

## Database Creation Script

```mysql
-- Table vertical
CREATE TABLE vertical (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    name VARCHAR(255) NOT NULL, 
    PRIMARY KEY (id)
)

-- Table brand
CREATE TABLE brand (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    name VARCHAR(255) NOT NULL, 
    vertical INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT brand_vertical_id_fkey FOREIGN KEY(vertical) REFERENCES vertical (id) ON DELETE RESTRICT
)

-- Table ad
CREATE TABLE ad (
    ad_spot_id INTEGER NOT NULL AUTO_INCREMENT, 
    brand INTEGER NOT NULL, 
    household_id INTEGER NOT NULL, 
    ad_date DATE NOT NULL, 
    view_duration BIGINT NOT NULL, 
    PRIMARY KEY (ad_spot_id), 
    CONSTRAINT ad_brand_id_fkey FOREIGN KEY(brand) REFERENCES brand (id) ON DELETE RESTRICT
)
```

## Schema

```
mysql> describe vertical;
+-------+--------------+------+-----+---------+----------------+
| Field | Type         | Null | Key | Default | Extra          |
+-------+--------------+------+-----+---------+----------------+
| id    | int          | NO   | PRI | NULL    | auto_increment |
| name  | varchar(255) | NO   |     | NULL    |                |
+-------+--------------+------+-----+---------+----------------+
2 rows in set (0.01 sec)

mysql> describe brand;
+----------+--------------+------+-----+---------+----------------+
| Field    | Type         | Null | Key | Default | Extra          |
+----------+--------------+------+-----+---------+----------------+
| id       | int          | NO   | PRI | NULL    | auto_increment |
| name     | varchar(255) | NO   |     | NULL    |                |
| vertical | int          | NO   | MUL | NULL    |                |
+----------+--------------+------+-----+---------+----------------+
3 rows in set (0.00 sec)

mysql> describe ad;
+---------------+--------+------+-----+---------+----------------+
| Field         | Type   | Null | Key | Default | Extra          |
+---------------+--------+------+-----+---------+----------------+
| ad_spot_id    | int    | NO   | PRI | NULL    | auto_increment |
| brand         | int    | NO   | MUL | NULL    |                |
| household_id  | int    | NO   |     | NULL    |                |
| ad_date       | date   | NO   |     | NULL    |                |
| view_duration | bigint | NO   |     | NULL    |                |
+---------------+--------+------+-----+---------+----------------+
5 rows in set (0.00 sec)
```
