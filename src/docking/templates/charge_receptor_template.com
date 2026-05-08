open $receptor
delete solvent
delete ligand
addh
addcharge
save $name
exit