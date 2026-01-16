import numpy as np
import config as cf


def Get_cfd_time(waveform):
        
        delayed = np.copy(waveform)
        delayed[cf.CFD_DELAY:] = waveform[:-cf.CFD_DELAY]
        delayed *= -cf.CFD_GAIN_DELAYED

        cf_samples = waveform + delayed
        if (cf_samples.min() >= 0) or (cf_samples.max() <= 0):
            return None, None, cf_samples, None
        else:
            idx_min = np.argmin(cf_samples)
        
        idx = idx_min
        while idx > 0 and cf_samples[idx] < 0:
            idx -= 1

        if idx > 0:
            x1 = idx
            x2 = x1+1
            y1 = cf_samples[x1]
            y2 = cf_samples[x2]
            # Linear interpolation                                                                                                                                                                                                                                                
            y_ratio = y1/(y1-y2)
            cf_time = x1+y_ratio  # time in samples                                                                                                                                                                                                                               
            cf_time_ns = cf_time*cf.DIGITIZED_TIME_BASE  # time in ns                                                                                                                                                                                                                       
            return cf_time_ns, cf_time, cf_samples, idx
        else:
            return None, None, cf_samples, None
