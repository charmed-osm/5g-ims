#!/usr/bin/python3
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
                    db_ip = model.get_status().applications["mysql"]["units"][
                unit.entity_id
            ]["address"]
            myclient = pymysql.connect(db_ip, "root", "root", "hss_db")
        except pymysql.Error:
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
        try:
            db_client.execute(ins_rec)
                documents = mysql_read_data(db_client, identity)
            for record in documents:
                data = record[2]
                        self.assertEqual("jack@mnc001.mcc001.3gppnetwork.org", data)
        except pymysql.Error:
            myclient.close()

    def test3_mysql_delete_data(self):
        """ ***** Delete document in mysqldb ***** """
        myclient = create_connection()
        db_client = myclient.cursor()
        del_rec = "DELETE FROM impi where identity = %s"
        identity = "joe@mnc001.mcc001.3gppnetwork.org"
        try:
            db_client.execute(del_rec, identity)
                documents = mysql_read_data(db_client, identity)
            rowcount = len(documents)
            self.assertEqual(0, rowcount)
        except pymysql.Error:
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
                documents = mysql_read_data(db_client, identity)
                for record in documents:
                data = record[2]
                        self.assertEqual("joe@mnc001.mcc001.3gppnetwork.org", data)
        except pymysql.Error:
            myclient.close()

    def test4_tcp_pcscf_connection(self):
        """ ***** Checking pcscf TCP connection ***** """
        for unit in model.get_units("pcscf"):
                pcscf_ip = model.get_status().applications["pcscf"]["units"][
                unit.entity_id
            ]["address"]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((pcscf_ip, 4070))
            if result == 0:
                        self.assertEqual(0, result)
            else:
        
    def test5_tcp_icscf_connection(self):
        """ ***** Checking icscf TCP connection ***** """
        for unit in model.get_units("icscf"):
                icscf_ip = model.get_status().applications["icscf"]["units"][
                unit.entity_id
            ]["address"]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((icscf_ip, 4060))
            if result == 0:
                        self.assertEqual(0, result)
            else:
        
    def test6_tcp_scscf_connection(self):
        """ ***** Checking scscf TCP connection ***** """
        for unit in model.get_units("scscf"):
                scscf_ip = model.get_status().applications["scscf"]["units"][
                unit.entity_id
            ]["address"]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((scscf_ip, 6060))
            if result == 0:
                        self.assertEqual(0, result)
            else:
        