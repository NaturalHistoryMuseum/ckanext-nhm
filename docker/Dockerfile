# use the bionic base image because it matches the current real servers
FROM ubuntu:bionic

ENV CKAN_START_SUPERVISOR="TRUE"
ENV CKAN_RUN_INIT="FALSE"
ENV BASE_CKAN_BRANCH="ckan-2.9.5"

RUN DEBIAN_FRONTEND=noninteractive && \
    apt-get -q -y update && \
    apt-get -q -y upgrade && \
    apt-get -q -y install software-properties-common && \
    add-apt-repository universe && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get -q -y update && \
    apt-get -q -y install \
        # install system packages required by ckan
        python3.8 \
        python3.8-dev \
        python3.8-venv \
        libpq-dev \
        libxml2-dev \
        libxslt-dev \
        libgeos-dev \
        libssl-dev \
        libffi-dev \
        postgresql-client \
        build-essential \
        supervisor \
        # install packages for additional bits and bobs (like the entrypoint script)
        wget \
        git \
        curl \
        netcat \
        uuid-runtime \
        # these two are required by ckanext-ldap
        libldap2-dev \
        libsasl2-dev \
    && apt-get -q clean \
    && rm -rf /var/lib/apt/lists/*

# install nodejs
RUN curl -sL https://deb.nodesource.com/setup_15.x | bash && \
    apt-get install -q -y nodejs

# we're gonna use a venv for a couple of reasons. Firstly, it avoids any OS level python package
# clashes/dependencies. Secondly, it matches how we run stuff on the live servers. And finally, it
# means we can use a different version of python3 to the one shipped with ubuntu 18.04.
# For info on the next 3 lines: https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
ENV VIRTUAL_ENV=/venv
RUN python3.8 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install -U pip && pip install wheel

#COPY src/ckan/ /base/src/ckan/

RUN mkdir -p /base/data/ckan/storage && \
    mkdir -p /base/src/ckan

WORKDIR /base/src/ckan

# setup ckan and its dependencies
RUN git clone -b ${BASE_CKAN_BRANCH} https://github.com/ckan/ckan.git . && \
    pip install -r requirement-setuptools.txt && \
    pip install -r requirements.txt && \
    pip install -r dev-requirements.txt && \
    pip install -e . && \
    npm install . --only=prod

WORKDIR /base/src/ckanext-nhm

# copy over the ckanext-nhm source
COPY . .

# might as well update pip while we're here!
RUN pip3 install --upgrade pip

# fixes this https://github.com/ckan/ckan/issues/5570
RUN pip3 install pytest-ckan

# install the dependencies
RUN python setup.py develop && \
    pip install -r requirements.txt && \
    pip install -r dev_requirements.txt

# ultrahack - the ckanext-dcat extension doesn't bother to put its dependencies in its setup.py and
# therefore installing it doesn't install its dependencies and it breaks. Great! Because we're
# installing the extensions not in editable mode we can't get to the requirements.txt which means
# we have this ultrahack. It works a treat but it feels real nasty. Note that the version here will
# need to be kept up to date with the one in our setup.py.
RUN curl -s "https://raw.githubusercontent.com/ckan/ckanext-dcat/6b7ec505f303fb18e0eebcebf67130d36b3dca82/requirements.txt" | pip3 install -r /dev/stdin

# this entrypoint ensures our service dependencies (postgresql, solr and redis) are running before
# running the cmd
ENTRYPOINT ["/bin/bash", "docker/entrypoint.sh"]

# run the tests with coverage output
CMD ["pytest", "--cov=ckanext.nhm", "--ckan-ini=test.ini", "tests"]
