FROM openknowledge/ckan-dev:2.9

RUN apk add openldap-dev geos-dev geos

# ckan is installed in /srv/app/src/ckan in the ckan-dev image we're basing this image on
WORKDIR /srv/app/src/ckanext-nhm

# copy over the ckanext-nhm source
COPY . .

# might as well update pip while we're here!
RUN pip3 install --upgrade pip

# fixes this https://github.com/ckan/ckan/issues/5570
RUN pip3 install pytest-ckan

# install the dependencies
RUN python3 setup.py develop && \
    pip3 install -r requirements.txt && \
    pip3 install -r dev_requirements.txt

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
