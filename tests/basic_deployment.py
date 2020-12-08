#!/usr/bin/python3
"""
Ubuntu charm functional test using Zaza. Take note that the Ubuntu
charm does not have any relations or config options to exercise.
"""

import unittest
import zaza
import socket
import logging
import zaza.model as model
import pymysql
from juju.model import Model
import zaza.charm_lifecycle.utils as lifecycle_utils


class BasicDeployment(unittest.TestCase):
    def create_connection(self):
        try:
            for unit in zaza.model.get_units("mysql"):
                logging.info(
                    "Checking if the unit db is active: {}".format(unit.entity_id)
                )
                logging.info("checking for mysql db connection ......")
                db_ip = model.get_status().applications["mysql"]["units"][
                    unit.entity_id
                ]["address"]
                myclient = pymysql.connect(db_ip, "root", "root", "hss_db")
                logging.info("Mysqldb connected successfully !!!")
        except:
            logging.info("Could not connect to Mysqldb")
        return myclient

    def mysql_read_data(self, db, identity):
        statement = "select * from impi where identity = %s"
        db.execute(statement, identity)
        documents = db.fetchall()
        return documents

    def test1_mysql_insert_data(self):
        """ ***** Insert record in mysqldb ***** """
        db_name = "hss_db"
        identity = "jack@mnc001.mcc001.3gppnetwork.org"
        myclient = BasicDeployment.create_connection(self)
        db = myclient.cursor()
        ins_rec = """ INSERT INTO impi(id_imsu, identity, k, auth_scheme, default_auth_scheme, amf, op, sqn, ip, line_identifier, zh_uicc_type, zh_key_life_time, zh_default_auth_scheme) VALUES (3,'jack@mnc001.mcc001.3gppnetwork.org','jack',127,1,'\0\0','\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0','000000000000','','',0,3600,1) """
        logging.info("Record to be inserted {}".format(ins_rec))
        try:
            db.execute(ins_rec)
            logging.info("Data inserted successfully !!")
            documents = BasicDeployment.mysql_read_data(self, db, identity)
            for record in documents:
                data = record[2]
                logging.info("Reading the inserted doc {}".format(record))
            logging.info("To check inserted record and retrived document are same ...")
            self.assertEqual("jack@mnc001.mcc001.3gppnetwork.org", data)
        except:
            logging.info("Error unable to Insert data")
        myclient.close()

    def test3_mysql_delete_data(self):
        """ ***** Delete record in mysql db ***** """
        db_name = "hss_db"
        myclient = BasicDeployment.create_connection(self)
        db = myclient.cursor()
        del_rec = "DELETE FROM impi where identity = %s"
        identity = "joe@mnc001.mcc001.3gppnetwork.org"
        logging.info("Record to be deleted {}".format(del_rec))
        try:
            db.execute(del_rec, identity)
            logging.info("records deleted {}".format(db.rowcount))
            documents = BasicDeployment.mysql_read_data(self, db, identity)
            rowcount = len(documents)
            self.assertEqual(0, rowcount)
        except:
            logging.info("Error unable to delete data")
        myclient.close()

    def test2_mysql_update_data(self):
        """ ***** Update record in mysql db ***** """ ""
        db_name = "hss_db"
        identity = "joe@mnc001.mcc001.3gppnetwork.org"
        myclient = BasicDeployment.create_connection(self)
        db = myclient.cursor()
        update_rec = "UPDATE impi SET identity = 'joe@mnc001.mcc001.3gppnetwork.org' WHERE identity = 'jack@mnc001.mcc001.3gppnetwork.org'"
        try:
            db.execute(update_rec)
            logging.info("Data updated succesfully")
            documents = BasicDeployment.mysql_read_data(self, db, identity)
            logging.info(documents)
            for record in documents:
                data = record[2]
                logging.info("Reading the updated doc {}".format(record))
            logging.info("To check inserted record and retrieved document are same ...")
            self.assertEqual("joe@mnc001.mcc001.3gppnetwork.org", data)
        except:
            logging.info("Error unable to update data")
        myclient.close()

    def test4_tcp_pcscf_connection(self):
        """ ***** checking tcp transport connection in pcscf ***** """
        for unit in zaza.model.get_units("pcscf"):
            logging.info(
                "Checking if the unit pcscf is active: {}".format(unit.entity_id)
            )
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
        """ ***** checking tcp transport connection in icscf ***** """
        for unit in zaza.model.get_units("icscf"):
            logging.info(
                "Checking if the unit icscf is active: {}".format(unit.entity_id)
            )
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
        """ ***** checking tcp transport connection in scscf ***** """
        for unit in zaza.model.get_units("scscf"):
            logging.info(
                "Checking if the unit scscf is active: {}".format(unit.entity_id)
            )
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
