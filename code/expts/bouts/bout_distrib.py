import pandas as pd
from matplotlib import pyplot as plt

from expts.utils.persist import load_data

pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_rows', 2000)
pd.set_option('display.float_format', '{:.5f}'.format)
boutsf = '~/data/ezfish/analysis/common/bouts.feather'
allbouts = load_data(boutsf)

nbouts = len(allbouts)

less250 = (len(allbouts.bout_duration[allbouts.bout_duration < 0.25]) / nbouts) * 100
less200 = (len(allbouts.bout_duration[allbouts.bout_duration < 0.2]) / nbouts) * 100

print(f"percentage bouts with duration < 200ms {less200} < 250ms {less250}")

omrbouts = allbouts[allbouts.omr_bout]

otherbouts = allbouts[~allbouts.omr_bout]

fig, axes = plt.subplots(3, 3, figsize=(15, 12))

(ax1, ax2, ax3), (ax4, ax5, ax6), (ax7, ax8, ax9) = axes

ax1.hist(allbouts.bout_initial_speed, bins=40)
ax1.set_title('bout initial speeds')

ax2.hist(allbouts.bout_initial_speed[allbouts.bout_initial_speed < 20], bins=10)
ax2.set_title('bout initial speeds up to 20 mm/s')

ax4.hist(allbouts.bout_duration, bins=40)
ax4.set_title('bout duration - all bouts')

ax5.hist(allbouts.bout_duration[allbouts.bout_duration < 0.5], bins=20)
ax5.set_title('bout duration up to 500ms - all bouts')

ax6.hist(omrbouts.bout_duration[omrbouts.bout_duration < 0.5], bins=20)
ax6.set_title('bout duration up to 500ms - omr bouts only')

ax7.hist(otherbouts.bout_duration, bins=40)
ax7.set_title('bout duration - non-omr bouts')

ax8.hist(otherbouts.bout_duration[otherbouts.bout_duration < 0.5], bins=20)
ax8.set_title('bout duration up to 500ms - non-omr bouts')

plt.show()

