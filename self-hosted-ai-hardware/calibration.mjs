// Written by fit.mjs from anchors.json. Do not edit by hand: change the runs or the model, then run node fit.mjs.
export const calibration = {
 "strata": {
  "amd": 2.244,
  "eff": 1,
  "lat": 2,
  "beta": 2.13,
  "ramEff": 0.65,
  "single": 0.7989,
  "multi": 0.7228,
  "full": 0.4767,
  "longCtx": 0.7323,
  "kappaResident": 0.45,
  "kappaGpus": 0.67,
  "pa": 0.01453,
  "pb": 2.104e-38,
  "pScale": 0.08442,
  "pLen": 4000000,
  "sweeps": 4,
  "decodeLo": 0.683,
  "decodeHi": 1.416,
  "prefillLo": 0.334,
  "prefillHi": 1.459,
  "runs": {
   "decode": 224,
   "prefill": 117,
   "outliers": 11,
   "medianError": {
    "decode": 0.146,
    "prefill": 0.265
   },
   "heldOut": {
    "decode": 225,
    "prefill": 127,
    "machines": {
     "decode": 56,
     "prefill": 35
    },
    "medianError": {
     "decode": 0.167,
     "prefill": 0.322
    }
   }
  }
 },
 "maya": {
  "amd": 1.593,
  "eff": 0.4905,
  "lat": 4.659,
  "beta": 6,
  "ramEff": 0.2609,
  "single": 1,
  "multi": 1.473,
  "longCtx": 0.3642,
  "kappaResident": 0.5,
  "kappaGpus": 0,
  "pa": 0.009347,
  "pb": 0.0001902,
  "pScale": 0.2831,
  "pLen": 4000000,
  "sweeps": 9,
  "decodeLo": 0.607,
  "decodeHi": 1.787,
  "prefillLo": 0.402,
  "prefillHi": 2.01,
  "runs": {
   "decode": 128,
   "prefill": 114,
   "outliers": 39,
   "medianError": {
    "decode": 0.239,
    "prefill": 0.387
   },
   "heldOut": {
    "decode": 130,
    "prefill": 151,
    "machines": {
     "decode": 36,
     "prefill": 34
    },
    "medianError": {
     "decode": 0.291,
     "prefill": 0.488
    }
   }
  }
 },
 "vllm": {
  "amd": 1,
  "eff": 1,
  "lat": 3.681,
  "attention": 4.895,
  "tpGain": 0.75,
  "kappa": 0.082,
  "pa": 0.002481,
  "pScale": 1.526e-15,
  "pLen": 24320,
  "sweeps": 46,
  "decodeLo": 0.782,
  "decodeHi": 1.379,
  "prefillLo": 0.583,
  "prefillHi": 1.675,
  "runs": {
   "decode": 77,
   "prefill": 68,
   "outliers": 2,
   "medianError": {
    "decode": 0.072,
    "prefill": 0.303
   },
   "heldOut": {
    "decode": 78,
    "prefill": 69,
    "machines": {
     "decode": 12,
     "prefill": 6
    },
    "medianError": {
     "decode": 0.088,
     "prefill": 0.297
    }
   }
  }
 },
 "sglang": {
  "amd": 1,
  "eff": 0.9068,
  "lat": 3.591,
  "attention": 0.99,
  "tpGain": 0.75,
  "kappa": 0.058,
  "pa": 0.001256,
  "pScale": 0.85,
  "pLen": 74050,
  "sweeps": 41,
  "decodeLo": 0.7,
  "decodeHi": 1.742,
  "prefillLo": 0.7,
  "prefillHi": 2.879,
  "runs": {
   "decode": 6,
   "prefill": 14,
   "outliers": 0,
   "medianError": {
    "decode": 0,
    "prefill": 0.019
   },
   "heldOut": {
    "decode": 6,
    "prefill": 14,
    "machines": {
     "decode": 1,
     "prefill": 1
    },
    "medianError": {
     "decode": 0.184,
     "prefill": 0.823
    }
   }
  }
 },
 "llamacpp": {
  "amd": 4.111,
  "eff": 0.8982,
  "lat": 4.192,
  "attention": 0.7637,
  "tpGain": 0,
  "kappa": 0.35,
  "pa": 0.004352,
  "pScale": 0.742,
  "pLen": 43140,
  "sweeps": 0,
  "decodeLo": 0.831,
  "decodeHi": 1.15,
  "prefillLo": 0.349,
  "prefillHi": 2.257,
  "runs": {
   "decode": 120,
   "prefill": 50,
   "outliers": 5,
   "medianError": {
    "decode": 0.061,
    "prefill": 0.376
   },
   "heldOut": {
    "decode": 124,
    "prefill": 51,
    "machines": {
     "decode": 21,
     "prefill": 5
    },
    "medianError": {
     "decode": 0.076,
     "prefill": 0.616
    }
   }
  }
 }
};
