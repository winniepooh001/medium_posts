import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np

color_set = [c for c in mcolors.CSS4_COLORS.keys() if 'black' not in c and 'blue' not in c][1::11]
def plot_comparison(truth, observation, model_result, total_len, title, file_name=None, x=None, additional_text=None,
                    init_pos=0):
    fig, ax = plt.subplots(1,1,figsize=(12,12))

    x = np.arange(total_len) if x is None else x
    if len(observation) > 1:
        num_ob = len(observation)
        ax.scatter(x[init_pos:num_ob], observation[init_pos:num_ob], c='b', label='observation')
    else:
        num_ob = observation[0]

    if len(truth) == 1:
        ax.axhline(truth, color='k', linestyle='solid', label='truth')
    else:
        print('true values')
        ax.plot(x[init_pos:], truth[init_pos:], color='k', linestyle='solid', label='truth')
    i = 0

    for label, y_ in model_result.items():
        print(label)
        ax.plot(x[init_pos:],y_[init_pos:], c=color_set[i], alpha=0.5,
                linestyle=np.random.choice(['dotted','dashed', 'dashdot']), label=label)
        i = (i+1)%(len(color_set))

    if num_ob > init_pos:
        ax.fill_between(x[init_pos:], 0, 1, where=x[init_pos:]>x[num_ob],
                        color='green', alpha=0.9, transform=ax.get_xaxis_transform())
    else:
        ax.set_facecolor('green')
    ax.relim()
    plt.suptitle(title)
    plt.legend(loc=1)
    if additional_text is not None:
        plt.text(.99, .01, additional_text, ha='right', va='bottom', style='italic',
                 bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10},transform=ax.transAxes)

    if file_name:
        plt.savefig(f'{file_name}.png')
    else:
        plt.show()
    plt.close()