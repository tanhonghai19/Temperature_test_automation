from time import sleep
import datetime
import os
import write_display
import VT_DMM_Auto
import VT_DMM_Manual
import TTC_DMM_Auto
import TTC_DMM_Manual
import VT_SM_Auto
import VT_SM_Manual
import TTC_SM_Auto
import TTC_SM_Manual
import VT_LCR_Auto
import VT_LCR_Manual
import TTC_LCR_Auto
import TTC_LCR_Manual
import TTC_IMP_Auto
import TTC_IMP_Manual
import VT_IMP_Auto
import VT_IMP_Manual
import RelayMode
import Oven_TTC_auto
import Oven_TTC_manual
import Oven_VT_auto
import Oven_VT_manual
from TempProfile import readTempProfile
import detect_file

NX_SERIAL_PORT = "/dev/ttyUSB0"
DIS = write_display.Nextion(NX_SERIAL_PORT)
folder = "/media/pi/"

command_sample = 'get n123.val\xff\xff\xff'  # sample number

# multimeter parameter
command_dmm_temp = 'get n567.val\xff\xff\xff'  # set temperature

# source meter parameter
command_sm_AV = 'get n3.val\xff\xff\xff'  # set temperature
command_sm_MT = 'get n345.val\xff\xff\xff'  # set temperature
command_sm_startV = 'get n10.val\xff\xff\xff'  # start voltage
command_sm_endV = 'get n11.val\xff\xff\xff'  # end voltage

# LCR parameter
command_lcr_temp = 'get n234.val\xff\xff\xff'  # set temperature
command_lcr_setAV = 'get n1.val\xff\xff\xff'  # auto mode set voltage
command_lcr_setAF = 'get n5.val\xff\xff\xff'  # auto mode set frequency
command_lcr_setMV = 'get n4.val\xff\xff\xff'  # manual mode set voltage
command_lcr_setMF = 'get n0.val\xff\xff\xff'  # manual mode set frequency

# IMP parameter
command_imp_temp = 'get n456.val\xff\xff\xff'  # set temperature
command_imp_startAF = 'get n27.val\xff\xff\xff'  # auto mode start frequency
command_imp_endAF = 'get n25.val\xff\xff\xff'  # auto mode end frequency
command_imp_setAV = 'get n26.val\xff\xff\xff'  # auto mode set voltage
command_imp_setMV = 'get n20.val\xff\xff\xff'  # manual mode set voltage
command_imp_startMF = 'get n21.val\xff\xff\xff'  # manual mode start frequency
command_imp_endMF = 'get n24.val\xff\xff\xff'  # manual mode end frequency

# get oven parameter
command_oven_temp = 'get n765.val\xff\xff\xff'  # set temperature

# get relay parameter
command_rel_num = 'get n543.val\xff\xff\xff'  # set temperature
command_rel_interval = 'get n432.val\xff\xff\xff'  # auto mode start frequency


class Device_select:
    # get sample quantity
    def get_sample_number(self):
        self.number_sample = DIS.get_val(command_sample)
        return self.number_sample

    def get_value(self, cmd):
        self.value = DIS.get_val(cmd)
        return self.value

    # get oven mode parameter
    def get_ovenInfo(self):
        self.oven_setTemp = self.get_value(command_oven_temp)
        return self.oven_setTemp

    # get relay mode parameter
    def get_relPara(self):
        self.rel_num = self.get_value(command_rel_num)
        self.rel_interval = self.get_value(command_rel_interval)
        return self.rel_num, self.rel_interval

    # get multimeter parameter
    def get_multiPara(self):
        self.dmm_setT = self.get_value(command_dmm_temp)
        return self.dmm_setT

    # get source meter auto mode parameter
    def get_smApara(self):
        self.sm_AV = self.get_value(command_sm_AV)
        return self.sm_AV

    # get source meter manual mode parameter
    def get_smMPara(self):
        self.sm_MT = self.get_value(command_sm_MT)
        self.sm_startV = self.get_value(command_sm_startV)
        self.sm_endV = self.get_value(command_sm_endV)
        return self.sm_MT, self.sm_startV, self.sm_endV

    # get LCR auto mode parameter
    def get_lcrAPara(self):
        self.lcr_AV = self.get_value(command_lcr_setAV)
        self.lcr_AF = self.get_value(command_lcr_setAF)
        return self.lcr_AF, self.lcr_AV

    # get LCR manual mode parameter
    def get_lcrMPara(self):
        self.lcr_MT = self.get_value(command_lcr_temp)
        self.lcr_MV = self.get_value(command_lcr_setMV)
        self.lcr_MF = self.get_value(command_lcr_setMF)
        return self.lcr_MT, self.lcr_MV, self.lcr_MF

    # get IMP auto mode parameter
    def get_IMPApara(self):
        self.imp_AV = self.get_value(command_imp_setAV)
        self.imp_startAF = self.get_value(command_imp_startAF)
        self.imp_endAF = self.get_value(command_imp_endAF)
        return self.imp_AV, self.imp_startAF, self.imp_endAF

    # get IMP manual mode parameter
    def get_IMPMpara(self):
        self.imp_MT = self.get_value(command_imp_temp)
        self.imp_startMF = self.get_value(command_imp_startMF)
        self.imp_endMF = self.get_value(command_imp_endMF)
        self.imp_MV = self.get_value(command_imp_setMV)
        return self.imp_MT, self.imp_startMF, self.imp_MV, self.imp_endMF

    # read temperature profile
    def read_profile(self):
        print("here")
        FILENAME = detect_file.File(folder)[0]
        Profile = str(readTempProfile(FILENAME)[0])
        if len(Profile) >= 200:
            content = Profile[:200]
        else:
            content = Profile
        print(content)
        DIS.write('t0.txt="' + content + '"\xff\xff\xff')

    def updateMultimeter(self, list_val):
        print(list_val)
        DIS.write('t5.txt="' + str(list_val[0]) + '"\xff\xff\xff')  # SET_TEMP
        DIS.write('t2.txt="' + str(list_val[1]) + '"\xff\xff\xff')  # CUR_TEMP
        DIS.write('t3.txt="' + str(list_val[2]) + '"\xff\xff\xff')  # S_TEMP
        DIS.write('t4.txt="' + str(list_val[3]) + '"\xff\xff\xff')  # S_HUMID
        DIS.write('t8.txt="' + str(list_val[4]) + '"\xff\xff\xff')  # t_run

        # update of sample values
        list_blank = [9, 10, 11, 12, 13, 14, 15, 16]
        rv = list_val[5]
        seq = list_blank[list_val[6]]
        cmd_value = 't%d.txt="%s"\xff\xff\xff' % (seq, rv)
        DIS.write(cmd_value)

    def updateSweep(self, list_val):
        print(list_val)
        DIS.write('t5.txt="' + str(list_val[0]) + '"\xff\xff\xff')  # SET_TEMP
        DIS.write('t2.txt="' + str(list_val[1]) + '"\xff\xff\xff')  # CUR_TEMP
        DIS.write('t3.txt="' + str(list_val[2]) + '"\xff\xff\xff')  # S_TEMP
        DIS.write('t4.txt="' + str(list_val[3]) + '"\xff\xff\xff')  # S_HUMID
        DIS.write('t8.txt="' + str(list_val[4]) + '"\xff\xff\xff')  # t_run

        # update of sample values
        list_blank = [9, 10, 11, 12, 13, 14, 15, 16]
        rv = list_val[5]
        last_val = list_val[6]
        seq = list_blank[list_val[7]]
        seq_last = list_blank[list_val[7] - 1]
        cmd_value = 't%d.txt="%s"\xff\xff\xff' % (seq, rv)
        cmd_lastVAL = 't%d.txt="%s"\xff\xff\xff' % (seq_last, last_val)
        DIS.write(cmd_value)
        DIS.write(cmd_lastVAL)

    def updateIMPTemp(self, list_val):
        print(list_val)
        DIS.write('t2.txt="' + str(list_val[0]) + '"\xff\xff\xff')  # SET_TEMP
        DIS.write('t3.txt="' + str(list_val[1]) + '"\xff\xff\xff')  # CUR_TEMP
        DIS.write('t4.txt="' + str(list_val[2]) + '"\xff\xff\xff')  # S_TEMP
        DIS.write('t5.txt="' + str(list_val[3]) + '"\xff\xff\xff')  # S_HUMID
        DIS.write('t8.txt="' + str(list_val[4]) + '"\xff\xff\xff')  # t_run

    def updateRelay(self, list_val):
        print(list_val)
        DIS.write('t2.txt="' + str(list_val[0]) + '"\xff\xff\xff')  # t_run
        DIS.write('t3.txt="' + str(list_val[1]) + '"\xff\xff\xff')  # seq

    def updateOven(self, list_val):
        print(list_val)
        DIS.write('t0.txt="' + str(list_val[1]) + '"\xff\xff\xff')  # SET_TEMP
        DIS.write('t1.txt="' + str(list_val[2]) + '"\xff\xff\xff')  # CUR_TEMP
        DIS.write('t2.txt="' + str(list_val[0]) + '"\xff\xff\xff')  # T_RUN

    def updateIMPStatus(self, list_val):
        # update of sample values
        list_blank = [9, 11, 13, 15, 17, 19, 21, 23]
        rv = list_val[0]
        last_val = list_val[1]
        seq = list_blank[list_val[2]]
        seq_last = list_blank[list_val[2] - 1]
        cmd_value = 't%d.txt="%s"\xff\xff\xff' % (seq, rv)
        cmd_lastVAL = 't%d.txt="%s"\xff\xff\xff' % (seq_last, last_val)
        DIS.write(cmd_value)
        DIS.write(cmd_lastVAL)

    def VT_DMM_Auto(self):
        start_time = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print(start_time)
        FILENAME = detect_file.File(folder)[0]
        total_time = readTempProfile(FILENAME)[1] * 60
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=total_time)
        end_time_formated = str(end_time.strftime("%Y-%m-%d %H:%M:%S"))
        VMA = VT_DMM_Auto.VT4002_DMM_Auto()
        print ("Run VT4002 + DMM196 Auto")
        DIS.write('t0.txt="Auto"\xff\xff\xff')
        DIS.write('t1.txt="VT4002 + DMM196"\xff\xff\xff')
        DIS.write('t6.txt="' + start_time + '"\xff\xff\xff')
        DIS.write('t7.txt="' + end_time_formated + '"\xff\xff\xff')
        VMA.main(self.number_sample, self)

    def VT_DMM_Manual(self):
        start_time = str(datetime.datetime.now())[0:19]
        print (start_time)
        VMM = VT_DMM_Manual.VT_DMM_Manual()
        print ("Run VT4002 + DMM196 Manual")
        DIS.write('t0.txt="Manual"\xff\xff\xff')
        DIS.write('t1.txt="VT4002 + DMM196"\xff\xff\xff')
        DIS.write('t6.txt="' + start_time + '"\xff\xff\xff')
        VMM.main(self.number_sample, self.dmm_setT, self)

    def TTC_DMM_Auto(self):
        start_time = str(datetime.datetime.now())[0:19]
        print(start_time)
        FILENAME = detect_file.File(folder)[0]
        total_time = readTempProfile(FILENAME)[1] * 60
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=total_time)
        end_time_formated = str(end_time.strftime("%Y-%m-%d %H:%M:%S"))
        TMA = TTC_DMM_Auto.TTC_DMM_Auto()
        print ("Run TTC4006 + DMM196 Auto")
        DIS.write('t0.txt="Auto"\xff\xff\xff')
        DIS.write('t1.txt="TTC4006 + DMM196"\xff\xff\xff')
        DIS.write('t6.txt="' + start_time + '"\xff\xff\xff')
        DIS.write('t7.txt="' + end_time_formated + '"\xff\xff\xff')
        TMA.main(self.number_sample, self)

    def TTC_DMM_Manual(self):
        start_time = str(datetime.datetime.now())[0:19]
        print(start_time)
        TMM = TTC_DMM_Manual.TTC_DMM_Manual()
        print ("Run TTC4006 + DMM196 Manual")
        DIS.write('t0.txt="Manual"\xff\xff\xff')
        DIS.write('t1.txt="TTC4006 + DMM196"\xff\xff\xff')
        DIS.write('t2.txt="' + start_time + '"\xff\xff\xff')
        TMM.main(self.number_sample, self.dmm_setT, self)

    def VT_LCR_Auto(self):
        start_time = str(datetime.datetime.now())[0:19]
        print(start_time)
        VLA = VT_LCR_Auto.VT_LCR_Auto()
        print ("Run VT4002 + LCR Auto")
        DIS.write('t0.txt="Auto"\xff\xff\xff')
        DIS.write('t1.txt="VT4002 + LCR"\xff\xff\xff')
        DIS.write('t2.txt="' + start_time + '"\xff\xff\xff')
        VLA.main(self.number_sample, self.lcr_AV, self.lcr_AF, self)

    def VT_LCR_Manual(self):
        start_time = str(datetime.datetime.now())[0:19]
        print(start_time)
        VLM = VT_LCR_Manual.VT_LCR_Manual()
        print ("Run VT4002 + LCR Manual")
        DIS.write('t0.txt="Manual"\xff\xff\xff')
        DIS.write('t1.txt="VT4002 + LCR"\xff\xff\xff')
        DIS.write('t2.txt="' + start_time + '"\xff\xff\xff')
        VLM.main(self.number_sample, self.lcr_MT, self.lcr_MV, self.lcr_MF, self)

    def TTC_LCR_Auto(self):
        start_time = str(datetime.datetime.now())[0:19]
        print(start_time)
        TLA = TTC_LCR_Auto.TTC_LCR_Auto()
        print ("Run TTC4006 + LCR Auto")
        DIS.write('t0.txt="Auto"\xff\xff\xff')
        DIS.write('t1.txt="TTC4006 + LCR"\xff\xff\xff')
        DIS.write('t2.txt="' + start_time + '"\xff\xff\xff')
        TLA.main(self.number_sample, self.lcr_AV, self.lcr_AF, self)

    def TTC_LCR_Manual(self):
        start_time = str(datetime.datetime.now())[0:19]
        print(start_time)
        TLM = TTC_LCR_Manual.TTC_LCR_Manual()
        print ("Run TTC4006 + LCR Manual")
        DIS.write('t0.txt="Manual"\xff\xff\xff')
        DIS.write('t1.txt="TTC4006 + LCR"\xff\xff\xff')
        DIS.write('t2.txt="' + start_time + '"\xff\xff\xff')
        TLM.main(self.number_sample, self.lcr_MT, self.lcr_MV, self.lcr_MF, self)

    def VT_SM_Auto(self):
        start_time = str(datetime.datetime.now())[0:19]
        print (start_time)
        FILENAME = detect_file.File(folder)[0]
        total_time = readTempProfile(FILENAME)[1] * 60
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=total_time)
        end_time_formated = str(end_time.strftime("%Y-%m-%d %H:%M:%S"))
        VSA = VT_SM_Auto.VT_SM_Auto()
        print ("Run VT4002 + Sourcemeter Auto")
        DIS.write('t0.txt="Auto"\xff\xff\xff')
        DIS.write('t1.txt="VT4002 + Sourcemeter"\xff\xff\xff')
        DIS.write('t2.txt="' + start_time + '"\xff\xff\xff')
        DIS.write('t7.txt="' + end_time_formated + '"\xff\xff\xff')
        VSA.main(self.number_sample, self.sm_AV, self)

    def VT_SM_Manual(self):
        start_time = str(datetime.datetime.now())[0:19]
        print(start_time)
        VSM = VT_SM_Manual.VT_SM_Manual()
        print("Run VT4002 + Sourcemeter Manual")
        DIS.write('t0.txt="Manual"\xff\xff\xff')
        DIS.write('t1.txt="VT4002 + Sourcemeter"\xff\xff\xff')
        DIS.write('t2.txt="' + start_time + '"\xff\xff\xff')
        VSM.main(self.number_sample, self.sm_MT, self.sm_startV, self.sm_endV, 0.01, self)

    def TTC_SM_Auto(self):
        start_time = str(datetime.datetime.now())[0:19]
        print(start_time)
        FILENAME = detect_file.File(folder)[0]
        total_time = readTempProfile(FILENAME)[1] * 60
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=total_time)
        end_time_formated = str(end_time.strftime("%Y-%m-%d %H:%M:%S"))
        TSA = TTC_SM_Auto.TTC_SM_Auto()
        print ("Run TTC4006 + Sourcemeter Auto")
        DIS.write('t0.txt="Auto"\xff\xff\xff')
        DIS.write('t1.txt="TTC4006 + Sourcemeter"\xff\xff\xff')
        DIS.write('t6.txt="' + start_time + '"\xff\xff\xff')
        DIS.write('t7.txt="' + end_time_formated + '"\xff\xff\xff')
        setV = self.sm_AV
        TSA.main(self.number_sample, setV, self)

    def TTC_SM_Manual(self):
        start_time = str(datetime.datetime.now())[0:19]
        print(start_time)
        FILENAME = detect_file.File(folder)[0]
        total_time = readTempProfile(FILENAME)[1] * 60
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=total_time)
        end_time_formated = str(end_time.strftime("%Y-%m-%d %H:%M:%S"))
        TIM = TTC_SM_Manual.TTC_SM_Manual()
        print ("Run TTC4006 + Sourcemeter Manual")
        DIS.write('t0.txt="Manual"\xff\xff\xff')
        DIS.write('t1.txt="TTC4006 + Sourcemeter"\xff\xff\xff')
        DIS.write('t6.txt="' + start_time + '"\xff\xff\xff')
        DIS.write('t7.txt="' + end_time_formated + '"\xff\xff\xff')
        TIM.main(self.number_sample, self.sm_MT, self.sm_startV, self.sm_endV, 0.01, self)

    def TTC_IMP_Auto(self):
        start_time = str(datetime.datetime.now())[0:19]
        print(start_time)
        FILENAME = detect_file.File(folder)[0]
        total_time = readTempProfile(FILENAME)[1] * 60
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=total_time)
        end_time_formated = str(end_time.strftime("%Y-%m-%d %H:%M:%S"))
        TIA = TTC_IMP_Auto.TTC_IMP_Auto()
        print ("Run TTC4006 + IMP Auto")
        DIS.write('t0.txt="Auto"\xff\xff\xff')
        DIS.write('t1.txt="TTC4006 + IMP"\xff\xff\xff')
        DIS.write('t6.txt="' + start_time + '"\xff\xff\xff')
        DIS.write('t7.txt="' + end_time_formated + '"\xff\xff\xff')
        setV = float(self.imp_AV) / 1000
        start_f = self.imp_startAF
        end_f = self.imp_endAF
        TIA.main(self.number_sample, start_f, end_f, setV, self)

    def TTC_IMP_Manual(self):
        start_time = str(datetime.datetime.now())[0:19]
        print(start_time)
        FILENAME = detect_file.File(folder)[0]
        total_time = readTempProfile(FILENAME)[1] * 60
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=total_time)
        end_time_formated = str(end_time.strftime("%Y-%m-%d %H:%M:%S"))
        TIM = TTC_IMP_Manual.TTC_IMP_Manual()
        print ("Run TTC4006 + IMP Manual")
        DIS.write('t0.txt="Manual"\xff\xff\xff')
        DIS.write('t1.txt="TTC4006 + IMP"\xff\xff\xff')
        DIS.write('t6.txt="' + start_time + '"\xff\xff\xff')
        DIS.write('t7.txt="' + end_time_formated + '"\xff\xff\xff')
        set_temp = self.imp_MT
        setV = float(self.imp_MV) / 1000
        start_f = self.imp_startMF
        end_f = self.imp_endMF
        TIM.main(self.number_sample, set_temp, start_f, end_f, setV, self)

    def VT_IMP_Auto(self):
        start_time = str(datetime.datetime.now())[0:19]
        print(start_time)
        FILENAME = detect_file.File(folder)[0]
        total_time = readTempProfile(FILENAME)[1] * 60
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=total_time)
        end_time_formated = str(end_time.strftime("%Y-%m-%d %H:%M:%S"))
        VIA = VT_IMP_Auto.VT_IMP_Auto()
        print ("Run VT4002 + IMP Auto")
        DIS.write('t0.txt="Auto"\xff\xff\xff')
        DIS.write('t1.txt="VT4002 + IMP"\xff\xff\xff')
        DIS.write('t6.txt="' + start_time + '"\xff\xff\xff')
        DIS.write('t7.txt="' + end_time_formated + '"\xff\xff\xff')
        setV = float(self.imp_AV) / 1000
        start_f = self.imp_startAF
        end_f = self.imp_endAF
        VIA.main(self.number_sample, start_f, end_f, setV, self)

    def VT_IMP_Manual(self):
        start_time = str(datetime.datetime.now())[0:19]
        print(start_time)
        FILENAME = detect_file.File(folder)[0]
        total_time = readTempProfile(FILENAME)[1] * 60
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=total_time)
        end_time_formated = str(end_time.strftime("%Y-%m-%d %H:%M:%S"))
        VIM = VT_IMP_Manual.VT_IMP_Manual()
        print ("Run VT2002 + IMP Manual")
        DIS.write('t0.txt="Manual"\xff\xff\xff')
        DIS.write('t1.txt="VT2002 + IMP"\xff\xff\xff')
        DIS.write('t6.txt="' + start_time + '"\xff\xff\xff')
        DIS.write('t7.txt="' + end_time_formated + '"\xff\xff\xff')
        set_temp = self.imp_MT
        setV = float(self.imp_MV) / 1000
        start_f = self.imp_startMF
        end_f = self.imp_endMF
        VIM.main(self.number_sample, set_temp, start_f, end_f, setV, self)

    def VT_Auto(self):
        start_time = str(datetime.datetime.now())[0:19]
        print(start_time)
        DIS.write('t3.txt="VT4002"\xff\xff\xff')
        OVA = Oven_VT_auto.VT_Auto()
        OVA.main(self)

    def VT_Manual(self):
        print("here")
        start_time = str(datetime.datetime.now())[0:19]
        print(start_time)
        DIS.write('t3.txt="VT4002"\xff\xff\xff')
        set_temp = self.oven_setTemp
        OVM = Oven_VT_manual.VT_Manual()
        OVM.main(set_temp, self)

    def TTC_Auto(self):
        start_time = str(datetime.datetime.now())[0:19]
        print(start_time)
        DIS.write('t3.txt="TTC4006"\xff\xff\xff')
        OTA = Oven_TTC_auto.TTC_Auto()
        OTA.main(self)

    def TTC_Manual(self):
        start_time = str(datetime.datetime.now())[0:19]
        print(start_time)
        DIS.write('t3.txt="TTC4006"\xff\xff\xff')
        set_temp = self.oven_setTemp
        OTM = Oven_TTC_manual.TTC_Manual()
        OTM.main(set_temp, self)

    def RelayMode(self):
        start_time = str(datetime.datetime.now())[0:19]
        print(start_time)
        sample_num = self.rel_num
        sample_time = self.rel_interval
        DIS.write('t0.txt="' + str(sample_num) + '"\xff\xff\xff')
        DIS.write('t1.txt="' + str(sample_time) + '"\xff\xff\xff')
        RM = RelayMode.Relay_mode()
        RM.main(sample_num, sample_time, self)


def main():
    DIS.write("rest\xff\xff\xff")
    sleep(5)
    DS = Device_select()
    RETURN_VAL = set()

    while True:
        DEVICE = str(DIS.read())
        RETURN_VAL.add(DEVICE)
        print(RETURN_VAL)

        if "['e\\x01\\x06\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\x0b\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\x04\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            DIS.write("page Mode Multi\xff\xff\xff")
            RETURN_VAL.discard("['e\\x01\\x06\\x01\\xff\\xff\\xff']")
            RETURN_VAL.discard("['e\\x01\\x04\\x01\\xff\\xff\\xff']")

        elif "['e\\x01\\x06\\x01\\xff\\xff\\xff']"in RETURN_VAL and "['e\\x01\\r\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\x04\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            DIS.write("page Mode Multi\xff\xff\xff")
            RETURN_VAL.discard("['e\\x01\\x06\\x01\\xff\\xff\\xff']")
            RETURN_VAL.discard("['e\\x01\\x04\\x01\\xff\\xff\\xff']")

        elif "['e\\x01\\x08\\x01\\xff\\xff\\xff']"in RETURN_VAL and "['e\\x01\\x0b\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\x04\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            DIS.write("page Mode LCR\xff\xff\xff")
            RETURN_VAL.discard("['e\\x01\\x08\\x01\\xff\\xff\\xff']")
            RETURN_VAL.discard("['e\\x01\\x04\\x01\\xff\\xff\\xff']")

        elif "['e\\x01\\x08\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\r\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\x04\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            DIS.write("page Mode LCR\xff\xff\xff")
            RETURN_VAL.discard("['e\\x01\\x08\\x01\\xff\\xff\\xff']")
            RETURN_VAL.discard("['e\\x01\\x04\\x01\\xff\\xff\\xff']")

        elif "['e\\x01\\x07\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\x0b\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\x04\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            DIS.write("page Mode Source\xff\xff\xff")
            RETURN_VAL.discard("['e\\x01\\x07\\x01\\xff\\xff\\xff']")
            RETURN_VAL.discard("['e\\x01\\x04\\x01\\xff\\xff\\xff']")

        elif "['e\\x01\\x07\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\r\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\x04\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            DIS.write("page Mode Source\xff\xff\xff")
            RETURN_VAL.discard("['e\\x01\\x07\\x01\\xff\\xff\\xff']")
            RETURN_VAL.discard("['e\\x01\\x04\\x01\\xff\\xff\\xff']")

        elif "['e\\x01\\x0c\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\x0b\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\x04\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            DIS.write("page Mode IMP\xff\xff\xff")
            RETURN_VAL.discard("['e\\x01\\x0c\\x01\\xff\\xff\\xff']")
            RETURN_VAL.discard("['e\\x01\\x04\\x01\\xff\\xff\\xff']")

        elif "['e\\x01\\x0c\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\r\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\x04\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            DIS.write("page Mode IMP\xff\xff\xff")
            RETURN_VAL.discard("['e\\x01\\x0c\\x01\\xff\\xff\\xff']")
            RETURN_VAL.discard("['e\\x01\\x04\\x01\\xff\\xff\\xff']")

        elif "['e\\x01\\x0e\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            DIS.write("page Mode Oven\xff\xff\xff")
            RETURN_VAL.discard("['e\\x01\\x0e\\x01\\xff\\xff\\xff']")

        elif "['e\\x01\\x0f\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            DIS.write("page Mode Relay\xff\xff\xff")
            RETURN_VAL.discard("['e\\x01\\x0f\\x01\\xff\\xff\\xff']")

        elif "['e\\x03\\x05\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\0b\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            try:
                DS.VT_DMM_Auto()
                RETURN_VAL.clear()
            except:
                RETURN_VAL.clear()
                DIS.write("page Device Select\xff\xff\xff")

        elif "['e\\x03\\x06\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\0b\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            try:
                DS.VT_DMM_Manual()
                RETURN_VAL.clear()
            except:
                RETURN_VAL.clear()
                DIS.write("page Device Select\xff\xff\xff")

        elif "['e\\x03\\x05\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\r\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            try:
                DS.TTC_DMM_Auto()
                RETURN_VAL.clear()
            except:
                RETURN_VAL.clear()
                DIS.write("page Device Select\xff\xff\xff")

        elif "['e\\x03\\x06\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\r\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            try:
                DS.TTC_DMM_Manual()
                RETURN_VAL.clear()
            except:
                RETURN_VAL.clear()
                DIS.write("page Device Select\xff\xff\xff")

        elif "['e\\x06\\x07\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\0b\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            try:
                DS.VT_LCR_Auto()
                RETURN_VAL.clear()
            except:
                RETURN_VAL.clear()
                DIS.write("page Device Select\xff\xff\xff")

        elif "['e\\x06\\x08\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\0b\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            try:
                DS.VT_LCR_Manual()
                RETURN_VAL.clear()
            except:
                RETURN_VAL.clear()
                DIS.write("page Device Select\xff\xff\xff")

        elif "['e\\x06\\x07\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\r\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            try:
                DS.TTC_LCR_Auto()
                RETURN_VAL.clear()
            except:
                RETURN_VAL.clear()
                DIS.write("page Device Select\xff\xff\xff")

        elif "['e\\x06\\x08\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\r\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            try:
                DS.TTC_LCR_Manual()
                RETURN_VAL.clear()
            except:
                RETURN_VAL.clear()
                DIS.write("page Device Select\xff\xff\xff")

        elif "['e\\x05\\x05\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\0b\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            try:
                DS.VT_SM_Auto()
                RETURN_VAL.clear()
            except:
                RETURN_VAL.clear()
                DIS.write("page Device Select\xff\xff\xff")

        elif "['e\\x05\\x06\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\0b\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            try:
                DS.VT_SM_Manual()
                RETURN_VAL.clear()
            except:
                RETURN_VAL.clear()
                DIS.write("page Device Select\xff\xff\xff")

        elif "['e\\x05\\x05\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\r\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            try:
                DS.TTC_SM_Auto()
                RETURN_VAL.clear()
            except:
                RETURN_VAL.clear()
                DIS.write("page Device Select\xff\xff\xff")

        elif "['e\\x05\\x06\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\r\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            try:
                DS.TTC_SM_Manual()
                RETURN_VAL.clear()
            except:
                RETURN_VAL.clear()
                DIS.write("page Device Select\xff\xff\xff")

        elif "['e\\x07\\x07\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\r\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            try:
                DS.TTC_IMP_Auto()
                RETURN_VAL.clear()
            except:
                RETURN_VAL.clear()
                DIS.write("page Device Select\xff\xff\xff")

        elif "['e\\x07\\x08\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\r\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            try:
                DS.TTC_IMP_Manual()
                RETURN_VAL.clear()
            except:
                RETURN_VAL.clear()
                DIS.write("page Device Select\xff\xff\xff")

        elif "['e\\x07\\x07\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\x0b\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            try:
                DS.VT_IMP_Auto()
                RETURN_VAL.clear()
            except:
                RETURN_VAL.clear()
                DIS.write("page Device Select\xff\xff\xff")

        elif "['e\\x07\\x08\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x01\\x0b\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            try:
                DS.VT_IMP_Manual()
                RETURN_VAL.clear()
            except:
                RETURN_VAL.clear()
                DIS.write("page Device Select\xff\xff\xff")

        elif "['e\\x04\\x07\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x04\\x05\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            try:
                DS.VT_Auto()
                RETURN_VAL.clear()
            except:
                RETURN_VAL.clear()
                DIS.write("page Device Select\xff\xff\xff")

        elif "['e\\x04\\x07\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x04\\x06\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            try:
                DS.VT_Manual()
                RETURN_VAL.clear()
            except:
                RETURN_VAL.clear()
                DIS.write("page Device Select\xff\xff\xff")

        elif "['e\\x04\\x08\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x04\\x05\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            try:
                DS.TTC_Auto()
                RETURN_VAL.clear()
            except:
                RETURN_VAL.clear()
                DIS.write("page Device Select\xff\xff\xff")

        elif "['e\\x04\\x08\\x01\\xff\\xff\\xff']" in RETURN_VAL and "['e\\x04\\x06\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            try:
                DS.TTC_Manual()
                RETURN_VAL.clear()
            except:
                RETURN_VAL.clear()
                DIS.write("page Device Select\xff\xff\xff")

        elif "['e\\x08\\x03\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            try:
                DS.RelayMode()
                RETURN_VAL.clear()
            except:
                RETURN_VAL.clear()
                DIS.write("page Device Select\xff\xff\xff")

        elif "['e\\x01\\x03\\x01\\xff\\xff\\xff']" in RETURN_VAL or "['e\\x0e\\x13\\x01\\xff\\xff\\xff']" in RETURN_VAL or "['e\\x0f\\x1b\\x01\\xff\\xff\\xff']" in RETURN_VAL or "['e\\x10\\x02\\x01\\xff\\xff\\xff']" in RETURN_VAL or "['e\\x11\\x04\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            RETURN_VAL.clear()

        elif "['e\\x0e\\x14\\x01\\xff\\xff\\xff']" in RETURN_VAL or "['e\\x0f\\x1c\\x01\\xff\\xff\\xff']" in RETURN_VAL or "['e\\x10\\x01\\x01\\xff\\xff\\xff']" in RETURN_VAL or "['e\\x11\\x05\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            os.system("sudo reboot")
            RETURN_VAL.clear()

        elif "['e\\x01\\x05\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            DS.get_sample_number()
            print ("Sample number:", DS.number_sample)
            RETURN_VAL.remove("['e\\x01\\x05\\x01\\xff\\xff\\xff']")

        elif "['e\\x03\\x03\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            DS.get_multiPara()
            print("Set temperature:", DS.get_multiPara())
            RETURN_VAL.discard("['e\\x03\\x03\\x01\\xff\\xff\\xff']")

        elif "['e\\x05\\x03\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            DS.get_smMPara()
            print("Set temperature:", str(DS.sm_MT))
            print("Start voltage:", str(DS.sm_startV))
            print("End voltage:", str(DS.sm_endV))
            RETURN_VAL.discard("['e\\x05\\x03\\x01\\xff\\xff\\xff']")

        elif "['e\\x05\\x0c\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            DS.get_smApara()
            print("Set voltage:", DS.get_smApara())
            RETURN_VAL.remove("['e\\x05\\x0c\\x01\\xff\\xff\\xff']")

        elif "['e\\x06\\x0b\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            DS.get_lcrAPara()
            print("Set voltage:", DS.lcr_AV)
            print("Set frequency:", DS.lcr_AF)
            RETURN_VAL.discard("['e\\x06\\x0b\\x01\\xff\\xff\\xff']")

        elif "['e\\x06\\x05\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            DS.get_lcrMPara()
            print("Set temperature:", DS.lcr_MT)
            print("Set voltage:", DS.lcr_MV)
            print("Set frequency:", DS.lcr_MF)
            RETURN_VAL.discard("['e\\x06\\x05\\x01\\xff\\xff\\xff']")

        elif "['e\\x07\\x0b\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            DS.get_IMPApara()
            print("Set voltage:", DS.imp_AV)
            print("Start frequency:", DS.imp_startAF)
            print("End frequency:", DS.imp_endAF)
            RETURN_VAL.discard("['e\\x07\\x0b\\x01\\xff\\xff\\xff']")

        elif "['e\\x07\\x05\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            DS.get_IMPMpara()
            print("Set temperature:", DS.imp_MT)
            print("Set voltage:", DS.imp_MV)
            print("Start frequency:", DS.imp_startMF)
            print("End frequency:", DS.imp_endMF)
            RETURN_VAL.discard("['e\\x07\\x05\\x01\\xff\\xff\\xff']")

        elif "['e\\x08\\x04\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            DS.get_relPara()
            print("Set num:", DS.rel_num)
            print("Set interval:", DS.rel_interval)
            RETURN_VAL.discard("['e\\x08\\x04\\x01\\xff\\xff\\xff']")

        elif "['e\\x04\\x03\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            DS.get_ovenInfo()
            print("Set Temperature:", DS.oven_setTemp)
            RETURN_VAL.discard("['e\\x04\\x03\\x01\\xff\\xff\\xff']")

        elif "['e\\x03\\x04\\x01\\xff\\xff\\xff']" in RETURN_VAL or "['e\\x05\\x04\\x01\\xff\\xff\\xff']" in RETURN_VAL or "['e\\x06\\x04\\x01\\xff\\xff\\xff']" in RETURN_VAL or "['e\\x07\\x04\\x01\\xff\\xff\\xff']" in RETURN_VAL or "['e\\x04\\x04\\x01\\xff\\xff\\xff']" in RETURN_VAL:
            DS.read_profile()
            # print("1")
            RETURN_VAL.discard("['e\\x03\\x04\\x01\\xff\\xff\\xff']")
            RETURN_VAL.discard("['e\\x04\\x04\\x01\\xff\\xff\\xff']")
            RETURN_VAL.discard("['e\\x05\\x04\\x01\\xff\\xff\\xff']")
            RETURN_VAL.discard("['e\\x06\\x06\\x01\\xff\\xff\\xff']")
            RETURN_VAL.discard("['e\\x07\\x06\\x01\\xff\\xff\\xff']")



if __name__ == '__main__':
    main()
