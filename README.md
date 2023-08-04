# GetWawe

A radio broadcast downloader designed to simplify the downloading of broadcasts from Orthodox radio stations.
As of now, it operates solely through the terminal, contributions for GUI integration are welcome.

## Features

- Quickly and efficiently download broadcasts.
- Supports Kol-Hay station (kol-barama site is [broken](http://archive.kol-barama.co.il/)).
- Ability to download entire programs.

![image](https://github.com/danielmayost/getwave/assets/41772276/eccd119d-7c71-482a-8a37-05f8dea331b8)

## Usage
**Note**: It's recommended to use a terminal that supports Hebrew (bidi) like 'Terminal' in Windows. Avoid using the older 'cmd' as it might reverse Hebrew letters.

- Run the program from a Terminal.
- Follow the instructions.

### Pre-defined
You can run the program with pre-defined arguments. For instance:
```
./getwave --station 1 --program 222 --broadcasts "2-5,8" --yes --output "./dist" -pr 3 --index 5 
```
- `--station 1` selects station 1 (kol-hay).
- `--program 222` chooses program number 222.
- `--broadcasts "2-5,8"` selects a range of broadcasts from 2 to 5, as well as broadcast 8.
- `--yes` skips the confirmation prompt.
- `--output "./dist"` designates the 'dist' folder for output files.
- `-pr 3` indicates that up to 3 files can be downloaded simultaneously.
- `--index 5` determines the starting index for display and filenames.

  
