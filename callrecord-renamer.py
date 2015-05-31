#!/usr/bin/env python3
import argparse
import configparser
import os
import phonenumbers
import pprint
import re
import sys
import time
from datetime import datetime, timedelta
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
FILENAME_PATTERN = re.compile(r'^(?P<type>0|1)d(?P<datetime>\d{14})p(?P<phonenum>[+\d]+|null)$')
DATETIME_PATTERN = re.compile(r'^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})'
                              '(?P<hour>\d{2})(?P<min>\d{2})(?P<sec>\d{2})$')
INTERNATIONAL_PHONENUM_TEMPLATE = re.compile(r'^(?P<country>[+\d]+) (?P<region>\d+) (?P<digits1>\d+) (?P<digits2>\d+)$')

FILENAME_TEMPLATE = Template('${type} ${datetime} ${phonenum} ${contact}')
DATETIME_TEMPLATE = '%Y.%m.%d-%H.%M'
PHONENUM_TEMPLATE = Template('${country}(${region})${digits1}-${digits2}')
TYPE_ENUM = {0: 'BE', 1: 'KI'}


class MissingContact(Exception):
    pass


class Contacts(object):
    SECTION_CONTACTS = 'contacts'
    SECTION_UNKNOWN = 'unknown_contacts'
    EMPTY_DATABASE = {
        SECTION_CONTACTS: {},
        SECTION_UNKNOWN: {},
    }

    def __init__(self, ini_file_path: str):
        self.database = configparser.ConfigParser()
        self.file_path = ini_file_path

    def load(self):
        self.database.read_dict(self.EMPTY_DATABASE)
        self.database.read(self.file_path)

    def save(self):
        with open(self.file_path, 'w') as fd:
            self.database.write(fd)

    def get_contact_name_by_number(self, number: str) -> str:
        if number not in self.database[self.SECTION_CONTACTS]:
            self.__add_as_new_contact(number)
            raise MissingContact('Missing contact name for number: {}'.format(number))
        return self.database[self.SECTION_CONTACTS][number]

    def __add_as_new_contact(self, number: str):
        self.database.set(self.SECTION_UNKNOWN, number, '?')


class FileManager(object):
    class ParseError(Exception):
        pass

    def __init__(self, base_directory: str, contacts: Contacts, no_change=False,
                 skip_errors=False):
        self.path = base_directory
        self.contacts = contacts
        self.no_change = no_change
        self.skip_errors = skip_errors

    def update_files_in_directory(self):
        files = self.__get_prepared_renameable_files()
        substituted_files = map(FileManager.__substitute_fields_of_file, files)

        self.contacts.load()

        for file in substituted_files:
            contact_name = self.__get_contact_name_for_phone_number(file)
            if contact_name is None:
                continue

            file['substitutes']['contact'] = contact_name
            self.__rename_and_fix_times(old_name=file['substitutes']['name'],
                                        new_name=FileManager.__new_name_for_file(file['substitutes']),
                                        extension=file['substitutes']['extension'],
                                        change_time=file['data']['datetime'])

        self.contacts.save()

    def __get_contact_name_for_phone_number(self, file: dict) -> (str, None):
        phonenum = file['substitutes']['phonenum']
        if phonenum == 'null':
            return 'null'

        try:
            return self.contacts.get_contact_name_by_number(phonenum)
        except MissingContact:
            print('{name}\tskipped - missing phone number for {phonenum}'.format(
                name=file['substitutes']['name'],
                phonenum=file['substitutes']['phonenum']
            ))
            return None

    def __get_prepared_renameable_files(self):
        files = os.listdir(self.path)
        split_files = map(FileManager.__split_full_filename, files)
        parsed_files = map(self.__parse_file_name, split_files)
        filtered_parsed_files = filter(lambda f: f is not None, parsed_files)

        return filtered_parsed_files

    @classmethod
    def __split_full_filename(cls, file_name: str):
        split_file_name = os.path.splitext(file_name)
        return {'name': split_file_name[0], 'extension': split_file_name[1][1:]}

    def __parse_file_name(self, file: dict):
        if not file['extension'].lower() in EXTENSIONS:
            return None

        matches = FILENAME_PATTERN.match(file['name'])
        if matches is None:
            return None
        file_matches = matches.groupdict()

        try:
            file['type'] = FileManager.__parse_type(file_matches['type'])
            file['datetime'] = FileManager.__parse_datetime(file_matches['datetime'])
            file['phonenum'] = self.__parse_phone_number(file_matches['phonenum'])
        except Exception as e:
            self.print_error('PARSE ERROR!', {'file': file, 'file_matches': file_matches}, e)
            return None

        return file

    @classmethod
    def __parse_type(cls, raw_type):
        int_type = int(raw_type)
        if int_type not in TYPE_ENUM.keys():
            raise cls.ParseError('Bad type format! %s' % raw_type)

        return int_type

    @classmethod
    def __parse_datetime(cls, raw_datetime):
        matches = DATETIME_PATTERN.match(raw_datetime)
        if matches is None:
            raise cls.ParseError('Bad date-time format! %s' % raw_datetime)
        datetime_matches = {k: int(v) for k, v in matches.groupdict().items()}

        hour24_workaround = datetime_matches['hour'] == 24
        if hour24_workaround:
            datetime_matches['hour'] = 0

        date_object = datetime(datetime_matches['year'], datetime_matches['month'], datetime_matches['day'],
                               datetime_matches['hour'], datetime_matches['min'], datetime_matches['sec'])

        if hour24_workaround:
            date_object += timedelta(days=1)

        return date_object

    def __parse_phone_number(self, raw_phone_number):
        parsed_phone_number = None

        if raw_phone_number == 'null':
            return None

        if FileManager.__is_full_length_phone_number(raw_phone_number):
            try:
                parsed_phone_number = FileManager.__parse_full_length_phone_number(raw_phone_number)
            except (phonenumbers.NumberParseException, self.ParseError) as e:
                self.print_error('ERROR: Can not parse this full length phone number! '
                                 'It will be leave in original form.',
                                 {'phone_number': raw_phone_number}, e)

        if parsed_phone_number is None:
            parsed_phone_number = {'raw': raw_phone_number}

        return parsed_phone_number

    @classmethod
    def __parse_full_length_phone_number(cls, phone_number):
        parsed_number = phonenumbers.parse(phone_number, None)
        international_number = phonenumbers.format_number(parsed_number,
                                                          phonenumbers.PhoneNumberFormat.INTERNATIONAL)

        matches = INTERNATIONAL_PHONENUM_TEMPLATE.match(international_number)
        if matches is None:
            raise cls.ParseError('Bad international phone number! %s' % international_number)

        return matches.groupdict()

    @classmethod
    def __is_full_length_phone_number(cls, phone_number):
        return phone_number[0] == '+' or phone_number[0:1] == '06'

    @classmethod
    def __substitute_fields_of_file(cls, file: dict):
        substitutes = dict()

        for key in file.keys():
            if key == 'type':
                substitutes[key] = TYPE_ENUM[file['type']]

            elif key == 'datetime':
                substitutes[key] = file['datetime'].strftime(DATETIME_TEMPLATE)

            elif key == 'phonenum':
                if file[key] is None:
                    substitutes[key] = 'null'
                elif 'raw' in file[key].keys():
                    substitutes[key] = file[key]['raw']
                else:
                    substitutes[key] = PHONENUM_TEMPLATE.substitute(file[key])

            else:
                substitutes[key] = file[key]

        return {'data': file, 'substitutes': substitutes}

    @classmethod
    def __new_name_for_file(cls, file: dict):
        return FILENAME_TEMPLATE.substitute(file)

    def __rename_and_fix_times(self, old_name: str, new_name: str, extension: str, change_time: datetime):
        old_full_name = '%s%s%s' % (old_name, os.extsep, extension)
        new_full_name = '%s%s%s' % (new_name, os.extsep, extension)
        print('%s\t=>\t%s' % (old_full_name, new_full_name))

        if not self.no_change:
            old_path = os.path.join(self.path, old_full_name)
            new_path = os.path.join(self.path, new_full_name)

            FileManager.__set_change_times(old_path, change_time)
            os.rename(old_path, new_path)

    @classmethod
    def __set_change_times(cls, path: str, change_time: datetime):
        timestamp = int(time.mktime(change_time.timetuple())) + 3600
        os.utime(path, (timestamp, timestamp))

    def print_error(self, text: str, variables_for_debug=None, error=None):
        error_message = ['', '=' * 80, text, '-' * 80]

        if variables_for_debug is not None:
            if self.skip_errors:
                variables_for_debug['error'] = error
            error_message.append(pprint.pformat(variables_for_debug))

        error_message.extend(['=' * 80, '', ''])

        sys.stdout.flush()
        sys.stderr.write(os.linesep.join(error_message))
        sys.stderr.flush()

        if error is not None and not self.skip_errors:
            raise error


class ArgParser(object):
    def __init__(self):
        supported_extensions = ', '.join(map(lambda e: '*.%s' % e, EXTENSIONS))

        self.parser = argparse.ArgumentParser(description='Automatic rename tool for files of call recorder')
        self.parser.add_argument('-t', '--test', action='store_true', dest='no_change',
                                 help='test mode; filesystem will not be changed')
        self.parser.add_argument('-s', '--skip', action='store_true', dest='skip_errors',
                                 help='skip errors; process will not break when an error occurred')
        self.parser.add_argument('-c', '--contacts', dest='contacts_path', type=str, metavar='PATH',
                                 help='path of contacts INI file for mapping names to numbers')
        self.parser.add_argument('path', type=str,
                                 help='path of call files (%s)' % supported_extensions)

    def parse(self):
        args = self.parser.parse_args()
        if not os.path.isdir(args.path):
            self.parser.error('The specified directory is not exists: %r' % args.path)
        if not os.path.isfile(args.contacts_path):
            self.parser.error('The specified contacts INI file is not exists: %r' % args.contacts_path)

        return args


def main():
    args = ArgParser().parse()

    contacts_path = Contacts(args.contacts_path)
    FileManager(args.path, contacts_path, args.no_change, args.skip_errors).update_files_in_directory()


if __name__ == '__main__':
    main()
