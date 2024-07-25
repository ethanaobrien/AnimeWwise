import os
import io
import tempfile
import wavescan
import subprocess
from mapper import Mapper
from allocator import Allocator
from filereader import FileReader

cwd = os.getcwd()
path = lambda base, path: os.path.join(base, path)
call = lambda args: subprocess.call(args, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

class WwiseExtract:
	def __init__(self):
		self.allocator = Allocator()
		self.hdiff_dir = None

	### loading files ###

	def load_folder(self, _map, folder_path, diff_path):
		self.mapper = None
		if _map is not None:
			self.mapper = Mapper(path(cwd, f"maps/{_map}"))
		self.file_structure = {"folders": {}, "files": []}

		files = [f for f in os.listdir(folder_path) if f.endswith(".pck")]
		hdiff_files = [f for f in os.listdir(diff_path) if f.endswith(".pck.hdiff")]

		if len(files) == 0:
			return None

		for file in files:
			hdiff = None
			if f"{file}.hdiff" in hdiff_files:
				hdiff = path(diff_path, hdiff_files[hdiff_files.index(f"{file}.hdiff")])
			self.load_file(path(folder_path, file), hdiff)

		return self.file_structure

	def load_file(self, _input, hdiff):
		with open(_input, "rb") as f:
			data = f.read()
			f.close()
		self.get_wems(data, os.path.basename(_input), hdiff)

	def get_wems(self, data, filename, hdiff):
		reader = FileReader(io.BytesIO(data), "little")
		files = wavescan.get_data(reader)
		if hdiff is not None:
			with open(hdiff, "rb") as f:
				hdiff_data = f.read()
				f.close()
			hdiff_files = self.get_hdiff_files(data, hdiff_data, filename)
			files = self.compare_diff(files, hdiff_files)

		self.map_names(files, filename, hdiff is not None)

	def compare_diff(self, old, new):
		old_dict = {file[0]:file[2] for file in old}
		new_files = [file for file in new if file not in list(old_dict.keys())]
		changed_files = [file for file in new if file in list(old_dict.keys()) and file[2] != old_dict[file[0]]]

		return [new_files, changed_files]

	def get_hdiff_files(self, data, hdiff_data, source_name):
		working_dir = tempfile.TemporaryDirectory()
		self.hdiff_dir = tempfile.TemporaryDirectory()

		with open(path(working_dir.name, "source.pck"), "wb") as f:
			f.write(data)
			f.close()

		with open(path(working_dir.name, "patch.pck.hdiff"), "wb") as f:
			f.write(hdiff_data)
			f.close()

		args = [
			path(cwd, "tools/hpatchz/hpatchz.exe"),
			"-f",
			path(working_dir.name, "source.pck"),
			path(working_dir.name, "patch.pck.hdiff"),
			path(working_dir.name, "patch.pck")
		]

		call(args)

		with open(path(working_dir.name, "patch.pck"), "rb") as f:
			data = f.read()
			f.close()

		with open(path(self.hdiff_dir.name, source_name), "wb") as f:
			f.write(data)
			f.close()

		reader = FileReader(io.BytesIO(data), "little")
		files = wavescan.get_data(reader)

		working_dir.cleanup()

		return files
	
	def map_names(self, files, filename, hdiff=False):
		mapper = self.mapper
		base = self.file_structure

		if hdiff:
			old_files = files
			filename = f"{filename} (hdiff)"
			files = [*files[0], *files[1]]

		for file in files:
			if mapper is not None:
				key = mapper.get_key(file[0].split(".")[0])
			else:
				key = None

			if key is not None:
				if hdiff:
					if file in old_files[0]:
						key[0] = f"new_files\\{key[0]}"
					else:
						key[0] = f"changed_files\\{key[0]}"
				self.add_to_structure(f"{filename}\\{key[0]}.wem".split("\\"), [file[1], file[2]])
			else:
				temp = base["folders"]
				if filename not in temp:
					temp[filename] = {"folders": {}, "files": []}
				temp = temp[filename]["folders"]
				
				if hdiff:
					if file in old_files[0]:
						if "new_files" not in temp:
							temp["new_files"] = {"folders": {}, "files": []}
						temp = temp["new_files"]["folders"]

					if file in old_files[1]:
						if "changed_files" not in temp:
							temp["changed_files"] = {"folders": {}, "files": []}
						temp = temp["changed_files"]["folders"]

				if "unmapped" not in temp:
					temp["unmapped"] = {"folders": {}, "files": []}
				temp["unmapped"]["files"].append(file)

		self.file_structure = base

	def add_to_structure(self, parts, meta):
		current_level = self.file_structure
		for part in parts[:-1]:
			if "folders" not in current_level:
				current_level["folders"] = {}
			if part not in current_level["folders"]:
				current_level["folders"][part] = {"folders": {}, "files": []}
			current_level = current_level["folders"][part]
		if "files" not in current_level:
			current_level["files"] = []
		current_level["files"].append([parts[-1], meta[0], meta[1]])

	### extracting files ###

	def extract_files(self, _input, files, output, _format, progress):
		temp_dir = tempfile.TemporaryDirectory()
		self.progress = progress
		self.steps = {
			"wem": 1,
			"wav": 2,
			"mp3": 3,
			"ogg": 3
		}[_format]

		# wem
		if _format == "wem":
			output_folder = output
		else:
			output_folder = path(temp_dir.name, "wem")

		self.extract_wem(_input, files, output_folder)

		if _format == "wem":
			temp_dir.cleanup()
			return

		# wav
		new_input = output_folder
		files = [path("/".join(file["path"]), file["name"]) for file in files]

		if _format == "wav":
			output_folder = output
		else:
			output_folder = path(temp_dir.name, "wav")

		self.extract_wav(new_input, files, output_folder)

		if _format == "wav":
			temp_dir.cleanup()
			return

		# mp3 & ogg
		files = [path(os.path.dirname(file), f'{os.path.basename(file).split(".")[0]}.wav') for file in files]
		new_input = output_folder
		output_folder = output

		self.extract_ffmpeg(new_input, files, output_folder, _format)

		temp_dir.cleanup()
		return

	def extract_wem(self, _input, files, output):
		print(": Extracting audio as wem")
		all_sources = list(set([e["source"] for e in files]))

		for source in all_sources:
			load_path = path(_input, source)
			if self.hdiff_dir is not None:
				source = source.split(" (hdiff)")[0]
				hdiff_path = path(self.hdiff_dir.name, source)
				
				if os.path.isfile(hdiff_path):
					load_path = hdiff_path
			
			self.allocator.load_file(load_path)

		pos = 0
		for file in files:
			pos += 1
			self.update_progress(pos, len(files), 1)

			file["source"] = file["source"].split(" (hdiff)")[0]
			data = self.allocator.read_at(file["source"], file["offset"], file["size"])
			
			filepath = path("/".join(file["path"]), file["name"])
			fullpath = path(output, filepath)
			os.makedirs(os.path.dirname(fullpath), exist_ok=True)
			
			with open(fullpath, "wb") as f:
				f.write(data)
				f.close()

		self.allocator.free_mem()

	def extract_wav(self, _input, files, output):
		print(": Converting audio to wav")
		pos = 0
		for file in files:
			pos += 1
			self.update_progress(pos, len(files), 2)

			filename = f'{os.path.basename(file).split(".")[0]}.wav'
			filepath = path(output, os.path.dirname(file), filename)
			os.makedirs(os.path.dirname(filepath), exist_ok=True)

			args = [
				path(cwd, "tools/vgmstream/vgmstream-cli.exe"),
				"-o",
				filepath,
				path(_input, file)
			]

			call(args)

	def extract_ffmpeg(self, _input, files, output, _format):
		print(f": Converting audio to {_format}")

		encoders = {
			"mp3": "libmp3lame",
			"ogg": "libvorbis"
		}
		
		encoder = encoders[_format]

		pos = 0
		for file in files:
			pos += 1
			self.update_progress(pos, len(files), 3)

			filename = f'{os.path.basename(file).split(".")[0]}.{_format}'
			filepath = path(output, os.path.dirname(file), filename)
			os.makedirs(os.path.dirname(filepath), exist_ok=True)

			args = [
				path(cwd, "tools/ffmpeg/ffmpeg.exe"),
				"-i",
				path(_input, file),
				"-acodec",
				encoder,
				"-b:a",
				"192k", # 192|4
				filepath
			]

			call(args)
		
	### other ###

	def update_progress(self, current, total, step):
		base = 100 / self.steps
		self.progress(["total", current * base // total + base * (step - 1)])
		self.progress(["file", current * 100 // total])

	def reset(self):
		if self.mapper is not None:
			self.mapper.reset()
		self.allocator.free_mem()
		self.hdiff_dir.cleanup()
		self.hdiff_dir = None
