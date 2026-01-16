#include <cstddef>
#include <iostream>
#include <vector>

#include "TMath.h"
#include "TRandom3.h"
#include "TTree.h"
#include "TFile.h"

using namespace std;
// --- Configuration ---
const double SAMPLING_PERIOD = 8.0;   // 8 ns
const int N_SAMPLES = 32;             // 32 points
const double ANALOG_STEP = 0.01;      // 10 ps resolution for simulation
const double NOISE_LEVEL = 0.05;      // Noise amplitude
const int N_EVENTS = 1;            // Number of events

// Bi-Exponential Pulse Function
double GetPulseValue(double t, double t0, double amp, double noise) {
	if (t < t0) {return noise;}
	double dt = t - t0;
	double tau_rise = 1.5;
	double tau_fall = 45.0;
	// Normalized approx
	return amp * (TMath::Exp(-dt / tau_fall) - TMath::Exp(-dt / tau_rise)) + noise;
}

void Simulate_waveforms() {
	TFile *f = new TFile("SiPM_Simulation.root", "RECREATE");

	// ======================================================
	// TREE 1: Configuration (The Constants)
	// ======================================================
	// We create a tree just to store the setup parameters
	TTree *tConfig = new TTree("Config", "Run Parameters");

	// Variables to hold the constants
	double cfg_sampling_period = SAMPLING_PERIOD;
	double cfg_analog_step_ns = ANALOG_STEP;


	// Create Branches
	tConfig->Branch("sampling_period_ns", &cfg_sampling_period, "sampling_period_ns/D");
	tConfig->Branch("analog_step_ns", &cfg_analog_step_ns, "analog_step_ns/D");

	// FILL ONCE: We only need to save this info one time
	tConfig->Fill(); 


	// ======================================================
	// TREE 2: The Data (The Waveforms)
	// ======================================================

	cout << "Filling config tree: " << endl;

	TTree *tWave = new TTree("Waveforms", "Simulated SiPM Data");

	unsigned int n_events_simulated = N_EVENTS;

	int event_id;
	double true_time;
	std::vector<double>* waveform = new vector<double>();
	std::vector<double>* true_waveform = new vector<double>();

	// Note: We removed the 'time_axis' array from here because 
	// we can now reconstruct it using the 'Config' tree!

	tWave->Branch("event_id", &event_id, "event_id/I");
	tWave->Branch("true_time", &true_time, "true_time/D");
	tWave->Branch("digitized_waveform", waveform, "waveform");
	tWave->Branch("true_waveform", true_waveform, "true_waveform");

	cout << "Config tree filled " << endl;

	TRandom3 *rnd = new TRandom3(0);

	cout << "Filling tree " << endl;
	for (int i = 0; i < n_events_simulated; i++) {
		event_id = i;
		true_time = 20.0 + rnd->Gaus(0, 2);  // true time in nanoseconds

		// True waveform
		for (int s = 0; s < N_SAMPLES * (SAMPLING_PERIOD / ANALOG_STEP); s++){
			double t = s * ANALOG_STEP;
			double true_signal = GetPulseValue(t, true_time, 1.0, 0.0);
			true_waveform->push_back(true_signal);
		}

		
		for (int s = 0; s < N_SAMPLES; s++) {
			// Reconstruct time using the constant we know
			double t = s * SAMPLING_PERIOD; 
			double noise = rnd->Gaus(0, NOISE_LEVEL);
			double signal = GetPulseValue(t, true_time, 1.0, noise);
			waveform->push_back(signal);
		}
		tWave->Fill();
		waveform->clear();
		true_waveform->clear();
	}


	// ======================================================
	// SAVE EVERYTHING
	// ======================================================
	// This writes both Trees to the file
	f->Write(); 
	f->Close();

	std::cout << "Done! File contains 'Waveforms' and 'Config' trees." << std::endl;

}
