from numpy import random

from optical_simulation.gratingLib.PointSource import PointSource
from optical_simulation.gratingLib.Slit import Slit


class Grating:

    def __init__(self, x, length, numberOfSlits, slitWidth, slitHeight, sourcesPerSlit, sourceSpacing):

        # all attributes are necessary for a grating to initialize itself and fill itself with slits and point sources
        self.x = x
        self.length = length
        self.numberOfSlits = numberOfSlits
        self.slitWidth = slitWidth
        self.slitHeight = slitHeight
        self.sourceSpacing = sourceSpacing
        self.sourcesPerSlit = sourcesPerSlit
        self.slits = []
        self.pointSourcePositions = []
        self.pointSourceAmplitudes = []
        self.pointSourcePhases = []

        # fill grating with slits, makeSlits also fills slits with point sources
        makeSlits(self, self.slitWidth, self.slitHeight, self.sourcesPerSlit, self.sourceSpacing)

    def addAmplitudes(self, newAmplitudes, newPhases):

        # method takes an array of amplitudes, replaces point source amplitude array, and populates all slits and
        # point sources with new amplitudes

        self.pointSourceAmplitudes = newAmplitudes
        self.pointSourcePhases = newPhases

        for slit in self.slits:
            for i in range(0, len(slit) - 1):
                for source, newAmplitude in zip(slit[i].sources, newAmplitudes):
                    source.amplitude = newAmplitude


def makeSlits(grating, slit_width, slit_height, num_sources, source_spacing):
    # This function will create a set amount of slits based on the amount of slits a Grating class wants. Each slit is created with
    # 'num_sources' number of sources with a slit width of 'slit_width.' Depending on the amount of sources a grating wants, this
    # function sets up different diffraction scenarios, like single slit diffraction, double slit diffraction, and Grating
    # diffraction

    if grating.numberOfSlits == 1:
        # Modeling Single Slit Diffraction

        # place a slit in the middle of the Grating.
        # Note: the y position of a slit is defined as its endpoint closest to the x axis
        center = grating.length / 2
        thisSlit = [Slit(grating.x, center - slit_width / 2, slit_width, num_sources, []) for i in range(slit_height)]
        # thisSlit = Slit(Grating.x, center - slit_width/2, slit_width, num_sources, [])
        grating.slits.append(thisSlit)
        makeSources(thisSlit, slit_height, 0, source_spacing)

        for slit in grating.slits:
            for i in range(0, slit_height - 1):
                for source in slit[i].sources:
                    grating.pointSourcePositions.append(source.y)
                    grating.pointSourceAmplitudes.append(source.amplitude)

    elif grating.numberOfSlits == 2:
        # Modeling Double Slit Diffraction
        # place two slits, with one 'slit_width' of distance between them

        center = grating.length / 2
        slit1 = [Slit(grating.x, center - slit_width / 2, slit_width, num_sources, []) for i in range(slit_height)]
        slit2 = [Slit(grating.x, center - slit_width / 2, slit_width, num_sources, []) for i in range(slit_height)]
        # slit1 = Slit(Grating.x, center - slit_width*1.5, slit_width, num_sources, [])
        # slit2 = Slit(Grating.x, center + slit_width*1.5, slit_width, num_sources, [])
        grating.slits.append(slit1)
        grating.slits.append(slit2)

        for slit in grating.slits:
            makeSources(slit, slit_height, 0, source_spacing)

        for slit in grating.slits:
            for i in range(0, slit_height - 1):
                for source in slit[i].sources:
                    grating.pointSourcePositions.append(source.y)
                    grating.pointSourceAmplitudes.append(source.amplitude)

    elif grating.numberOfSlits > 2:
        # Modeling a Grating with numberOfSlits
        # this Grating is expected to have at least a slit_width of distance between each slit
        # numberOfSlits is a variable input and each should start from the center and built outwards

        if grating.numberOfSlits % 2 == 0:

            center = grating.length / 2

            i = 0

            while grating.numberOfSlits / 2 > i:
                slit1_y = center + slit_width * 0.5 + 2 * i * slit_width
                slit2_y = center - slit_width * 1.5 - 2 * i * slit_width

                # Made slit 2 dimentional by making an array of slit height size, with identical slits.
                slit_1 = [Slit(grating.x, slit1_y, slit_width, num_sources, []) for i in range(slit_height)]
                slit_2 = [Slit(grating.x, slit2_y, slit_width, num_sources, []) for i in range(slit_height)]
                grating.slits.append(slit_1)
                grating.slits.append(slit_2)

                i += 1

            for slit in grating.slits:
                makeSources(slit, slit_height, 0, source_spacing)

            for slit in grating.slits:
                for i in range(0, slit_height - 1):
                    for source in slit[i].sources:
                        grating.pointSourcePositions.append(source.y)
                        grating.pointSourceAmplitudes.append(source.amplitude)

        else:
            center = grating.length / 2

            first_slit = Slit(grating.x, center - slit_width / 2, slit_width, num_sources, [])
            grating.slits.append(first_slit)

            i = 0

            while (grating.numberOfSlits - 1) / 2 > i:
                slit1_y = center + slit_width * 1.5 + 2 * i * slit_width
                slit2_y = center - slit_width * 2.5 - 2 * i * slit_width

                # Made slit 2 dimentional by making an array of slit height size, with identical slits.
                slit_1 = [Slit(grating.x, slit1_y, slit_width, num_sources, []) for i in range(slit_height)]
                slit_2 = [Slit(grating.x, slit2_y, slit_width, num_sources, []) for i in range(slit_height)]
                grating.slits.append(slit_1)
                grating.slits.append(slit_2)

                i += 1

            for slit in grating.slits:
                makeSources(slit, slit_height, 0, source_spacing)

            for slit in grating.slits:
                # for i in range(0, slit_height -1):
                for source in slit[i].sources:
                    grating.pointSourcePositions.append(source.y)
                    grating.pointSourceAmplitudes.append(source.amplitude)

            fh = open('pspos.txt','w')
            for pos in grating.pointSourcePositions:
                fh.write(str(pos)+'\n')
            fh.close()


def makeSources(Slit, SlitHeight, amplitude, spacing_type):
    if spacing_type.lower() == "uniform":

        # makes sources in each slit array
        # TODO: make differences in y-dimention on slit array

        for x in range(0, SlitHeight - 1):

            if Slit[x].num_sources == 1:

                testSource = PointSource(Slit[x].x, Slit[x].y + Slit[x].width / 2, amplitude)
                Slit[x].sources.append(testSource)

            elif Slit[x].num_sources == 2:

                spacing = Slit[x].width / (Slit[x].num_sources - 1)
                ts1 = PointSource(Slit[x].x, Slit[x].y, amplitude)
                ts2 = PointSource(Slit[x].x, Slit[x].y + Slit[x].width, amplitude)
                Slit[x].sources.append(ts1)
                Slit[x].sources.append(ts2)

            else:

                spacing = Slit[x].width / (Slit[x].num_sources - 1)
                ts_first = PointSource(Slit[x].x, Slit[x].y, amplitude)
                Slit[x].sources.append(ts_first)

                y_position = spacing

            for i in range(0, Slit[x].num_sources - 2):
                Slit[x].sources.append(PointSource(Slit[x].x, Slit[x].y + y_position, amplitude))
                y_position = y_position + spacing

            ts_last = PointSource(Slit[x].x, Slit[x].y + Slit[x].width, amplitude)
            Slit[x].sources.append(ts_last)

    elif spacing_type.lower() == "random":

        # makes sources in each slit array
        # TODO: make differences in y-dimention on slit array
        for x in range(0, SlitHeight - 1):
            for point in range(0, Slit[x].num_sources):
                y_position = random.rand(1, 1)[0][0] * Slit[x].width
                Slit[x].sources.append(PointSource(Slit[x].x, Slit[x].y + y_position, amplitude))
