import os, subprocess

GS_PATH = "/usr/bin/gs"

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

class NonZeroExitCode(Exception):
    pass

def default_internal_progress(line, internal_progress_extra, external_progress):
    external_progress.progress(line)

def get_bounding_boxes_progress(line, internal_progress_extra, external_progress):
    if "%%HiResBoundingBox" in str(line):
        bbox = line.decode("utf-8")[:-1].split(" ")
        internal_progress_extra["boxes"] += "[" + bbox[1] + " " + bbox[2] + " " + bbox[3] + " " + bbox[4] + "]"
    external_progress.progress(line)

def run(args, external_progress, internal_progress=default_internal_progress, internal_progress_extra=None):
    p = subprocess.Popen([GS_PATH] + ["-sstdout=%stderr"] + args, stderr=subprocess.PIPE, cwd=DIR_PATH)
    output = ""
    while True:
        line = p.stderr.readline()
        if not line:
            break
        internal_progress(line, internal_progress_extra, external_progress)
        output += line.decode("utf-8")
    if p.wait() != 0:
        raise NonZeroExitCode(output)

def generate_safe_pdf(input_path, output_path, progress):
    args = [
        "-dNOPAUSE", "-dBATCH", "-dSAFER",
        "-sDEVICE=pdfwrite",
        "-sOutputFile=" + output_path,
        "-c", "<< /EndPage { 0 eq {/Page# where {Page# pdfpagecount div 100 mul cvi == flush}if true}{false}ifelse } >> setpagedevice",
        "-f", input_path
    ]
    run(args, progress)

def generate_bounding_boxes(input_path, layout_id, output_path, progress):
    output_file = open(output_path, "w")

    args = [
        "-dNOPAUSE", "-dBATCH",
        "-sDEVICE=bbox",
        "-r300"
    ]

    layouts = {
        1: ["-c", "<< /EndPage { 0 eq {/Page# where {Page# pdfpagecount div 100 mul cvi == flush}if true}{false}ifelse } >> setpagedevice",
            "-f" + input_path],
        2: ["-sFile=" + input_path,
            "-f", "slidenotes_cut_in_half.ps"]
    }
    args += layouts[layout_id]

    extra = {"boxes": "/Boxes ["}
    run(args, progress, get_bounding_boxes_progress, extra)
    extra["boxes"] += "] def"

    output_file.write(extra["boxes"])
    output_file.close()

def generate_imposed_pdf(input_path, output_path, options, progress):
    args = [
        "-dNOPAUSE", "-dBATCH",
        "-sDEVICE=pdfwrite", "-sFile=" + input_path, "-sOutputFile=" + output_path
    ]
    if "npage" in options:
        args += ["-dNPage=" + str(options["npage"])]
    if "boxes" in options:
        args += ["-dNBoxesPerPage=" + str(options["boxes"]["nperpage"]), "-sBoxes=" + options["boxes"]["boxesfilepath"]]
    if "percentage" in options:
        args += ["-dDesiredFreeSpacePercentage=" + str(options["percentage"])]
    args += ["slidenotes_impose.ps"]
    run(args, progress)
