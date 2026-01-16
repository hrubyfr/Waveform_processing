#include <vector>
#include <iostream>
#include <algorithm>

#include "TString.h"
#include "TFile.h"
using std::vector;
using std::cout;
using std::endl;

const int CFD_GAIN_DELAYED = 2;
const int CFD_DELAY = 1;
const int TIME_BASE_NS = 8;

 double CalculateTimeCFD(std::vector<double> waveform){
	std::vector<double> delayed_waveform = waveform;


	for(int i = delayed_waveform.size()-1; i > 0; i--){
		delayed_waveform[i] = delayed_waveform[i-1];
		delayed_waveform[i]*=-CFD_GAIN_DELAYED;
	}
	delayed_waveform.at(0) *= -CFD_GAIN_DELAYED;



	std::vector<double> constant_fraction_sample;
	for (int i = 0; i < delayed_waveform.size(); i++){
		constant_fraction_sample.emplace_back(waveform[i] + delayed_waveform[i]);
	}
	auto min_element = std::min_element(constant_fraction_sample.begin(), constant_fraction_sample.end());
	auto max_element = std::max_element(constant_fraction_sample.begin(), constant_fraction_sample.end());
	if (*min_element >= 0 || *max_element <= 0) return -999;
	auto current_element = min_element;
	while (* current_element < 0){
		if (current_element == constant_fraction_sample.begin()){
			return -999;
		}
		current_element--;
	}

	int x1 = std::distance(constant_fraction_sample.begin(), current_element);
	double y1 = *current_element;
	double y2 = *(current_element + 1);
	auto y_ratio = y1 / (y1 + y2);

	double cfd_time = x1 + y_ratio;
	double cfd_time_ns = cfd_time * TIME_BASE_NS;

	double final_time_ns = cfd_time_ns;

	
	
	return cfd_time_ns;

}

void Analyze_waveform(){
	TString filename = "SiPM_Simulation.root";

	TFile* file = TFile::Open(filename, "READ");

}

