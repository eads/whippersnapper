#!/usr/bin/env python

import logging
import os
import subprocess
import sys
import time

import yaml

import screenshotter
import uploader

class ElectionsScreenshotter(object):
    """
    Implements all screenshot-related logic.
    """

    def __init__(self):
        if len(sys.argv) != 2:
            self.usage()
            sys.exit(1)

        config_filepath = sys.argv[1]
        self.config = self.load_config(config_filepath)
        self.log_file = self.init_logging()
        self.screenshotter = screenshotter.Screenshotter(self.config)
        if not self.config.get('skip_upload'):
            self.uploader = uploader.Uploader(self.config)

    def main(self):
        """
        Runs through the full screenshot process.
        """

        print """
Screenshotter is running. To view its log file:

    tail -f %s

To quit, press ^C (ctrl-C).""" % (self.log_file)

        while True:
            targets = self.screenshotter.take_screenshots()
            try:
                filepaths = self.uploader.upload_screenshots(targets)
                # TODO Image delete code probably doesn't belong here
                if (self.config.get('delete_local_images')):
                    [os.remove(path.get('local_filepath')) for path in targets]
            except AttributeError:
                pass
            time.sleep(self.config.get('time_between_screenshots'))

    def init_logging(self):
        """
        Create a log file, and attach a basic logger to it.
        """
        log_file = self.config.get('log_file')
        # Create the log file if it does not yet exist
        with open(log_file, 'a+'):
            pass
        logging.basicConfig(filename=log_file,
                format='%(levelname)s:%(asctime)s %(message)s',
                level=logging.INFO)
        return log_file

    def load_config(self, config_filepath):
        """
        Load configuration from config.yaml.

        Many options have defaults; use these unless they are overwritten in
        config.yaml. This file includes the urls, css selectors and slugs for
        the targets to screenshot.
        """
        config = {
            'skip_upload': False,
            'aws_bucket': '',
            'aws_subpath': '',
            'aws_access_key': None,
            'aws_secret_key': None,
            'log_file': os.path.dirname(os.path.abspath(__file__)) +
                   '/../screenshotter.log',
            'delete_local_images': False,
            'time_between_screenshots': 60,
            'override_css_file': None,
            'page_load_delay': 2,
            'wait_for_js_signal': False,
            'failure_timeout': 30,
        }

        required = (
            'targets',
            'local_image_directory',
        )

        raw_config = None

        with open(config_filepath) as f:
            raw_config = yaml.load(f)

        for option_name, option_value in raw_config.iteritems():
            config[option_name] = option_value

        for option in required:
            try:
                config[option] = raw_config[option]
            except KeyError:
                raise RuntimeError('Config is missing required attribute: %s'
                        % option)

        return config

    def usage(self):
        """
        Print usage information.
        """
        print """
        USAGE: elections_screenshotter CONFIG_FILEPATH
        """

def launch_new_instance():
    """
    Launch an instance of ElectionsScreenshotter.

    This is the entry function of the command-line tool
    `elections_screenshotter`.
    """
    try:
        s = ElectionsScreenshotter()
        s.main()
    except KeyboardInterrupt:
        # Print a blank line
        print

if __name__ == '__main__':
    launch_new_instance()
