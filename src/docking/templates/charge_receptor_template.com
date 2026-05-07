open $receptor
delete solvent
delete ligand
addh
addcharge
save ${name}_charged.mol2
exit