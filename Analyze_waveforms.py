import numpy as np
import ROOT
from array import array
import os
import dCFD_algorithm as cfd


file = ROOT.TFile.Open("SiPM_Simulation.root", "READ")

if not file or file.IsZombie():
    print("Error opening file")
    exit()

my_tree = file.Get("Waveforms")


for entry in my_tree:
    true_waveform = entry.true_waveform
    true_time = entry.true_time
    digitized_waveform = entry.waveform

    true_waveform_size = len(true_waveform)
    digitized_waveform_size = len(digitized_waveform)

    h_digitized = ROOT.TH1D("h_digitized", "h_digitized", digitized_waveform_size, 0, digitized_waveform_size)
    for i in range(digitized_waveform_size):
        h_digitized.SetBinContent(i+1, digitized_waveform[i])

    h = ROOT.TH1D("h1", "h1", true_waveform_size, 0, true_waveform_size)
    for i in range(true_waveform_size):
        h.SetBinContent(i+1, true_waveform[i])

    c1 = ROOT.TCanvas()
    h.Draw("HIST")

    folder_name = "plots"
    os.makedirs(folder_name, exist_ok=True)
    savepath = os.path.join(folder_name, "true_waveform.png")

    c1.SaveAs(savepath)
    c1.Clear()
    h_digitized.Draw("hist")
    c1.SaveAs(folder_name + "/" + "digitized_waveform.png")
    c1.Clear()

    reconstructed_time_ns, reconstructed_time_cc, cf_waveform, inx = cfd.Get_cfd_time(digitized_waveform)

    


    print("True time was: ", true_time)
    print("reconstructed time was: ", reconstructed_time_ns)

    
