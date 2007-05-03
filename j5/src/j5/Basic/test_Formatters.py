from j5.Test import IterativeTester
from j5.Test import DictDim
from j5.Basic import Formatters
import datetime

class FormatTestResource(object):
    def __init__(self,formatter,result_type,data_result_list):
        self.formatter = formatter
        self.result_type = result_type
        self.data_result_list = data_result_list # tuple of (input, result) pairs

class TestFormatters(IterativeTester.IterativeTester):

    FORMAT_TESTS = {
        'float': FormatTestResource(Formatters.FloatFormatter("%.2f"),Formatters.FormattedFloat,[
                    (5.5,"5.50"),
                    (10.617,"10.62"),
                    ("5.15","5.15"),
                    ('foo',None),
                    (Formatters.FormattedFloat("%.2f",10.2234),"10.22")
                 ]),
        'datetime': FormatTestResource(Formatters.DatetimeFormatter("%Y:%m:%d %H:%M:%S"),Formatters.FormattedDatetime,[
                    (datetime.datetime(1993,11,3,12,51,50),"1993:11:03 12:51:50"),
                    ("1994:12:07 13:17:25","1994:12:07 13:17:25"),
                    ("1994:15:09 13:51:19",None),
                    (Formatters.FormattedDatetime("%Y:%m:%d %H:%M:%S",1996,9,3,12,51,50),"1996:09:03 12:51:50")
                 ]),
        'time': FormatTestResource(Formatters.TimeFormatter("%H %S %M"),Formatters.FormattedTime,[
                    (datetime.time(21,51,12),"21 12 51"),
                    ("13 17 51","13 17 51"),
                    ("moo",None),
                    (Formatters.FormattedTime("%H %S %M",19,17,8),"19 08 17")
                 ]),
        'date': FormatTestResource(Formatters.DateFormatter("%Y %d %m"),Formatters.FormattedDate,[
                    (datetime.date(1987,11,30),"1987 30 11"),
                    ("1990 13 12","1990 13 12"),
                    ("moo",None),
                    (Formatters.FormattedDate("%Y %d %m",2001,11,5),"2001 05 11")
                 ]),
        'loosedatetime': FormatTestResource(Formatters.LooseDatetimeFormatter("%Y:%m:%d %H:%M:%S"),Formatters.FormattedDatetime,[
                    (datetime.datetime(1994,12,6,15,51,52),"1994:12:06 15:51:52"),
                    ("1994:11:07 15:51:53","1994:11:07 15:51:53"),
                    ("2005:12:01","2005:12:01"),
                    ("15:51:02","15:51:02"),
                    ("12:01",None),
                    ("moo",None),
                    (Formatters.FormattedDatetime("%Y:%m:%d %H:%M:%S",1999,6,7,16,15,47),"1999:06:07 16:15:47")
                 ])
    }

    DIMENSIONS = { "ftest" : [ DictDim.DictDim(FORMAT_TESTS) ] }

    def ftest_format(self,formatresource):
        format = formatresource.formatter.format
        result_type = formatresource.result_type

        for data, expected in formatresource.data_result_list:
            result = format(data)
            if result is None:
                assert result == expected
            else:
                assert type(result) == result_type
                assert str(result) == expected