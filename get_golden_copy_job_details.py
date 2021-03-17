#! /opt/.pyenv/shims/python

import os
from subprocess import Popen, PIPE
import argparse
import sys
import shlex


class collect_job_info():
    def __init__(self):
        #
        # Initalizing class with order function calls
        #
        self.argparser = self.argparser()
        if self.list:
            self.get_folder_list = self.get_folder_list()
            print(self.list_data)
        if self.name:
            self.get_folder_id_and_paths = self.get_folder_id_and_paths()
            self.display_job_view = self.display_job_view()
        if self.all:
            self.name = 'ifs'
            self.get_folder_id_and_paths = self.get_folder_id_and_paths()
            self.display_job_view = self.display_job_view()

    def argparser(self):
        #
        # checking for flag all, name and list. No flags gets help menu.
        #
        parser = argparse.ArgumentParser(description="displays \
                                    job info with path information")
        parser.add_argument("-a", "--all", action='store_true', required=False,
                            help="Will display all active running jobs")
        parser.add_argument("-n", "--folder-name", required=False,
                            help="Displays active job \
                                    info for the specified folder")
        parser.add_argument("-l", "--list",
                            action='store_true', required=False,
                            help="Lists all folders in archive list")

        args = parser.parse_args()

        self.list = args.list
        self.all = args.all
        self.name = args.folder_name

        if len(sys.argv) <= 1:
            parser.print_help()

    def get_folder_list(self):
        #
        # Get list of folders register to be archived (-l).
        #
        list_cmd = '/opt/superna/bin/ecactl search archivedfolders list'
        list_cmd = shlex.split(list_cmd)
        try:
            list_run = Popen(list_cmd, stdout=PIPE, stderr=PIPE)
            list_out, list_err = list_run.communicate()
            if not list_out and not list_err:
                print("nada!")
            elif not list_out:
                print("Um not getting any items")
            elif list_err.rstrip():
                print("Error:<<%s>>" % list_err)
            else:
                self.list_data = list_out.decode("utf-8")
        except OSError as e:
            print("OSError: %s" % e)

    def get_folder_id_and_paths(self):
        #
        # Parse Folder ID and Paths for matching in next step (-a,-n).
        # This is a list of key value pairs.
        #
        list_info = []
        self.get_folder_list()
        for item in self.list_data.split("\n")[1:]:
            if self.name in item:
                info = {'id': (item.split()[0]), 'path': (item.split()[2])}
                list_info.append(info)
        self.list_info = list_info

    def display_job_view(self):
        #
        # Display archive list caught by search term and then
        # Drill down and display view on each running job for
        # those archive folder(s) in the list.
        #
        job_cmd = '/opt/superna/bin/ecactl search jobs running'
        job_cmd = shlex.split(job_cmd)
        try:
            job_run = Popen(job_cmd, stdout=PIPE, stderr=PIPE)
            job_out, job_err = job_run.communicate()
            if not job_out and not job_err:
                print("nada!")
            elif not job_out:
                print("Um not getting any items")
            elif job_err.rstrip():
                print("Error:<<%s>>" % job_err)
            else:
                self.job_data = job_out.decode("utf-8")
        except OSError as e:
            print("OSError: %s" % e)
        count = 0
        for job in self.job_data.split("\n"):
            if count == 0:
                print("%s\t path:" % job)
                count = count + 1
            elif count == 1:
                print("%s\t ------------------------------" % job)
                count = count + 1
            for ids in self.list_info:
                if ids['id'] in job:
                    print("%s\t\t\t %s" % (job, ids['path']))
        for job in self.job_data.split("\n"):
            for ids in self.list_info:
                if ids['id'] in job:
                    job_id = job.split()[0]
                    job_view_cmd = '/opt/superna/bin/ecactl \
                                    search jobs view --id ' + job_id
                    job_view_cmd = shlex.split(job_view_cmd)
                    try:
                        job_view_cmd = Popen(job_view_cmd,
                                             stdout=PIPE, stderr=PIPE)
                        job_view_out, job_view_err = job_view_cmd.communicate()
                        if not job_view_out and not job_view_err:
                            print("nada!")
                        elif not job_view_out:
                            print("Um not getting any items")
                        elif job_view_err.rstrip():
                            print("Error:<<%s>>" % job_view_err)
                        else:
                            self.job_view_data = job_view_out.decode("utf-8")
                            print("\
                                ======================================\n\
                                PATH: %s\n\
                                JOB_ID:  %s\n\
                                ======================================"
                                  % (ids['path'], job_id))
                            print(self.job_view_data)
                    except OSError as e:
                        print("OSError: %s" % e)


if __name__ == "__main__":
    collect_job_info()
