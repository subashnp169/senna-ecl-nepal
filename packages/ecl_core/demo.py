"""Demo entry point."""

from __future__ import annotations

from .types import Loan, Stage
from .staging import classify_stage
from .pd import marginal_pd_from_cumulative, amortisation_profile, discount_factors
from .ecl import lifetime_ecl


def run_demo() -> None:
    loans = [
        Loan(name="AlphaIndustries", principal=2_000_000, origination_rating="BBB",
             current_rating="BBB", lgd=0.45, eir=0.035, maturity=5, region="europe"),
        Loan(name="GammaRetail", principal=5_000_000, origination_rating="BBB",
             current_rating="BB-", lgd=0.45, eir=0.045, maturity=5, region="europe"),
        Loan(name="ZetaServices", principal=800_000, origination_rating="BB",
             current_rating="CCC", lgd=0.45, lgd_downturn=0.65, eir=0.060,
             maturity=3, days_past_due=95, region="europe"),
    ]
    cum_pd = [0.01, 0.025, 0.04, 0.06, 0.08]
    marginals = marginal_pd_from_cumulative(cum_pd)
    for ln in loans:
        staging = classify_stage(ln)
        res = lifetime_ecl(ln.principal, 0.02, marginals, ln.lgd if staging.stage != Stage.STAGE_3 else (ln.lgd_downturn or ln.lgd), ln.eir, ln.amort_type, staging.stage.value)
        print(f"{ln.name}: stage={staging.stage.value} 12m={res['ecl_12m']} lifetime={res['ecl_lifetime']}")


if __name__ == "__main__":
    run_demo()
