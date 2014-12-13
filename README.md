## Requirements

* Python 3.x:

   Download and install Python from: https://www.python.org/downloads/

* Python 'phonenumbers' Module: 

   Run the following command: `C:\Python34\Scripts\easy_install.exe phonenumbers`

## Examples
```
0d20141212160318p+36305566778 xyz.mp4 (skipped)
1d20141207215358p+36305588778.tmp     (skipped)
temporary.mp4                         (skipped)
0d20141126091240pnull.mp4             => BE 2014.11.26-09.12 null.mp4
0d20141212160318p+36305566778.mp4     => BE 2014.12.12-16.03 +36(30)556-6778.mp4
1d20141125144524p+3630556677.mp4      => KI 2014.11.25-14.45 +36(30)556-677.mp4
1d20141207215358p+3615566778.mp4      => KI 2014.12.07-21.53 +36(1)556-6778.mp4
1d20141207215358p+3628556677.mp4      => KI 2014.12.07-21.53 +36(28)556-677.mp4
1d20141207215358p+36305566778.mp4     => KI 2014.12.07-21.53 +36(30)556-6778.mp4
```
