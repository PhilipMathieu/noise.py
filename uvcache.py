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
        current = self.objs[self.next_file % self.size]
        current.read_miriad(
            self.files[self.next_file])
        self.file_index[self.next_file % self.size] = self.next_file
        # print "Loaded file {0} of {1} into cache of size {2}".format(
        # self.next file + 1, len(self.files), self.size)
        # do some checks
        if hasattr(self, 'Nbls'):
            if not current.baseline_array.size % self.Nbls == 0:
                print "Warning: baseline count may not match."
            if current.baseline_array.size >= 2 * self.Nbls:
                if not set(current.baseline_array[0:self.Nbls]) == set(current.baseline_array[self.Nbls:2 * self.Nbls]):
                    print "Warning: baselines may not be sorted."
        self.next_file += 1

    def increment(self, index):
        if index > self.file_index.max() + self.size or index < self.file_index.min():
            # prevent you from trying to index a negative number
            self.reset(max(index - self.size, 0))
        else:
            while self.next_file <= index:
                self.increment_one()

    def get_sub_array(self, cursor, shape):
        beg_file = int(cursor[0] / self.Nblts)
        end_file = int((cursor[0] + shape[0]) / self.Nblts)
        if end_file - beg_file > self.size:
            print "Shape exceeds buffer!"
            return
        elif end_file > self.next_file:
            self.increment(end_file)
        data = np.ndarray(shape, dtype='cfloat')
        flag = np.ndarray(shape)
        if beg_file == end_file:
            data = self.objs[beg_file % self.size].data_array[cursor[0]:cursor[0] + shape[0], cursor[
                1]:cursor[1] + shape[1], cursor[2]:cursor[2] + shape[2], cursor[3]:cursor[3] + shape[3]]
            flag = self.objs[beg_file % self.size].flag_array[cursor[0]:cursor[0] + shape[0], cursor[
                1]:cursor[1] + shape[1], cursor[2]:cursor[2] + shape[2], cursor[3]:cursor[3] + shape[3]]
        else:
            # handling first file
            first_block_len = self.Nblts - (cursor[0] % self.Nblts)
            data[: first_block_len, :, :, :] = self.objs[beg_file % self.size].data_array[
                cursor[0] % self.Nblts:, cursor[1]: cursor[1] + shape[1], cursor[2]: cursor[2] + shape[2], cursor[3]: cursor[3] + shape[3]]
            flag[: first_block_len, :, :, :] = self.objs[beg_file % self.size].flag_array[
                cursor[0] % self.Nblts:, cursor[1]: cursor[1] + shape[1], cursor[2]: cursor[2] + shape[2], cursor[3]: cursor[3] + shape[3]]
            file_cnt = 0
            for file in range(beg_file + 1, end_file):
                data[file_cnt * self.Nblts + first_block_len: (file_cnt + 1) * self.Nblts + first_block_len, :, :, :] = self.objs[file % self.size].data_array[
                    :, cursor[1]: cursor[1] + shape[1], cursor[2]: cursor[2] + shape[2], cursor[3]: cursor[3] + shape[3]]
                flag[file_cnt * self.Nblts + first_block_len: (file_cnt + 1) * self.Nblts + first_block_len, :, :, :] = self.objs[file % self.size].flag_array[
                    :, cursor[1]: cursor[1] + shape[1], cursor[2]: cursor[2] + shape[2], cursor[3]: cursor[3] + shape[3]]
                file_cnt += 1
            if not shape[0] == file_cnt * self.Nblts + first_block_len:
                # handling last file
                data[shape[0] - self.Nblts * file_cnt - first_block_len:, :, :, :] = self.objs[end_file % self.size].data_array[
                    0: shape[0] % self.Nblts, cursor[1]: cursor[1] + shape[1], cursor[2]: cursor[2] + shape[2], cursor[3]: cursor[3] + shape[3]]
                flag[shape[0] - self.Nblts * file_cnt - first_block_len:, :, :, :] = self.objs[end_file % self.size].flag_array[
                    0: shape[0] % self.Nblts, cursor[1]: cursor[1] + shape[1], cursor[2]: cursor[2] + shape[2], cursor[3]: cursor[3] + shape[3]]
        return [data, flag, self.objs[beg_file % self.size].time_array[cursor[0] % self.Nblts], self.objs[beg_file % self.size].freq_array[cursor[1], cursor[2]], self.objs[beg_file % self.size].lst_array[cursor[0] % self.Nblts]]

    def get_uvp(self, uvp):
        try:
            return getattr(self.objs[0], uvp)
        except:
            print "Could not find {0} in {1}.".format(uvp, objs[0])
            return None
