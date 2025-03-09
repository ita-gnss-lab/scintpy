*Research Opportunities on Ionospheric Scintillation Mitigation and Monitoring Using Synthetic Time Series Generated by a Two-Component Power Law Phase Screen Model*

- Introduction

- Phase screen theory foundation of the TPPSM

- Irregularity parameter estimation
--> Initial review of what has been done (not a subsection)
--> Current State-of-Art estimation techniques
--> Issues to be addressed
----> Weak Scintillation Cases (Talk about Why this is a problem and how could we approach this. Show a Picture that depicts what happens when S4 is set to a value below 0.5)
----> Current State of TPPSM Matlab code (only considers a linear movement, i.e., a instantaneous velocity. Maybe talk about a new version that is being developed)

- Usage of the TPPSM to simulate scintillation for different application
--> Ionospheric Scintillation Monitoring Stations
--> Plane landing
--> Flight of Drones

- Preliminary statistical analysis of the TPPSM parameters for each application
--> Ionospheric Scintillation Monitoring Stations
= Fix their velocities to 0
= Vary the receiver position. (Emphasize that we could consider other receiver positions on the paper)
= Vary the satellites
= Vary the values of S4 (0.6 and 0.9) and the values of \tau_0 (1.0, 0.6)

For each frequency:
----> Show the pdf of \rho_F/v_{eff}
----> Show the pdf of \tau_0
----> Show the pdf of S4
----> Show an example of the time series of amplitude and phase
----> Show the pdf of amplitude and phase

--> Plane landing
= Fix their velocities
= Fix their initial position close to the landing site of an airport
= Vary the values of S4 (0.6 and 0.9) and the values of \tau_0 (1.0, 0.6)
= Vary the satellites

For each frequency:
----> Show the pdf of \rho_F/v_{eff}
----> Show the pdf of \tau_0
----> Show the pdf of S4
----> Show an example of the time series of amplitude and phase
----> Show the pdf of amplitude and phase

--> Flying Drones
= Fix their velocities at 4 different directions as shown in Yu Jiao Paper.
= Fix their initial position arbitrarily
= Vary the values of S4 (0.6 and 0.9) and the values of \tau_0 (1.0, 0.6)
= Vary the satellites

For each frequency:
----> Show the pdf of \rho_F/v_{eff}
----> Show the pdf of \tau_0
----> Show the pdf of S4
----> Show an example of the time series of amplitude and phase
----> Show the pdf of amplitude and phase