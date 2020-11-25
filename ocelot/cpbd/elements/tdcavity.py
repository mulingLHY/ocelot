import numpy as np

from ocelot.cpbd.transformations.first_order import TransferMap
from ocelot.cpbd.transformations.second_order import SecondTM
from ocelot.cpbd.high_order import m_e_GeV
from ocelot.common.globals import speed_of_light
from ocelot.cpbd.elements.element import Element


class TDCavity(Element):
    """
    Transverse deflecting cavity - by default kick in horizontal plane

    l - length [m]
    v - voltage [GV/m]
    freq - frequency [Hz]
    phi - phase in [deg]
    tilt - tilt of cavity in [rad]
    """
    default_tm = TransferMap
    additional_tms = [SecondTM]

    def __init__(self, l=0., freq=0.0, phi=0.0, v=0., tilt=0.0, eid=None):
        Element.__init__(self, eid)
        self.l = l
        self.v = v  # in GV
        self.freq = freq  # Hz
        self.phi = phi  # in deg
        self.tilt = tilt

    def __str__(self):
        s = 'TDCavity : '
        s += 'id = ' + str(self.id) + '\n'
        s += 'l    =%8.4f m\n' % self.l
        s += 'v    =%8.5f GV\n' % self.v
        s += 'freq =%8.1e Hz\n' % self.freq
        s += 'phi  =%8.2f deg\n' % self.phi
        s += 'tilt =%8.2f deg\n' % (self.tilt * 180.0 / np.pi)
        return s

    def create_r_matrix(self):
        """
         R - matrix for TDS - NOT TESTED
         """

        def tds_R_z(z, energy, freq, v, phi):
            """

            :param z:  length [m]
            :param freq: freq [Hz]
            :param v: voltage in [GeV]
            :param phi: phase [deg]
            :param energy: Energy in [GeV]
            :return:
            """
            phi = phi * np.pi / 180.

            gamma = energy / m_e_GeV
            igamma2 = 0.
            k0 = 2 * np.pi * freq / speed_of_light
            if gamma != 0:
                igamma2 = 1. / (gamma * gamma)
            if gamma > 1:
                pref = m_e_GeV * np.sqrt(gamma ** 2 - 1)
                K = v * k0 / pref
            else:
                K = 0.
            cos_phi = np.cos(phi)
            cos2_phi = np.cos(2 * phi)

            rm = np.eye(6)

            rm[0, 1] = z
            rm[0, 4] = -z * K * cos_phi / 2.
            rm[1, 4] = -K * cos_phi
            rm[2, 3] = z
            rm[4, 5] = - z * igamma2 / (1. - igamma2)
            rm[5, 0] = rm[1, 4]
            rm[5, 1] = rm[0, 4]
            rm[5, 4] = -z * K ** 2 * cos2_phi / 6
            return rm

        r_z_e = lambda z, energy: tds_R_z(z, energy, freq=self.freq, v=self.v * z / self.l, phi=self.phi)
        return r_z_e
