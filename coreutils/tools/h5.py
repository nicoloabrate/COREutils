"""
Author: N. Abrate.

File: h5.py

Description: Utility to read/write objects from/to HDF5 files.
"""
import re
import os
import h5py
import numpy
import logging
from collections import OrderedDict
from numpy import string_, ndarray, array, asarray
from numpy import int8, int16, int32, int64, float16, float32, float64, \
                  complex128, zeros, asarray, bytes_, dtype


_float_types = (float, float16, float32, float64, complex, complex128)
_int_types = (int, int8, int16, int32, int64)
_scalar_types = (*_int_types, *_float_types, bool)
_iter_types = (ndarray, list, dict, tuple, OrderedDict)
_types = (*_scalar_types, *_iter_types, str, bytes_,
            h5py._hl.dataset.Dataset, )
_str2type = {i.__name__: i for i in _types}

class read():
    """
    Class that reads a .hdf5/.h5 file and stores it into an object.

    h5name : str
        HDF5 file name that is parsed.
    """
    def __init__(self, h5name, metadata=True):
        """
        Read .hdf5/.h5 formatted files and store in object.

        Parameters
        ----------
        h5name : string
            File where data are stored.
        metadata : bool, optional
            bool to choose if metadata are parsed or ignored, by default
            ``True``.

        Returns
        -------
        ``None``
        """
        # open hdf5 file
        h5name = _checkname(h5name)
        fh5 = h5py.File(h5name, "r")

        # TODO: add selective reading (maybe specifying group paths)

        # extract groups
        for gro in fh5.keys():
            # get attributes
            try:
                attrs = read._attrs2dict(fh5[gro])
                if attrs == {}:
                    attrs['pytype'] = None
            except TypeError:
                attrs = {}
                attrs['pytype'] = None

            # get sub-groups and datasets
            try:
                dic = {}
                for k, v in fh5[gro].items():
                    try:
                        pytype = v.attrs['pytype']
                    except KeyError:
                        pytype = None
                    try:
                        keytype = v.attrs['keytype']
                    except KeyError:
                        keytype = None

                    dic[k] = read._h52py(v, pytype=pytype, keytype=keytype)
                    if metadata:
                        attrs = read._attrs2dict(v)
                        try:
                            if attrs != {}:
                                dic[k]['{}_metadata'.format(str(k))] = attrs
                        except (IndexError, TypeError):
                            if attrs != {}:
                                dic['{}_metadata'.format(str(k))] = attrs

                self.__dict__[gro.replace(" ", "_")] = dic

            except AttributeError:
                s = gro.replace(" ", "_")
                self.__dict__[s] = read._h52py(fh5[gro],
                                               pytype=attrs['pytype'], )

            if metadata:
                self.__dict__[f'{gro}_metadata'] = attrs

        fh5.close()
        self.h5name = h5name

    def _h52py(item, pytype=None, keytype=None):
        """
        Convert item from HDF5 file to the closest Python-3 type.

        Parameters
        ----------
        item : string, int, float, numpy.array, dict, list
            Dataset/subgroup read from HDF5 file.
        pytype : type
            Python type assigned as attribute to the Dataset/subgroup. Default
            is ``None`` if the attribute does not exist.

        Returns
        -------
        val : int
            Item converted in Python type (str, int, float, numpy.array, dict,
            list).
        """
        if pytype is None:
            try:
                pytype = item.dtype.name
            except AttributeError:
                if isinstance(item, str):
                    val = item
                else:
                    val = read._h52dict(item, keytype=keytype)
                return val
        else:
            if "<class" in pytype:
                tmp = re.findall("<class '(.*?)'>", pytype)[0]
                try:
                    pytype = eval(tmp)
                except  NameError:
                    pytype = None
        # if type(item).__name__ in read._str2type:
        if pytype in _str2type.values():
            if isinstance(item, h5py._hl.dataset.Dataset):
                if pytype is str:
                    if item.shape == ():
                        val = array(item)[()].decode()
                    else:
                        val = []
                        for i in item:
                            val.append(i.decode())
                        val = asarray(val)
                else:
                    if pytype in _scalar_types:
                        val = array(item, dtype=pytype)[()]
                    elif pytype in  _iter_types:
                        dt = item.dtype
                        if len(item.shape) == 0:
                            val = asarray(item).item()
                        else:
                            val = zeros(item.shape, dtype=dt)
                            item.read_direct(val)
                            if dt == dtype(object):
                                # FIXME TODO temporary patch to avoid b_strings
                                if isinstance(item[0], bytes):
                                    val = val.astype(str)
                    else:
                        raise TypeError(f'Cannot read data {item} with type {type(item)}!')
            elif pytype in _scalar_types:
                val = pytype(item)
            elif pytype in _iter_types:
                dt = item.dtype
                if len(item.shape) == 0:
                    val = asarray(item).item()
                else:
                    val = zeros(item.shape, dtype=dt)
                    item.read_direct(val)
                    if pytype == list or pytype == tuple:
                        val = val.to_list()
                    elif pytype == tuple:
                        val = tuple(map(tuple, val))
            elif pytype is str:
                val = item
            elif pytype is bytes:
                enc = item.attrs['encoding'].decode('ascii')
                val = item.value.decode(enc)
            elif pytype is bool:
                val = item.value
            elif pytype == b'str':
                try:
                    enc = item.attrs['encoding'].decode('ascii')
                except KeyError:
                    enc = 'ascii'
                    logging.warning('type b''str'' read with'
                          ' ''ascii'' encoding')
                val = item.value.decode(enc)
            else:
                raise TypeError(f'Cannot read data {item} with type {type(item)}!')
        elif type(item).__name__ == 'Group':
            val = read._h52dict(item, keytype=keytype)
        elif pytype is None:
            val = None
        else:
            raise TypeError(f'Cannot read data {item} with type {type(item)}!')
        return val

    def _h52dict(path, keytype=None):
        """
        Convert group/subgroup/dataset to dictionaries.

        Parameters
        ----------
        path : str
            Path to dataset in the HDF5 file.

        Returns
        -------
        dic: dict
            group/subgroup/dataset converted to dictionary.
        """
        dic = {}
        for key, item in path.items():
            if isinstance(item, h5py._hl.dataset.Dataset):
                pytype = item.attrs['pytype']
                keytype = item.attrs['keytype']
                key = read._h52py(key, pytype=keytype)
                dic[key] = read._h52py(item, pytype=pytype, keytype=keytype)
            elif isinstance(item, h5py._hl.group.Group):
                dic[key] = read._h52dict(item)

        return dic

    def _attrs2dict(path):
        """
        Parse attributes from group/subgroup/dataset.

        Convert group/subgroup/dataset to dictionaries.

        Parameters
        ----------
        path : str
            Path to dataset in the HDF5 file.

        Returns
        -------
        dic: dict
            attributes converted to dictionary.
        """
        dic = {}
        for k, v in path.attrs.items():
            dic[k] = read._h52py(v)

        return dic


class write():

    def __init__(self, obj, groupname, h5name, attributes=None, chunks=True,
                 compression=True, overwrite=True, skip=None):
        """
        Write object in .h5 format.

        Parameters
        ----------
        obj : object or iterable
            class object to be saved in HDF5.
        groupname : str or iterable
            Group name(s).
        h5name : string
            File where data are stored.
        attributes : dict
            Dictionary attributes that can be assigned for further description
            (default is ``None``).
        chunks : bool, optional
            Flag to save HDF5 in chunks.
        compression : bool, optional
            Flag to save compressed HDF5.
        overwrite : bool, optional
            Flag to overwrite HDF5, by default ``True``.

        Returns
        -------
        ``None``
        """
        # --- open hdf5 file
        h5name = _checkname(h5name)
        self.fh5 = _wopen(h5name, overwrite=overwrite)

        # --- convert data and group name to iterable
        if isinstance(obj, list) is False:
            if isinstance(obj, ndarray):
                obj = obj
            elif isinstance(obj, (dict, object)):
                obj = asarray([obj])
        
        if isinstance(groupname, list) is False:
            if isinstance(groupname, str):
                groupname = [groupname]
            else:
                self.fh5.close()
                raise OSError(f'Unknown type {groupname.type} for groupname!')

        if len(obj) != len(groupname):
            self.fh5.close()
            raise OSError('Number of objects and group names must be equal!')

        if attributes is not None:
            if isinstance(attributes, list) is False:
                attributes = [attributes]
        else:
            attributes = [None]

        if self.fh5 == -1:
            logging.info("HDF5 file not overwritten.")

        logging.info("Writing object in HDF5 file...")
        # --- loop over objects, attributes and group names
        for i, (ob, at, grp) in enumerate(zip(obj, attributes, groupname)):
            if isinstance(ob, (list, tuple, ndarray)):
                write.iterable2h5(self.fh5, grp, ob, attributes=at)
                self.fh5[grp].attrs['pytype'] = str(type(ob))
            elif isinstance(ob, (dict)):
                write.dict2h5(self.fh5, grp, ob, attributes=at, skip=skip)
                self.fh5[grp].attrs['pytype'] = str(type(ob))
            elif isinstance(ob, object):
                write.dict2h5(self.fh5, grp, ob.__dict__, skip=skip)
                self.fh5[grp].attrs['pytype'] = str(type(ob))

        self.fh5.close()

    def dict2h5(fh5, grp, dic, attributes=None, skip=None):
        """
        Recursively write dict to HDF5 format.

        Parameters
        ----------
        h5id : str
            HDF5 file object.
        path : str
            Group name inside HDF5 file.
        dic : dict
            Dictionary to be saved in HDF5 format.

        Raises
        ------
        ValueError
            If the dict contains types different from ndarray, int64, float64,
            bytes, int, string, list or dict, the method raises the error
            "Cannot save XXX type with dict2h5".

        Returns
        -------
        ``None``.

        """
        grptype = type(grp)
        grp = str(grp) if not isinstance(grp, str) else grp
        dt = type(dic).__name__
        if type(dic).__name__ not in _str2type.keys():
            if dic is not None:
                dic = dic.__dict__
            else:
                fh5[grp] = string_('None')
                dic = {}

        if dic:
            fh5.create_group(grp)

        fh5g = fh5[grp]
        # if grptype != str:
        fh5g.attrs['grptype'] = str(grptype)
        # else:
        #     fh5g.attrs['grptype'] = 'str'
        if attributes:
            for k, v in attributes.items():
                fh5g.attrs[k] = v

        if 'pytype' not in fh5g.attrs.keys():
            fh5g.attrs['pytype'] = dt

        for key, item in dic.items():
            doskip = False
            if skip is not None:
                for i, s in enumerate(skip):
                    if str(key) == s:
                        logging.info(f"Skipping key {s}")
                        doskip = True
                    elif str(key) in s:
                        tmp = s.split('.')[1:][0]
                        skip[i] = tmp
            if doskip:
                continue

            write.item2h5(fh5, grp, key, item, attributes=attributes, skip=skip)


    def iterable2h5(fh5, dataname, iterable, attrs=None, grp=None, skip=None):

        if isinstance(iterable, (list, tuple)):
            iterable = asarray(iterable)
        # --- store iterable
        if grp:
            fh5.create_group(grp)
            fh5 = fh5[grp]
        else:
            fh5 = fh5

        ittype = iterable.dtype
        datanametype = str(type(dataname))
        if type(dataname) != str:
            dataname = str(dataname)
        
        if skip is not None:
            for i, s in enumerate(skip):
                if dataname == s:
                    return None
                elif dataname in s:
                    tmp = s.split('.')[1:][0]
                    skip[i] = tmp

        if isinstance(iterable, ndarray):
            if 'U' in str(ittype):  # string array
                iterable = iterable.astype(dtype='O')
                dt_str = h5py.special_dtype(vlen=str)
                fh5.create_dataset(dataname, data=iterable, dtype=dt_str)
                fh5[dataname].attrs['pytype'] = str(type(iterable))
                fh5[dataname].attrs['keytype'] = str(datanametype)
            elif 'object' in str(ittype):
                fh5.create_group(dataname)
                # fh5[grp].attrs.create('pytype', type(iterable))
                # for i, obj in enumerate(iterable):
                #     write.dict2h5(fh5[grp], i, obj.__dict__)
                # fh5.attrs.create('pytype', type(iterable))
                for i, obj in enumerate(iterable):
                    objtype = type(obj)
                    write.item2h5(fh5, dataname, str(i), obj, attributes=attrs, skip=skip)

                #     if 'dict' in str(objtype):
                #         write.dict2h5(fh5[dataname], i, obj)
                #     else:
                #         write.dict2h5(fh5[dataname], i, obj.__dict__)
                #     fh5[dataname][str(i)].attrs['pytype'] = str(objtype)
                # fh5[dataname].attrs['pytype'] = str(type(iterable))
            elif ittype in [*_int_types, *_float_types]:
                fh5.create_dataset(dataname, data=iterable, chunks=True,
                                   compression="gzip", compression_opts=4)
                fh5[dataname].attrs['pytype'] = str(type(iterable))
                fh5[dataname].attrs['keytype'] = str(datanametype)
            else:
                fh5.file.close()
                raise OSError(f'{ittype} iterable cannot be handled!')
        else:
            fh5.file.close()
            raise OSError(f'{ittype} iterable cannot be handled!')

        # --- set attributes
        fh5.attrs.create('pytype', str(ittype))
        if attrs:
            for k, v in attrs.items():
                fh5.attrs.create(k, v)

    def item2h5(fh5, group, key, item, attributes=None, skip=None):
        """Dump item to h5 file.

        Parameters
        ----------
        fh5 : object
            h5 handle
        group : str
            Group containing the item
        key : str
            name of the item
        item : object
            Item to be dumped
        attributes : object, optional
            attributes object, by default `None`
        skip : iterable, optional
            list of sub-items to be skipped, by default `None`

        Raises
        ------
        ValueError
            _description_
        """
        # --- float and int
        if isinstance(item, (*_int_types, *_float_types, bytes)):
            fh5[group].create_dataset(str(key), data=item)
        # --- string
        elif isinstance(item, str):
            dt_str = h5py.special_dtype(vlen=str)
            fh5[group].create_dataset(str(key), data=item, dtype=dt_str)
        # --- iterable
        elif isinstance(item, (list, tuple, ndarray, set)):
            write.iterable2h5(fh5[group], key, item, skip=skip)
        # --- dict
        elif isinstance(item, dict):
            if type(item) != dict: # any subclass of dict
                item = dict(item)
            write.dict2h5(fh5[group], key, item, attributes=attributes, skip=skip)
        # --- object
        elif isinstance(item, object):
            write.dict2h5(fh5[group], key, item, skip=skip)
        # --- raise error if type not recognised
        else:
            raise ValueError('Cannot save {} type!'.format(type(item)))
        # --- assign key and value types
        fh5[group][str(key)].attrs['pytype'] = str(type(item))
        fh5[group][str(key)].attrs['keytype'] = str(type(key))


def _checkname(fname):
    """
    Check file extension.

    Parameters
    ----------
    fname : str
        Input filename (optional extension).

    Raises
    ------
    OSError
        -File extension is wrong. Only HDF5 can be parsed

    Returns
    -------
    ``None``.
    """
    lst = fname.split(".")

    if len(lst) == 1:
        msg = ("File extension is missing. Only HDF5 can be read/written!")
        raise OSError(msg)

    else:

        if lst[-1] != "hdf5" and lst[-1] != "h5":
            msg = ("File extension is wrong. Only HDF5 can be read/written!")
            raise OSError(msg)

    return fname


def _wopen(h5name, overwrite=False):
    """
    Open the hdf5 file "h5name.hdf5" in "append" mode.

    Parameters
    ----------
    h5name : str
        File name

    Returns
    -------
    fh5 : object
        h5py object

    """
    if os.path.isfile(h5name):
        if overwrite:
            ans = 'yes'
        else:
            ans = 'append'

    else:  # if file do not exist, it creates it
        ans = "create"

    if ans in ['yes', 'y', 'Yes', 'Y', 'YES']:
        os.remove(h5name)
        # open file in write mode
        fh5 = h5py.File(h5name, "a")
        return fh5

    else:
        # create file in append mode
        fh5 = h5py.File(h5name, "a")
        return fh5
