if __name__ == "__main__":
    import os, sys, json, argparse

    parser = argparse.ArgumentParser(description="TRMBF Appender")

    append_file_action = parser.add_argument(
        "-a", "--append", help="Append to an existing buffer."
    )

    parser.add_argument("folder", help="The folder containing the buffers.")
    parser.add_argument("outfile", help="The path to the resulting json output.")

    args = parser.parse_args()

    if args.append:
        infile = open(args.append, "rb")
        buf = json.loads(infile.read())
        infile.close()
    else:
        buf = {"unused": 0, "buffers": []}

    files = os.listdir(args.folder)

    for filename in files:
        if ".trmbf.json" in filename:
            infile = open(os.path.join(args.folder, filename), "rb")
            new_data = json.loads(infile.read())
            infile.close()

            new_buffer = {"index_buffer": [{"buffer": []}], "vertex_buffer": [{"buffer": []}]}

            new_buffer["index_buffer"][0]["buffer"].extend(new_data["index_buffer"])
            new_buffer["vertex_buffer"][0]["buffer"].extend(new_data["vertex_buffer"])

            buf["buffers"].append(new_buffer)

    outfile = open(args.outfile, "w")
    outfile.write(json.dumps(buf, indent=4))
    outfile.close()
