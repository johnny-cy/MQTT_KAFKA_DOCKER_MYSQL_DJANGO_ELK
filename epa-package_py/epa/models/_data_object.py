#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" This hidden module defines DataObject class.

Notes
-----
We using Python 3.7 dataclasses to define DataObject.

"""

import dataclasses

from epa.models.sqlalchemy import SQLAlchemyHandler
from epa.models.kafka import KafkaHandler


class DataIOHandlerMetaClass(type):
    """ DataObject meta-class

    DataObject's meta-class.

    This meta-class will force every inherited DataObject class to own
    DataIOHandler.

    Attributes
    ----------
    sql : SQLAlchemyHandler
        SQL IO handler
    mysql
        Alias to sql
    mariadb
        Alias to sql
    db
        Alias to sql
    kafka : KafkaHandler
        Kafka IO handler
    """
    def __init__(self, name, bases, attrs):
        super().__init__(name, bases, attrs)

        self.sql = SQLAlchemyHandler(self, self._sqlalchemy_cls)
        self.mysql = self.sql
        self.mariadb = self.sql
        self.db = self.sql

        self.kafka = KafkaHandler(self, [self._kafka_topic])


class DataObject(object, metaclass=DataIOHandlerMetaClass):
    """ DataObject class represnts data object

    Attributes
    ----------
    _sqlalchemy_cls : 
        SQLAlchemyHandler base class.
    _kafka_topic : str
        Kafka topic.
    """

    _sqlalchemy_cls = None
    _kafka_topic = None

    def __setattr__(self, name, value):
        """ setattr

        Set value to dataclass will affect underlying data_instance
        """
        super().__setattr__(name, value)
        setattr(self.data_instance, name, value)

    @property
    def data_instance(self):
        """ Underlying data class instance.

        Raises
        ------
        TypeError
            If _sqlalchemy_cls is not specified.
        """
        if not hasattr(self, "_data_instance"):
            if self._sqlalchemy_cls is None:
                raise TypeError("_sqlalchemy_cls not specified.")
            self._data_instance = self._sqlalchemy_cls(**self.as_dict())
        return self._data_instance

    @property
    def field_names(self):
        """ Get a tuple of field names

        Returns
        -------
        tuple
            tuple of field names
        """
        return (f.name for f in dataclasses.fields(self))

    def as_dict(self, dict_factory=dict):
        """ Converts the dataclass instance to a dict

        Args
        ----
        dict_factory : default dict
            Factory function for dict

        Returns
        -------
        dict
            key-value paried dict value for this object
        """
        return dataclasses.asdict(self, dict_factory=dict_factory)

    def as_tuple(self, tuple_factory=tuple):
        """ Converts the dataclass instance to a tuple.

        Each dataclass is converted to a tuple of its field values.

        Parameters
        ----------
        tuple_factory : default tuple
            Factory function for dict

        Returns
        -------
        tuple
            tuple of values
        """
        return dataclasses.astuple(self, tuple_factory=tuple_factory)

    def save(self):
        """ Save

        This function will save `DataObject` to its underlying store class,
        most likely SQLAlchemyHandler.

        Returns
        -------
        None
        """
        self.data_instance.save()

    @classmethod
    def load(cls, where=[], **kwargs):
        """ Load exactly one instance of this data class.

        Args
        ----
        where : list(str)
            where condition to filter data.
        **kwargs
            Parameters will pass to underlying data store engine.

        Returns
        -------
        DataObject or None
        """
        try:
            result = cls.db.read(where=where, limit=1, **kwargs).get_one()
            if result:
                result = {k: v for k, v in result.items() if not k.startswith("_")}
                return cls(**result)
            else:
                return None
        except IndexError:
            return None
