import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

def main():
    """
    Main function to parse arguments and orchestrate the PE file build process.
    """
    parser = argparse.ArgumentParser(
        description="Build a minimal Windows PE file from a shellcode blob.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-s", "--source",
        required=True,
        help="Path to the input shellcode blob."
    )
    parser.add_argument(
        "-d", "--destination",
        required=True,
        help="Path for the output PE file (e.g., output.exe)."
    )
    parser.add_argument(
        "-a", "--arch",
        choices=['32', '64'],
        required=True,
        help="Specify the architecture: 32 for 32-bit or 64 for 64-bit."
    )
    args = parser.parse_args()

    # The script's location is the anchor for finding the 'deps' directory.
    try:
        script_dir = Path(__file__).parent.resolve()
    except NameError:
        # Fallback for interactive interpreters or frozen apps
        script_dir = Path.cwd()

    deps_dir = script_dir / "deps"
    nasm_path = deps_dir / "nasm.exe"
    link_path = deps_dir / "golink.exe"
    source_path = Path(args.source).resolve()
    dest_path = Path(args.destination).resolve()

    # Ensure the destination directory exists
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Validate that the required tools and source file exist
    if not nasm_path.exists() or not link_path.exists():
        print(f"Error: Could not find 'nasm.exe' or 'link.exe' in {deps_dir}")
        sys.exit(1)

    if not source_path.exists():
        print(f"Error: Source file not found at {source_path}")
        sys.exit(1)

    print(f"Script directory: {script_dir}")
    print(f"Dependencies:     {deps_dir}")
    print(f"Source file:      {source_path}")
    print(f"Destination file: {dest_path}")
    print(f"Architecture:     {args.arch}-bit")
    print("-" * 30)

    escaped_source_path = str(source_path).replace("\\", "\\\\")

    asm_template = f"""
bits {args.arch}
section .text readable executable
global _start
_start:
incbin "{escaped_source_path}"
"""

    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".asm", delete=False) as f:       
            temp_asm_path = Path(f.name)
            f.write(asm_template)
        print(f"Generated temporary assembly file: {temp_asm_path}")

        with tempfile.NamedTemporaryFile(mode="wb", suffix=".obj", delete=False) as f:
            temp_obj_path = Path(f.name)

        # --- Assemble and Link ---
        # Define commands based on architecture
        nasm_format = "win32" if args.arch == '32' else "win64"
        nasm_cmd = [
            str(nasm_path),
            "-f", nasm_format,
            str(temp_asm_path),
            "-o", str(temp_obj_path)
        ]

        link_cmd_base = [
            str(link_path),
            "/ni",
            "/fo", f"{dest_path}",
            "/entry", "_start",
            str(temp_obj_path),
        ]
        # Add machine type for 64-bit linking
        #if args.arch == '64':
        #    link_cmd_base.append("/MACHINE:X64")

        # Execute NASM
        print(f"\nRunning NASM...\n> {' '.join(nasm_cmd)}")
        subprocess.run(nasm_cmd, check=True, capture_output=True, text=True)

        # Execute LINK
        print(f"\nRunning LINK...\n> {' '.join(link_cmd_base)}")
        subprocess.run(link_cmd_base, check=True, capture_output=True, text=True)

        print(f"\n✅ Success! PE file created at: {dest_path}")

    except subprocess.CalledProcessError as e:
        print("\n❌ Error during build process:")
        print(f"Command: {' '.join(e.cmd)}")
        print(f"Return Code: {e.returncode}")
        print(f"--- STDOUT ---\n{e.stdout}")
        print(f"--- STDERR ---\n{e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)
    finally:
        # Clean up the temporary .asm and .obj files
        print("\nCleaning up temporary files...")
        if temp_asm_path.exists():
            temp_asm_path.unlink()
            print(f"Removed {temp_asm_path}")
        if temp_obj_path.exists():
            temp_obj_path.unlink()
            print(f"Removed {temp_obj_path}")

if __name__ == "__main__":
    main()
