# UVBuffer() is a way of accessing data arrays split between multiple
# miriad files with pyuvdata.  It essentially maintains a buffer of
# UVData() objects and allows you to access each without needing to keep
# them all loaded in ram at once.  It currently allows you to access the
# data_array and flag_array seamlessly between files.
import numpy as np
from uvdata.uv import UVData


class UVBuffer():

    def __init__(self, files, min_files):
        self.min_files = min_files
        self.files = files
        # makes a list of UVData objects
        self.objs = [UVData() for _ in range(min_files)]
        self.file_index = np.arange(min_files)
        self.next_file = 0
        while self.next_file < min_files:
            self.objs[self.next_file % self.min_files].read_miriad(
                self.files[self.next_file])
            self.file_index[self.next_file % self.min_files] = self.next_file
            self.next_file += 1
        self.Ntimes = self.objs[0].Ntimes
        self.Nbls = self.objs[0].Nbls
        self.Nblts = self.objs[0].Nblts

    def reset(self, index):
        self.next_file = index
        while self.next_file < index + self.min_files:
            # use of modulus here ensures that the files are always indexed
            # sensibly, i.e. in a 6 file buffer file 10 will always be at
            # position 5
            self.objs[self.next_file % self.min_files].read_miriad(
                self.files[self.next_file])
            self.file_index[self.next_file % self.min_files] = self.next_file
            self.next_file += 1

    def increment_one(self):
        if self.next_file == len(self.files):
            print "No files left to increment!"
            return
        self.objs[self.next_file % self.min_files].read_miriad(
            self.files[self.next_file])
        self.file_index[self.next_file % self.min_files] = self.next_file
        self.next_file += 1

    def increment(self, index):
        if index > self.file_index.max() + self.min_files or index < self.file_index.min():
            # prevent you from trying to index a negative number
            self.reset(max(index - self.min_files, 0))
        else:
            while self.next_file <= index:
                self.increment_one()
    # need to add decrement code here

    def get_sub_array(self, cursor, shape):
        beg_file = cursor[0] / self.Nblts
        end_file = beg_file + int(math.ceil(float(shape[0]) / self.Nblts))
        if end_file - beg_file > self.min_files:
            print "Shape exceeds buffer!"
            return
        elif end_file > self.next_file:
            self.increment(end_file)
        data = np.ndarray(shape)
        flag = np.ndarray(shape)
        print data.shape
        # later you could add more things here if you want to pass along more
        # than just data and flags
        file_cnt = 0
        for file in range(beg_file, end_file - 1):
            data[file_cnt * self.Nblts:(file_cnt + 1) * self.Nblts,
                 :, :, :] = self.objs[file % self.min_files].data_array[:, cursor[1]:cursor[1] + shape[1], cursor[2]:cursor[2] + shape[2], cursor[3]:cursor[3] + shape[3]]
            flag[file_cnt * self.Nblts:(file_cnt + 1) * self.Nblts,
                 :, :, :] = self.objs[file % self.min_files].flag_array[:, cursor[1]:cursor[1] + shape[1], cursor[2]:cursor[2] + shape[2], cursor[3]:cursor[3] + shape[3]]
            file_cnt += 1
        # handling last file
        data[file_cnt * self.Nblts:, :, :, :] = self.objs[end_file %
                                                          self.min_files].data_array[:shape[0] % self.Nblts, cursor[1]:cursor[1] + shape[1], cursor[2]:cursor[2] + shape[2], cursor[3]:cursor[3] + shape[3]]
        flag[file_cnt * self.Nblts:, :, :, :] = self.objs[end_file %
                                                          self.min_files].flag_array[:shape[0] % self.Nblts, cursor[1]:cursor[1] + shape[1], cursor[2]:cursor[2] + shape[2], cursor[3]:cursor[3] + shape[3]]
        return [data, flag]
