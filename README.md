# the BABACOOL project

We present the BABACOOL (BAby Brain Atlas COnstruction for Optimized Labeled segmentation) approach for creating multi-modal developmental atlases, which we used to produce BaBa21, a population-based longitudinal developmental baboon template. BaBa21 consists of structural (T1- and T2-weighted) images and tissue probability maps from a population of 21 baboons (Papio anubis) scanned at 4 timepoints beginning from 2 weeks after birth and continuing to sexual maturity (5 years).
This resource is made available to provide a normalization target for baboon data across the lifespan, and further, facilitate neuroimaging research in baboons, comparative research with humans and nonhuman primate species for which developmental templates are available (e.g., macaques). 

## How to use ?
[# PART1: pipeline processing steps for **3D** template construction](pipeline3D.md) 

[# PART2: pipeline processing steps **(4D+t)** longitudinal template interpolation](pipeline4D.md)

<table>
<tr>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/animations/T1w_snap.gif" width="400" height="150" />
    </td>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/animations/T2w_snap.gif" width="400" height="150" />
    </td>
</tr>
<tr> 
    <td align="center">T1w</td> 
    <td align="center">T2w</td> 
</tr>
<tr>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/animations/WM_snap.gif" width="400" height="150" />
    </td>
    <td align="center">
    <img src="https://github.com/arnaudletroter/BABACOOL/blob/main/animations/WM_gii_snap_top.gif" width="150" height="150" />
    </td>
</tr>
<tr> 
    <td align="center">WM priors maps</td> 
    <td align="center">Cortical Surface</td> 
</tr>
</table>

## If you use it, please cite the paper:
Katherine L. Bryant, Arnaud Le Troter, David Meunier, Yannick Becker, Scott A. Love, Siham Bouziane, Kep Kee Loh, Julien Sein, Luc Renaud, Olivier Coulon, Adrien Meguerditchian, 
under revision in Imaging Neuroscience. Longitudinal MRI template of the baboon brain from birth to adolescence

Arnaud Le Troter, David Meunier, Katherine Bryant, Julien Sein, Siham Bouziane, Adrien Meguerditchian,
BaBa21. OpenNeuro. [Dataset] doi: doi:10.18112/openneuro.ds005424.v1.0.0

## Acknowledgements
We are very grateful to the Station de Primatologie CNRS, particularly animal care staff, vets and technicians as well as administrative staff of the ILCB, the CRPN and the LPC: Nadia Melili, Nadera Bureau, Frederic Lombardo and Colette Pourpe respectively.
