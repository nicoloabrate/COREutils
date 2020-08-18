def uncformat(data, std, fmtn=".5e", fmts=None):

    if len(data) != len(std):
        raise ValueError("Data and std dimension mismatch!")

    if std is None:
        try:
            # data are ufloat
            inptup = [(d.n, d.s) for d in data]
        except OSError:
            raise TypeError("If std is not provided, data must be ufloat type")
    else:
        inptup = list(zip(data, std))

    percent = False

    if '%' in fmtn:
        fmtn.replace('%', '')

    if fmts is None:
        fmt = "{:%s}%s{:%s}" % (fmtn, u"\u00B1", fmtn)
    else:
        if '%' in fmts:
            percent = True
            fmts = fmts.replace('%', '')
            fmt = "{:%s}%s{:%s}%%" % (fmtn, u"\u00B1", fmts)
        else:
            fmt = "{:%s}%s{:%s}" % (fmtn, u"\u00B1", fmts)

    out = []
    outapp = out.append
    for tup in inptup:
        d, s = tup
        if percent is True:
            s = s/100
        outapp(fmt.format(d, s))

    return out


data = [1e6, 2e6]
std = [0.1, 0.2]
x = uncformat(data, std, fmtn=".2f", fmts="%.2f")
print(x)