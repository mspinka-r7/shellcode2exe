# Create EXEs from shellcode blobs

Tool that creates a runnable PE from shellcode (assumes entry point is at 0).

Inspired by https://github.com/repnz/shellcode2exe with some improvements:

- Uses `nasm` instead of `yasm`,
- does not rely on relative paths &mdash; you can add it to your `PATH` and run from anywhere,
- does not clutter the working directory with temporary files.

It is up to you to run either the Python script (`shellcode2exe.py`) or the compiled binary (`shellcode2exe.exe`).

- The Python script has no dependencies and has been tested on Python 3.10.
- The executable was compiled from the script using PyInstaller.

The only requirement is to keep the `deps` directory in the same place as the Python script or compiled binary.

## Usage

```
PS C:\Users\luke\Tools\Shellcode2Exe> .\shellcode2exe.exe -h
usage: shellcode2exe.exe [-h] -s SOURCE -d DESTINATION -a {32,64}

Build a minimal Windows PE file from a shellcode blob.

options:
  -h, --help            show this help message and exit
  -s SOURCE, --source SOURCE
                        Path to the input shellcode blob.
  -d DESTINATION, --destination DESTINATION
                        Path for the output PE file (e.g., output.exe).
  -a {32,64}, --arch {32,64}
                        Specify the architecture: 32 for 32-bit or 64 for 64-bit.
```
