import csv
import os
import datetime


class create_file:
    def folder(self, Driver_root, start_time):
        if not os.path.exists(Driver_root + start_time):
            os.makedirs(Driver_root + "/" + start_time)
            self.path = Driver_root + "/" + start_time + "/"
            return self.path

    def folder_IMP(self, step):
        if not os.path.exists(self.path + str(step[0])):
            os.makedirs(self.path + "/" + str(step[0]))
            self.step_path = self.path + "/" + str(step[0]) + "/"
            return self.step_path
        else:
            return self.path + "/" + str(step[0])  + "/"  

    def step_folder(self, sample_name):
        if not os.path.exists(self.step_path + sample_name):
            os.makedirs(self.step_path + sample_name)
            self.sample_path = self.step_path + sample_name + "/"
            return self.sample_path
        else:
            return self.step_path + sample_name + "/"

    def sample_folder(self, sample_name):
        if not os.path.exists(self.path + sample_name):
            os.makedirs(self.path + sample_name)
            self.sample_path = self.path + sample_name + "/"
            return self.sample_path
        else:
            return self.path + sample_name + "/"

    def header(self, path, filename, start_time, equipment_Info, test_mode, num_sample):
        header = []
        header.append(('#############################################################', ' '))
        header.append(('#Test results', ' '))
        header.append(('#############################################################', ' '))
        header.append(('#Test mode........:', test_mode))
        header.append(('#Equipment........:', equipment_Info))
        header.append(('#Number of samples:', num_sample))
        header.append(('#File.............:', filename))
        header.append(('#Date/Time........:', start_time))
        header.append(('#############################################################', ' '))
        with open(path + filename + ".txt", "a") as op:
            write = csv.writer(op, delimiter='\t', lineterminator='\n')
            write.writerows(header)

        for i in range(int(num_sample)):
            name = 'Sample' + str(i)
            locals()['v' + str(i)] = i
            op = open(path + name + ".txt", "a")

    def header_LCR(self, path, filename, start_time, equipment_Info, test_mode, num_sample, voltage, frequency):
        header = []
        header.append(('#############################################################', ' '))
        header.append(('#Test results', ' '))
        header.append(('#############################################################', ' '))
        header.append(('#Test mode........:', test_mode))
        header.append(('#Equipment........:', equipment_Info))
        header.append(('#Number of samples:', num_sample))
        header.append(('#Set Voltage:', voltage))
        header.append(('#Set Frequency:', frequency))
        header.append(('#File.............:', filename))
        header.append(('#Date/Time........:', start_time))
        header.append(('#############################################################', ' '))
        with open(path + filename + ".txt", "a") as op:
            write = csv.writer(op, delimiter='\t', lineterminator='\n')
            write.writerows(header)

        for i in range(int(num_sample)):
            name = 'Sample' + str(i)
            locals()['v' + str(i)] = i
            op = open(path + name + ".txt", "a")

    def header_sm(self, file_path, filename, start_time, equipment_Info, test_mode, num_sample, V_start, V_end, V_step, temperature):
        header = []
        header.append(('#############################################################', ' '))
        header.append(('#Test results', ' '))
        header.append(('#############################################################', ' '))
        header.append(('#Test mode........:', test_mode))
        header.append(('#Equipment........:', equipment_Info))
        header.append(('#Number of samples:', num_sample))
        header.append(('#Start voltage:', V_start))
        header.append(('#End voltage:', V_end))
        header.append(('#Voltage step:', V_step))
        header.append(('#Temperature:', temperature))
        header.append(('#File.............:', filename))
        header.append(('#Date/Time........:', start_time))
        header.append(('#############################################################', ' '))
        header.append(('Voltage(V)', 'Current(A)', 'measuresedResistance(Ohms)', 'calculatedResistance(Ohms)'))
        with open(file_path + filename + ".txt", "a") as op:
            write = csv.writer(op, delimiter='\t', lineterminator='\n')
            write.writerows(header)

    def header_imp(self, file_path, filename, start_time, equipment_Info, test_mode, F_start, F_end, V_set):
        header = []
        header.append(('#############################################################', ' '))
        header.append(('#Test results', ' '))
        header.append(('#############################################################', ' '))
        header.append(('#Test mode........:', test_mode))
        header.append(('#Equipment........:', equipment_Info))
        header.append(('#Start Frequency:', F_start))
        header.append(('#End Frequency:', F_end))
        header.append(('#Osilation:', V_set))
        header.append(('#File.............:', filename))
        header.append(('#Date/Time........:', start_time))
        header.append(('#############################################################', ' '))
        header.append(('Frequency(Hz)', 'R(Ohms)', 'X(Ohms)'))
        with open(file_path + filename + ".txt", "a") as op:
            write = csv.writer(op, delimiter='\t', lineterminator='\n')
            write.writerows(header)

    def content(self, file_path, filename, content):
        # val = []
        with open(file_path + filename + ".txt", "a") as op_file:
            saveData = csv.writer(op_file, delimiter="\t", lineterminator="\n")
            # val.append(content)
            saveData.writerows(content)

    def main(self):
        current_time = str(datetime.datetime.now())
        time_str = current_time.replace(" ", "_").replace(".", "-").replace(":", "-")
        cf = create_file()
        path = cf.folder("D:/", time_str)
        for step in ([60, 20], [60, 30], [60, 40], [60, 50], [60, 60], [60, 70]):
            cf.folder_IMP(step)
            for i in [0, 1, 2, 3, 4, 5, 6, 7]:
                name = 'Sample' + str(i)
                locals()['v' + str(i)] = i
                PA = cf.sample_folder(name)
                cf.header_sm(time_str, time_str, "Alienware", "Auto", "8", -40, 40, 0.1, 1, 20)
                #cf.content(step_path, time_str, str(number)+"\n")
                cf.content(PA, time_str , str(i))


if __name__ == "__main__":
    cf = create_file()
    cf.main()
