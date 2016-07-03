# Set graph styling to common styles
from matplotlib import pyplot as plt
import matplotlib
import seaborn as sns
plt.style.use('seaborn-poster')
matplotlib.rcParams['font.family'] = 'League Spartan'

# So I don't have to keep looking up how to do this...
def f_int(x):
    return format(int(x), ',')
# some matplotlib functions pass in a position, which we don't need
def mf_int(x, pos):
    return f_int(x)
def format_axis_labels_with_commas(axis):
    axis.set_major_formatter(matplotlib.ticker.FuncFormatter(mf_int))
def format_plt_labels_with_commas(plt):
    # I have no idea what the 111 magic number is. It was in a quora post and seems to work.
    axis = plt.get_subplot(111)
    format_axis_labels_with_commas(axis)
def annotate(axis, text, xy, xy_text):
    axis.annotate("${:,}".format(int(text)), xy=xy,
             xytext=xy_text,
             arrowprops=dict(facecolor='black', connectionstyle="arc3,rad=.2"),
             fontsize=14)

def find_smallest(s):
    smallest = min(s)
    index_of = s.index(smallest)
    return(index_of, smallest)

def find_biggest(s):
    biggest = max(s)
    index_of = s.index(biggest)
    return(index_of, biggest)

def annotate_smallest(axis, s, location=None):
    (x, y) = find_smallest(s)
    if location == None:
        location = (x * Decimal('1.1'), y * Decimal('.9'))

    annotate(axis, y, (x, y), location)

def annotate_biggest(axis, s, location=None):
    (x, y) = find_biggest(s)
    if location == None:
        location = (x * Decimal('0.9'), y * Decimal('1.1'))

    annotate(axis, y, (x, y), location)

def plot(s, x_label='', y_label='', y_lim=None, title=''):
    fig, ax1 = plt.subplots()
    ax1.plot(s, 'b')
    ax1.set_ylabel(y_label, color='b')
    if y_lim:
        ax1.set_ylim(y_lim)
    ax1.set_xlabel(x_label)

    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    plt.title(title)
    plt.show()

def plot_two(s1, s2, s1_title='', s2_title='', x_label='', title='', y_lim=None):
    fig, ax1 = plt.subplots()
    ax1.plot(s1, 'b')
    ax1.set_ylabel(s1_title, color='b')
    ax1.set_xlabel(x_label)
    if y_lim:
        ax1.set_ylim(y_lim)
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    format_axis_labels_with_commas(ax1.get_yaxis())

    ax2 = ax1.twinx()
    ax2.plot(s2, 'g')
    ax2.set_ylabel(s2_title, color='g')
    if y_lim:
        ax2.set_ylim(y_lim)
    for tl in ax2.get_yticklabels():
        tl.set_color('g')
    format_axis_labels_with_commas(ax2.get_yaxis())

    plt.xlabel(x_label)
    plt.title(title)
    plt.show()
