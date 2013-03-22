# Twitterbot #

This script provides an easy way to authenticate an api request in python-twitter.

## Dependencies ##

Requires: 
* python-twitter

## Usage ##

    import tb
    t = tb.Twitterbot(consumer_secret, consumer_key)
    api = t.getAPI()
