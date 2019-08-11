import os, random, string
from slidenotes import gs

class SlideConvert:

    def __init__(self, progress):
        self.external_progress_obj = progress

    def progress(self, line):
        try:
            stage_percentage = int(line)
            self.external_progress_obj.progress(int((stage_percentage / float(self.total_stages)) + ((self.current_stage - 1) * 100 / float(self.total_stages)) + 0.5))
        except ValueError:
            pass

    def convert(self, input_path, original_layout, options, cache=True):

        options = options.copy()

        options_str = "_" + "_".join(("{}_{}".format(*i) for i in sorted(original_layout.items()))) + "_".join(("{}_{}".format(*i) for i in sorted(options.items())))
        safe_output_path = input_path + ".safe.pdf"
        boxes_output_path = input_path + options_str + ".boxes.ps"
        imposed_output_path = input_path + options_str + ".imposed.pdf"
        random_str = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(10))

        if os.path.isfile(imposed_output_path) and cache:
            self.external_progress_obj.progress(100)
            return imposed_output_path

        generate_safe = True if not os.path.isfile(safe_output_path) or not cache else False
        generate_boxes = False

        if (original_layout["slides"] == 1 and options["trim"] == True) or original_layout["slides"] > 1:
            if os.path.isfile(boxes_output_path) and cache:
                options["boxes"] = {"nperpage": str(original_layout["slides"]), "boxesfilepath": boxes_output_path}
            else:
                generate_boxes = True
                options["boxes"] = {"nperpage": str(original_layout["slides"]), "boxesfilepath": boxes_output_path + random_str}

        self.current_stage = 1
        self.total_stages = (1 if generate_safe else 0) + (1 if generate_boxes else 0) + 1

        self.external_progress_obj.progress(0)

        if generate_safe:
            gs.generate_safe_pdf(input_path, safe_output_path + random_str, self)
            self.current_stage = self.current_stage + 1

        if generate_boxes:
            gs.generate_boxes(safe_output_path + random_str if generate_safe else safe_output_path, {"slides": original_layout["slides"], "trim": original_layout["trim"], "whitespacetrim": options["trim"]}, boxes_output_path + random_str, self)
            self.current_stage = self.current_stage + 1

        gs.generate_imposed_pdf(safe_output_path + random_str if generate_safe else safe_output_path, imposed_output_path + random_str, options, self)

        if generate_safe:
            os.rename(safe_output_path + random_str, safe_output_path)
        if generate_boxes:
            os.rename(boxes_output_path + random_str, boxes_output_path)
        os.rename(imposed_output_path + random_str, imposed_output_path)

        return imposed_output_path
