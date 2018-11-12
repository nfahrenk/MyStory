MyStory (FullStory Clone)
==================

When I first used FullStory (https://www.fullstory.com/), I found it to be an incredibly interesting engineer feat. I was very curious about how they were able to build video replays of sessions at such a large scale, so I decided to make my own assumptions to see what I would build.

Installation & Setup
==================
brew cask install homebrew/cask-versions/java8
brew install kafka
zookeeper-server-start /usr/local/etc/kafka/zookeeper.properties & kafka-server-start /usr/local/etc/kafka/server.properties
kafka-topics /usr/local/etc/kafka/server.properties --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic events


Yelp Hack 23.0 (Two 8 Hour Days)
==================
I wrote the initial code during Hack 23.0 at Yelp. The prototype was functional, albeit not elegant at all.

Yelp Hack 27.0 (One 8 Hour Day)
==================
One of the technical challenges that I faced during the previous hackathon was ending a session. I knew that I wanted to end the session after 30 seconds of inactivity, but the solution I came up with was to a recurring cron job every five seconds to have a celery worker check for all active sessions that haven't had activity in 30 seconds, then end their session. It worked, but I wanted something more elegant. I decided that I would insert all events into a kafka queue, and use session windows to handle the inactivity. Unfortunately I wrote all of the code in Python/Django and had selected Postgres as the database and I could not find a good package for kafka-streams in Python. Ideally I would just have a NoSQL collection to store the session events. I am writing the Kafka producer in Python, the Kafka streams in Java.
