FROM naturalhistorymuseum/ckantest:0.1

# these two are required by ckanext-ldap
RUN apt-get -q -y install libldap2-dev libsasl2-dev \
    && apt-get -q clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /base/src/ckanext-nhm

# copy over the ckanext-nhm source
COPY . .

# install the dependencies
RUN python setup.py develop && \
    pip install -r requirements.txt && \
    pip install -r dev_requirements.txt

# ultrahack - the ckanext-dcat extension doesn't bother to put its dependencies in its setup.py and
# therefore installing it doesn't install its dependencies and it breaks. Great! Because we're
# installing the extensions not in editable mode we can't get to the requirements.txt which means
# we have this ultrahack. It works a treat but it feels real nasty. Note that the version here will
# need to be kept up to date with the one in our setup.py.
RUN curl -s "https://raw.githubusercontent.com/ckan/ckanext-dcat/6b7ec505f303fb18e0eebcebf67130d36b3dca82/requirements.txt" | pip install -r /dev/stdin

# this entrypoint ensures our service dependencies (postgresql, solr and redis) are running before
# running the cmd
ENTRYPOINT ["/bin/bash", "/opt/waits/all.sh"]

# run the tests with coverage output
CMD ["pytest", "--cov=ckanext.nhm", "--ckan-ini=test.ini", "tests"]
