# -*- coding: utf-8 -*-
# noinspection PyPackageRequirements
from P4 import P4, P4Exception
import yaml


# noinspection DuplicatedCode
class P4Util(object):

    def __init__(self, port, user, logging):
        self.port = port
        self.user = user
        self.client = None
        self.changelist = 0
        self.logging = logging
        self.stream_path = None
        self.root_path = None
        self.opened_files = []
        self.opened_files_sha1 = None
        self.shelved_files = []

        self.p4 = P4()
        self.p4.port = self.port
        self.p4.user = self.user
        self.p4.client = self.client
        self.p4.encoding = "utf8"

    def __del__(self):
        try:
            self.p4.disconnect()
        except P4Exception:
            for e in self.p4.errors:
                self.logging.error("[P4 ERROR] " + e)
            for w in self.p4.warnings:
                self.logging.warning("[P4 WARN] " + w)
        del self.p4

    def _run_p4_with_log(self, cmd):
        try:
            result = self.p4.run(cmd)
            return result
        except P4Exception as ex:
            for e in self.p4.errors:
                self.logging.error("[P4 ERROR] " + e)
            for w in self.p4.warnings:
                self.logging.warning("[P4 WARN] " + w)
            if len(self.p4.errors) > 0:
                raise ex
            return None

    def connect(self):
        try:
            self.p4.connect()
        except P4Exception:
            for e in self.p4.errors:
                self.logging.error("[P4 ERROR] " + e)
            for w in self.p4.warnings:
                self.logging.warning("[P4 WARN] " + w)
            return False
        return True

    # valid whether changelist belong to current client
    def valid_user_and_workspace(self):
        if self.changelist == "default" or self.changelist is None:
            return True

        try:
            result = self.p4.run(["describe", "-s", self.changelist])
            if result[0]['user'] != self.user or result[0]['client'] != self.client:
                return False
        except P4Exception:
            for e in self.p4.errors:
                self.logging.error("[P4 ERROR] " + e)
            for w in self.p4.warnings:
                self.logging.warning("[P4 WARN] " + w)
            return False

        return True

    def get_stream_path(self):
        result = self.p4.run(["client", "-o"])
        self.stream_path = result[0]['Stream']
        return self.stream_path

    def get_root_path(self):
        result = self.p4.run(["client", "-o"])
        self.root_path = result[0]['Root']
        return self.root_path

    def get_latest(self, path):
        self._run_p4_with_log(["sync", path])

    def get_opened_files(self):
        def get_sort_item(elem):
            return elem['depotFile']

        result = self.p4.run(["opened", "-c", self.changelist])
        result.sort(key=get_sort_item)
        self.opened_files = result
        from hashlib import sha1
        s = ""
        for opened_file in self.opened_files:
            s = s + opened_file['depotFile']
        self.opened_files_sha1 = sha1(s.encode('utf-8')).hexdigest()

        return result

    def check_opened_files_change(self):
        def get_sort_item(elem):
            return elem['depotFile']

        opened_files = self.p4.run(["opened", "-c", self.changelist])
        opened_files.sort(key=get_sort_item)
        from hashlib import sha1
        s = ""
        for opened_file in opened_files:
            s = s + opened_file['depotFile']
        opened_files_sha1 = sha1(s.encode('utf-8')).hexdigest()

        return opened_files_sha1 != self.opened_files_sha1

    def move_opened_files_to_new_changelist(self):
        result = self.p4.save_change({'Change': 'new', "Description": ""})
        self.changelist = result[0].split()[1]
        for opened_file in self.opened_files:
            self.p4.run(["reopen", "-c", self.changelist, opened_file["depotFile"]])

    def move_files_to_new_changelist(self, selected_files):
        result = self.p4.save_change({'Change': 'new', "Description": ""})
        self.changelist = result[0].split()[1]
        for selected_file in selected_files:
            try:
                self.p4.run(["reopen", "-c", self.changelist, selected_file])
            except P4Exception:
                # ignore the files not in workspace.
                pass

    def get_shelved_files(self):
        result = self.p4.run(["describe", "-S", self.changelist])
        if "depotFile" in result[0]:
            self.shelved_files = result[0]["depotFile"]
        else:
            self.shelved_files = []

    def revert_unchanged_files(self):
        try:
            self.reverted_unchanged_files = []
            # do NOT revert unchanged when there is a branch file.
            for file in self.opened_files:
                if file["action"].find("branch") != -1:
                    return
            has_edit_or_add_file = False
            for file in self.opened_files:
                if file["action"].find("edit") != -1 or file["action"].find("add") != -1:
                    has_edit_or_add_file = True
                    break
            if has_edit_or_add_file:
                result = self.p4.run(["revert", "-a", "-c", self.changelist])
                for r in result:
                    if isinstance(r, dict):
                        self.reverted_unchanged_files.append(r)
        except P4Exception as ex:
            self.logging.error(ex)

    def edit_files(self, file_info_list):
        for file_info in file_info_list:
            self.p4.run(["edit", "-c", self.changelist, file_info["depotFile"]])

    def list_file(self, filepath):
        try:
            result = self.p4.run(["files", "-i", "-m", "1", filepath])
            return result[0]
        except P4Exception:
            return None

    def list_first_file(self, path):
        try:
            result = self.p4.run(["files", "-i", "-m", "1", path + "/..."])
            return result[0]
        except P4Exception:
            return None

    def get_local_path(self, path):
        result = self.p4.run(["where", path])
        return result[0]["path"]

    def is_in_depot(self, path):
        try:
            result = self.p4.run(["files", path])
            return "delete" not in result[0]["action"]
        except P4Exception:
            return False

    def shelve_changelist(self, changelist):
        shelved_files = []
        results = self._run_p4_with_log(["shelve", "-f", "-Af", "-c", changelist])
        for result in results:
            if isinstance(result, dict):
                shelved_files.append(result)
        return shelved_files

    def revert_changelist(self, changelist):
        return self._run_p4_with_log(["revert", "-w", "-c", changelist, "//..."])

    def unshelve_changelist(self, changelist):
        return self._run_p4_with_log(["unshelve", "-s", changelist, "-f", "-Af", "-c", changelist])

    def delete_shelved_changelist(self, changelist):
        return self._run_p4_with_log(["shelve", "-d", "-Af", "-c", changelist])

    def get_jobs(self, max_jobs, expr):
        try:
            result = self.p4.run(["jobs", "-m", str(max_jobs), "-e", expr])
            return result
        except P4Exception as ex:
            self.logging.error(ex)
            return []

    def get_description(self, desc_dict):
        try:
            result = self.p4.run(["change", "-o", self.changelist])
            desc = result[0]["Description"]
            origin_desc = desc

            if "Jobs" in result[0]:
                job = result[0]["Jobs"][0]
                desc_dict["Job"] = job
            # if description is already format
            use_base64_desc = "[Desc]" in desc
            if use_base64_desc:
                start_index = desc.find("[Desc]")
                end_index = desc.find("[", start_index + 1)
                if end_index == -1:
                    end_index = len(desc)
                origin_description = desc[start_index:end_index]
                desc_dict["Desc"] = origin_description.replace("[Desc]", "").strip()
                desc = desc[:start_index] + desc[end_index:]
                desc = desc.replace("[", "").replace("]", ":")
            parse_result, yaml_desc_dict = self.parse_description_to_yaml(desc)
            if parse_result:
                for key in desc_dict:
                    if key in yaml_desc_dict:
                        desc_dict[key] = yaml_desc_dict[key]
                return True
            elif use_base64_desc and desc_dict["Desc"] != "":
                return True
            else:
                desc_dict["Desc"] = origin_desc
                return True
        except P4Exception as ex:
            self.logging.error(ex)
            return False
        except yaml.YAMLError as ex:
            self.logging.error(ex)
            return False

    def set_description(self, desc_dict, filter_options=None):
        if not self.changelist.isnumeric():
            return False
        desc = ""
        for key in desc_dict:
            raw_key = key
            if key.startswith("[") and key.endswith("]"):
                raw_key = key[1:-1]
            if filter_options is not None:
                if key in filter_options:
                    desc += "[{}] {}\r\n".format(raw_key, desc_dict[key])
            else:
                desc += "[{}] {}\r\n".format(raw_key, desc_dict[key])
        result = self.p4.run(["change", "-o", self.changelist])
        result[0]["Description"] = desc
        self.p4.input = result[0]
        return self.p4.run(["change", "-i"])

    def submit(self, is_keep_check_out):
        if not self.changelist.isnumeric():
            return None
        try:
            if is_keep_check_out:
                submit_result = self.p4.run(["submit", "-r", "-c", self.changelist])
            else:
                submit_result = self.p4.run(["submit", "-c", self.changelist])
            return submit_result
        except P4Exception as ex:
            for e in self.p4.errors:
                self.logging.error("[P4 ERROR] " + e)
            for w in self.p4.warnings:
                self.logging.warning("[P4 WARN] " + w)
            if len(self.p4.errors) > 0:
                raise ex
            return None

    def remove_options_from_description(self, submitted_change_number, remove_options):
        if not self.changelist.isnumeric():
            return False

        result = self.p4.run(["change", "-o", submitted_change_number])
        prev_desc = result[0]["Description"]
        cur_desc = ""
        for remove_key in remove_options:
            real_key = "[{}]".format(remove_key)
            if remove_key in prev_desc and real_key in prev_desc:
                start_index = prev_desc.find(real_key)
                end_index = prev_desc.find("[", start_index + 1)
                if end_index < 0:
                    end_index = len(prev_desc)
                cur_desc = prev_desc[:start_index] + prev_desc[end_index:]
        result[0]["Description"] = cur_desc
        self.p4.input = result[0]
        return self._run_p4_with_log(["change", "-i", "-u"])  # -u is used for submitted changelist

    @staticmethod
    def parse_description_to_yaml(desc):
        try:
            desc_dict = yaml.load(desc, Loader=yaml.FullLoader)
            if isinstance(desc_dict, dict) and desc_dict is not None:
                return True, desc_dict
            return False, None
        except yaml.YAMLError:
            return False, None

    def add_job_to_changelist(self, job_name):
        try:
            result = self.p4.run(["change", "-o", self.changelist])[0]
            result["Jobs"] = job_name
            self.p4.input = result
            self.p4.run(["change", "-i"])
        except P4Exception as ex:
            self.logging.info(ex)

    def get_file_changelist(self, filepath):
        try:
            result = self.p4.run(["opened", filepath])
            return result[0]['change']
        except P4Exception as ex:
            # pass all file which can not where.
            return None

    def move_file_to_changelist(self, changelist, filepath):
        try:
            self.p4.run(["reopen", "-c", changelist, filepath])
        except P4Exception:
            # ignore the files not in workspace.
            pass

    def remove_empty_changelist(self, changelist):
        try:
            self.p4.run(["change", "-d", changelist])
        except P4Exception as ex:
            self.logging.info(ex)

    def get_local_have_changelist(self, depot_path):
        try:
            self.p4.run(["changes", "-m1", "{}#have".format(depot_path)])
        except P4Exception as ex:
            self.logging.info(ex)

    def get_server_head_changelist(self, depot_path):
        try:
            self.p4.run(["changes", "-m1", "{}#head".format(depot_path)])
        except P4Exception as ex:
            self.logging.info(ex)
