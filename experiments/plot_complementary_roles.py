"""Plot saved experiment 007 records only; never generate or train a world."""
import json
from pathlib import Path
import statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RESULTS=Path(__file__).resolve().parents[1]/'results/complementary-roles-v1'
NAMES=('full','no_feedback','no_teaching','disconnected','online','misaligned')
LABELS=('Both paths','No feedback','No teaching','Both cut','Joint online','Misaligned')
COLORS=('#167a58','#c67622','#7855ac','#777777','#2275b4','#c84955')


def main():
    data=json.loads((RESULTS/'metrics.json').read_text())
    runs=data['runs']
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,3,figsize=(14,5),layout='constrained')
    specs=(('noisy_position_mse','Tracking with noisy position sensor'),
           ('gain_mse','Learned response curve'),('HH','Motion with both sensors noisy'))
    for ax,(key,title) in zip(axes,specs):
        for i,(name,color) in enumerate(zip(NAMES,COLORS)):
            ms=[r['metrics'] for r in runs if r['variant']==name]
            values=[m['by_regime']['HH']['loop_mse'] if key=='HH' else m[key] for m in ms]
            ax.scatter([i+.045*(j-2) for j in range(5)],values,color=color,s=28,alpha=.7)
            ax.scatter([i],[statistics.mean(values)],color=color,marker='_',s=250,linewidths=3)
        ax.set(yscale='log',title=title,ylabel='Mean squared error (log scale; lower is better)')
        ax.set_xticks(range(6),LABELS,rotation=35,ha='right')
        ax.grid(axis='y',alpha=.2)
    fig.suptitle('Complementary roles · one fixed run per seed\nDots: five seeds; bars: arithmetic means',fontsize=15)
    fig.savefig(RESULTS/'comparisons.png',dpi=160)
    fig.savefig(RESULTS/'comparisons.svg')
    plt.close(fig)
    fig,axes=plt.subplots(2,3,figsize=(14,8),layout='constrained')
    for seed,ax in enumerate(axes.flat):
        if seed==5:
            ax.axis('off')
            handles=[plt.Line2D([0],[0],color='black',linestyle='--',label='Simulator relationship')]
            handles += [plt.Line2D([0],[0],color=c,label=l) for c,l in zip(COLORS[:5],LABELS[:5])]
            ax.legend(handles=handles,loc='center',frameon=False)
            ax.text(.5,.15,'Misaligned uses the same retained curve as Both paths.\nOnly its evaluation feedback query is shifted.',
                    transform=ax.transAxes,ha='center',va='center',fontsize=10)
            continue
        rs={r['variant']:r for r in runs if r['seed']==seed}
        grid=rs['full']['grid']; x=[g['x'] for g in grid]
        ax.plot(x,[g['truth'] for g in grid],'k--',lw=2)
        for name,color in zip(NAMES[:5],COLORS[:5]):
            ax.plot(x,[g['prediction'] for g in rs[name]['grid']],color=color,lw=1.6,alpha=.85)
        ax.set(title=f'Seed {seed}',xlabel='Position',ylabel='Action response gain',ylim=(.1,1.))
        ax.grid(alpha=.15)
    fig.suptitle('Retained forms as smooth response relationships\n32 evaluator-only positions; no category boundaries or test-time retained learning',fontsize=15)
    fig.savefig(RESULTS/'learned-curves.png',dpi=160)
    fig.savefig(RESULTS/'learned-curves.svg')
    print('Saved comparisons and learned-curves figures (PNG/SVG) from existing records.')


if __name__=='__main__': main()
