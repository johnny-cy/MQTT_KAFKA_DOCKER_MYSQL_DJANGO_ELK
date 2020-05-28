#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" This hidden module defines DataObject IO class.
"""

import pandas as pd


class DataIOWriteError(Exception):
    """ `DataObject` IO exceptions.

    Attributes
    ----------
    errors
        List of errors.
    """

    def __init__(self, *errors):
        """
        Args
        ----
        *errors
            errors
        """
        self.errors = list(errors)

    def combine(self, err):
        """ Combine other error class.

        Args
        ----
        err : DataIOWriteError
            Other error to combine.

        Returns
        -------
        DataIOWriteError
            `self` with combined errors.
        """
        self.errors.extend(err.errors)
        return self

    def __len__(self):
        return len(self.errors)

    def __repr__(self):
        return str([e for e in self.errors])

    def __str__(self):
        if len(self) > 10:
            return str(self.errors[:10]) + f" ... and {len(self)-10} mores"
        else:
            return str(self.errors)


class DataResultProxy(object):
    """ The query result proxy returned by `DataIOHandler` operations.

    `DataIOHandler` object's `read()` function will return `DataResultProxy` for
    easier accessing DB results.

    The data stored in `DataResultProxy` will be a list of python dict objects
    with key-value paris to describe a data record. We JSON-ize dict object to
    communicate with others via Kafka publisher-comsumer systems.

    Attributes
    ----------
    data_cls : DataObject
        Referenced `DataObject` class.
    data : list(dict)
        List of dict contains key-value paired records.
    """

    def __init__(self, data_cls, data):
        """
        Args
        ----
        data_cls : DataObject
            Referenced `DataObject` class.
        data : list(dict)
            List of dict contains key-value paired records.
        """
        self.data_cls = data_cls
        self.data = data

    def get_one(self):
        """ Get one result.

        This function will get first result returned from `DataIOHandler` 
        read function. Depends on how you read you data and underlay database
        system, we can't guarantee what the first result is.

        Returns
        -------
        dict or None
            If no result, None, otherwises a Dict object will be returned.
        """
        try:
            return self.data.pop()
        except IndexError:
            return None

    def get_object(self):
        """ Get one object.

        This function will get first result returned from `DataIOHandler` 
        read function. Depends on how you read you data and underlay database
        system, we can't guarantee what the first result is.

        Returns
        -------
        DataObject or None
            If no result, None, otherwises a Dataobject will be returned.
        """
        try:
            one = self.get_one()
            return self.data_cls(**one)
        except IndexError:
            return None

    def as_dict_list(self):
        """ Alias to `as_list()`.
        """
        return self.as_list()

    def as_list(self):
        """ Return a list of results which is key-value paired dict.

        Returns
        -------
        list
            List of results.
        """
        return self.data

    def as_object_list(self):
        """ Alias to `as_objects()`.
        """
        return self.as_objects()

    def as_objects(self):
        """ Return a list of `DataObject` results.

        Returns
        -------
        list
            List of `DataObject` results.
        """
        return [self.data_cls(**x) for x in self.data]

    def as_df(self):
        """ Return a pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame.
        """
        return pd.DataFrame(self.data)

    def as_stream(self, as_object=False):
        """ Yield streaming data results.

        Args
        ----
        as_object : bool, optional
            If True, yield `DataObject`, else yield python dict.

        Yields
        ------
        dict or `DataObject`
            Yield results.
        """
        if as_object:
            yield from self.as_object_list()
        else:
            yield from self.data


class DataIOHandler(object):
    """ `DataIOHandler` handlers read/write functions.

    `DataIOHandler` must handle underlying read/write functions depends on its
    data store, likt: MySQL, Kafka, ... etc.
    """

    def read(self, fields=[], where=[], sort=[], limit=None, offset=None, **kwargs):
        """ The read function.

        Args
        ----
        fields : list(str)
            Only fields included in returned results, empty list for all.
        where : list(str)
            Conditions to filter data.
        sort : list(str)
            Sorting fields.
        limit : int
            Number of results to return.
        offset : int
            Result offset.
        **kwargs
            Parameters will pass to underlying data store engine.

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError

    def write(self, data, batch_size=1000):
        """ The write function.

        Args
        ----
        data : list(dict) or list(DataObject)
            Data to be written.
        batch_size : int, optional
            Batch size, default: 1000

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError
