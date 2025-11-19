from neuro.utils import internal_utils


process_list = internal_utils.get_process("name", "nw")

if process_list:
    for process in process_list:
        process.kill()
