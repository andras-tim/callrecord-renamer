# Callrecord Renamer
[![Releases](https://img.shields.io/github/release/andras-tim/callrecord-renamer.svg)](https://github.com/andras-tim/callrecord-renamer/releases)
[![Open issues](https://img.shields.io/github/issues/andras-tim/callrecord-renamer.svg)](https://github.com/andras-tim/callrecord-renamer/issues)
[![License](https://img.shields.io/badge/license-GPL%202.0-blue.svg)](https://github.com/andras-tim/callrecord-renamer/blob/master/LICENSE)

Reformat special file names and update change times (access and modification times too).


## Requirements

* Python 3.x:

   Download and install Python from: https://www.python.org/downloads/

* Python ``phonenumbers`` Module:

   Run the following command on Windows: `C:\Python34\Scripts\easy_install.exe phonenumbers`


## Setup

1. Install requirements
2. Run script with specifying the **recording_path**:

    ```bash
    ./callrecord-renamer.py /my/call/recordings/path
    ```

## Examples
```
0d20141212160318p+36305566778.mp4     => BE 2014.12.12-16.03.18 +36(30)556-6778 Foo Bar.mp4
1d20141125144524p+3630556677.mp4      => KI 2014.11.25-14.45.24 +36(30)556-677 Orange Bar.mp4
1d20141207215358p+3615566778.mp4      => KI 2014.12.07-21.53.58 +36(1)556-6778 Apple Juice.mp4
1d20141207215358p+3628556677.mp4      => KI 2014.12.07-21.53.58 +36(28)556-677 Carrot Line.mp4
1d20141207215358p+36305566778.mp4     => KI 2014.12.07-21.53.58 +36(30)556-6778 Foo Bar.mp4
1d20141207215358p+36305566778899.mp4  => KI 2014.12.07-21.53.58 +36305566778899 Fly City.mp4
1d20141207215358p180.mp4              => KI 2014.12.07-21.53.58 180 Time Service.mp4
0d20141126091240pnull.mp4             => BE 2014.11.26-09.12.40 null null.mp4
0d20141126241240pnull.mp4             => BE 2014.11.27-00.12.40 null null.mp4
0d20141212160318p+36305566778 xyz.mp4 (skipped)
1d20141207215358p+36305588778.tmp     (skipped)
temporary.mp4                         (skipped)
```
