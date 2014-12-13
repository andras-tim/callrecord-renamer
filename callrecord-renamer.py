#!/usr/bin/env python3
import argparse
import time
from datetime import datetime
import phonenumbers
import os
import re
from string import Template

# REQUIREMENTS
# * Python 3.x:
#     Download and install Python from:
#       https://www.python.org/downloads/
#
# * Python 'phonenumbers' Module:
#     Run the following command:
#       C:\Python34\Scripts\easy_install.exe phonenumbers


__author__ = 'Andras Tim'

EXTENSIONS = ['mp4']  # lowercase
FILENAME_PATTERN = re.compile(r"^(?P<type>0|1)d(?P<datetime>\d{14})p(?P<phonenum>[+\d]+|null)$")
DATETIME_PATTERN = '%Y%m%d%H%M%S'
INTERNATIONAL_PHONENUM_TEMPLATE = re.compile(r"^(?P<country>[+\d]+) (?P<region>\d+) (?P<digits1>\d+) (?P<digits2>\d+)$")

FILENAME_TEMPLATE = Template('${type} ${datetime} ${phonenum}')
DATETIME_TEMPLATE = '%Y.%m.%d-%H.%M'
PHONENUM_TEMPLATE = Template('${country}(${region})${digits1}-${digits2}')
TYPE_ENUM = {0: "BE", 1: "KI"}


class FileManager(object):
    class PhoneNumberParseError(Exception):
        pass

    def __init__(self, base_directory: str, no_change=False):
        self.path = base_directory
        self.no_change = no_change

    def update_files_in_directory(self):
        files = self.__get_prepared_renameable_files()
        substituted_files = map(FileManager.__substitute_fields_of_file, files)

        for file in substituted_files:
            self.__rename_and_fix_times(old_name=file["substitutes"]["name"],
                                        new_name=FileManager.__new_name_for_file(file["substitutes"]),
                                        extension=file["substitutes"]["extension"],
                                        change_time=file["data"]["datetime"])

    def __get_prepared_renameable_files(self):
        files = os.listdir(self.path)
        split_files = map(FileManager.__split_full_filename, files)
        parsed_files = map(FileManager.__parse_file_name, split_files)
        filtered_parsed_files = filter(lambda f: f is not None, parsed_files)

        return filtered_parsed_files

    @classmethod
    def __split_full_filename(cls, file_name: str):
        split_file_name = os.path.splitext(file_name)
        return {"name": split_file_name[0], "extension": split_file_name[1][1:]}

    @classmethod
    def __parse_file_name(cls, file: dict):
        if not file["extension"].lower() in EXTENSIONS:
            return None

        matches = FILENAME_PATTERN.match(file["name"])
        if matches is None:
            return None

        file["type"] = int(matches.group("type"))
        file["datetime"] = datetime.strptime(matches.group("datetime"), DATETIME_PATTERN)
        file["phonenum"] = FileManager.__parse_phone_number(matches.group("phonenum"))

        return file

    @classmethod
    def __parse_phone_number(cls, phone_number):
        if phone_number == "null":
            return None

        parsed_number = phonenumbers.parse(phone_number, None)
        international_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

        matches = INTERNATIONAL_PHONENUM_TEMPLATE.match(international_number)
        if matches is None:
            raise cls.PhoneNumberParseError("Can not parse the following phone number: %s" % phone_number)

        return matches.groupdict()

    @classmethod
    def __substitute_fields_of_file(cls, file: dict):
        substitutes = dict()

        for key in file.keys():
            if key == "type":
                substitutes[key] = TYPE_ENUM[file["type"]]

            elif key == "datetime":
                substitutes[key] = file["datetime"].strftime(DATETIME_TEMPLATE)

            elif key == "phonenum":
                if file[key] is None:
                    substitutes[key] = "null"
                else:
                    substitutes[key] = PHONENUM_TEMPLATE.substitute(file[key])

            else:
                substitutes[key] = file[key]

        return {"data": file, "substitutes": substitutes}

    @classmethod
    def __new_name_for_file(cls, file: dict):
        return FILENAME_TEMPLATE.substitute(file)

    def __rename_and_fix_times(self, old_name: str, new_name: str, extension: str, change_time: datetime):
        old_full_name = "%s%s%s" % (old_name, os.extsep, extension)
        new_full_name = "%s%s%s" % (new_name, os.extsep, extension)
        print("%s\t=>\t%s" % (old_full_name, new_full_name))

        if not self.no_change:
            old_path = os.path.join(self.path, old_full_name)
            new_path = os.path.join(self.path, new_full_name)

            FileManager.__set_change_times(old_path, change_time)
            os.rename(old_path, new_path)

    @classmethod
    def __set_change_times(cls, path: str, change_time: datetime):
        timestamp = int(time.mktime(change_time.timetuple()))+3600
        os.utime(path, (timestamp, timestamp))


class ArgParser(object):
    def __init__(self):
        supported_extensions = ", ".join(map(lambda e: "*.%s" % e, EXTENSIONS))

        self.parser = argparse.ArgumentParser(description='Automatic rename tool for files of call recorder')
        self.parser.add_argument('-t', '--test', action='store_true', dest='no_change',
                                 help='test mode; filesystem will not be changed')
        self.parser.add_argument('path', type=str,
                                 help='path of call files (%s)' % supported_extensions)

    def parse(self):
        args = self.parser.parse_args()
        if not os.path.isdir(args.path):
            self.parser.error("The specified directory is not exists: %s" % args.path)

        return args


def main():
    args = ArgParser().parse()
    FileManager(args.path, args.no_change).update_files_in_directory()


if __name__ == '__main__':
    main()
