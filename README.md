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
CREATE TABLE verticals (
        name VARCHAR(255) NOT NULL, 
        PRIMARY KEY (name), 
        UNIQUE (name)
)

-- Table brand
CREATE TABLE brands (
        name VARCHAR(255) NOT NULL, 
        vertical VARCHAR(255) NOT NULL, 
        PRIMARY KEY (name), 
        UNIQUE (name, vertical), 
        CONSTRAINT brand_vertical_name_fkey FOREIGN KEY(vertical) REFERENCES verticals (name) ON DELETE RESTRICT
)

-- Table ad
CREATE TABLE ads (
        ad_spot_id INTEGER NOT NULL AUTO_INCREMENT, 
        brand VARCHAR(255) NOT NULL, 
        household_id INTEGER NOT NULL, 
        ad_date DATE NOT NULL, 
        view_duration BIGINT NOT NULL, 
        PRIMARY KEY (ad_spot_id), 
        CONSTRAINT ad_brand_name_fkey FOREIGN KEY(brand) REFERENCES brands (name) ON DELETE RESTRICT
)
```

## Schema

```
mysql> describe vertical;
+-------+--------------+------+-----+---------+----------------+
| Field | Type         | Null | Key | Default | Extra          |
+-------+--------------+------+-----+---------+----------------+
| name  | varchar(255) | NO   | PRI | NULL    | auto_increment |
+-------+--------------+------+-----+---------+----------------+
2 rows in set (0.01 sec)

mysql> describe brand;
+----------+--------------+------+-----+---------+----------------+
| Field    | Type         | Null | Key | Default | Extra          |
+----------+--------------+------+-----+---------+----------------+
| name     | varchar(255) | NO   | PRI | NULL    | auto_increment |
| vertical | varchar(255) | NO   | MUL | NULL    |                |
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

## Processing the Input File
### Assumptions
- The input file is a valid ``.csv``-format file
- A file containing billions of records of data can be processed in batches:
    - By splitting it into multiple smaller files which will be loaded one after the other
    - By loading the single file in chunks of a predefined range. This range can user-defined

Before denormalizing the database it is possible to batch load the ``.csv`` file
in a MySQL database by running the following sample script:

```mysql
LOAD DATA LOCAL INFILE  '/path/to/sample.csv'
INTO TABLE old_table
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
```

to get the following sample output

```
   HOUSEHOLD_ID    BRAND     VERTICAL   AD_SPOT_ID      AD_DATE   VIEW_DURATION
0             1   Toyota   Automotive            1   2016-01-01              10
1             2   Toyota   Automotive            1   2016-01-01               9
2             1      KFC   Fast Foods            2   2016-01-02              15

```

While this works to an extent, it is inefficient when we are dealing with a considerably
large dataset with billions of records. Particularly, we encounter:

* Create anomalies,
* Update anomalies and
* Delete anomalies 
