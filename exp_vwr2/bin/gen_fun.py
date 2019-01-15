

def metric(org):

    if org == 'Worm':
        metric = 'area'
    elif org == 'Yeast':
        metric = 'O.D.'
    elif org == 'Cell':
        metric == 'Normfluor(RFUpercell)'

    return(metric)
