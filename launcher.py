#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

"""
This is a wrapper for Windows Desktops
Runs git commands to update source code of the BitDust p2p-app before start
"""

import os
import sys 
import subprocess


def run_cmd(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    return p.wait()


def launch():
    run_cmd(['..\\git\\bin\\git.exe', '-c', 'http.sslBackend=schannel', 'fetch', '--all', ])
    run_cmd(['..\\git\\bin\\git.exe', '-c', 'http.sslBackend=schannel', 'reset', '--hard', 'origin/master', ])

    sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

    from main import main
    return main()


if __name__ == '__main__':
    launch()
