#!/usr/bin/python3
# Copyright 2020 Tata Elxsi
#
# Licensed under the Apache License, Version 2.0 (the License); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an AS IS BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# For those usages not covered by the Apache License, Version 2.0 please
# contact: canonical@tataelxsi.onmicrosoft.com
#
# To get in touch with the maintainers, please contact:
# canonical@tataelxsi.onmicrosoft.com
##

"""
Ubuntu charm functional test using Zaza. Take note that the Ubuntu
charm does not have any relations or config options to exercise.
"""

import unittest
import socket
import logging
import zaza.model as model
import pymysql


def create_connection():
    """ creating mysqldb connection """
    try:
        for unit in model.get_units("mysql"):
            logging.info("Checking if the unit db is active: %s", unit.entity_id)
            logging.info("checking for mysql db connection ......")
            db_ip = model.get_status().applications["mysql"]["units"][unit.entity_id][
                "address"
            ]
            myclient = pymysql.connect(db_ip, "root", "root", "hss_db")
            logging.info("Mysqldb connected successfully !!!")
    except pymysql.Error:
        logging.info("Could not connect to Mysqldb")
    return myclient


def mysql_read_data(db_client, identity):
    """ Reading data from mysqldb """
    statement = "select * from impi where identity = %s"
    db_client.execute(statement, identity)
    documents = db_client.fetchall()
    return documents


class BasicDeployment(unittest.TestCase):
    """ class defines functional testing of ims charms """

    def test1_mysql_insert_data(self):
        """ ***** Insert Document in mysqldb ***** """
        identity = "jack@mnc001.mcc001.3gppnetwork.org"
        myclient = create_connection()
        db_client = myclient.cursor()
        ins_rec = """ INSERT INTO impi \
                (id_imsu, identity, k, auth_scheme, default_auth_scheme, amf,\
                op, sqn, ip, line_identifier, zh_uicc_type, zh_key_life_time, \
                zh_default_auth_scheme) VALUES (3,'jack@mnc001.mcc001.3gppnetwork.org',\
                'jack',127,1,'\0\0','\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',\
                '000000000000','','',0,3600,1) """
        logging.info("Record to be inserted %s", ins_rec)
        try:
            db_client.execute(ins_rec)
            logging.info("Data inserted successfully !!")
            documents = mysql_read_data(db_client, identity)
            for record in documents:
                data = record[2]
                logging.info("Reading the inserted doc %s", record)
            logging.info("To check inserted record and retrived document are same ...")
            self.assertEqual("jack@mnc001.mcc001.3gppnetwork.org", data)
        except pymysql.Error:
            logging.info("Error unable to Insert data")
        myclient.close()

    def test3_mysql_delete_data(self):
        """ ***** Delete document in mysqldb ***** """
        myclient = create_connection()
        db_client = myclient.cursor()
        del_rec = "DELETE FROM impi where identity = %s"
        identity = "joe@mnc001.mcc001.3gppnetwork.org"
        logging.info("Record to be deleted %s", del_rec)
        try:
            db_client.execute(del_rec, identity)
            logging.info("records deleted %d", db_client.rowcount)
            documents = mysql_read_data(db_client, identity)
            rowcount = len(documents)
            self.assertEqual(0, rowcount)
        except pymysql.Error:
            logging.info("Error unable to delete data")
        myclient.close()

    def test2_mysql_update_data(self):
        """ ***** Update document in mysqldb ***** """
        identity = "joe@mnc001.mcc001.3gppnetwork.org"
        myclient = create_connection()
        db_client = myclient.cursor()
        update_rec = "UPDATE impi SET identity = 'joe@mnc001.mcc001.3gppnetwork.org' \
                      WHERE identity = 'jack@mnc001.mcc001.3gppnetwork.org'"
        try:
            db_client.execute(update_rec)
            logging.info("Data updated succesfully")
            documents = mysql_read_data(db_client, identity)
            logging.info(documents)
            for record in documents:
                data = record[2]
                logging.info("Reading the updated doc %s", record)
            logging.info("To check inserted record and retrieved document are same ...")
            self.assertEqual("joe@mnc001.mcc001.3gppnetwork.org", data)
        except pymysql.Error:
            logging.info("Error unable to update data")
        myclient.close()

    def test4_tcp_pcscf_connection(self):
        """ ***** Checking pcscf TCP connection ***** """
        for unit in model.get_units("pcscf"):
            logging.info("Checking if the unit pcscf is active: %s", unit.entity_id)
            pcscf_ip = model.get_status().applications["pcscf"]["units"][
                unit.entity_id
            ]["address"]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((pcscf_ip, 4070))
            if result == 0:
                logging.info("pcscf unit has TCP connection Established!!")
                self.assertEqual(0, result)
            else:
                logging.info("Failed to connect")

    def test5_tcp_icscf_connection(self):
        """ ***** Checking icscf TCP connection ***** """
        for unit in model.get_units("icscf"):
            logging.info("Checking if the unit icscf is active: %s", unit.entity_id)
            icscf_ip = model.get_status().applications["icscf"]["units"][
                unit.entity_id
            ]["address"]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((icscf_ip, 4060))
            if result == 0:
                logging.info("icscf unit has TCP connection Established!!")
                self.assertEqual(0, result)
            else:
                logging.info("Failed to connect")

    def test6_tcp_scscf_connection(self):
        """ ***** Checking scscf TCP connection ***** """
        for unit in model.get_units("scscf"):
            logging.info("Checking if the unit scscf is active: %s", unit.entity_id)
            scscf_ip = model.get_status().applications["scscf"]["units"][
                unit.entity_id
            ]["address"]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((scscf_ip, 6060))
            if result == 0:
                logging.info("scscf unit has TCP connection Established!!")
                self.assertEqual(0, result)
            else:
                logging.info("Failed to connect")
