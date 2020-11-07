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
        id INTEGER NOT NULL AUTO_INCREMENT, 
        name VARCHAR(255) NOT NULL, 
        PRIMARY KEY (id), 
        UNIQUE (name)
)

-- Table brand
CREATE TABLE brands (
        id INTEGER NOT NULL AUTO_INCREMENT, 
        name VARCHAR(255) NOT NULL, 
        vertical INTEGER NOT NULL, 
        PRIMARY KEY (id), 
        UNIQUE (name, vertical), 
        CONSTRAINT brand_vertical_pk_fkey FOREIGN KEY(vertical) REFERENCES verticals (id) ON DELETE RESTRICT
)

-- Table ad
CREATE TABLE ads (
        id INTEGER NOT NULL AUTO_INCREMENT, 
        ad_spot_id INTEGER NOT NULL, 
        brand INTEGER NOT NULL, 
        household_id INTEGER NOT NULL, 
        ad_date DATE NOT NULL, 
        view_duration BIGINT NOT NULL, 
        PRIMARY KEY (id), 
        CONSTRAINT ad_brand_pk_fkey FOREIGN KEY(brand) REFERENCES brands (id) ON DELETE RESTRICT
)
```

## Schema

```
mysql> describe verticals;
+-------+--------------+------+-----+---------+----------------+
| Field | Type         | Null | Key | Default | Extra          |
+-------+--------------+------+-----+---------+----------------+
| id    | int          | NO   | PRI | NULL    | auto_increment |
| name  | varchar(255) | NO   | UNI | NULL    |                |
+-------+--------------+------+-----+---------+----------------+
2 rows in set (0.01 sec)

mysql> describe brands;
+----------+--------------+------+-----+---------+----------------+
| Field    | Type         | Null | Key | Default | Extra          |
+----------+--------------+------+-----+---------+----------------+
| id       | int          | NO   | PRI | NULL    | auto_increment |
| name     | varchar(255) | NO   | MUL | NULL    |                |
| vertical | int          | NO   | MUL | NULL    |                |
+----------+--------------+------+-----+---------+----------------+
3 rows in set (0.00 sec)

mysql> describe ads;
+---------------+--------+------+-----+---------+----------------+
| Field         | Type   | Null | Key | Default | Extra          |
+---------------+--------+------+-----+---------+----------------+
| id            | int    | NO   | PRI | NULL    | auto_increment |
| ad_spot_id    | int    | NO   |     | NULL    |                |
| brand         | int    | NO   | MUL | NULL    |                |
| household_id  | int    | NO   |     | NULL    |                |
| ad_date       | date   | NO   |     | NULL    |                |
| view_duration | bigint | NO   |     | NULL    |                |
+---------------+--------+------+-----+---------+----------------+
6 rows in set (0.00 sec)
```

## Processing the Input File
### Assumptions and Considerations
- The input file is a valid ``.csv``-format file
- A file containing billions of records of data can be processed in batches:
    - By splitting it into multiple smaller files which will be loaded one after the other
    - By loading the single file in chunks of a predefined range. This range can user-defined. This process can also be automated using asynchronous celery tasks that run at periodic intervals

Before normalizing the database it is possible to batch load the ``.csv`` file
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

This kind of setup makes querying the table inefficient because when we apply filter params, 
each row is evaluated individually which can get slower.

Normalizing the data, allows us to implement faster queries using ``INNER JOINS``. It also affords
us other benefits, including:

- helps alleviate Create, Update, Delete (CUD) anomalies
- searching, sorting, and creating indexes is faster, since tables are narrower
- fewer null values and less redundant data, making your database more compact
- data integrity and consistency guarantees

Normalizing the database will result in the following:

```mysql
mysql> select * from ads;
+----+------------+-------+--------------+------------+---------------+
| id | ad_spot_id | brand | household_id | ad_date    | view_duration |
+----+------------+-------+--------------+------------+---------------+
|  1 |          1 |     1 |            1 | 2016-01-01 |            10 |
|  2 |          1 |     1 |            2 | 2016-01-01 |             9 |
|  3 |          2 |     2 |            1 | 2016-01-02 |            15 |
+----+------------+-------+--------------+------------+---------------+
3 rows in set (0.00 sec)

mysql> select * from verticals;
+----+------------+
| id | name       |
+----+------------+
|  1 | Automotive |
|  2 | Fast Foods |
+----+------------+
2 rows in set (0.00 sec)

mysql> select * from brands;
+----+--------+----------+
| id | name   | vertical |
+----+--------+----------+
|  2 | KFC    |        2 |
|  1 | Toyota |        1 |
+----+--------+----------+
2 rows in set (0.00 sec)

mysql> 
```

## Querying and Fetching Data

#### Per Vertical

```bash
>>> # Get total number of ads viewed
>>> data_processor.get_number_of_ads_viewed("Automotive")
2020-11-07 07:49:13,661 INFO sqlalchemy.engine.base.Engine 
        SELECT COUNT(a.id) 
        FROM ads a
            INNER JOIN brands b ON a.brand = b.id 
            INNER JOIN verticals v on b.vertical = v.id 
        WHERE v.name = 'Automotive'
    
2020-11-07 07:49:13,661 INFO sqlalchemy.engine.base.Engine {}
2
>>>
>>> # Get distinct number of ads
>>> data_processor.get_number_of_distinct_ads("Automotive")
2020-11-07 07:51:16,495 INFO sqlalchemy.engine.base.Engine 
        SELECT COUNT(DISTINCT a.ad_spot_id) 
        FROM ads a 
            INNER JOIN brands b ON a.brand = b.id 
            INNER JOIN verticals v ON b.vertical = v.id 
        WHERE v.name = 'Automotive'
    
2020-11-07 07:51:16,496 INFO sqlalchemy.engine.base.Engine {}
1
>>>
>>> # Get total duration of ads viewed per household
>>> data_processor.get_total_duration_of_ads_viewed_per_household("Automotive")
2020-11-07 07:52:23,308 INFO sqlalchemy.engine.base.Engine 
        SELECT a.household_id, SUM(a.view_duration) 
        FROM ads a 
            INNER JOIN brands b ON a.brand = b.id 
            INNER JOIN verticals v ON b.vertical = v.id 
        WHERE v.name = 'Automotive'
      GROUP BY 1;
2020-11-07 07:52:23,308 INFO sqlalchemy.engine.base.Engine {}
[(1, Decimal('10')), (2, Decimal('9'))]
```

#### Per Vertical and optional Brands
```bash
>>> data_processor.get_number_of_ads_viewed("Automotive", brands=("KFC",))
2020-11-07 07:54:16,133 INFO sqlalchemy.engine.base.Engine 
        SELECT COUNT(a.id) 
        FROM ads a
            INNER JOIN brands b ON a.brand = b.id 
            INNER JOIN verticals v on b.vertical = v.id 
        WHERE v.name = 'Automotive'
     AND b.name = 'KFC'
2020-11-07 07:54:16,133 INFO sqlalchemy.engine.base.Engine {}
0
>>> 
>>> data_processor.get_number_of_distinct_ads("Automotive", brands=("Toyota",))
2020-11-07 07:55:02,030 INFO sqlalchemy.engine.base.Engine 
        SELECT COUNT(DISTINCT a.ad_spot_id) 
        FROM ads a 
            INNER JOIN brands b ON a.brand = b.id 
            INNER JOIN verticals v ON b.vertical = v.id 
        WHERE v.name = 'Automotive'
     AND b.name = 'Toyota'
2020-11-07 07:55:02,030 INFO sqlalchemy.engine.base.Engine {}
1
>>> 
>>> data_processor.get_total_duration_of_ads_viewed_per_household("Automotive", brands=("Toyota",))
2020-11-07 07:55:29,342 INFO sqlalchemy.engine.base.Engine 
        SELECT a.household_id, SUM(a.view_duration) 
        FROM ads a 
            INNER JOIN brands b ON a.brand = b.id 
            INNER JOIN verticals v ON b.vertical = v.id 
        WHERE v.name = 'Automotive'
     AND b.name = 'Toyota'  GROUP BY 1;
2020-11-07 07:55:29,342 INFO sqlalchemy.engine.base.Engine {}
[(1, Decimal('10')), (2, Decimal('9'))]
```

#### Per Vertical and optional Household IDs
```bash
>>> data_processor.get_number_of_ads_viewed("Automotive", household_ids=(2,))
2020-11-07 07:56:25,141 INFO sqlalchemy.engine.base.Engine 
        SELECT COUNT(a.id) 
        FROM ads a
            INNER JOIN brands b ON a.brand = b.id 
            INNER JOIN verticals v on b.vertical = v.id 
        WHERE v.name = 'Automotive'
     AND household_id = 2
2020-11-07 07:56:25,142 INFO sqlalchemy.engine.base.Engine {}
1
>>> 
>>> data_processor.get_number_of_distinct_ads("Automotive", household_ids=(2,))
2020-11-07 07:56:54,656 INFO sqlalchemy.engine.base.Engine 
        SELECT COUNT(DISTINCT a.ad_spot_id) 
        FROM ads a 
            INNER JOIN brands b ON a.brand = b.id 
            INNER JOIN verticals v ON b.vertical = v.id 
        WHERE v.name = 'Automotive'
     AND household_id = 2
2020-11-07 07:56:54,656 INFO sqlalchemy.engine.base.Engine {}
1
>>> 
>>> data_processor.get_total_duration_of_ads_viewed_per_household("Automotive", household_ids=(2,))
2020-11-07 07:57:25,154 INFO sqlalchemy.engine.base.Engine 
        SELECT a.household_id, SUM(a.view_duration) 
        FROM ads a 
            INNER JOIN brands b ON a.brand = b.id 
            INNER JOIN verticals v ON b.vertical = v.id 
        WHERE v.name = 'Automotive'
     AND household_id = 2  GROUP BY 1;
2020-11-07 07:57:25,154 INFO sqlalchemy.engine.base.Engine {}
[(2, Decimal('9'))]
```

#### Per Vertical and optional date ranges
```
>>> data_processor.get_number_of_ads_viewed("Automotive", date_from="2015-01-01", date_to="2017-01-01")
2020-11-07 07:58:28,320 INFO sqlalchemy.engine.base.Engine 
        SELECT COUNT(a.id) 
        FROM ads a
            INNER JOIN brands b ON a.brand = b.id 
            INNER JOIN verticals v on b.vertical = v.id 
        WHERE v.name = 'Automotive'
     AND ad_date BETWEEN '2015-01-01' AND '2017-01-01'
2020-11-07 07:58:28,320 INFO sqlalchemy.engine.base.Engine {}
2
>>> 
>>> data_processor.get_total_duration_of_ads_viewed_per_household("Automotive", date_from="2015-01-01", date_to="2017-01-01")
2020-11-07 07:59:08,759 INFO sqlalchemy.engine.base.Engine 
        SELECT a.household_id, SUM(a.view_duration) 
        FROM ads a 
            INNER JOIN brands b ON a.brand = b.id 
            INNER JOIN verticals v ON b.vertical = v.id 
        WHERE v.name = 'Automotive'
     AND ad_date BETWEEN '2015-01-01' AND '2017-01-01'  GROUP BY 1;
2020-11-07 07:59:08,759 INFO sqlalchemy.engine.base.Engine {}
[(1, Decimal('10')), (2, Decimal('9'))]
>>> 
>>> data_processor.get_number_of_distinct_ads("Automotive", date_from="2015-01-01", date_to="2017-01-01")
2020-11-07 07:59:35,723 INFO sqlalchemy.engine.base.Engine 
        SELECT COUNT(DISTINCT a.ad_spot_id) 
        FROM ads a 
            INNER JOIN brands b ON a.brand = b.id 
            INNER JOIN verticals v ON b.vertical = v.id 
        WHERE v.name = 'Automotive'
     AND ad_date BETWEEN '2015-01-01' AND '2017-01-01'
2020-11-07 07:59:35,723 INFO sqlalchemy.engine.base.Engine {}
1
```

#### By everything
```bash
>>> data_processor.get_number_of_distinct_ads("Automotive", date_from="2015-01-01", date_to="2017-01-01", household_ids=(2,), brands=("Toyota",))
2020-11-07 08:00:23,413 INFO sqlalchemy.engine.base.Engine 
        SELECT COUNT(DISTINCT a.ad_spot_id) 
        FROM ads a 
            INNER JOIN brands b ON a.brand = b.id 
            INNER JOIN verticals v ON b.vertical = v.id 
        WHERE v.name = 'Automotive'
     AND b.name = 'Toyota' AND household_id = 2 AND ad_date BETWEEN '2015-01-01' AND '2017-01-01'
2020-11-07 08:00:23,413 INFO sqlalchemy.engine.base.Engine {}
1
>>> 
>>> data_processor.get_total_duration_of_ads_viewed_per_household("Automotive", date_from="2015-01-01", date_to="2017-01-01", household_ids=(2,), brands=("Toyota",))
2020-11-07 08:01:04,765 INFO sqlalchemy.engine.base.Engine 
        SELECT a.household_id, SUM(a.view_duration) 
        FROM ads a 
            INNER JOIN brands b ON a.brand = b.id 
            INNER JOIN verticals v ON b.vertical = v.id 
        WHERE v.name = 'Automotive'
     AND b.name = 'Toyota' AND household_id = 2 AND ad_date BETWEEN '2015-01-01' AND '2017-01-01'  GROUP BY 1;
2020-11-07 08:01:04,765 INFO sqlalchemy.engine.base.Engine {}
[(2, Decimal('9'))]
```

### Invalid Inputs

#### Invalid date formats
```bash
>>> data_processor.get_total_duration_of_ads_viewed_per_household("Automotive", date_from="incorrect", date_to="date", household_ids=(2,), brands=("Toyota",))
Traceback (most recent call last):
  ...
ValueError: Incorrect data format, should be YYYY-MM-DD
>>> 
```

#### Invalid household_id value types
```bash
>>> data_processor.get_total_duration_of_ads_viewed_per_household("Automotive", date_from="2015-01-01", date_to="2017-01-01", household_ids=("Invalid ID",), brands=("Toyota",))
2020-11-07 08:03:36,679 INFO sqlalchemy.engine.base.Engine 
        SELECT a.household_id, SUM(a.view_duration) 
        FROM ads a 
            INNER JOIN brands b ON a.brand = b.id 
            INNER JOIN verticals v ON b.vertical = v.id 
        WHERE v.name = 'Automotive'
     AND b.name = 'Toyota' AND household_id = Invalid ID AND ad_date BETWEEN '2015-01-01' AND '2017-01-01'  GROUP BY 1;
2020-11-07 08:03:36,679 INFO sqlalchemy.engine.base.Engine {}
2020-11-07 08:03:36,685 INFO sqlalchemy.engine.base.Engine ROLLBACK
Traceback (most recent call last):
  
...
mysql.connector.errors.ProgrammingError: 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'ID AND ad_date BETWEEN '2015-01-01' AND '2017-01-01'  GROUP BY 1' at line 6
...
sqlalchemy.exc.ProgrammingError: (mysql.connector.errors.ProgrammingError) 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'ID AND ad_date BETWEEN '2015-01-01' AND '2017-01-01'  GROUP BY 1' at line 6
[SQL: 
        ...
(Background on this error at: http://sqlalche.me/e/13/f405)
>>> 
```

References:
- [Sybase Infocentre](http://infocenter.sybase.com/help/index.jsp?topic=/com.sybase.dc20020_1251/html/databases/databases216.htm)
- [Database.Guide](https://database.guide/what-is-normalization/)
- [DZone](https://dzone.com/articles/pros-and-cons-of-database-normalization)
