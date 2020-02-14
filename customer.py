#!/usr/bin/env python3
import pika
import subprocess
import os
import yaml

with open("config.yml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
credential_params = pika.PlainCredentials(cfg['rbmq']['user'],cfg['rbmq']['passwd'])
connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=cfg['rbmq']['host'],credentials=credential_params))
channel = connection.channel()

channel.queue_declare(queue=cfg['rbmq']['queue'])


def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)
        print(type(body))
        encoding = 'utf-8'
        rsync_cmd="/usr/bin/rsync -rvz -e 'ssh -p 2205' --bwlimit=1000 --progress root@" + cfg['rbmq']['host']  + ":" + str(body, encoding) + " /tmp/"
        os.system(rsync_cmd)

channel.basic_consume(queue=cfg['rbmq']['queue'], on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

