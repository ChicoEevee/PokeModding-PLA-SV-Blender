if __name__ == "__main__":
    import os, sys, json, argparse

    parser = argparse.ArgumentParser(description="TRMSH Appender")
    append_file_action = parser.add_argument(
        "-a", "--append", help="Append to an existing mesh."
    )

    append_file_action = parser.add_argument(
        "-b", "--buffer", help="Path to the buffer file."
    )

    parser.add_argument("folder", help="The folder containing the meshes.")
    parser.add_argument("outfile", help="The path to the resulting json output.")

    args = parser.parse_args()

    if args.append:
        infile = open(args.append, "rb")
        buf = json.loads(infile.read())
        infile.close()
    else:
        buf = {"unk0": 0, "meshes": [], "buffer_name": ""}

    if args.buffer:
        buf["buffer_name"] = args.buffer

    files = os.listdir(args.folder)

    for filename in files:
        if ".trmsh.json" in filename:
            infile = open(os.path.join(args.folder, filename), "rb")
            mesh = json.loads(infile.read())
            infile.close()

            buf["meshes"].append(mesh)

    outfile = open(args.outfile, "w")
    outfile.write(json.dumps(buf, indent=4))
    outfile.close()