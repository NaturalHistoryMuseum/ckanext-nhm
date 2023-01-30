FROM naturalhistorymuseum/ckantest:latest

# required by python-ldap (via ckanext-ldap)
RUN apt-get -q -y install libldap2-dev libsasl2-dev \
    && apt-get -q clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /base/src/ckanext-nhm

# copy over the source
COPY . .

# see readme for explanation of why this is here and not installed automatically in the
# next step
RUN pip install git+https://github.com/ckan/ckanext-dcat@v1.3.0#egg=ckanext-dcat

# install the base + test dependencies
RUN pip install -e .[test]

# ultrahack - the ckanext-dcat extension doesn't bother to put its dependencies in its setup.py and
# therefore installing it doesn't install its dependencies and it breaks. Great! Because we're
# installing the extensions not in editable mode we can't get to the requirements.txt which means
# we have this ultrahack. It works a treat but it feels real nasty. Note that the version here will
# need to be kept up to date with the one in our setup.py.
RUN curl -s "https://raw.githubusercontent.com/ckan/ckanext-dcat/v1.3.0/requirements.txt" | pip install -r /dev/stdin

# this entrypoint ensures our service dependencies (postgresql, solr, redis, elasticsearch, and mongodb) are running before
# running the cmd
ENTRYPOINT ["/bin/bash", "/opt/waits/all.sh"]

# run the tests with coverage output
CMD ["bash", "/opt/scripts/run-tests.sh", "ckanext.nhm"]
