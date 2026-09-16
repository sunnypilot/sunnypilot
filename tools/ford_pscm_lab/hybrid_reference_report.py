"""Build an offline command-comparison report; no simulated PSCM response."""
# ruff: noqa: E501
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


LABELS = ['149', '151', '157', '15a', '15b']
VARIANTS = ['action', 'geometry', 'direct', 'stronger', 'half', 'hybrid']
TITLES = {'action': 'Action only', 'geometry': 'Geometry only', 'direct': 'Direct path',
          'stronger': 'Stronger source', 'half': '50/50 blend', 'hybrid': 'Hybrid'}
COLORS = {'action': '#1971c2', 'geometry': '#d18a00', 'hybrid': '#087f5b', 'initial': '#bd3545'}


def load(path):
  with np.load(path) as z:
    return dict(zip(z['names'], z['rows'].T, strict=True))


def cells(values):
  return '<tr>'+''.join('<td>'+str(v)+'</td>' for v in values)+'</tr>'


def table(headers, rows):
  return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+x+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'


def plot(a, dest, title, window, direction, initial=None):
  t = a['t']
  mask = (t >= window[0]) & (t <= window[1])
  live = a['valid'][mask].astype(bool)
  x = t[mask]
  sign = 1 if direction == 'left' else -1
  fig, axes = plt.subplots(4, 1, figsize=(11.4, 9.2), sharex=True, gridspec_kw={'height_ratios': [2, 1.35, 1.35, .8]})
  fig.suptitle(title, x=.09, ha='left', fontsize=17, fontweight='bold')
  labels = ['Reference\n(wheel-equivalent °)', 'C0 command\n(m)', 'C1 command\n(rad)']
  for ax, key, ylabel in zip(axes, ['angle', 'c0', 'c1'], labels, strict=False):
    for name in ['geometry', 'action', 'hybrid']:
      y = a[name+'_'+key][mask]*sign*(1 if key == 'angle' else -1)
      ax.plot(x, np.where(live, y, np.nan), label=TITLES[name], color=COLORS[name], lw=2.1 if name == 'hybrid' else 1.6)
    if initial is not None:
      y = initial['hybrid_'+key][mask]*sign*(1 if key == 'angle' else -1)
      ax.plot(x, np.where(live, y, np.nan), label='Rejected first hybrid', color=COLORS['initial'], ls='--', lw=1.5)
    ax.set_ylabel(ylabel)
  axes[0].legend(loc='best', fontsize=9, framealpha=.95, ncol=2)
  axes[-1].plot(x, a['weight'][mask]*100, color=COLORS['hybrid'], lw=1.5)
  axes[-1].set_ylabel('Geometry\nassistance (%)')
  axes[-1].set_ylim(-5, 105)
  axes[-1].set_yticks([0, 50, 100])
  axes[-1].set_xlabel('Seconds from route start · positive values point into the named turn')
  for ax in axes:
    ax.grid(alpha=.2)
    ax.axhline(0, color='#868e96', lw=.7)
    ax.fill_between(x, 0, 1, where=(a['driver'][mask] > 0) & live, color='#89939e', alpha=.10,
                    transform=ax.get_xaxis_transform(), linewidth=0)
    ax.spines[['top', 'right']].set_visible(False)
    ax.margins(x=0)
  fig.text(.09, .018, 'Gray shading: recorded driver/override indication. These are replayed requests, not predicted wheel motion.',
           fontsize=9, color='#495057')
  fig.subplots_adjust(left=.10, right=.98, top=.92, bottom=.075, hspace=.12)
  fig.savefig(dest, dpi=150, facecolor='white')
  plt.close(fig)


def run(root, initial_root, dest):
  dest.mkdir(parents=True, exist_ok=True)
  arrays = {s: load(root/s/'commands.npz') for s in LABELS}
  reports = {s: json.loads((root/s/'report.json').read_text()) for s in LABELS}
  initial = {s: load(initial_root/s/'commands.npz') for s in ['15a', '15b']}
  all_a = {k: np.concatenate([a[k] for a in arrays.values()]) for k in arrays['15a']}
  live = all_a['valid'].astype(bool)
  ordinary = live & (abs(all_a['action_raw']) < .01) & (abs(all_a['geometry_raw']) < .01)
  events = [(s, e) for s, r in reports.items() for e in r['events']]
  retained, release_delta, entry_lead = [], [], []
  censored = []
  for s, e in events:
    a, h = [e['variants'][v] for v in ['action', 'hybrid']]
    if h['entry_geometry_extra_retained_fraction'] is not None:
      retained.append(h['entry_geometry_extra_retained_fraction'])
    if None not in (a['release_25_s'], h['release_25_s']):
      release_delta.append(h['release_25_s']-a['release_25_s'])
    elif a['release_25_s'] is not None:
      censored.append([s, e['id']])
    if None not in (a['entry_50_s'], h['entry_50_s']):
      entry_lead.append(a['entry_50_s']-h['entry_50_s'])
  metrics = {
    'route_labels': LABELS, 'unique_control_cycles': len(live), 'active_valid_cycles': int(live.sum()),
    'active_valid_seconds': sum(r['active_valid_s'] for r in reports.values()),
    'marked_windows_including_overlaps': len(events), 'entry_extra_eligible_windows': len(retained),
    'entry_geometry_extra_retained_p10_p50_p90': np.quantile(retained, [.1, .5, .9]).tolist(),
    'paired_reference_releases': len(release_delta), 'reference_release_delay_p50_p90_max': np.quantile(release_delta, [.5, .9, 1]).tolist(),
    'hybrid_release_not_observed_before_disengagement': censored,
    'paired_reference_entries': len(entry_lead), 'reference_entry_lead_p50_p90_max': np.quantile(entry_lead, [.5, .9, 1]).tolist(),
    'ordinary_cycles': int(ordinary.sum()), 'ordinary_p95_difference_from_action': {}, 'totals': {},
    'comparison_baseline_commit': '01f5d5429', 'report_scope': 'offline_command_comparison',
  }
  ordinary_rows, totals_rows, route_rows = [], [], []
  for v in VARIANTS:
    ordinary_diff = {k: np.quantile(abs(all_a[v+'_'+k]-all_a['action_'+k])[ordinary], [.5, .95, 1]).tolist() for k in ['angle', 'c0', 'c1']}
    metrics['ordinary_p95_difference_from_action'][v] = ordinary_diff
    ordinary_rows.append(cells([TITLES[v], *[f'{ordinary_diff[k][1]:.4f}' for k in ['angle', 'c0', 'c1']]]))
    sums = {k: sum(r['variants'][v][k] for r in reports.values()) for k in [
      'c0_bound_s', 'c1_bound_s', 'low_speed_c0_steps_over_025m', 'low_speed_c1_steps_over_005rad']}
    metrics['totals'][v] = sums
    totals_rows.append(cells([TITLES[v], f"{sums['c0_bound_s']:.1f}", f"{sums['c1_bound_s']:.1f}",
                             sums['low_speed_c0_steps_over_025m'], sums['low_speed_c1_steps_over_005rad']]))
  for s, r in reports.items():
    route_rows.append(cells([s, f"{r['cycles']:,}", f"{r['active_valid_s']/60:.2f}", len(r['events']),
                            'Logged separately' if s in ['15a', '15b'] else 'Reconstructed from logged plans']))
  sweep_rows = []
  for s in ['15a', '15b']:
    for row in json.loads((root/s/'sweep.json').read_text()):
      sweep_rows.append(cells([s, f"{row['start']:.3f}–{row['full']:.3f}", f"{row['power']:.0f}",
                               f"{row['geometry_entry_extra_retained_p10_p50_p95_max'][1]*100:.1f}%",
                               f"{row['release_later_than_action_s_p10_p50_p95_max'][-1]:.3f}", row['target_steps_over_20deg']]))
  event_rows = []
  for s, id_ in [('15a', 1), ('15a', 5), ('15b', 1), ('15b', 4), ('15b', 7)]:
    e = next(e for e in reports[s]['events'] if e['id'] == id_)
    a, g, h = [e['variants'][v] for v in ['action', 'geometry', 'hybrid']]
    event_rows.append(cells([f'{s} / {id_} {e["direction"]}',
                            f"{a['peak_angle_deg']:.0f} / {g['peak_angle_deg']:.0f} / <b>{h['peak_angle_deg']:.0f}</b>",
                            f"{a['peak_abs_c0']:.2f} / {g['peak_abs_c0']:.2f} / <b>{h['peak_abs_c0']:.2f}</b>",
                            f"{a['peak_abs_c1']:.3f} / {g['peak_abs_c1']:.3f} / <b>{h['peak_abs_c1']:.3f}</b>",
                            f"{h['release_25_s']-a['release_25_s']:+.3f}"]))
  plots = [
    ('15b', 'large-left', '15b · large left: geometry strength, action-led release', [164., 176.], 'left', False),
    ('15a', 'exit', '15a · left turn: geometry rebound during the exit', [188., 198.], 'left', False),
    ('15b', 'rearm', '15b · exit rebound caught and fixed offline', [43., 48.5], 'left', True),
    ('15b', 'conflict', '15b · source disagreement: the hybrid follows the action', [79., 85.], 'left', False),
    ('151', 'dip', '151 · a temporary action dip also reduces geometry assistance', [2590., 2603.], 'right', False),
    ('157', 'large-geometry', '157 · stronger requests do not establish that the path is correct', [166., 180.], 'right', False),
  ]
  for s, slug, title, window, direction, show_initial in plots:
    plot(arrays[s], dest/f'hybrid-{slug}.png', title, window, direction, initial.get(s) if show_initial else None)
  def get_image(slug):
    return f'<img src="hybrid-{slug}.png" alt="Reference, C0, C1 and geometry assistance over time">'
  report = f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ford action + geometry · offline hybrid</title><style>
:root{{color-scheme:light}}*{{box-sizing:border-box}}body{{font-family:system-ui,-apple-system,sans-serif;color:#17232e;background:#f4f6f8;margin:0;line-height:1.55}}
main{{max-width:1190px;margin:auto;padding:35px 25px 70px}}h1{{font-size:38px;letter-spacing:-1.2px;line-height:1.15;margin:12px 0 20px}}h2{{font-size:24px;margin:30px 0 12px}}h3{{font-size:19px}}
p{{max-width:1000px}}.eyebrow{{color:#556373;font-size:13px;letter-spacing:1px;text-transform:uppercase}}.lead{{font-size:21px;max-width:950px}}.card{{background:white;padding:24px;border:1px solid #dce3e9;border-radius:12px;margin:20px 0}}
.stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}.stats div{{background:#e4f3ec;padding:20px;border-radius:10px}}.stats strong{{font-size:30px;display:block;color:#087f5b}}.note{{color:#526171;font-size:14px}}.caution{{background:#fff4dc;border-left:4px solid #d18a00;padding:16px 20px}}
img{{max-width:100%;display:block;border:1px solid #e0e6eb;border-radius:8px;margin:16px 0}}table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{padding:11px 12px;border-bottom:1px solid #e1e7ed;text-align:left;white-space:nowrap}}th{{background:#edf2f6;font-size:13px}}.scroll{{overflow:auto}}code{{background:#eaf0f4;padding:2px 5px;border-radius:4px}}pre{{white-space:pre-wrap;background:#eef3f7;padding:16px;border-radius:8px}}summary{{cursor:pointer;font-weight:600;padding:12px 0}}a{{color:#1263a0}}li{{margin:8px 0}}
@media(max-width:700px){{main{{padding:20px 12px}}h1{{font-size:30px}}.stats{{grid-template-columns:1fr}}.card{{padding:16px}}}}
</style></head><body><main>
<div class="eyebrow">Ford Lightning · offline experiment · 16 September 2026</div>
<h1>Geometry for turn strength.<br>Action to lead the unwind.</h1>
<p class="lead">The revised hybrid produces the intended command pattern in many turns: requests close to geometry at the peak, then close to the action at the exit. It preserves the action reference for gentle bends. It does not resolve which source is right when they disagree.</p>
<div class="stats"><div><strong>4.33 vs 4.41 m</strong>Hybrid vs geometry peak C0<br>15b, large left</div><div><strong>0.50 vs 0.50 rad</strong>Same peak C1 on that turn<br>Both reach the field bound</div><div><strong>0.85 s earlier</strong>Hybrid reference releases before geometry<br>Matches action’s 25° crossing</div></div>
<p class="note">These are replayed requests using recorded vehicle motion. They are not predictions of the wheel response, path accuracy, comfort, or safety. This report evaluates requests offline; the repository deployment notes describe the current integration.</p>
<section class="card"><h2>The proposed rule</h2>
<ol><li><b>Start with the original model action.</b> Gentle requests stay with the action.</li>
<li><b>Add geometry’s extra demand</b> when geometry describes a tighter turn, both sources agree on direction, and the action supports meaningful demand.</li>
<li><b>Fade that extra demand as the action falls from its peak.</b> Half the peak action leaves at most a quarter of the extra geometry request. Zero or opposite action removes the boost.</li></ol>
<p>Both C0 and C1 receive <b>one combined curvature reference</b> through the existing scalar mapper and feedback. C0 uses the existing 7 m circular-arc calculation. C1 uses the existing heading calculation. This does not give one source to C0 and a conflicting source to C1.</p>
<p>Geometry here is the earlier, smoothed orientation-derived curvature reference from the first geometry drives. The latest direct-path controller is included as a separate comparison.</p>
<details><summary>Formula and tuning choices</summary><pre>H = A + gate(|G|) × (|A| / max(0.01, A_peak))² × (G − A)
Apply assistance only when A and G have the same sign and |G| &gt; |A|.
gate = smoothstep from 0 at |G| = 0.01/m to 1 at |G| = 0.02/m.
A_peak = largest same-direction action magnitude during the current geometry excursion.
Reset at inactive/invalid geometry, geometry sign change, or |G| ≤ 0.01/m.</pre>
<p>The 0.01/0.02 band and squared fade are explicit experimental tuning choices. They are not Ford constants. P/I gains, ordinary controller gates, upstream curvature limits and CAN field bounds are unchanged. The selector has peak memory; it is not a stateless average.</p></details></section>
<section class="card"><h2>Turn strength really reaches C0/C1</h2>
<p>On the large left, the hybrid reaches a 359° wheel-equivalent reference versus geometry’s 361° and action’s 218°. Around 170 s, its C0/C1 are −4.04 m / −0.50 rad, close to geometry’s −4.09 m / −0.50 rad. Around 173 s, hybrid and action both request −0.26 m / −0.0745 rad.</p>
{get_image('large-left')}
<p class="note">Raw CAN command signs above are retained. The chart flips signs so positive means into this left turn. C1’s 0.50 rad bound is a message-field bound; this replay cannot identify the PSCM’s physical limit.</p>
<p>Each cell below lists <b>action / geometry / hybrid</b>. Peaks need not occur at the same instant.</p>
{table(['Window','Peak reference °','Peak |C0| m','Peak |C1| rad','Hybrid − action release, s'],event_rows)}
<p class="note">Release is the first reference below 25° in the turn direction, sustained for 0.2 s after the action peak. It is not a measured wheel unwind time.</p></section>
<section class="card"><h2>Exit behavior: useful, but not a perfect phase detector</h2>
<p>In this 15a exit, the action-led fade removes geometry’s later extra demand. The hybrid reaches the reference release threshold with the action, roughly 0.50 s before geometry.</p>{get_image('exit')}
<p>The first prototype had a real flaw: after a geometry dip reset its memory, a tiny action rebound could authorize full geometry again. At 46.73 s on 15b, action requested 3.2°, but that prototype requested 103°. The revised denominator limits it to <b>4.3°</b>; C1 becomes −0.0095 rad rather than −0.1805 rad.</p>{get_image('rearm')}
<p class="caution"><b>The remaining ambiguity:</b> a temporary dip in the action also reduces assistance. The selector cannot know from that dip alone whether the road is ending the turn or the action is briefly weak. When sources point opposite ways, it follows the action and can lose geometry’s early entry.</p>
<details><summary>See the unfavorable cases</summary>
<p>15b: the action and geometry disagree on turn phase/direction. This rule keeps only about 5% of geometry’s eligible extra demand before the marked action peak. That is a deliberate source choice, not evidence the road needed less steering.</p>{get_image('conflict')}
<p>151: before a later action peak, the action briefly falls to a 26° request while geometry still requests 122°. Hybrid falls to 30°. This is the unresolved tradeoff in using action reductions to lead release.</p>{get_image('dip')}
<p>157: some geometry requests are far larger than the action (about 807° versus 266° peak in this window). The hybrid can inherit that demand and encounter the existing field bounds. Matching previous geometry numbers does not show that the model path is correct.</p>{get_image('large-geometry')}</details></section>
<section class="card"><h2>Across five routes</h2>
<p><b>{len(live):,} unique control cycles</b>, {metrics['active_valid_seconds']/60:.1f} minutes of active valid input, and {len(events)} previously marked windows, some overlapping. Median retained geometry extra demand during eligible entries is <b>{np.median(retained)*100:.0f}%</b>; the 10th percentile is {np.quantile(retained,.1)*100:.0f}%. This metric includes only same-direction entry samples where geometry already requests at least 50° and exceeds the action by more than 5°.</p>
<p>For {len(release_delta)} paired reference-release crossings, median added delay versus action is <b>{np.median(release_delta):.2f} s</b>, with a maximum of {max(release_delta):.2f} s. One additional window (157 / 5) disengages before hybrid’s 0.2 s release crossing can be observed. First crossings do not rule out a later rebound; the plots and final-crossing checks matter.</p>
{table(['Route suffix','Control cycles','Active valid minutes','Marked windows','Geometry source'],route_rows)}
<h3>Gentle requests stay near action</h3>
<p>For {int(ordinary.sum()):,} active valid samples where both source curvatures are below 0.01/m, these are the 95th-percentile absolute differences from action. Earlier integrator state and curvature-limiter history can still differ: hybrid’s worst C1 difference in this cohort is {metrics['ordinary_p95_difference_from_action']['hybrid']['c1'][2]:.4f} rad.</p>
{table(['Candidate','Reference difference °','C0 difference m','C1 difference rad'],ordinary_rows)}
<h3>Sharp low-speed changes remain</h3>
<p>At below 15 mph, count adjacent valid command changes greater than 0.25 m C0 or 0.05 rad C1. These counts include source changes and recorded driver-gate transitions; they are a diagnostic proxy, not a comfort score. The hybrid is <b>not a general fix for rapid actuation</b>.</p>
{table(['Candidate','C0 at field bound, s','C1 at field bound, s','C0 jumps','C1 jumps'],totals_rows)}
<p>The always-stronger rule retains geometry on exits. A 50/50 blend weakens peaks and changes gentle driving. The hybrid more closely matches the requested division of work, but requires an explicit compromise when source demand drops and then recovers.</p></section>
<section class="card"><h2>Sensitivity and validation</h2>
<p>Twelve settings were checked on each recent route. Smaller thresholds admit more preview, including more small-action assistance. Larger release exponents clear the extra request faster but discard more entry demand and often increase abrupt target changes. The selected 0.010–0.020/m band with power 2 is a compromise, not an optimized or vehicle-validated calibration.</p>
<details><summary>All 24 sensitivity results</summary>
{table(['Route','Curvature band /m','Fade power','Median entry extra retained','Max release delay vs action, s','Target jumps &gt;20°'],sweep_rows)}
<p class="note">Sensitivity alternatives replay references through the upstream curvature limiter. Full C0/C1/controller replay was run for the selected configuration, both initial and revised, and all five comparison baselines.</p></details>
<ul><li>20 prototype tests pass, including the exit-rebound regression, direction changes, input validity, causality and repeated model frames.</li>
<li>Native control-cycle replay checks finite C0/C1, field bounds, zero C2/C3, driver feedback suppression and identical validity gates. Real CAN packing/unpacking is checked every tenth cycle.</li>
<li>The first six-variant replay performed 347,256 CAN checks; the revised hybrid added 57,876. Reusing unchanged baseline columns was checked against a complete fresh 15a run: every output value matched exactly.</li>
<li>15a/15b join separately logged original action and geometry by exact model timestamp. Older geometry is reconstructed with recorded delay/model smoothing; speed uses the first consuming control sample.</li>
<li>All candidates see the same recorded wheel motion, road inputs and driver interventions. Their feedback states are recomputed, but the vehicle never responds to the hypothetical new commands. No new camera/model inference or PSCM dynamics are simulated.</li></ul>
<p><b>Recommendation:</b> keep this as the candidate hybrid design. It achieves the requested numeric pattern on several major turns and catches an exit flaw before deployment. Retain the action-dip and source-disagreement cases as explicit unresolved limitations. Comparison baseline: <code>01f5d5429</code>. The installed hybrid identifies itself as <code>geometry-assisted-action-feedback-v18</code>.</p>
<p><a href="geometry-action-hybrid-validation.json">Validation numbers and source fingerprints</a></p></section>
</main></body></html>'''
  (dest/'geometry-action-hybrid.html').write_text(report)
  metrics['sources_sha256'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in [
    Path(__file__), Path('tools/ford_pscm_lab/geometry_action_hybrid.py'),
    *[root/s/'report.json' for s in LABELS], *[root/s/'sweep.json' for s in ['15a', '15b']]]}
  (dest/'geometry-action-hybrid-validation.json').write_text(json.dumps(metrics, indent=2, allow_nan=False)+'\n')
  print(json.dumps({'report': str(dest/'geometry-action-hybrid.html'), 'metrics': metrics}, indent=2))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--output', type=Path, required=True)
  parser.add_argument('--root', type=Path, default=Path('.cache/ford_hybrid_guarded'))
  parser.add_argument('--initial-root', type=Path, default=Path('.cache/ford_hybrid'))
  args = parser.parse_args()
  run(args.root, args.initial_root, args.output)
