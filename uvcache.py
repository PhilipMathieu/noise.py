# UVCache() is a way of accessing data_arrays split between multiple
# miriad files with pyuvdata.  It essentially maintains a cache of
# UVData() objects and allows you to access each without needing to keep
# them all loaded in RAM at once.  It currently allows you to access the
# data_array and flag_array seamlessly between files, and could be easily extended to other UVData attributes.
# Author: Philip Mathieu
# Email: philip.eng.mathieu@gmail.com
import numpy as np
from uvdata.uv import UVData
from os import listdir
from os.path import isdir, join
import math


class UVCache():

    def __init__(self, files, size):
        # allow
        if not isinstance(files, list):
            dirfiles = [f for f in listdir(files) if isdir(join(files, f))]
            if len(dirfiles) < 1:
                print "Could not load files.  Are you sure you didn't mean [{dirfiles}]?".format(dirfiles)
            else:
                self.files = dirfiles
        else:
            self.files = files
        if len(self.files) < size:
            self.size = len(self.files)
            print "Warning: Could only load {0} files.".format(self.size)
        else:
            self.size = size
        # makes a list of UVData objects
        self.objs = [UVData() for _ in range(size)]
        self.file_index = np.arange(size)
        self.next_file = 0
        self.reset(0)
        self.Ntimes = self.objs[0].Ntimes
        self.Nbls = self.objs[0].Nbls
        self.Nblts = self.objs[0].Nblts

    def reset(self, index):
        self.next_file = index
        while self.next_file < index + self.size:
            # use of modulus here ensures that the files are always indexed
            # sensibly, i.e. in a 6 file buffer file 10 will always be at
            # position 5
            self.increment_one()

    def increment_one(self):
        if self.next_file == len(self.files):
            print "Increment Error!"
            while(True):
                a = 1
            return
        self.objs[self.next_file % self.size].read_miriad(
            self.files[self.next_file])
        self.file_index[self.next_file % self.size] = self.next_file
        print "Loaded file {0} of {1} into cache of size {2}".format(self.next_file + 1, len(self.files),self.size)
        self.next_file += 1

    def increment(self, index):
        if index > self.file_index.max() + self.size or index < self.file_index.min():
            # prevent you from trying to index a negative number
            self.reset(max(index - self.size, 0))
        else:
            while self.next_file <= index:
                self.increment_one()
    # need to add decrement code here

    def get_sub_array(self, cursor, shape):
        beg_file = int(cursor[0] / self.Nblts)
        end_file = beg_file + int(math.ceil(float(shape[0]) / self.Nblts))
        if end_file - beg_file > self.size:
            print "Shape exceeds buffer!"
            return
        elif end_file > self.next_file:
            self.increment(end_file)
        data = np.ndarray(shape, dtype='cfloat')
        flag = np.ndarray(shape)
        # later you could add more things here if you want to pass along more
        # than just data and flags
        file_cnt = 0
        for file in range(beg_file, end_file):
            data[file_cnt * self.Nblts:(file_cnt + 1) * self.Nblts, :, :, :] = self.objs[file % self.size].data_array[
                :, cursor[1]:cursor[1] + shape[1], cursor[2]:cursor[2] + shape[2], cursor[3]:cursor[3] + shape[3]]
            flag[file_cnt * self.Nblts:(file_cnt + 1) * self.Nblts, :, :, :] = self.objs[file % self.size].flag_array[
                :, cursor[1]:cursor[1] + shape[1], cursor[2]:cursor[2] + shape[2], cursor[3]:cursor[3] + shape[3]]
            file_cnt += 1
        # handling last file
        data[file_cnt * self.Nblts:, :, :, :] = self.objs[end_file % self.size].data_array[
            :shape[0]%self.Nblts, cursor[1]:cursor[1] + shape[1], cursor[2]:cursor[2] + shape[2], cursor[3]:cursor[3] + shape[3]]
        flag[file_cnt * self.Nblts:, :, :, :] = self.objs[end_file % self.size].flag_array[
            :shape[0]%self.Nblts, cursor[1]:cursor[1] + shape[1], cursor[2]:cursor[2] + shape[2], cursor[3]:cursor[3] + shape[3]]
        return [data, flag]
