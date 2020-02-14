#!/usr/bin/python3
# -*-coding:Utf-8 -*
import configparser
import sys
import os.path
import datetime
from os import listdir
from os.path import isfile, join
import pika
import time
import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

with open("config.yml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile)


class Watcher:
    DIRECTORY_TO_WATCH = cfg['rbmq']['path']

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            print("Received created event " + event.src_path)
            credential_params = pika.PlainCredentials(cfg['rbmq']['user'],cfg['rbmq']['passwd'])
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost',credentials=credential_params))
            channel = connection.channel()
            channel.queue_declare(queue=cfg['rbmq']['queue']) # Declare a queue
            channel.basic_publish(exchange='', routing_key=cfg['rbmq']['queue'], body=event.src_path)
            print("[x] We have a new file")
            connection.close()

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print("Received modified event " + event.src_path)


if __name__ == '__main__':
    w = Watcher()
    w.run()

def list_files(path):
	onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
	return onlyfiles

def return_pattern(pattern,path):
	result = []
	for i in list_files(path):
		if pattern in i:
			result.append(i)
	return result

