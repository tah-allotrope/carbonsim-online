from engine.playtest import run_playtest
for seed in [1, 2, 3]:
    for diff in ['easy', 'standard', 'hard']:
        r = run_playtest(seed=seed, difficulty=diff)
        print(f"seed={seed} diff={diff} years={r['completed_years']} cash={r['final_cash']:.0f} penalties={r['total_penalties']:.0f} gap={r['compliance_gap']:.2f}")
