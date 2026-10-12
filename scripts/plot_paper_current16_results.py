"""从论文证据包复现十区域、六全局七算法图表。"""
from dataclasses import replace
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import argparse
import csv
import hashlib
import json
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pubfig as pf
import pubtab
from openpyxl import Workbook
from openpyxl.styles import Font

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'vault/Results/Evidence/paper-fullspeed-update-20261009'
OUT = ROOT / 'outputs/paper-fullspeed-update-20261009'
FIGURES = ROOT / 'vault/Writing/figures'
METHODS = ['R-ALNS', 'A-ALNS', 'HCGA', 'HPSO', 'HeDEA', 'RK-HMA', 'Auto-Hybrid']
COLORS = ['#A6ADB4', '#CBB681', '#B3A0BB', '#91B3A4', '#C69382', '#0072B2', '#D55E00']
THEME = replace(pf.themes.get_theme('nature'), font_family=['DejaVu Sans'])
SPEC = pf.FigureSpec(name='auto-hybrid-current16', font_family='DejaVu Sans')

def load_rows():
    manifest = json.loads((EVIDENCE / 'manifest.json').read_text(encoding='utf-8'))
    data = EVIDENCE / 'data.csv'
    assert hashlib.sha256(data.read_bytes()).hexdigest() == manifest['canonicalData']['sha256']
    rows = list(csv.DictReader(data.open(encoding='utf-8-sig', newline='')))
    scenes = {r['scene'] for r in rows}
    assert len(rows) == 560 and len(scenes) == 16
    assert '1000-20-0-0-12' not in scenes and '2000-20-0-0-12' in scenes
    cells = {(r['scene'], r['method'], int(r['perRun'])) for r in rows}
    assert len(cells) == len(rows)
    assert cells == {(s, m, k) for s in scenes for m in METHODS for k in range(5)}
    for r in rows:
        assert int(r['seedId']) == 10 + int(r['perRun'])
        assert int(r['tasks']) == int(r['scene'].split('-')[0])
        assert int(r['satellites']) == int(r['scene'].split('-')[1])
        value = float(r['profitRatePercent'])
        assert np.isfinite(value) and 0 <= value <= 100.001
        if r['profit'] and r['totalPriority']:
            assert abs(value - 100 * float(r['profit']) / float(r['totalPriority'])) < 1e-8
    for scene in scenes:
        for method in METHODS:
            assert len({r['actualSeed'] for r in rows if r['scene']==scene and r['method']==method}) == 5
    return rows

def scenes_for(rows, distribution):
    scenes = sorted({r['scene'] for r in rows if r['sceneType'] == distribution},
                    key=lambda s:tuple(map(int,s.split('-')[:2])))
    assert len(scenes) == (10 if distribution=='regional' else 6)
    return scenes

def cell_rows(rows, scene, method):
    return sorted([r for r in rows if r['scene']==scene and r['method']==method], key=lambda r:int(r['perRun']))

def values(rows, scene, method):
    return np.asarray([float(r['profitRatePercent']) for r in cell_rows(rows,scene,method)])

def timing(group):
    # 与参考论文合同相同：五条 solver 全有才用 solver；否则用无粗粒度轮询的 process。
    for field in ('solverSeconds','processSeconds'):
        if all(r[field] for r in group):
            if field == 'processSeconds' and any('poll' in r['timingScope'].lower() for r in group):
                continue
            return float(np.mean([float(r[field]) for r in group])), field
    return None, 'unavailable'

def display_mean(group, field):
    mean=sum((Decimal(r[field]) for r in group),Decimal(0))/Decimal(len(group))
    return str(mean.quantize(Decimal('0.01'),rounding=ROUND_HALF_UP))

def label_check(fig):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    boxes = []
    for axis in fig.axes:
        low,high=axis.get_ylim()
        visible = [t for y,t in zip(axis.get_yticks(),axis.get_yticklabels()) if low <= y <= high]
        for t in [axis.title,axis.xaxis.label,axis.yaxis.label,*axis.get_xticklabels(),*visible]:
            if t.get_text():
                boxes.append((t.get_text(),t.get_window_extent(renderer)))
    for legend in fig.legends:
        boxes.extend((t.get_text(),t.get_window_extent(renderer)) for t in legend.get_texts())
    for name,box in boxes:
        assert box.x0>=-0.5 and box.y0>=-0.5 and box.x1<=fig.bbox.width+0.5 and box.y1<=fig.bbox.height+0.5, name
    for index,(name,box) in enumerate(boxes):
        for other,other_box in boxes[index+1:]:
            assert not box.overlaps(other_box), (name,other)

def export(fig,stem,height):
    label_check(fig)
    pf.batch_export(fig,FIGURES/stem,formats=('png','svg'),spec=SPEC,width='double',
                    height_mm=height,dpi=400,transparent=False,trim=False,svg_fonttype='none')
    plt.close(fig)

def grouped_bars(rows,distribution):
    scenes=scenes_for(rows,distribution)
    means=np.asarray([[np.mean(values(rows,s,m)) for m in METHODS] for s in scenes])
    fig,axis=plt.subplots(figsize=(7.2,3.1))
    pf.bar(means,category_names=[str(i) for i in range(1,len(scenes)+1)],series_names=METHODS,
           category_spacing=1.0,x_label=f'{distribution.capitalize()} scenario',y_label='Profit rate (%)',
           color_palette=COLORS,grouped_total_span=0.82,grouped_bar_width_ratio=0.90,
           grouped_bar_edgecolor='#333333',grouped_bar_line_width=0.25,
           legend_show=False,show_x_grid=False,show_y_grid=True,theme=THEME,ax=axis)
    axis.set_ylim(0,105)
    axis.tick_params(labelsize=9)
    handles=[plt.Rectangle((0,0),1,1,facecolor=c,edgecolor='#333333',linewidth=.25) for c in COLORS]
    fig.legend(handles,METHODS,loc='upper center',ncol=7,frameon=False,
               bbox_to_anchor=(.54,.99),fontsize=7.8,handlelength=1.2,columnspacing=.9)
    fig.subplots_adjust(left=.09,right=.99,top=.85,bottom=.17)
    export(fig,f'auto_hybrid_current16_{distribution}',78)

def boxplots(rows):
    scenes=scenes_for(rows,'regional')
    fig,axes=plt.subplots(5,2,figsize=(7.2,9.25))
    methods=METHODS[-2:]
    colors=COLORS[-2:]
    for index,(axis,scene) in enumerate(zip(axes.flat,scenes)):
        series=[values(rows,scene,m) for m in methods]
        pf.box(series,category_names=methods,category_spacing=1.0,color_palette=colors,
               box_face_alpha=.28,box_width=.52,line_color='#333333',show_means=False,
               show_fliers=False,tick_direction='out',show_full_box=False,
               show_x_grid=False,show_y_grid=True,theme=THEME,ax=axis)
        for pos,(vals,color) in enumerate(zip(series,colors),start=1):
            axis.scatter(pos+np.asarray([-.10,-.05,0,.05,.10]),vals,s=12,
                         facecolor=color,edgecolor='white',linewidth=.35,zorder=4)
        all_values=np.concatenate(series)
        pad=max(.04,float(np.ptp(all_values))*.10)
        axis.set_ylim(max(0,float(np.min(all_values))-pad),min(100.2,float(np.max(all_values))+pad))
        n,m=scene.split('-')[:2]
        axis.set_title(f'({"abcdefghij"[index]}) Regional {index+1}\n({n} tasks, {m} satellites)',fontsize=8.5,pad=5)
        axis.tick_params(axis='x',labelsize=7.8)
        axis.tick_params(axis='y',labelsize=8)
        axis.set_ylabel('Profit rate (%)' if index%2==0 else '')
    fig.subplots_adjust(left=.10,right=.99,top=.95,bottom=.045,wspace=.28,hspace=.70)
    export(fig,'rk_hma_auto_hybrid_current10_boxplots',235)

def result_table(rows,distribution):
    scenes=scenes_for(rows,distribution)
    workbook=Workbook()
    sheet=workbook.active
    sheet.title='Results'
    sheet.append(['Scenario','Algorithm','Profit rate (%)','Elapsed (s)'])
    stats=[]
    for index,scene in enumerate(scenes,start=1):
        displayed=[display_mean(cell_rows(rows,scene,m),'profitRatePercent') for m in METHODS]
        best=max(map(float,displayed))
        for method,rate in zip(METHODS,displayed):
            group=cell_rows(rows,scene,method)
            time,scope=timing(group)
            sheet.append([f'{distribution[0].upper()}{index}' if method==METHODS[0] else '',
                          method,rate,'--' if time is None else display_mean(group,scope)])
            if float(rate)==best:
                sheet.cell(sheet.max_row,3).font=Font(bold=True)
            vals=values(rows,scene,method)
            stats.append(dict(sceneType=distribution,scenario=index,scene=scene,method=method,
                              mean=float(np.mean(vals)),std=float(np.std(vals,ddof=1)),
                              min=float(np.min(vals)),max=float(np.max(vals)),median=float(np.median(vals)),
                              elapsed=time,timingField=scope))
    xlsx=OUT/f'{distribution}_results.xlsx'
    workbook.save(xlsx)
    tex=pubtab.xlsx2tex(xlsx,output=OUT/f'{distribution}_pubtab.tex',sheet=0,theme='three_line',
                       col_spec='llrr',font_size='small',preview=False)
    body=re.search(r'\\begin\{tabular\}[^\n]*\n(.*?)\\end\{tabular\}',tex,re.S)
    if body is None:
        raise ValueError('pubtab tabular output missing')
    content=body.group(1)
    # 只复用 pubtab 生成的数据行；longtable 页头、续页和组内不分页由论文控制。
    content=content.split('\\midrule',1)[1].rsplit('\\bottomrule',1)[0].strip()
    lines=[]
    seen=0
    for line in content.splitlines():
        if '&' in line and line.rstrip().endswith('\\\\'):
            if seen and seen%7==0:
                lines.append('\\midrule')
            seen+=1
            if seen%7:
                line=line.rstrip()+'*'
        lines.append(line)
    assert seen==len(scenes)*7
    caption=f'Mean profit rates and elapsed times on {distribution} scenarios (five runs per method).'
    header='Scenario & Algorithm & Profit rate (\\%) & Elapsed (s) \\\\'
    longtable='\n'.join([
        '\\begingroup','\\small','\\renewcommand{\\arraystretch}{1.03}',
        '\\setlength{\\tabcolsep}{4pt}', '\\setlength{\\LTleft}{0pt}','\\setlength{\\LTright}{0pt}',
        '\\makeatletter',
        '\\renewcommand{\\LT@makecaption}[3]{\\LT@mcol\\LT@cols c{\\hbox to\\z@{\\hss\\parbox[t]{\\linewidth}{\\sffamily\\small #1{\\textbf{#2}\\par}#3\\par\\vspace{6pt}}\\hss}}}',
        '\\makeatother',
        '\\begin{longtable}{@{}p{0.12\\linewidth}p{0.28\\linewidth}>{\\raggedleft\\arraybackslash}p{0.25\\linewidth}>{\\raggedleft\\arraybackslash}p{0.25\\linewidth}@{}}',
        '\\caption{'+caption+'}\\\\','\\toprule',header,'\\midrule','\\endfirsthead',
        '\\multicolumn{4}{@{}l}{\\small\\sffamily\\textbf{Table \\thetable} (continued)}\\\\',
        '\\toprule',header,'\\midrule','\\endhead','\\midrule',
        '\\multicolumn{4}{r@{}}{\\small Continued on next page}\\\\','\\endfoot',
        '\\bottomrule','\\endlastfoot',*lines,'\\end{longtable}','\\endgroup'])
    (OUT/f'{distribution}_results.tex').write_text(longtable+'\n',encoding='utf-8')
    return stats

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tables-only',action='store_true',help='只更新结果表；收益不变时保留已有图形')
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    rows=load_rows()
    stats=[]
    for distribution in ('regional','global'):
        if not args.tables_only:
            grouped_bars(rows,distribution)
        stats.extend(result_table(rows,distribution))
    if not args.tables_only:
        boxplots(rows)
    qa=dict(rows=len(rows),cells=len(stats),runsPerCell=5,statistics=stats,
            layout=('tables only; unchanged profit inputs preserve existing figures' if args.tables_only else
                    '2 grouped-bar figures; 10 regional boxplot panels; rendered labels in canvas with no overlaps'),
            tools={'pubfig':pf.__version__,'pubtab':pubtab.__version__},
            scope='descriptive comparisons; different actual seeds and historical/current batches')
    (OUT/'figure-table-qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for distribution in ('regional','global'):
        print(distribution,{m:round(float(np.mean([r['mean'] for r in stats if r['sceneType']==distribution and r['method']==m])),6) for m in METHODS})
    print('Validated 560 rows / 112 cells; generated 2 result tables.' if args.tables_only else
          'Validated 560 rows / 112 cells; generated 3 PNG+SVG figures and 2 result tables.')

if __name__=='__main__':
    main()
