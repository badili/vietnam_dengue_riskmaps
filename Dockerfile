FROM rocker/rstudio-stable:latest

MAINTAINER Wangoru Kihara wangoru.kihara@badili.co.ke

# Install the basics of R
RUN apt-get update && \
	apt-get upgrade -y && \
	apt-get install -y Rscript \
    apt-get install -y python2.7 


# Install the needed R packages

# Install the python requisites
pip install 'django<2.0' MySQL-python
