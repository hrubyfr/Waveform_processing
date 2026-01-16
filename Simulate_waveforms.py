import numpy as np
import ROOT
from array import array
import sys

import config as cf

# t_axis -- array of double, t0 -- detection time, double; tau_rise/fall -- rise/fall time of waveform, double; amplitude -- maximum value, double
def generate_sipm_pulse(t_axis, t0, tau_rise = 8.0, tau_fall = 170.0, amplitude = 100.0):
    """Generates a normalized bi-exponential pulse starting at t0."""
    mask = (t_axis >= t0)
    dt = t_axis[mask] - t0
    pulse = np.zeros_like(t_axis)
    pulse[mask] = amplitude * (np.exp(-dt / tau_fall) - np.exp(-dt / tau_rise))
    return pulse

# --- Simulation Parameters ---

# Setup Time Axes
total_time = cf.N_DIGITAL_POINTS * (1 / cf.DIGITAL_FS) # ~256 ns
t_analog = np.arange(0, total_time, 1/cf.ANALOG_FS)
t_digital = np.arange(0, total_time, 1/cf.DIGITAL_FS)

# --- ROOT File Setup ---
output_file = ROOT.TFile("SiPM_Simulation.root", "RECREATE")
tree = ROOT.TTree("Waveforms", "Simulated SiPM Data")

# --- Define Branches ---
# 1. Single values (Event ID, True Time)
event_id = array('i', [0])
true_time = array('d', [0.0])

# 2. Arrays (The Waveform)
# ROOT needs a fixed size array for simple branches, or std::vector for dynamic
# Here we use a C-style array of size 32
waveform_samples = array('d', [0.0]*cf.N_DIGITAL_POINTS)
true_waveform = np.zeros(len(t_analog), dtype=np.float64)

tree.Branch("event_id", event_id, "event_id/I")
tree.Branch("true_time", true_time, "true_time/D")
tree.Branch("waveform", waveform_samples, f"waveform[{cf.N_DIGITAL_POINTS}]/D")
tree.Branch("true_waveform", true_waveform, f"true_waveform[{len(t_analog)}]/D")


print(f"Generating {cf.N_EVENTS} events...")
np.set_printoptions(threshold=sys.maxsize)

# --- Simulation Loop ---
for i in range(cf.N_EVENTS):
    event_id[0] = i
    
    # 1. Randomize Arrival Time (gaussian around 20 ns)
    t0 = 40 + np.random.normal(0.0, 5.0)
    true_time[0] = t0

    # 2. Generate and save Analog Pulse

    amplitude = cf.AMPLITUDE_VALUE + np.random.uniform(-300, 300)
    analog_waveform = generate_sipm_pulse(t_analog, t0=t0, amplitude=amplitude)
    np.copyto(true_waveform, analog_waveform)

    # Check true waveform contents
    # print("Saving true_waveform to .txt file")
    # np.savetxt("plots/true_waveform.txt", true_waveform);
    # print("printing analog_waveform to .txt file")
    # np.savetxt("plots/analog_waveform.txt", analog_waveform);

    # 3. Add Noise
    noise = np.random.normal(0, 2.5, len(analog_waveform))
    analog_waveform += noise

    # 4. Digitize (Interpolate to 8ns grid)
    digitized = np.interp(t_digital, t_analog, analog_waveform)

    # 5. Fill ROOT Branch
    for j in range(cf.N_DIGITAL_POINTS):
        waveform_samples[j] = digitized[j]

    tree.Fill()

# --- Write & Close ---
tree.Write()
output_file.Close()

print("Done! Data saved to 'SiPM_Simulation.root'")
