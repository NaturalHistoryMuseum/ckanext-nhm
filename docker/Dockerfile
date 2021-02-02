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

# ultrahack
RUN curl -s "https://raw.githubusercontent.com/ckan/ckanext-dcat/v1.1.0/requirements.txt" | pip3 install -r /dev/stdin

# this entrypoint ensures our service dependencies (postgresql, solr and redis) are running before
# running the cmd
ENTRYPOINT ["/bin/bash", "docker/entrypoint.sh"]

# run the tests with coverage output
CMD ["pytest", "--cov=ckanext.nhm", "--ckan-ini=test.ini", "tests"]
