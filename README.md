
## Requirement

1. System Memory at least 4GB for Docker Swarm mode
2. Docker version >= 18.05.0 (we will switch to 18.06 stable version after it is released)
3. Docker in swarm mode (See below.)
4. Python >= 3.6

## Documents

* [Run Python3.6 with Ubuntu 16.04](documents/ubuntu_16.04_with_python3.6.md)
* [Start Django Hello World App](documents/start_django_hello_world_app.md)


## Setup

1. Docker in swarm mode

```
docker swarm init
```

This will config your machine to become single docker swarm mode. The is enough
for our developement.

For more information: <https://docs.docker.com/engine/swarm/swarm-tutorial/>


## How-to Use

There is a helper script `docker-util.sh` and its config file `docker-util.conf`

### `docker-util.conf`

Now, we need them all to be ON.

- [ ] TODO


### Prepare Docker images

```
./docker-util.sh build
```

This command will build all docker iamges needed in our services.

You may see some error messages, like:
```
ERROR: for sql_table_creator  pull access denied for cameo/sql_table_creator, repository does not exist or may require 'docker login'
ERROR: for iot_data  pull access denied for cameo/logstash-iot_data, repository does not exist or may require 'docker login'
ERROR: for logspout  pull access denied for cameo/logspout, repository does not exist or may require 'docker login'
ERROR: for mysql  pull access denied for cameo/mariadb, repository does not exist or may require 'docker login'
ERROR: for epa-package_py  pull access denied for cameo/epa-python, repository does not exist or may require 'docker login'
ERROR: pull access denied for cameo/epa-python, repository does not exist or may require 'docker login'
```
Ignore these error messages.

### Run Docker services

```
./docker-util.sh start
```

This command will run all services in which are ON in `docker-utils.conf`


### Stop Docker services

```
./docker-util.sh stop
```

### Remove local volumes

In the case, you need to reset your local volumes used by Docker services,
ex: stored MySQL DB, you can clean all of them:

```
./docker-util.sh clean-volume
```


## Examples

* [Read ORM Data-Layer](examples/read_database)


## Logging and ELK

By default, all Docker services' log messages are re-directed to ELK stack.

After running all of the services, open Kibana url to view logs: `http://localhost/5601`


## Commitment rule

1. No push to `master` and `staging` branch.Instead, create a new branch on
   top of latest `staging` branch with name related to your development.
2. Push your local branch to Github.com.
3. Send a `Pull Request`.


## TODO

- [ ] pre-commit documents

## 如何使用GitLab

### 1. 連接 GitHub與GitLab
1. Create a project
![001](https://user-images.githubusercontent.com/4774659/42207120-b3f141fc-7edb-11e8-9264-30677f7a2e6f.png)

2. Select `CI/CD for external repo` and click `GitHub`
![002](https://user-images.githubusercontent.com/4774659/42207412-7056fec2-7edc-11e8-879b-c6a28e2e77a2.png)

3. Click `Authorize`
![003](https://user-images.githubusercontent.com/4774659/42207445-801cbdb0-7edc-11e8-8958-41df6b00e6ab.png)

4. Select the repo and click `Connect`
![004](https://user-images.githubusercontent.com/4774659/42207490-9b4ed956-7edc-11e8-922b-723b9f503931.png)

5. Waiting the status until `Done`
![005](https://user-images.githubusercontent.com/4774659/42207507-acaa352e-7edc-11e8-914d-253d27967df6.png)

6. You can view your CI project
![006](https://user-images.githubusercontent.com/4774659/42207534-bcbe28d0-7edc-11e8-8242-5498605c726a.png)


### 2. 在 GitHub 加 .gitlab-ci.yml 檔案

- .gitlab-ci.yml要怎麼寫？參考 [這份文件](https://docs.gitlab.com/ee/ci/yaml/README.html)
- .gitlab-ci.yaml的格式檢查，可以在 **Pipelines** 裡的 `CI Lint`
![ci lint](https://user-images.githubusercontent.com/4774659/42212689-72168d9c-7ee9-11e8-9729-a4493df31cf1.png)

- 如果要指定Job可以在哪個branch被執行，可以用 `only` or `except`

1. 只要一有push，到GitLab裡的Pipeline
![2001](https://user-images.githubusercontent.com/4774659/42207558-caa673f8-7edc-11e8-8374-98823ff42dfe.png)

2. 就可以看到有一個pipeline被trigger
![2002](https://user-images.githubusercontent.com/4774659/42208222-4164a932-7ede-11e8-968f-79d6639d9555.png)

### 參考文件
- [gitlab-ci django example project](https://gitlab.com/gableroux/gitlab-ci-example-django)
- [gitlab-ci Docker example project](https://gitlab.com/gableroux/gitlab-ci-example-docker)
- [Test all the things in GitLab CI with Docker by example](https://about.gitlab.com/2018/02/05/test-all-the-things-gitlab-ci-docker-examples/)
- [GitLab Build and Deploy to a Server via SSH](https://codeburst.io/gitlab-build-and-push-to-a-server-via-ssh-6d27ca1bf7b4)
