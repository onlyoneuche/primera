"""Generate a WCAG contrast record for actual Daybreak text/control colours."""
from ml.config import ROOT

PAIRS=[
 ('Body text','#17324D','#F4FAF8',4.5),('Card text','#17324D','#FFFFFF',4.5),
 ('Secondary text','#4B6277','#FFFFFF',4.5),('Welcome secondary text','#4B6277','#EDF6FC',4.5),
 ('Primary button text','#FFFFFF','#0B7A5E',4.5),('Selected option text','#17324D','#FFF9E6',4.5),
 ('Inline error','#B4430B','#FFFFFF',4.5),('Lower-risk label','#0B4D3B','#D5F3E6',4.5),
 ('Higher-risk label','#5A3E00','#FFF1CC',4.5),('Support links','#075C47','#FFFFFF',4.5),
 ('Input/option boundary','#768A80','#FFFFFF',3),('Selected boundary','#0B7A5E','#FFF9E6',3),
 ('Focus outline','#1F6FEB','#FFFFFF',3),('Focus outline on page','#1F6FEB','#F4FAF8',3),
 ('Current progress marker border','#B47D00','#FFFFFF',3),
]


def luminance(hex_value):
    values=[int(hex_value[i:i+2],16)/255 for i in (1,3,5)]
    linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values]
    return sum(v*w for v,w in zip(linear,[.2126,.7152,.0722]))


def main():
    lines=['# Daybreak contrast checks','',
           'Computed from the CSS text and interactive-control colours. Decorative lines, illustration fills, and the supplementary progress path do not convey information without text.',
           '', '| Use | Foreground | Background | Ratio | Required | Result |',
           '| --- | --- | --- | ---: | ---: | --- |']
    passed=True
    for name,fg,bg,minimum in PAIRS:
        light,dark=sorted([luminance(fg),luminance(bg)],reverse=True)
        ratio=(light+.05)/(dark+.05)
        passed &= ratio>=minimum
        lines.append(f'| {name} | {fg} | {bg} | {ratio:.2f}:1 | {minimum:.1f}:1 | {"Pass" if ratio>=minimum else "Fail"} |')
    out=ROOT/'docs/design/previews/contrast.md'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text('\n'.join(lines)+'\n')
    if not passed: raise SystemExit('A Daybreak contrast pair failed; inspect the generated report.')
    print(f'All {len(PAIRS)} contrast pairs passed.')


if __name__=='__main__': main()
