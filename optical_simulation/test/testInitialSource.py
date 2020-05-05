from gratingLib.InitialSource import InitialSource


if __name__ == "__main__":
    source = InitialSource(3, 3, 'spherical', 2)

    var1, var2 = source.propogate(20, [0, 0.5, 1, 1.5, 2], 5, False)


    print(var1)

    print(var2)
