#!/usr/bin/env python3
import argparse
import logging
import os
from time import sleep

import watchdog.observers
import watchdog.events


class PurgeAmountCheckPointHandler(watchdog.events.FileSystemEventHandler):
    def __init__(self, limit_amount: int = 25):
        self.h5_log_files = []
        self.limit_amount = limit_amount

    def on_created(self, event: watchdog.events.FileCreatedEvent):
        logging.info(f'File {event.src_path} created')
        if not event.is_directory:
            src_path = event.src_path
            if src_path.endswith('.h5') and os.path.split(src_path)[-1] != 'trained_final.h5':
                self.h5_log_files.append(src_path)

                if len(self.h5_log_files) > self.limit_amount:
                    remove_file = self.h5_log_files.pop(0)
                    logging.warning(f'Files amount already > then {self.limit_amount}, removing {remove_file}')
                    os.remove(remove_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--log_directory', type=str, required=True, help="The log directory for watchdog to watch")
    parser.add_argument('--limit_amount', type=int, required=False, default=25,
                        help='How much files you want to keep in the directory')
    args = parser.parse_args()

    event_handler = PurgeAmountCheckPointHandler(limit_amount=args.limit_amount)
    logging.basicConfig(level=logging.INFO)
    observer = watchdog.observers.Observer()

    observer.schedule(event_handler=event_handler, path=args.log_directory, recursive=True)
    observer.start()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
