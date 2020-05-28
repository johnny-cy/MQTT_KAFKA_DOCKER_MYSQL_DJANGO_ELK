
## Run this example

### Setup python virtual-environment

``` sh
python3 -m venv venv3
source  venv3/bin/active
```

### Install required packages

``` sh
pip install -r requirements.txt
```

### Modify MySQL Settings

open file `local_settings.py`

``` python
MYSQL_ADDRESS = "localhost"
MYSQL_DB = "epa"
MYSQL_USER = "epa"
MYSQL_PASSWORD = "epa"
MYSQL_CONNECTION_DIALECT = (
    f"mysql+mysqldb://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_ADDRESS}/"
    f"{MYSQL_DB}?charset=utf8mb4"
)
```

This is default setting, it shoud work in most development environment.


#### How does this work?

In Docker **dev** mode environment, all services will export ports to localhost.
This including MySQL server which will export 3306 port to local **dev** host.

In our `epa` pakcage, there is a setting for MySQL DB. The connection is default
to docker container which name is `mysq`. By setting `local_settings.py`, `epa` package
will try to load `local_settings.py` if exists.


> **Note:**
> `local_settings.py` is for development.
> In product environment, these variables will vary.  We use it for example here.
> Don't commit it to git.

### Run example

``` sh
cd examples/read_database
python3 read_lass.py
```

### Exit virtual-environment

``` sh
deactive
```


## How to Load DB data with ORM

``` python
def read_examples():
    print("Fetch all data for LassRawData")
    df = LassRawData.read_df()
    print(df)
    print()


    print("Fetch all data for LassRawData, but only specified columns")
    df = LassRawData.read_df(columns=["time", "device_id"])
    print(df)
    print()


    print("Filtering with where")
    df = LassRawData.read_df(where=["device_id = '1530068615'"])
    print(df)
    print()


    print("Multiple where statement with list, these statement are ANDed")
    where = [
        "time > '2018-05-01'",  # Not good to embeded variable in statement
        "time < '2018-05-08'",
    ]
    df = LassRawData.read_df(where=where)
    print(df)
    print()


    print("Statement with variables")
    start_time = datetime.date(2018, 5, 1)
    end_time = datetime.date(2018, 5, 8)
    where = [
        "time > :start_time",   # variable format ":var_name"
        "time < :end_time",
    ]
    df = LassRawData.read_df(where=where,
            start_time=start_time, end_time=end_time)
    print(df)
    print()


    print("Work-around for OR operation")
    where = [
        "device_id = '5870315151' or device_id = '5881917808'",
    ]
    df = LassRawData.read_df(where=where)
    print(df)
    print()


    print("IN Operation")
    where = [
        "device_id IN :devices"
    ]
    devices = ["5870315151", "5881917808"]
    df = LassRawData.read_df(where=where, devices=devices)
    print(df)
    print()

    print("limit")
    df = LassRawData.read_df(limit=4)
    print(df)
    print()
```
