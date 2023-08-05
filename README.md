# GetWave
A radio broadcast downloader designed to simplify ddownloading broadcasts from Orthodox radio stations.
As of now, it operates solely through the terminal, contributions for a GUI are welcome.

This is a small project I built to learn Python

## Features
- Quickly and efficiently download broadcasts.
- Supports Kol-Hay station (kol-barama site is [broken](http://archive.kol-barama.co.il/)).
- Ability to download entire programs.

![Screenshot 2023-08-04 112539](https://github.com/danielmayost/getwave/assets/41772276/65cdd2a5-c6ae-4bb0-a409-7f14549719cc)

## Usage
**Note**: It's recommended to use a terminal that supports Hebrew (bidi) like 'Terminal' in Windows. Avoid using the old 'cmd' as it might reverse Hebrew letters.

- Download **getwave** from [here](https://github.com/danielmayost/getwave/releases)
- Run the program from a Terminal.
- Follow the on-screen instructions.

### Pre-defined
You can run the program with pre-defined arguments. For instance:
```
./getwave --station 1 --program 222 --broadcasts "2-5,8" --yes --output "./dist" -pr 3 --index 5 
```
- `--station 1` selects station 1 (kol-hay).
- `--program 222` chooses program number 222.
- `--broadcasts "2-5,8"` selects a range of broadcasts from 2 to 5, as well as 8.
- `--yes` skips the confirmation prompt.
- `--output "./dist"` specifies the 'dist' folder for output files.
- `-pr 3` indicates that up to 3 files can be downloaded simultaneously.
- `--index 5` determines the starting index for display and filenames.

  
