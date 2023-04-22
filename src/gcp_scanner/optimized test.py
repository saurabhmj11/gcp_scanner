# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""The module to perform unit tests of the GCP Scanner."""

import datetime
import difflib
import filecmp
import json
import os
import shutil
import sqlite3
import unittest
from unittest.mock import patch, Mock

import requests
from google.oauth2 import credentials

from . import crawl
from . import credsdb
from . import scanner
from .credsdb import get_scopes_from_refresh_token


PROJECT_NAME = "test-gcp-scanner"


def print_diff(f1, f2):
    with open(f1, "r", encoding="utf-8") as file_1, \
            open(f2, "r", encoding="utf-8") as file_2:
        file_1_text, file_2_text = file_1.readlines(), file_2.readlines()
    # Find and print the diff:
    res = ""
    for line in difflib.unified_diff(file_1_text, file_2_text, fromfile=f1,
                                     tofile=f2, lineterm=""):
        print(line)
        res += line


def save_to_test_file(res):
    res = json.dumps(res, indent=2, sort_keys=False)
    with open("test_res", "w", encoding="utf-8") as outfile:
        outfile.write(res)


def compare_volatile(f1, f2):
    res = True
    with open(f1, "r", encoding="utf-8") as file_1, \
            open(f2, "r", encoding="utf-8") as file_2:
        file_1_text, file_2_text = file_1.readlines(), file_2.readlines()
    for line in file_2_text:
        if not line.startswith("CHECK"):
            continue  # we compare only important part of output
        line = line.replace("CHECK", "")
        if line in file_1_text:
            continue
        else:
            print(f"The following line was not identified in the output:\n{line}")
            res = False
    return res


def verify(res_to_verify, resource_type, volatile=True):
    save_to_test_file(res_to_verify)
    f1, f2 = "test_res", f"test/{resource_type}"
    if volatile is True:
        result = compare_volatile(f1, f2)
    else:
        result = filecmp.cmp(f1, f2)
        if result is False:
            print_diff(f1, f2)
    return result


def test_creds_fetching():
    os.mkdir("unit")
    conn = sqlite3.connect("unit/credentials.db")
    c = conn.cursor()
    c.execute("""
           CREATE TABLE credentials (account_id TEXT PRIMARY KEY, value BLOB)
            """)
    sqlite_insert_with_param = """INSERT INTO "credentials"
                                ("account_id", "value")
                                VALUES (?, ?);"""
    data_value = ("test_account@gmail.com", "test_data")
    c.execute(sqlite_insert_with_param, data_value)
   
