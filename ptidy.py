#!/usr/bin/env python2
# encoding: utf-8
'''
#=============================================================================
#     FileName: ptidy.py
#         Desc: tidy your photo automatically
#       Author: Mocker
#        Email: Zuckerwooo@gmail.com
#     HomePage: zuckonit.github.com
#      Version: 0.0.2
#   LastChange: 2013-10-29 07:22:08
#      History: bugfix in windows platform
#=============================================================================
'''
import os
import sys
import time
import optparse

SUPPORT_SUFFIX = ("bmp", "jpg", "jpeg", "jpe", "gif", "png", "ico")

def get_pic_format(f):
    return f.split('.')[-1]

def get_pic_date(f):
    ct = os.path.getctime(f)
    return time.gmtime(ct)

def get_pic_size(f):
    """return the bit"""
    return os.path.getsize(f)

def get_secure_dir(d):
    return os.path.expanduser(os.path.abspath(d)).replace('\\','/')

def get_all_file(d, fmt=None, size=None):
    d = get_secure_dir(d)
    files = []
    if fmt is not None:
        fmt = tuple(fmt.split(':'))
    else:
        fmt = SUPPORT_SUFFIX
    for i in os.walk(d):
        f = [os.path.join(i[0], f).replace('\\','/') for f in i[2] if len(i[2]) > 0 and f.endswith(fmt)]
        files.extend(f)
    if size is not None:
        size *= 0x3e8
        files = [i for i in files if get_pic_size(i) > size]
    return files

def get_all_date(files, by='day'):
    date = {}
    if by == 'day':
        for i in files:
            ctm = get_pic_date(i)
            d = "%s-%s-%s" % (ctm.tm_year, ctm.tm_mon, ctm.tm_mday)
            if date.has_key(d):
                date[d].extend([i])
            elif not date.has_key(d):
                date[d] = [i,]
    elif by == 'month':
        for i in files:
            ctm = get_pic_date(i)
            d = "%s-%s" % (ctm.tm_year, ctm.tm_mon)
            if date.has_key(d):
                date[d].extend([i])
            elif not date.has_key(d):
                date[d] = [i,]
    elif by == 'year':
        for i in files:
            ctm = get_pic_date(i)
            d = '%s'%ctm.tm_year
            if date.has_key(d):
                date[d].extend([i])
            elif not date.has_key(d):
                date[d] = [i,]
    return date

def backup(bk, src, dst):
    f = open(bk, 'wb')
    f.write('%s === %s' % (src, dst))
    f.close()

def opt(args):
    """
    -h | --help    get the usage
    -p | --pic-dir the dir where photo located
    -d | --day     tidy by day
    -m | --month   tidy by month
    -y | --year    tidy by year
    -s | --size    tidy pictures bigger than size
    -f | --format  filter the special format, split with ':'
    """
    parser = optparse.OptionParser(usage="usage: %prog [options] photo-dir")
    parser.add_option(
        "-p", "--pic-dir",
        dest="pic", type="string",
        help="directory where pictures located"
    )
    parser.add_option(
        "-d", "--day",
        dest="day", action="store_true", default=False,
        help="tidy the pictures by date"
    )
    parser.add_option(
        "-m", "--month",
        dest="month", action="store_true", default=False,
        help="tidy the pictures by month"
    )
    parser.add_option(
        "-y", "--year",
        dest="year", action="store_true", default=False,
        help="tidy the pictures by year"
    )
    parser.add_option(
        "-s", "--size",
        dest="size", type="int",
        help="filter the picture more than size"
    )
    parser.add_option(
        "-f", "--format",
        dest="fmt", type="string",
        help="filter the picture with special format, split with ':'"
    )

    (options, args) = parser.parse_args(args)

    if options.pic is None or not os.path.isdir(options.pic):
        print >> sys.stderr, "Argument directory at least"
        return -1
    files = get_all_file(options.pic,options.fmt, options.size)
    pic = get_secure_dir(options.pic)

    if os.name == 'nt':
        _f = '%s.bk'%(os.path.join(pic,'%s'%time.time()))
    else:
        _f = '%s.bk'%(os.path.join(pic,'.%s'%time.ctime()))
        _f = _f.replace('\\', '/')
    bk_f = open(_f, 'wb')
    if options.day:
        ff = get_all_date(files, 'day')
    elif options.month:
        ff = get_all_date(files, 'month')
    elif options.year:
        ff = get_all_date(files, 'year')
    else:
        ff = get_all_date(files)

    count = 0
    for d in ff:
        save_d = os.path.join(pic, d)
        os.path.isdir(save_d) or os.makedirs(save_d)
        for f in ff[d]:
            dst = os.path.join(save_d, f.split('/')[-1]).replace('\\', '/')
            if f != dst:
                os.rename(f,dst)
                bk_f.write('%s ==> %s\r\n'%(f,dst))
                count = 1
    bk_f.close()
    if count == 0:  #if there is no change, no bk file will generate
        os.remove(_f)

if __name__ == '__main__':
    opt(sys.argv)
