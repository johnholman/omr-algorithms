# refraction calc after Dunn & Fitzgerald 2020
#
import numpy as np
from matplotlib import pyplot as plt
from numpy import tan, arcsin, sin, arctan, cos

# n_a = 1.0  # diffractive index for air
# n_w = 1.333  # diffractive index for water
# n_p = 1.333  # diffractive index for plastic (we assume has no effect for the moment)
pi = np.pi


def theta_actual(theta_p, *, dw, da, n_w=1.333, n_a=1.0, dp=0.0):
    """ Return true angle from vertical of object with apparent angle thetap

    :param theta_p: percieved angle from the vertical of the object
    :param dw:  height of fish above top of plastic layer at bottom of lane
    :param dp:  thickness of plastic bottom of tank
    :param da:  distance from stimulus to bottom of tank
    :return:    the actual angle from the vertical
    """
    psi_p = arcsin((n_w / n_a) * sin(theta_p))
    psi_a = arcsin((n_w / n_a) * sin(theta_p))
    theta_a = arctan((dw * tan(theta_p) + dp * tan(psi_p) + da * tan(psi_a)) / (dw + dp + da))
    return theta_a

def xpos(theta, *, da, dw, n_w=1.333, n_a=1.0):
    xpos = dw * tan(theta) + da * tan(arcsin((n_w/n_a) * sin(theta)))
    return xpos

def plot_xpos():
    theta_p = np.linspace(0, 40 * pi/180, 1000)

    # diffraction with fish mid channel
    fig, ax = plt.subplots()
    for da in 4, 28, 52:
        x = xpos(theta_p, da=da, dw=4)
        ax.plot(x, theta_p * 180/pi, label=da)
    ax.set_xlabel('x position')
    ax.set_ylabel('perceived angle')
    ax.legend()
    ax.grid()


    # no diffraction with fish mid channel
    theta_p = np.linspace(0, pi/2.1, 1000)
    n_a = n_w = 1
    fig, ax = plt.subplots()
    for da in 4, 28, 52:
        x = xpos(theta_p, da=da, dw=4, n_a = 1, n_w=n_w)
        ax.plot(x, theta_p * 180/pi, label=da)
    ax.set_xlabel('x position')
    ax.set_ylabel('perceived angle')
    ax.legend()
    ax.grid()



def g(theta_p, *, da, dw, n_w=1.333, n_a=1.0):
    """ Return derivative of x with respect to theta_p

    :param theta_p: perceived angle from vertical of a point distance x away
    :param da:
    :param dw:
    :return:
    """
    r = n_w/n_a

    ret = dw / cos(theta_p)**2 + da * (r * cos(theta_p))/(1 - (r* sin(theta_p))**2)**(3/2)
    return ret

def plot_g():

    # diffraction with fish mid channel
    theta_p = np.linspace(0, 48 * pi/180, 1000)
    fig, ax = plt.subplots()
    for da in 4, 28, 52:
        dx = g(theta_p, da=da, dw=4)
        ax.plot(theta_p * 180/pi, dx, label=da)
    ax.set_xlabel('perceived angle')
    ax.set_ylabel('dx/dtheta')
    ax.legend()
    ax.grid()

    # no diffraction
    theta_p = np.linspace(0, 45 * pi/180, 1000)
    n_w = n_a = 1
    fig, ax = plt.subplots()
    for da in 4, 28, 52:
        dx = g(theta_p, da=da, dw=4, n_a = n_a, n_w=n_w)
        ax.plot(theta_p * 180/pi, dx, label=da)
    ax.set_xlabel('perceived angle')
    ax.set_ylabel('dx/dtheta')
    ax.legend()
    ax.grid()

def plot_compression():

    theta_p = np.linspace(0, 48 * pi/180, 1000)
    dw=4
    fig, ax = plt.subplots()
    for da in 4, 28, 52:
        c = g(theta_p, da=da, dw=dw)/ (da + dw)
        ax.plot(theta_p * 180/pi, c, label=da)
    ax.set_xlabel('perceived angle')
    ax.set_ylim(0, 10)
    ax.set_ylabel('compression')
    ax.legend()
    ax.grid()

    theta_p = np.linspace(0, 45 * pi/180, 1000)
    dw=4
    n_w = n_a = 1
    fig, ax = plt.subplots()
    for da in 4, 28, 52:
        c = g(theta_p, da=da, dw=dw, n_a=n_a, n_w=n_w) / (da + dw)
        ax.plot(theta_p * 180/pi, c, label=da)
    ax.set_xlabel('perceived angle')
    ax.set_ylabel('compression')
    ax.legend()
    ax.grid()


def plot_theta():
    theta_p = np.linspace(0, pi/3, 10000)
    # heights above stimulus at mid channel: 8, 32, 56
    # height of tank above stimulus (da): 4, 28, 52
    fig, ax = plt.subplots()
    for da in 4, 28, 52:
        theta_a = theta_actual(theta_p, da=da, dw=1)
        ax.plot(theta_a * 180/pi, theta_p * 180/pi, label=da)
    ax.set_xlabel('actual angle')
    ax.set_ylabel('perceived angle')
    ax.legend()
    ax.grid()

    fig, ax = plt.subplots()
    for da in 4, 28, 52:
        theta_a = theta_actual(theta_p, da=da, dw=4)
        ax.plot(theta_a * 180/pi, theta_p * 180/pi, label=da)
        print(theta_a)
    ax.set_xlabel('actual angle')
    ax.set_ylabel('perceived angle')
    ax.legend()
    ax.grid()

    fig, ax = plt.subplots()
    for da in 4, 28, 52:
        theta_a = theta_actual(theta_p, da=da, dw=8)
        ax.plot(theta_a * 180/pi, theta_p * 180/pi, label=da)
    ax.set_xlabel('actual angle')
    ax.set_ylabel('perceived angle')
    ax.legend()
    ax.grid()

    # fig, ax = plt.subplots()
    # for da in 4, 28, 52:
    #     theta_a = theta_actual(theta_p, da=da, dw=4)
    #     ax.plot(theta_a * 180/pi, theta_p * 180/pi, legend=da)
    # ax.set_xlabel('actual angle')
    # ax.set_ylabel('perceived angle')
    # ax.legend()
    # ax.grid()
    #
    # fig, ax = plt.subplots()
    # for da in 4, 28, 52:
    #     theta_a = theta_actual(theta_p, da=da, dw=8)
    #     ax.plot(theta_a * 180/pi, theta_p * 180/pi, legend=da)
    # ax.set_xlabel('actual angle')
    # ax.set_ylabel('perceived angle')
    # ax.legend()
    # ax.grid()




    print("done")

if __name__ == '__main__':
    plot_xpos()
    plot_g()
    # plot_theta()
    plot_compression()
    plt.show()
